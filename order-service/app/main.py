from fastapi import FastAPI, Depends, HTTPException
from sqlalchemy.orm import Session
from app import models, database
from app.models import Order
from pydantic import BaseModel

models.Base.metadata.create_all(bind=database.engine)

app = FastAPI()

class OrderCreate(BaseModel):
    items: str
    customer_name: str
    total_price: float

# Dependency
def get_db():
    db = database.SessionLocal()
    try:
        yield db
    finally:
        db.close()

@app.get("/")
def read_root():
    return {"message": "Order Service API is running."}

# GET endpoint - all
@app.get("/orders")
def get_orders(db: Session = Depends(get_db)):
    return db.query(models.Order).all()

# GET endpoint - by id 
@app.get("/orders/{order_id}")
def get_order_by_id(order_id: int, db: Session = Depends(get_db)):
    order = db.query(Order).filter(Order.id == order_id).first()
    if not order:
        raise HTTPException(status_code=404, detail="Order not found")
    return order

# POST endpoint
@app.post("/orders")
def create_order(order: OrderCreate, db: Session = Depends(get_db)):
    db_order = models.Order(**order.dict())
    db.add(db_order)
    db.commit()
    db.refresh(db_order)
    return db_order

# DELETE endpoint
@app.delete("/orders/{order_id}")
def delete_order(order_id: int, db: Session = Depends(get_db)):
    order = db.query(Order).filter(Order.id == order_id).first()
    if not order:
        raise HTTPException(status_code=404, detail="Order not found")
    db.delete(order)
    db.commit()
    return {"message": f"Order with id {order_id} deleted"}

# UPDATE endpoint
@app.put("/orders/{order_id}")
def update_order(order_id: int, updated_order: OrderCreate, db: Session = Depends(get_db)):
    order = db.query(Order).filter(Order.id == order_id).first()
    if not order:
        raise HTTPException(status_code=404, detail="Order not found")

    order.items = updated_order.items
    order.customer_name = updated_order.customer_name
    order.total_price = updated_order.total_price

    db.commit()
    db.refresh(order)
    return order
