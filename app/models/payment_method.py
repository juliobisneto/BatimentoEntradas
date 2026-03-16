from sqlalchemy import Column, Integer, String, Float, Boolean, DateTime
from sqlalchemy.orm import relationship
from datetime import datetime
from app.database import Base

class PaymentMethod(Base):
    __tablename__ = "payment_methods"
    
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, unique=True, nullable=False, index=True)  # Crédito, Débito, PIX, Dinheiro
    code = Column(String, unique=True, nullable=False)  # CREDIT, DEBIT, PIX, CASH
    
    # Regras de liquidação
    discount_rate = Column(Float, default=0.0)  # Taxa de desconto (%)
    settlement_days = Column(Integer, default=0)  # Dias para liquidação
    anticipation_rate = Column(Float, default=0.0)  # Taxa de antecipação (%)
    
    # Controle
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relacionamentos
    transactions = relationship("TransactionModel", back_populates="payment_method")

