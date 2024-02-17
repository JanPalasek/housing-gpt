import os
from typing import List

from langchain.output_parsers import OutputFixingParser, PydanticOutputParser
from langchain.prompts.chat import ChatPromptTemplate, HumanMessagePromptTemplate, SystemMessagePromptTemplate
from pydantic.v1 import BaseModel, Field


class Location(BaseModel):
    address: str = Field(default=None, description="Address of the property. If it is not specified, use null.")
    floor_level: int = Field(default=None, description="Floor level of the real estate (if there is any).")
    total_floor_levels: int = Field(default=None, description="How many total floors does the building have.")


class Size(BaseModel):
    floor_area: float = Field(
        description="Total floor area of the real estate. This area typically also includes size of loggia, size of built-in furniture. Typically in squared meters."
    )
    usable_floor_area: float = Field(
        description="Usable floor area of the real estate. This information typically excludes some in-built furniture etc."
    )
    balcony: bool = Field(
        default=None, description="If the real estate has a balcony, this field must be true. Otherwise false."
    )
    balcony_area: float = Field(default=None, description="Size of the balcony. Typically described in meters squared.")
    loggia: bool = Field(
        default=None, description="If this real estate has a loggia, this field must be true. Otherwise false."
    )
    loggia_area: float = Field(default=None, description="Size of the loggia.")
    cellar: bool = Field(
        default=None, description="If the real estate has a cellar, this field must be true. Otherwise false."
    )
    cellar_area: float = Field(default=None, description="Size of the cellar.")
    pantry: bool = Field(
        default=None, description="If the flat has a pantry, this field must be true. Otherwise false."
    )
    pantry_area: float = Field(default=None, description="Size of the pantry.")


class PropertyState(BaseModel):
    new_building: bool = Field(default=None, description="If the real estate is new, then this mut be true.")
    built_year: int = Field(default=None, description="Year when the property was built.")
    reconstructed_year: int = Field(default=None, description="Year when the property was last reconstructed.")
    revitalized_year: int = Field(default=None, description="Year when the real estate was last revitalized.")
    electrical_wiring: bool = Field(
        default=None, description="If true, then the wirings are new or were reconstructed."
    )
    pipes: bool = Field(default=None, description="If true, then the pipes are new or were reconstructed")
    insulated: bool = Field(default=None, description="If the building is insulated, this field must be true.")


class RealEstate(BaseModel):
    """
    Represents information parsed from a real estate.
    """

    price: float = Field(
        default=None,
        description="Price of the real-estate property. If there is not number describing the price, it should be null.",
    )
    additional_fees: bool = Field(
        default=False,
        description="Sometimes the price is not complete and it is also necessary to pay for real estate agent etc. If so, this field must be true.",
    )
    monthly_fees: float = Field(
        default=None, description="Monthly fees that the owners are expected to pay in this property."
    )
    layout: str = Field(
        default=None, description="Layout of the real estate. Typically something like '3+kk', '4+1' etc."
    )
    size: Size = Field(description="Size properties of the real estate.")
    location: Location = Field(description="Field 'location' describes the location of the apartment.")
    state: PropertyState = Field(description="Describes, what shape the property is in.")
    image_urls: List[str] = Field(default=[], description="Urls to images showing the property.")


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
        | OutputFixingParser.from_llm(parser=output_parser, llm=model, max_retries=3)
    )
