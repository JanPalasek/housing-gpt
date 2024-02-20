import logging
import sys
from datetime import datetime
from urllib.parse import urlparse

import scrapy
from langchain_openai import ChatOpenAI
from scrapy.responsetypes import Response
from scrapy_playwright.page import PageMethod

from hgpt.spiders._llm._detail import RealEstate
from hgpt.spiders._llm._detail import create_chain as create_detail_chain
from hgpt.spiders._llm._list import RealEstateListPage
from hgpt.spiders._llm._list import create_chain as create_list_chain

META = {"playwright": True, "playwright_page_coroutines": [PageMethod("wait_for_timeout", 30000)]}


class LLMSpider(scrapy.Spider):
    name = "llm"

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        handler = logging.StreamHandler(sys.stdout)
        formatter = logging.Formatter("%(asctime)s - %(name)s - %(levelname)s - %(message)s")
        handler.setFormatter(formatter)
        logging.getLogger(self.logger.name).addHandler(handler)

        self.searched_detail_pages = {}

    def start_requests(self):
        # create crawl chain
        model = ChatOpenAI(model=self.settings.get("OPENAI_MODEL"))
        self.list_chain = create_list_chain(model)
        model = ChatOpenAI(model=self.settings.get("OPENAI_MODEL"))
        self.detail_chain = create_detail_chain(model)

        # go to root request url, it should be a parse list
        for url in self.settings.get("ROOT_URLS"):
            self.logger.info("Submitting url to queue '%s'...", url)
            self.searched_detail_pages[urlparse(url).netloc] = 0
            yield scrapy.Request(url, meta=META, callback=self.parse_list)

    def _continue_scraping(self, url: str) -> bool:
        return self.searched_detail_pages[urlparse(url).netloc] < self.settings.get("MAX_DETAIL_PAGES")

    async def parse_list(self, response: Response):
        # scraped max pages => stop
        if not self._continue_scraping(response.url):
            return

        # extract all urls, remove duplicates
        urls = response.xpath("//a/@href").getall()
        urls = list(set(urls))

        # process urls by gpt
        input_ = "\n".join(urls)
        try:
            self.logger.info("Started extracting list page on url '%s'...", response.url)
            result: RealEstateListPage = await self.list_chain.ainvoke({"input": input_, "current_url": response.url})
            self.logger.info("Stopped extracting '%s'. Next page: %s", response.url, result.next_list_page)
        except Exception as exc:
            self.logger.error("An error was raised when processing LIST url '%s'. Error: %s", response.url, exc)
            return

        # go over all real estate detail urls and search them
        for url in result.detail_page_urls:
            # scraped max pages => break
            new_url = response.urljoin(url)
            if not self._continue_scraping(new_url):
                return
            self.searched_detail_pages[urlparse(new_url).netloc] += 1
            yield scrapy.Request(new_url, meta=META, callback=self.parse_detail)

        # follow the next page link
        yield scrapy.Request(response.urljoin(result.next_list_page), meta=META, callback=self.parse_list)

    async def parse_detail(self, response: Response):
        # get only text content
        text_nodes = response.xpath("//body//*[not(self::script or self::style)]/text()").getall()
        input_ = " ".join([text.strip() for text in text_nodes if text.strip()])

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
