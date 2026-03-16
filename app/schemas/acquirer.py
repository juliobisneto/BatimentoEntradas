import json
from pydantic import BaseModel, Field, field_validator
from datetime import datetime
from typing import Optional, Dict, Any, List


class AcquirerBase(BaseModel):
    name: str = Field(..., description="Nome do adquirente")
    code: str = Field(..., description="Código único (ex.: PAGBANK)")
    file_format: str = Field("xml_generic", description="Format: xml_generic, pagbank_xml, xlsx_generic, csv_generic")
    is_active: bool = True


class AcquirerCreate(AcquirerBase):
    parser_config: Optional[Dict[str, Any]] = None


class AcquirerUpdate(BaseModel):
    name: Optional[str] = None
    code: Optional[str] = None
    file_format: Optional[str] = None
    parser_config: Optional[Dict[str, Any]] = None
    is_active: Optional[bool] = None


class AcquirerResponse(AcquirerBase):
    id: int
    parser_config: Optional[Dict[str, Any]] = None
    created_at: datetime
    updated_at: datetime

    @field_validator("parser_config", mode="before")
    @classmethod
    def parse_parser_config(cls, v: Any) -> Optional[Dict[str, Any]]:
        if isinstance(v, str) and v:
            try:
                return json.loads(v)
            except Exception:
                return None
        return v if v else None

    class Config:
        from_attributes = True


class AcquirerPaymentMethodBase(BaseModel):
    name: str = Field(..., description="Nome (ex.: Pix, Crédito)")
    code: str = Field(..., description="Código (ex.: PIX, CREDIT)")
    discount_rate: float = Field(0.0, ge=0, le=100)
    settlement_days: int = Field(0, ge=0)
    anticipation_rate: float = Field(0.0, ge=0, le=100)
    is_active: bool = True
    payment_method_id: Optional[int] = None


class AcquirerPaymentMethodCreate(AcquirerPaymentMethodBase):
    pass


class AcquirerPaymentMethodUpdate(BaseModel):
    name: Optional[str] = None
    code: Optional[str] = None
    discount_rate: Optional[float] = None
    settlement_days: Optional[int] = None
    anticipation_rate: Optional[float] = None
    is_active: Optional[bool] = None
    payment_method_id: Optional[int] = None


class AcquirerPaymentMethodResponse(AcquirerPaymentMethodBase):
    id: int
    acquirer_id: int
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


class ParserConfigUpdate(BaseModel):
    parser_config: Dict[str, Any] = Field(..., description="Configuração completa do parser")


class AcquirerFileImportResponse(BaseModel):
    id: int
    acquirer_id: int
    file_name: str
    imported_at: datetime
    status: str
    records_count: int
    error_message: Optional[str] = None

    class Config:
        from_attributes = True


class AcquirerImportResult(BaseModel):
    success: bool
    message: str
    file_import_id: Optional[int] = None
    records_imported: int = 0
    duplicates_ignored: int = 0
    errors: List[str] = []


DEFAULT_PAGBANK_PARSER_CONFIG = {
    "root_element": "SummaryReport",
    "repeating_element": "Transaction",
    "field_mappings": {
        "settlement_date": "data_prevista_liberacao",
        "transaction_date": "data_transacao",
        "payment_type": "forma_pagamento",
        "net_amount": "valor_liquido",
        "gross_amount": "valor_bruto",
        "fee_amount": "valor_taxa",
        "reference": "codigo_refencia",
        "status": "status",
        "acquirer_transaction_id": "codigo_transacao",
    },
    "date_format": "%d/%m/%Y %H:%M",
    "decimal_separator": ",",
    "encoding": "ISO-8859-1",
}

# Rede: planilha "vendas", header na linha 1 (linha 0 é título). Colunas conforme export.
DEFAULT_REDE_PARSER_CONFIG = {
    "sheet": "vendas",
    "header_row": 1,
    "field_mappings": {
        "transaction_date": "data da venda",
        "status": "status da venda",
        "gross_amount": "valor da venda atualizado",
        "fee_amount": "valor total das taxas descontadas (MDR+recebimento automático)",
        "net_amount": "valor líquido",
        "reference": "número do pedido",
        "acquirer_transaction_id": "ID Transação",
        "payment_type": "meio de pagamento",
    },
    "date_format": "%d-%m-%Y",
    "decimal_separator": ",",
}
