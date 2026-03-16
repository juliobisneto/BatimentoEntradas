from sqlalchemy import Column, Integer, String, Float, DateTime, ForeignKey, UniqueConstraint
from sqlalchemy.orm import relationship
from datetime import datetime
from app.database import Base

class TransactionModel(Base):
    __tablename__ = "transactions"
    
    id = Column(Integer, primary_key=True, index=True)
    
    # Campos do arquivo CSV
    register = Column(Integer, nullable=False, index=True)  # #register
    order_timestamp = Column(DateTime, nullable=False, index=True)
    payment_method_id = Column(Integer, ForeignKey("payment_methods.id"), nullable=False)
    event_sponsor = Column(String(100), nullable=False)
    venue = Column(String(100), nullable=False)
    event = Column(String(255), nullable=False)
    number_of_items = Column(Integer, nullable=False)  # #of_items_in_order
    total_order_value = Column(Float, nullable=False)
    transaction_type = Column(String(10), nullable=False)  # type_transaction
    
    # Cálculos automáticos
    discount_amount = Column(Float, default=0.0)  # Valor do desconto aplicado
    net_amount = Column(Float, default=0.0)  # Valor líquido após desconto
    settlement_date = Column(DateTime, nullable=True)  # Data prevista de liquidação
    
    # Controle
    file_import_id = Column(String, nullable=True)  # ID do arquivo que originou esta transação
    file_name = Column(String, nullable=True, index=True)  # Nome do arquivo importado
    created_at = Column(DateTime, default=datetime.utcnow, index=True)
    
    # Relacionamentos
    payment_method = relationship("PaymentMethod", back_populates="transactions")
    
    # Constraint de unicidade: previne registros duplicados
    # Um registro é considerado duplicado se tiver o mesmo register, 
    # order_timestamp, evento e valor
    __table_args__ = (
        UniqueConstraint(
            'register', 
            'order_timestamp', 
            'event_sponsor',
            'venue',
            'event',
            'total_order_value',
            name='uq_transaction_record'
        ),
    )

