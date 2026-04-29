from datetime import datetime, date
from typing import Optional, List
from sqlmodel import SQLModel, Field, Relationship

class Driver(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    operator_id: str = Field(unique=True, index=True)
    name: str
    phone: Optional[str] = None
    driver_type: str = Field(default="external", index=True) # "internal" or "external"
    created_at: datetime = Field(default_factory=datetime.utcnow)
    
    expected_revenues: List["ExpectedRevenue"] = Relationship(back_populates="driver")
    transactions: List["TelebirrTransaction"] = Relationship(back_populates="driver")

class ExpectedRevenue(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    driver_id: int = Field(foreign_key="driver.id")
    date: date
    expected_amount: float
    created_at: datetime = Field(default_factory=datetime.utcnow)
    
    driver: Optional[Driver] = Relationship(back_populates="expected_revenues")

class TelebirrTransaction(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    transaction_id: str = Field(unique=True, index=True)
    amount: float
    sender_identifier: str = Field(index=True) # driver's operator ID or phone
    merchant_id: str
    timestamp: datetime
    status: str = "success"
    
    # Optional link to driver if attribution was successful
    driver_id: Optional[int] = Field(default=None, foreign_key="driver.id")
    driver: Optional[Driver] = Relationship(back_populates="transactions")
    
    created_at: datetime = Field(default_factory=datetime.utcnow)

class ReconciliationRecord(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    driver_id: int = Field(foreign_key="driver.id")
    date: date
    expected_amount: float
    actual_amount: float
    status: str # "Verified", "Partial Deposit", "Excess Deposit", "Missing Deposit"
    created_at: datetime = Field(default_factory=datetime.utcnow)

class Order(SQLModel, table=True):
    id: str = Field(primary_key=True) # Yango Order ID
    short_id: int
    status: str
    price: float
    payment_method: str
    driver_id: str = Field(index=True) # Yango Driver ID (operator_id)
    driver_name: str
    ended_at: datetime
    created_at: datetime = Field(default_factory=datetime.utcnow)
