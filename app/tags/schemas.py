import pydantic as pd


class TagSchema(pd.BaseModel):
    name: str
