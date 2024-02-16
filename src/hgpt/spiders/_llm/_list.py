import os
from typing import List

from langchain.output_parsers import OutputFixingParser, PydanticOutputParser
from langchain.prompts.chat import ChatPromptTemplate, HumanMessagePromptTemplate, SystemMessagePromptTemplate
from pydantic.v1 import BaseModel, Field


class RealEstateDetailPage(BaseModel):
    reasoning: str = Field(
        description="Detailed step-by-step reasoning explaining why the assistant thinks that this url is pointing to a detail page."
    )
    url: str = Field(
        description="Url of the detail real estate page. Does not need to be a full url, can only be its part."
    )


class RealEstateListPage(BaseModel):
    detail_pages: List[RealEstateDetailPage] = Field(
        description="List of real estates detail pages. A detail page is a page that contains a detailed information about the real estate, such as its price etc."
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
        | OutputFixingParser.from_llm(parser=output_parser, llm=model)
    )
