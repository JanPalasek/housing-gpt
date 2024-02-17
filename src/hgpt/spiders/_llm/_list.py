import os
from typing import List

from langchain.output_parsers import OutputFixingParser, PydanticOutputParser
from langchain.prompts.chat import ChatPromptTemplate, HumanMessagePromptTemplate, SystemMessagePromptTemplate
from pydantic.v1 import BaseModel, Field


class RealEstateListPage(BaseModel):
    reasoning: str = Field(
        description="Detailed step-by-step reasoning explaining what kind of urls, based on the input data, do the real estates have. It must also explain which page is the next. The assistant should use both input and current url in the reasoning process."
    )
    detail_page_urls: List[str] = Field(
        description="List of real estates detail pages urls. A detail page is a page that contains a detailed information about the real estate, such as its price etc. The urls do not need to be full urls. It can only be parts."
    )
    next_list_page: str = Field(
        default=None,
        description="Url pointing to the next page in the pagination. Ideally, it should be a 'next list' url.",
    )


def create_chain(model):
    output_parser = PydanticOutputParser(pydantic_object=RealEstateListPage)
    return (
        ChatPromptTemplate.from_messages(
            [
                SystemMessagePromptTemplate.from_template_file(
                    os.path.join(os.path.dirname(__file__), "sys-list.md"), input_variables=[]
                ),
                HumanMessagePromptTemplate.from_template_file(
                    os.path.join(os.path.dirname(__file__), "user-list.md"), input_variables=[]
                ),
            ]
        ).partial(format_instructions=output_parser.get_format_instructions())
        | model
        | OutputFixingParser.from_llm(parser=output_parser, llm=model, max_retries=3)
    )
