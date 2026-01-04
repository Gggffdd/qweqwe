from pydantic import BaseModel
from datetime import datetime
from typing import Optional, List

class UserBase(BaseModel):
    telegram_id: int
    username: Optional[str] = None
    first_name: Optional[str] = None
    last_name: Optional[str] = None

class UserCreate(UserBase):
    pass

class User(UserBase):
    id: int
    is_admin: bool
    created_at: datetime
    
    class Config:
        from_attributes = True

class CategoryBase(BaseModel):
    name: str
    emoji: Optional[str] = None
    is_game: bool = True
    icon_url: Optional[str] = None

class CategoryCreate(CategoryBase):
    pass

class Category(CategoryBase):
    id: int
    created_at: datetime
    
    class Config:
        from_attributes = True

class ProductBase(BaseModel):
    name: str
    description: Optional[str] = None
    price: float
    image_url: Optional[str] = None
    category_id: int
    delivery_data: str

class ProductCreate(ProductBase):
    pass

class Product(ProductBase):
    id: int
    is_available: bool
    created_at: datetime
    category: Optional[Category] = None
    
    class Config:
        from_attributes = True

class OrderBase(BaseModel):
    product_id: int
    payment_method: str
    payment_details: Optional[str] = None

class OrderCreate(OrderBase):
    pass

class Order(OrderBase):
    id: int
    user_id: int
    status: str
    total_amount: float
    created_at: datetime
    completed_at: Optional[datetime] = None
    product: Optional[Product] = None
    
    class Config:
        from_attributes = True

class ProductViewBase(BaseModel):
    product_id: int

class ProductViewCreate(ProductViewBase):
    pass

class ProductView(ProductViewBase):
    id: int
    user_id: int
    viewed_at: datetime
    product: Optional[Product] = None
    
    class Config:
        from_attributes = True

class OrderStatusUpdate(BaseModel):
    status: str
