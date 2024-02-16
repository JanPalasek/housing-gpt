from pathlib import Path
from urllib.parse import urlparse

import scrapy
from langchain_openai import ChatOpenAI
from scrapy.responsetypes import Response
from scrapy_playwright.page import PageMethod

from hgpt.settings import ROOT_URL
from hgpt.spiders._llm._detail import RealEstate
from hgpt.spiders._llm._detail import create_chain as create_detail_chain
from hgpt.spiders._llm._list import RealEstateListPage
from hgpt.spiders._llm._list import create_chain as create_list_chain
from hgpt.spiders._utils import ensure_full_url

META = {"playwright": True, "playwright_page_coroutines": [PageMethod("wait_for_timeout", 20000)]}

BASE_DOMAIN = f"https://{urlparse(ROOT_URL).netloc}"


class LLMSpider(scrapy.Spider):
    name = "llm"

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        # create crawl chain
        model = ChatOpenAI(model="gpt-3.5-turbo-0125")
        self.list_chain = create_list_chain(model)
        self.detail_chain = create_detail_chain(model)

    def start_requests(self):
        # go to root request url, it should be a parse list
        yield scrapy.Request(ROOT_URL, meta=META, callback=self.parse_list)

    async def parse_list(self, response: Response, **kwargs):
        # extract all urls and process them by gpt
        urls = response.xpath("//a/@href").getall()
        input_ = "\n".join(urls)
        response: RealEstateListPage = await self.list_chain.ainvoke({"input": input_})

        # go over all real estate detail urls and search them
        for real_estate in response.detail_pages:
            yield scrapy.Request(ensure_full_url(real_estate.url, BASE_DOMAIN), meta=META, callback=self.parse_detail)

        # follow the next page link
        yield scrapy.Request(ensure_full_url(real_estate.url, BASE_DOMAIN), meta=META, callback=self.parse_list)

    async def parse_detail(self, response: Response, **kwargs):
        # get only text content
        text_nodes = response.xpath("//body//*[not(self::script or self::style)]/text()").getall()
        input_ = " ".join([text.strip() for text in text_nodes if text.strip()])

        Path("detail.txt").write_text(input_)
        response: RealEstate = await self.detail_chain.ainvoke({"input": input_})
        return response.dict()
