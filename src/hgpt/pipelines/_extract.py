import os

from langchain.chat_models.base import BaseChatModel
from langchain.output_parsers import OutputFixingParser, PydanticOutputParser
from langchain.prompts.chat import ChatPromptTemplate, HumanMessagePromptTemplate, SystemMessagePromptTemplate
from langchain_openai import ChatOpenAI
from pydantic.v1 import BaseModel, Field


class RealEstate(BaseModel):
    price: float = Field(
        default=None,
        description="Price of the real-estate property. If there is not number describing the price, it should be null.",
    )
    address: str = Field(default=None, description="Address of the property.")


def extract(input_: str, model: BaseChatModel) -> RealEstate:
    output_parser = PydanticOutputParser(pydantic_object=RealEstate)
    chain = (
        ChatPromptTemplate.from_messages(
            [
                SystemMessagePromptTemplate.from_template_file(os.path.join(__package__, "sys-extract.txt")),
                HumanMessagePromptTemplate.from_template(os.path.join(__package__, "sys-extract.txt")),
            ]
        ).partial(format_instructions=output_parser.get_format_instructions())
        | model
        | OutputFixingParser(parser=output_parser, retry_chain=model)
    )
    response: RealEstate = chain.invoke({"input": input_})
    return response


class ExtractPipeline:
    def __init__(self) -> None:
        model = ChatOpenAI()
        output_parser = PydanticOutputParser(pydantic_object=RealEstate)
        self.chain = (
            ChatPromptTemplate.from_messages(
                [
                    SystemMessagePromptTemplate.from_template_file(os.path.join(__package__, "sys-extract.txt")),
                    HumanMessagePromptTemplate.from_template(os.path.join(__package__, "sys-extract.txt")),
                ]
            ).partial(format_instructions=output_parser.get_format_instructions())
            | model
            | OutputFixingParser(parser=output_parser, retry_chain=model)
        )

    def process_item(self, item, spider):
        response: RealEstate = self.chain.invoke({"input": item})
        return response.json()
