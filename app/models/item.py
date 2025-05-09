from pydantic import BaseModel, Field


class ItemBase(BaseModel):
    """Base item model with common attributes"""
    name: str = Field(..., min_length=1, max_length=100)
    description: str = Field(..., min_length=1)
    price: float = Field(..., gt=0)


class ItemCreate(ItemBase):
    """Model for creating a new item"""
    pass


class ItemUpdate(BaseModel):
    """Model for updating an item (all fields optional)"""
    name: str | None = Field(None, min_length=1, max_length=100)
    description: str | None = Field(None, min_length=1)
    price: float | None = Field(None, gt=0)


class Item(ItemBase):
    """Complete item model with ID"""
    id: int

    class Config:
        from_attributes = True
