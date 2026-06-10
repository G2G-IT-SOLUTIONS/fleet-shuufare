from datetime import datetime, date
from typing import Optional, List
from sqlmodel import SQLModel, Field, Relationship

class User(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    email: str = Field(unique=True, index=True)
    hashed_password: str
    full_name: Optional[str] = None
    phone: Optional[str] = Field(default=None, index=True)
    two_factor_enabled: bool = Field(default=False)
    role: str = Field(default="manager") # admin, manager, auditor
    is_active: bool = Field(default=True)
    last_login: Optional[datetime] = None
    created_at: datetime = Field(default_factory=datetime.utcnow)

class Driver(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    yango_driver_id: str = Field(unique=True, index=True)
    name: str
    phone: Optional[str] = None
    operator_id: str = Field(default="000-000", index=True)
    driver_type: str = Field(default="external", index=True) # "internal" or "external"
    shift: str = Field(default="None", index=True) # "Day", "Night", or "None"
    reconciliation_start_date: Optional[date] = Field(default=None)
    avatar_data: Optional[str] = Field(default=None, nullable=True)
    created_at: datetime = Field(default_factory=datetime.utcnow)
    
    expected_revenues: List["ExpectedRevenue"] = Relationship(back_populates="driver")
    transactions: List["TelebirrTransaction"] = Relationship(back_populates="driver")
    documents: List["DriverDocument"] = Relationship(back_populates="driver", sa_relationship_kwargs={"cascade": "all, delete-orphan"})

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
    opposite_party: Optional[str] = None
    is_reconciled: bool = Field(default=False)
    
    # Optional link to driver if attribution was successful
    driver_id: Optional[int] = Field(default=None, foreign_key="driver.id")
    driver: Optional[Driver] = Relationship(back_populates="transactions")
    
    created_at: datetime = Field(default_factory=datetime.utcnow)

class ReconciliationBatch(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    filename: str
    uploaded_by: int = Field(foreign_key="user.id")
    total_transactions: int = 0
    total_amount: float = 0.0
    drivers_matched: int = 0
    trips_reconciled: int = 0
    status: str = Field(default="active") # "active" or "reversed"
    created_at: datetime = Field(default_factory=datetime.utcnow)
    reversed_at: Optional[datetime] = None
    reversed_by: Optional[int] = Field(default=None, foreign_key="user.id")

class DepositTripLink(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    transaction_id: str = Field(foreign_key="telebirrtransaction.transaction_id", index=True)
    trip_id: str = Field(foreign_key="drivertrip.id", index=True)
    amount_applied: float
    batch_id: Optional[int] = Field(default=None, foreign_key="reconciliationbatch.id", index=True)
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
    driver_id: str = Field(index=True)
    driver_name: str
    ended_at: datetime = Field(index=True)
    address_from: Optional[str] = None
    created_at: datetime = Field(default_factory=datetime.utcnow)

class DriverTrip(SQLModel, table=True):
    id: str = Field(primary_key=True)       # Yango order ID (unique)
    short_id: Optional[int] = None
    driver_id: int = Field(foreign_key="driver.id")
    status: str
    category: Optional[str] = None
    payment_method: Optional[str] = None
    price: Optional[float] = None
    provider: Optional[str] = None
    booked_at: Optional[datetime] = None
    yango_created_at: Optional[datetime] = None
    ended_at: Optional[datetime] = None
    # Pickup address
    address_from: Optional[str] = None
    address_from_lat: Optional[float] = None
    address_from_lon: Optional[float] = None
    # Vehicle
    car_id: Optional[str] = None
    car_brand_model: Optional[str] = None
    car_license: Optional[str] = None
    car_callsign: Optional[str] = None
    # Order type & work rule
    order_type_name: Optional[str] = None
    driver_work_rule: Optional[str] = None
    # Passenger
    passenger_name: Optional[str] = None
    # Mileage
    mileage: Optional[str] = None
    # Reconciliation data
    deposited_amount: float = Field(default=0.0)
    reconciliation_status: str = Field(default="Pending") # Pending, Verified, Partial Deposit, Excess Deposit, Missing Deposit
    reconciliation_notes: Optional[str] = None
    
    # Sync metadata
    synced_at: datetime = Field(default_factory=datetime.utcnow)

class AuditLog(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    target_type: str = Field(index=True) # "driver", "trip", etc.
    target_id: str = Field(index=True)   # ID of the target object (e.g., driver_id or order_id)
    field_name: str
    old_value: Optional[str] = None
    new_value: Optional[str] = None
    user_id: int = Field(foreign_key="user.id")
    timestamp: datetime = Field(default_factory=datetime.utcnow)
    
    # Relationships
    user: Optional[User] = Relationship()

class Notification(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    title: str
    message: str
    type: str = Field(default="info") # "info", "warning", "error", "success"
    is_read: bool = Field(default=False)
    action_url: Optional[str] = None
    created_at: datetime = Field(default_factory=datetime.utcnow)

class SystemConfig(SQLModel, table=True):
    key: str = Field(primary_key=True)
    value: str
    description: str
    data_type: str = Field(default="int") # "int", "float", "string"
    updated_at: datetime = Field(default_factory=datetime.utcnow)

class DriverDocument(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    driver_id: int = Field(foreign_key="driver.id")
    document_type: str = Field(index=True) # "Librea", "Driver License", "ID Card", "Contract", "Other"
    filename: str
    content_type: str
    file_data: str # Contains base64 data URL e.g. "data:image/png;base64,..."
    uploaded_at: datetime = Field(default_factory=datetime.utcnow)
    notes: Optional[str] = None
    
    driver: Optional[Driver] = Relationship(back_populates="documents")
