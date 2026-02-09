from pydantic import BaseModel
from typing import Optional,Literal

class TicketCreate(BaseModel):
    title:str
    description:Optional[str]
    priority:Literal["Low","Medium","High"]
    customer_id: Optional[int] = None
