from sqlalchemy import Table, Column, Integer, String, Float, DateTime, ForeignKey, MetaData
from sqlalchemy.sql import func
from datetime import datetime

# Metadata instance that holds the schema definitions
metadata = MetaData()

# Categories table
categories = Table(
    'categories',
    metadata,
    Column('id', Integer, primary_key=True),
    Column('name', String(100), nullable=False, unique=True),
    Column('description', String(255)),
    Column('created_at', DateTime, default=func.now(), nullable=False),
)

# Transactions table
transactions = Table(
    'transactions',
    metadata,
    Column('id', Integer, primary_key=True),
    Column('amount', Float, nullable=False),
    Column('description', String(255)),
    Column('date', DateTime, nullable=False, default=func.now()),
    Column('category_id', Integer, ForeignKey('categories.id')),
    Column('created_at', DateTime, default=func.now(), nullable=False),
)