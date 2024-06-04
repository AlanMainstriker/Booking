from typing import Optional
from sqlmodel import SQLModel, Field

class User(SQLModel, table=True):
    id: Optional[int] = Field(primary_key=True, default=None)
    first_name: str
    last_name: str
    email: str
    password: str


class Hotel(SQLModel, table=True):
    id: Optional[int] = Field(primary_key=True, default=None)
    name: str
    country: str
    town: str
    rate: int
    price_per_night: int


class Contract(SQLModel, table=True):
    id: Optional[int] = Field(primary_key=True, default=None)
    user_id: int
    hotel_id: int
    nights: int
    total_price: int

