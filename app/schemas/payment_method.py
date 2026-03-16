from pydantic import BaseModel, Field
from datetime import datetime
from typing import Optional

class PaymentMethodBase(BaseModel):
    name: str = Field(..., description="Nome do método de pagamento")
    code: str = Field(..., description="Código do método")
    discount_rate: float = Field(0.0, ge=0, le=100, description="Taxa de desconto (%)")
    settlement_days: int = Field(0, ge=0, description="Dias para liquidação")
    anticipation_rate: float = Field(0.0, ge=0, le=100, description="Taxa de antecipação (%)")
    is_active: bool = True

class PaymentMethodCreate(PaymentMethodBase):
    pass

class PaymentMethodUpdate(BaseModel):
    name: Optional[str] = None
    discount_rate: Optional[float] = None
    settlement_days: Optional[int] = None
    anticipation_rate: Optional[float] = None
    is_active: Optional[bool] = None

class PaymentMethodResponse(PaymentMethodBase):
    id: int
    created_at: datetime
    updated_at: datetime
    
    class Config:
        from_attributes = True




