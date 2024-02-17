import scrapy
from langchain_openai import ChatOpenAI
from scrapy.responsetypes import Response
from scrapy_playwright.page import PageMethod

from hgpt.settings import ROOT_URL
from hgpt.spiders._llm._detail import RealEstate
from hgpt.spiders._llm._detail import create_chain as create_detail_chain
from hgpt.spiders._llm._list import RealEstateListPage
from hgpt.spiders._llm._list import create_chain as create_list_chain

META = {"playwright": True, "playwright_page_coroutines": [PageMethod("wait_for_timeout", 20000)]}


class LLMSpider(scrapy.Spider):
    name = "llm"

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        # create crawl chain
        model = ChatOpenAI(model="gpt-4-0125-preview")
        self.list_chain = create_list_chain(model)
        model = ChatOpenAI(model="gpt-4-0125-preview")
        self.detail_chain = create_detail_chain(model)

    def start_requests(self):
        # go to root request url, it should be a parse list
        yield scrapy.Request(ROOT_URL, meta=META, callback=self.parse_list)

    async def parse_list(self, response: Response):
        # extract all urls, remove duplicates
        urls = response.xpath("//a/@href").getall()
        urls = list(set(urls))

        # process urls by gpt
        input_ = "\n".join(urls)
        result: RealEstateListPage = await self.list_chain.ainvoke({"input": input_, "current_url": response.url})

        # go over all real estate detail urls and search them
        for url in result.detail_page_urls:
            yield scrapy.Request(response.urljoin(url), meta=META, callback=self.parse_detail)

        # follow the next page link
        yield scrapy.Request(response.urljoin(result.next_list_page), meta=META, callback=self.parse_list)

    async def parse_detail(self, response: Response) -> dict:
        # get only text content
        text_nodes = response.xpath("//body//*[not(self::script or self::style)]/text()").getall()
        input_ = " ".join([text.strip() for text in text_nodes if text.strip()])

        # parse output
        result: RealEstate = await self.detail_chain.ainvoke({"input": input_})
        result_dict = result.dict()
        result_dict["url"] = response.url
        return result_dict
