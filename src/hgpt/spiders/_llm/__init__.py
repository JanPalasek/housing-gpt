from hgpt.spiders._llm._detail import RealEstate
from hgpt.spiders._llm._detail import create_chain as create_detail_chain
from hgpt.spiders._llm._list import RealEstateListPage
from hgpt.spiders._llm._list import create_chain as create_list_chain
from hgpt.spiders._llm._spider import LLMSpider

__all__ = ["LLMSpider", "create_detail_chain", "create_list_chain", "RealEstate", "RealEstateListPage"]
