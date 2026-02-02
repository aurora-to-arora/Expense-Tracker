from pydantic import BaseModel, Field
from datetime import date, datetime
from typing import Optional

class ExpenseCreate(BaseModel):
    amount: float = Field(..., gt=0)
    category: str
    description: Optional[str] = None
    date: date

class ExpenseResponse(BaseModel):
    id: str
    amount: float
    category: str
    description: Optional[str]
    date: date
    created_at: datetime

    class Config:
        orm_mode = True
