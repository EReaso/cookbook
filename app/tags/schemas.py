import pydantic as pd


class TagSchema(pd.BaseModel):
    name: str

    @pd.validator("name")
    def name_to_lower(cls, v):
        return v.lower()
