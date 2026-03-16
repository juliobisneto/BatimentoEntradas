from sqlalchemy import Column, Integer, String, Float, Boolean, DateTime, ForeignKey, Text
from sqlalchemy.orm import relationship
from datetime import datetime
from app.database import Base


class Acquirer(Base):
    """Adquirente (banco/operadora de pagamento)."""
    __tablename__ = "acquirers"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(100), nullable=False, index=True)
    code = Column(String(50), unique=True, nullable=False, index=True)
    file_format = Column(String(50), nullable=False, default="xml_generic")
    parser_config = Column(Text, nullable=True)  # JSON string
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    payment_methods = relationship("AcquirerPaymentMethod", back_populates="acquirer", cascade="all, delete-orphan")
    file_imports = relationship("AcquirerFileImport", back_populates="acquirer", cascade="all, delete-orphan")


class AcquirerPaymentMethod(Base):
    """Meio de pagamento do adquirente (ex.: Pix, Crédito) com taxas e condições."""
    __tablename__ = "acquirer_payment_methods"

    id = Column(Integer, primary_key=True, index=True)
    acquirer_id = Column(Integer, ForeignKey("acquirers.id", ondelete="CASCADE"), nullable=False, index=True)
    name = Column(String(100), nullable=False)
    code = Column(String(50), nullable=False)
    discount_rate = Column(Float, default=0.0)
    settlement_days = Column(Integer, default=0)
    anticipation_rate = Column(Float, default=0.0)
    payment_method_id = Column(Integer, ForeignKey("payment_methods.id", ondelete="SET NULL"), nullable=True, index=True)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    acquirer = relationship("Acquirer", back_populates="payment_methods")


class AcquirerFileImport(Base):
    """Metadados de uma importação de arquivo do adquirente."""
    __tablename__ = "acquirer_file_imports"

    id = Column(Integer, primary_key=True, index=True)
    acquirer_id = Column(Integer, ForeignKey("acquirers.id", ondelete="CASCADE"), nullable=False, index=True)
    file_name = Column(String(255), nullable=False)
    imported_at = Column(DateTime, default=datetime.utcnow)
    status = Column(String(20), default="completed")
    records_count = Column(Integer, default=0)
    error_message = Column(Text, nullable=True)

    acquirer = relationship("Acquirer", back_populates="file_imports")
    transactions = relationship("AcquirerTransaction", back_populates="file_import", cascade="all, delete-orphan")


class AcquirerTransaction(Base):
    """Registro de uma transação extraída do arquivo do adquirente."""
    __tablename__ = "acquirer_transactions"

    id = Column(Integer, primary_key=True, index=True)
    acquirer_file_import_id = Column(
        Integer, ForeignKey("acquirer_file_imports.id", ondelete="CASCADE"), nullable=False, index=True
    )
    acquirer_id = Column(Integer, ForeignKey("acquirers.id", ondelete="CASCADE"), nullable=False, index=True)
    settlement_date = Column(DateTime, nullable=True, index=True)
    transaction_date = Column(DateTime, nullable=True)
    payment_type = Column(String(50), nullable=True)
    acquirer_payment_method_id = Column(
        Integer, ForeignKey("acquirer_payment_methods.id", ondelete="SET NULL"), nullable=True, index=True
    )
    gross_amount = Column(Float, default=0.0)
    fee_amount = Column(Float, default=0.0)
    net_amount = Column(Float, nullable=False)
    reference_code = Column(String(100), nullable=True, index=True)
    acquirer_transaction_id = Column(String(100), nullable=True, index=True)
    status = Column(String(50), nullable=True)

    file_import = relationship("AcquirerFileImport", back_populates="transactions")
    extra_fields = relationship(
        "AcquirerTransactionExtra",
        back_populates="transaction",
        cascade="all, delete-orphan",
    )


class AcquirerTransactionExtra(Base):
    """Campos do arquivo de importação não mapeados em field_mappings (chave/valor)."""
    __tablename__ = "acquirer_transaction_extras"

    id = Column(Integer, primary_key=True, index=True)
    acquirer_transaction_id = Column(
        Integer,
        ForeignKey("acquirer_transactions.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    acquirer_id = Column(
        Integer,
        ForeignKey("acquirers.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    field_name = Column(String(100), nullable=False, index=True)
    value = Column(Text, nullable=True)

    transaction = relationship("AcquirerTransaction", back_populates="extra_fields")
