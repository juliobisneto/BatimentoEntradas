from pydantic import BaseModel, Field, validator
from datetime import datetime
from typing import Optional

class TransactionBase(BaseModel):
    register: int = Field(..., description="Número do registro")
    order_timestamp: datetime = Field(..., description="Data e hora do pedido")
    payment_method_id: int = Field(..., description="ID do método de pagamento")
    event_sponsor: str = Field(..., max_length=100, description="Patrocinador do evento")
    venue: str = Field(..., max_length=100, description="Local do evento")
    event: str = Field(..., max_length=255, description="Nome do evento")
    number_of_items: int = Field(..., ge=1, description="Número de itens no pedido")
    total_order_value: float = Field(..., gt=0, description="Valor total do pedido")
    transaction_type: str = Field(..., max_length=10, description="Tipo de transação")
    
    @validator('event_sponsor', 'venue', 'event', 'transaction_type')
    def strip_whitespace(cls, v):
        return v.strip() if v else v

class TransactionCreate(TransactionBase):
    pass

class TransactionResponse(TransactionBase):
    id: int
    discount_amount: float
    net_amount: float
    settlement_date: Optional[datetime]
    file_import_id: Optional[str]
    file_name: Optional[str]
    created_at: datetime
    
    class Config:
        from_attributes = True

class TransactionWithPaymentMethod(TransactionResponse):
    payment_method: dict
    
    class Config:
        from_attributes = True

class ImportResult(BaseModel):
    success: bool
    message: str
    total_records_in_file: int
    total_imported: int
    total_duplicates: int
    total_errors: int
    file_import_id: str
    file_name: str
    file_location: str
    errors: list

