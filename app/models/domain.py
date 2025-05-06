from pydantic import BaseModel, Field, ConfigDict, field_validator
from datetime import datetime
from typing import Optional, List

class CategoryBase(BaseModel):
    name: str
    description: Optional[str] = None

class CategoryCreate(CategoryBase):
    pass

class Category(CategoryBase):
    id: int
    created_at: datetime
    
    model_config = ConfigDict(from_attributes=True)

class TransactionBase(BaseModel):
    amount: float
    description: Optional[str] = None
    date: datetime = Field(default_factory=datetime.now)
    category_id: Optional[int] = None

class TransactionCreate(TransactionBase):
    # Replace validator with field_validator in Pydantic v2
    @field_validator('amount')
    def amount_must_be_nonzero(cls, v):
        if v == 0:
            raise ValueError('Amount cannot be zero')
        return v

class Transaction(TransactionBase):
    id: int
    created_at: datetime
    
    model_config = ConfigDict(from_attributes=True)

class TransactionWithCategory(Transaction):
    category: Optional[Category] = None