from datetime import datetime
from pydantic import BaseModel


class Queries(BaseModel):
    created: list[datetime]
    type: str
    status: list[str]
