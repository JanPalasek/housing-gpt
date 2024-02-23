import re
from datetime import datetime

import scrapy
from langchain_openai import ChatOpenAI
from scrapy.responsetypes import Response
from scrapy_playwright.page import PageMethod

from hgpt.spiders._llm import RealEstate, create_detail_chain
from hgpt.utils import get_clean_hostname

META = {"playwright": True, "playwright_page_coroutines": [PageMethod("wait_for_timeout", 30000)]}


class SRealitySpider(scrapy.Spider):
    name = "sreality"
    LIST_REGEX = r"(http[s]?:\/\/)?(www\.sreality\.cz)?\/detail"

    def start_requests(self):
        # create crawl chain
        model = ChatOpenAI(model=self.settings.get("OPENAI_MODEL"))
        self.detail_chain = create_detail_chain(model)

        self.max_detail_pages = {get_clean_hostname(k): v for k, v in self.settings.get("MAX_DETAIL_PAGES").items()}
        self.allowed_domains = list(self.max_detail_pages.keys())

        # go to root request url, it should be a parse list
        self.searched_detail_pages = {}
        for url in self.settings.get("ROOT_URLS"):
            self.logger.info("Submitting url to queue '%s'...", url)
            self.searched_detail_pages[get_clean_hostname(url)] = 0
            yield scrapy.Request(url, meta=META, callback=self.parse_list)

    def _continue_scraping(self, url: str) -> bool:
        hostname = get_clean_hostname(url)
        if hostname not in self.searched_detail_pages:
            self.logger.error("Hostname '%s' not in searched_detail_pages", hostname)
            return False
        if hostname not in self.max_detail_pages:
            self.logger.error("Hostname '%s' not in max_detail_pages", hostname)
            return False
        return self.searched_detail_pages[hostname] < self.max_detail_pages[hostname]

    async def parse_list(self, response: Response):
        # scraped max pages => stop
        if not self._continue_scraping(response.url):
            return

        # extract all urls, remove duplicates
        urls = response.xpath("//a/@href").getall()
        urls = [url for url in urls if re.match(SRealitySpider.LIST_REGEX, url)]
        urls = list(set(urls))

        next_list_url = response.xpath("//a[contains(@class, 'paging-next')]/@href").getall()[0]

        # go over all real estate detail urls and search them
        for url in urls:
            # scraped max pages => break
            new_url = response.urljoin(url)
            if not self._continue_scraping(new_url):
                return
            self.searched_detail_pages[get_clean_hostname(new_url)] += 1
            yield scrapy.Request(new_url, meta=META, callback=self.parse_detail)

        # follow the next page link
        yield scrapy.Request(response.urljoin(next_list_url), meta=META, callback=self.parse_list)

    async def parse_detail(self, response: Response):
        # get only text content
        text_title = response.xpath("//div[contains(@class, 'property-title')]//text()").getall()
        text_content = response.xpath("//div[contains(@class, 'description')]//p/text()").getall()
        text_table = response.xpath("//div[contains(@class, 'params')]//text()").getall()
        input_ = " ".join([text.strip().replace("\xa0", " ") for text in text_title if text.strip()])
        input_ += "\n\n" + " ".join([text.strip().replace("\xa0", " ") for text in text_content if text.strip()])
        input_ += "\n\n" + " ".join([text.strip().replace("\xa0", " ") for text in text_table if text.strip()])

        # parse output
        try:
            self.logger.info("Started extracting detail page information on url '%s'...", response.url)
            result: RealEstate = await self.detail_chain.ainvoke({"input": input_})
            self.logger.info(
                "Finished extracting detail page information on url '%s'... Price: %s, address: %s",
                response.url,
                result.price,
                result.location.address,
            )
        except Exception as exc:
            self.logger.error("An error was raised when processing DETAIL url '%s'. Error: %s", response.url, exc)
            return

        result_dict = result.dict()
        result_dict["url"] = response.url
        result_dict["dt"] = datetime.now()
        yield result_dict
