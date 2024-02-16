import os

from langchain.output_parsers import OutputFixingParser, PydanticOutputParser
from langchain.prompts.chat import ChatPromptTemplate, HumanMessagePromptTemplate, SystemMessagePromptTemplate
from pydantic.v1 import BaseModel, Field


class RealEstate(BaseModel):
    """
    Represents information parsed from a real estate.
    """

    price: float = Field(
        default=None,
        description="Price of the real-estate property. If there is not number describing the price, it should be null.",
    )
    address: str = Field(default=None, description="Address of the property.")


def create_chain(model):
    output_parser = PydanticOutputParser(pydantic_object=RealEstate)
    return (
        ChatPromptTemplate.from_messages(
            [
                SystemMessagePromptTemplate.from_template_file(
                    os.path.join(os.path.dirname(__file__), "sys-detail.md"), input_variables=[]
                ),
                HumanMessagePromptTemplate.from_template_file(
                    os.path.join(os.path.dirname(__file__), "user-detail.md"), input_variables=[]
                ),
            ]
        ).partial(format_instructions=output_parser.get_format_instructions())
        | model
        | OutputFixingParser.from_llm(parser=output_parser, llm=model)
    )
