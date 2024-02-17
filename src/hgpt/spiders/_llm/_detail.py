import os

from langchain.output_parsers import OutputFixingParser, PydanticOutputParser
from langchain.prompts.chat import ChatPromptTemplate, HumanMessagePromptTemplate, SystemMessagePromptTemplate
from pydantic.v1 import BaseModel, Field


class Location(BaseModel):
    """Location of the real estate."""

    address: str = Field(default=None, description="Address of the property. If it is not specified, use null.")
    floor_level: int = Field(default=None, description="Floor level of the real estate (if there is any).")
    total_floor_levels: int = Field(
        default=None,
        description="How many total floors does the building have. Fill only if the information is present in the text.",
    )


class Size(BaseModel):
    """Size of the real estate."""

    floor_area: float = Field(
        description="Total floor area of the real estate. This area typically also includes size of loggia, size of built-in furniture. Typically in squared meters."
    )
    usable_floor_area: float = Field(
        description="Usable floor area of the real estate. This information typically excludes some in-built furniture etc."
    )
    balcony_area: float = Field(
        default=0,
        description="Size of the balcony. If the real estate does not have a balcony, must be 0.",
    )
    loggia_area: float = Field(
        default=0, description="Size of the loggia. If the real estate does not have a loggia, must be 0."
    )
    cellar_area: float = Field(
        default=0, description="Size of the cellar. If the real estate does not have a cellar, must be 0."
    )
    pantry_area: float = Field(
        default=0, description="Size of the pantry. Should only contain number if property has a pantry."
    )


class State(BaseModel):
    """Information about what shape the property is in."""

    new_building: bool = Field(description="If the real estate is new, then this mut be true.")
    built_year: int = Field(description="Year when the property was built.")
    reconstructed_year: int = Field(description="Year when the property was last reconstructed.")


class RealEstate(BaseModel):
    """
    Represents information parsed from a real estate.
    """

    price: float = Field(description="Price of the real-estate property.", required=True, ge=0)
    additional_fees: bool = Field(
        description="Sometimes the price is not complete and it is also necessary to pay for real estate agent etc. If so, this field must be true.",
    )
    monthly_fees: float = Field(
        default=None, description="Monthly fees that the owners are expected to pay in this property."
    )
    layout: str = Field(description="Layout of the real estate. Typically something like '3+kk', '4+1' etc.")
    size: Size = Field(description="Size properties of the real estate.")
    location: Location = Field(description="Field 'location' describes the location of the apartment.")
    state: State = Field(description="Describes, what shape the property is in.")


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
