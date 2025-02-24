from sqlalchemy import Column, Integer, Float, ForeignKey
from sqlalchemy.orm import relationship
from app.db.base_class import Base

class OrderItem(Base):
    """OrderItem Model for storing items within an order
    This model represents individual products purchased in each order,
    tracking quantity and price at time of purchase
    """
    __tablename__ = "order_items"

    id = Column(Integer, primary_key=True, index=True)
    # Reference to the parent order
    order_id = Column(Integer, ForeignKey('orders.id'))
    order = relationship("Order", back_populates="items")
    # Reference to the product being purchased
    product_id = Column(Integer, ForeignKey('products.id'))
    product = relationship("Product")
    # Quantity of the product ordered
    quantity = Column(Integer, nullable=False)
    # Price of the product at time of purchase
    unit_price = Column(Float, nullable=False)
    # Subtotal for this item (quantity * unit_price)
    subtotal = Column(Float, nullable=False)
    # Any discount applied to this item
    discount = Column(Float, default=0.0)
    # Final price after discount
    final_price = Column(Float, nullable=False)