from typing import List

from fastapi import APIRouter, HTTPException, status

from app.models.item import Item, ItemCreate, ItemUpdate

router = APIRouter()

# In-memory database for demo purposes
items_db = [
    Item(id=1, name="Item 1", description="Description for Item 1", price=10.99),
    Item(id=2, name="Item 2", description="Description for Item 2", price=20.50),
]


@router.get("/", response_model=List[Item])
async def get_items():
    """Get all items"""
    return items_db


@router.get("/{item_id}", response_model=Item)
async def get_item(item_id: int):
    """Get a specific item by ID"""
    for item in items_db:
        if item.id == item_id:
            return item
    raise HTTPException(
        status_code=status.HTTP_404_NOT_FOUND,
        detail=f"Item with ID {item_id} not found"
    )


@router.post("/", response_model=Item, status_code=status.HTTP_201_CREATED)
async def create_item(item: ItemCreate):
    """Create a new item"""
    new_id = max([i.id for i in items_db], default=0) + 1
    new_item = Item(id=new_id, **item.model_dump())
    items_db.append(new_item)
    return new_item


@router.put("/{item_id}", response_model=Item)
async def update_item(item_id: int, item_update: ItemUpdate):
    """Update an existing item"""
    for i, item in enumerate(items_db):
        if item.id == item_id:
            update_data = item_update.model_dump(exclude_unset=True)
            updated_item = item.model_copy(update=update_data)
            items_db[i] = updated_item
            return updated_item
    raise HTTPException(
        status_code=status.HTTP_404_NOT_FOUND,
        detail=f"Item with ID {item_id} not found"
    )


@router.delete("/{item_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_item(item_id: int):
    """Delete an item"""
    for i, item in enumerate(items_db):
        if item.id == item_id:
            items_db.pop(i)
            return
    raise HTTPException(
        status_code=status.HTTP_404_NOT_FOUND,
        detail=f"Item with ID {item_id} not found"
    )
