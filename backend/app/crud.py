from sqlalchemy.orm import Session
from . import models, schemas
from typing import List, Optional

def get_user_by_telegram_id(db: Session, telegram_id: int):
    return db.query(models.User).filter(models.User.telegram_id == telegram_id).first()

def create_user(db: Session, user: schemas.UserCreate):
    db_user = models.User(**user.dict())
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    return db_user

def get_or_create_user(db: Session, telegram_id: int, **kwargs):
    user = get_user_by_telegram_id(db, telegram_id)
    if not user:
        user_data = schemas.UserCreate(telegram_id=telegram_id, **kwargs)
        user = create_user(db, user_data)
    return user

def get_categories(db: Session, is_game: Optional[bool] = None):
    query = db.query(models.Category)
    if is_game is not None:
        query = query.filter(models.Category.is_game == is_game)
    return query.all()

def get_products(db: Session, category_id: Optional[int] = None):
    query = db.query(models.Product).filter(models.Product.is_available == True)
    if category_id:
        query = query.filter(models.Product.category_id == category_id)
    return query.all()

def get_product(db: Session, product_id: int):
    return db.query(models.Product).filter(models.Product.id == product_id).first()

def create_product(db: Session, product: schemas.ProductCreate):
    db_product = models.Product(**product.dict())
    db.add(db_product)
    db.commit()
    db.refresh(db_product)
    return db_product

def create_order(db: Session, order: schemas.OrderCreate, user_id: int):
    product = get_product(db, order.product_id)
    if not product:
        return None
    
    db_order = models.Order(
        **order.dict(),
        user_id=user_id,
        total_amount=product.price
    )
    db.add(db_order)
    db.commit()
    db.refresh(db_order)
    return db_order

def get_user_orders(db: Session, user_id: int):
    return db.query(models.Order).filter(models.Order.user_id == user_id).all()

def update_order_status(db: Session, order_id: int, status: str):
    order = db.query(models.Order).filter(models.Order.id == order_id).first()
    if not order:
        return None
    
    order.status = status
    if status == "completed":
        from datetime import datetime
        order.completed_at = datetime.utcnow()
    
    db.commit()
    db.refresh(order)
    return order

def add_product_view(db: Session, user_id: int, product_id: int):
    db_view = models.ProductView(user_id=user_id, product_id=product_id)
    db.add(db_view)
    db.commit()
    return db_view

def get_last_viewed_product(db: Session, user_id: int):
    return (db.query(models.ProductView)
            .filter(models.ProductView.user_id == user_id)
            .order_by(models.ProductView.viewed_at.desc())
            .first())
