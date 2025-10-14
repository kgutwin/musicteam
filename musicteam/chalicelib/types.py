from pydantic import BaseModel


class TestRow(BaseModel):
    count: int
