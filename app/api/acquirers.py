import json
from fastapi import APIRouter, Depends, HTTPException, status, UploadFile, File, Form
from sqlalchemy.orm import Session
from typing import List, Optional

from app.database import get_db
from app.models.acquirer import (
    Acquirer,
    AcquirerPaymentMethod,
    AcquirerFileImport,
    AcquirerTransaction,
    AcquirerTransactionExtra,
)
from app.schemas.acquirer import (
    AcquirerCreate,
    AcquirerUpdate,
    AcquirerResponse,
    AcquirerPaymentMethodCreate,
    AcquirerPaymentMethodUpdate,
    AcquirerPaymentMethodResponse,
    ParserConfigUpdate,
    AcquirerImportResult,
    AcquirerFileImportResponse,
    DEFAULT_PAGBANK_PARSER_CONFIG,
    DEFAULT_REDE_PARSER_CONFIG,
)
from app.services.acquirer_parser import parse_xml_with_config, parse_xlsx_with_config
from app.core.security import get_current_user
from app.models.user import User

router = APIRouter(prefix="/acquirers", tags=["Acquirers"])


def _serialize_parser_config(parser_config: Optional[dict]) -> Optional[str]:
    if parser_config is None:
        return None
    return json.dumps(parser_config, ensure_ascii=False)


# --- CRUD Adquirente ---
@router.post("/", response_model=AcquirerResponse, status_code=status.HTTP_201_CREATED)
def create_acquirer(
    data: AcquirerCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    existing = db.query(Acquirer).filter(Acquirer.code == data.code).first()
    if existing:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Acquirer code already exists")
    parser_config_str = _serialize_parser_config(data.parser_config)
    if data.file_format == "pagbank_xml" and parser_config_str is None:
        parser_config_str = _serialize_parser_config(DEFAULT_PAGBANK_PARSER_CONFIG)
    if data.file_format == "xlsx_generic" and parser_config_str is None:
        parser_config_str = _serialize_parser_config(DEFAULT_REDE_PARSER_CONFIG)
    acquirer = Acquirer(
        name=data.name,
        code=data.code,
        file_format=data.file_format,
        parser_config=parser_config_str,
        is_active=data.is_active,
    )
    db.add(acquirer)
    db.commit()
    db.refresh(acquirer)
    return acquirer


@router.get("/", response_model=List[AcquirerResponse])
def list_acquirers(
    is_active: Optional[bool] = None,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    q = db.query(Acquirer)
    if is_active is not None:
        q = q.filter(Acquirer.is_active == is_active)
    return q.order_by(Acquirer.name).all()


@router.get("/{acquirer_id}", response_model=AcquirerResponse)
def get_acquirer(
    acquirer_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    acquirer = db.query(Acquirer).filter(Acquirer.id == acquirer_id).first()
    if not acquirer:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Acquirer not found")
    return acquirer


@router.put("/{acquirer_id}", response_model=AcquirerResponse)
def update_acquirer(
    acquirer_id: int,
    data: AcquirerUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    acquirer = db.query(Acquirer).filter(Acquirer.id == acquirer_id).first()
    if not acquirer:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Acquirer not found")
    update = data.model_dump(exclude_unset=True)
    if "parser_config" in update and update["parser_config"] is not None:
        update["parser_config"] = _serialize_parser_config(update["parser_config"])
    for k, v in update.items():
        setattr(acquirer, k, v)
    db.commit()
    db.refresh(acquirer)
    return acquirer


@router.delete("/{acquirer_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_acquirer(
    acquirer_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    acquirer = db.query(Acquirer).filter(Acquirer.id == acquirer_id).first()
    if not acquirer:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Acquirer not found")
    db.delete(acquirer)
    db.commit()
    return None


# --- Parser config ---
@router.get("/{acquirer_id}/parser-config")
def get_parser_config(
    acquirer_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    acquirer = db.query(Acquirer).filter(Acquirer.id == acquirer_id).first()
    if not acquirer:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Acquirer not found")
    config = None
    if acquirer.parser_config:
        try:
            config = json.loads(acquirer.parser_config)
        except Exception:
            pass
    return {"parser_config": config}


@router.put("/{acquirer_id}/parser-config", response_model=AcquirerResponse)
def update_parser_config(
    acquirer_id: int,
    data: ParserConfigUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    acquirer = db.query(Acquirer).filter(Acquirer.id == acquirer_id).first()
    if not acquirer:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Acquirer not found")
    acquirer.parser_config = _serialize_parser_config(data.parser_config)
    db.commit()
    db.refresh(acquirer)
    return acquirer


# --- Meios de pagamento do adquirente ---
@router.post(
    "/{acquirer_id}/payment-methods",
    response_model=AcquirerPaymentMethodResponse,
    status_code=status.HTTP_201_CREATED,
)
def create_acquirer_payment_method(
    acquirer_id: int,
    data: AcquirerPaymentMethodCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    acquirer = db.query(Acquirer).filter(Acquirer.id == acquirer_id).first()
    if not acquirer:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Acquirer not found")
    pm = AcquirerPaymentMethod(acquirer_id=acquirer_id, **data.model_dump())
    db.add(pm)
    db.commit()
    db.refresh(pm)
    return pm


@router.get("/{acquirer_id}/payment-methods", response_model=List[AcquirerPaymentMethodResponse])
def list_acquirer_payment_methods(
    acquirer_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    acquirer = db.query(Acquirer).filter(Acquirer.id == acquirer_id).first()
    if not acquirer:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Acquirer not found")
    return db.query(AcquirerPaymentMethod).filter(AcquirerPaymentMethod.acquirer_id == acquirer_id).order_by(AcquirerPaymentMethod.name).all()


@router.get("/{acquirer_id}/payment-methods/{pm_id}", response_model=AcquirerPaymentMethodResponse)
def get_acquirer_payment_method(
    acquirer_id: int,
    pm_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    pm = db.query(AcquirerPaymentMethod).filter(
        AcquirerPaymentMethod.id == pm_id,
        AcquirerPaymentMethod.acquirer_id == acquirer_id,
    ).first()
    if not pm:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Payment method not found")
    return pm


@router.put("/{acquirer_id}/payment-methods/{pm_id}", response_model=AcquirerPaymentMethodResponse)
def update_acquirer_payment_method(
    acquirer_id: int,
    pm_id: int,
    data: AcquirerPaymentMethodUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    pm = db.query(AcquirerPaymentMethod).filter(
        AcquirerPaymentMethod.id == pm_id,
        AcquirerPaymentMethod.acquirer_id == acquirer_id,
    ).first()
    if not pm:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Payment method not found")
    for k, v in data.model_dump(exclude_unset=True).items():
        setattr(pm, k, v)
    db.commit()
    db.refresh(pm)
    return pm


@router.delete("/{acquirer_id}/payment-methods/{pm_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_acquirer_payment_method(
    acquirer_id: int,
    pm_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    pm = db.query(AcquirerPaymentMethod).filter(
        AcquirerPaymentMethod.id == pm_id,
        AcquirerPaymentMethod.acquirer_id == acquirer_id,
    ).first()
    if not pm:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Payment method not found")
    db.delete(pm)
    db.commit()
    return None


# --- Importação de arquivo ---
@router.post("/{acquirer_id}/import", response_model=AcquirerImportResult)
async def import_acquirer_file(
    acquirer_id: int,
    file: UploadFile = File(...),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    acquirer = db.query(Acquirer).filter(Acquirer.id == acquirer_id).first()
    if not acquirer:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Acquirer not found")
    if not acquirer.parser_config:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Configure the acquirer parser before importing",
        )
    try:
        config = json.loads(acquirer.parser_config)
    except Exception:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid parser configuration",
        )
    content = await file.read()
    filename = (file.filename or "").strip().lower()
    is_xlsx = filename.endswith(".xlsx")
    errors = []
    try:
        if is_xlsx:
            rows = parse_xlsx_with_config(content, config)
        else:
            rows = parse_xml_with_config(content, config, encoding=config.get("encoding"))
    except Exception as e:
        return AcquirerImportResult(success=False, message=str(e), errors=[str(e)])

    file_import = AcquirerFileImport(
        acquirer_id=acquirer_id,
        file_name=file.filename or ("file.xlsx" if is_xlsx else "file.xml"),
        status="processing",
        records_count=0,
    )
    db.add(file_import)
    db.commit()
    db.refresh(file_import)

    # Load existing acquirer_transaction_id for this acquirer (one query, set lookup)
    existing_ids = {
        r[0]
        for r in db.query(AcquirerTransaction.acquirer_transaction_id).filter(
            AcquirerTransaction.acquirer_id == acquirer_id,
            AcquirerTransaction.acquirer_transaction_id.isnot(None),
            AcquirerTransaction.acquirer_transaction_id != "",
        ).all()
    }
    seen_in_file: set = set()
    count = 0
    duplicates_ignored = 0
    for row in rows:
        try:
            tx_id = row.get("acquirer_transaction_id")
            if tx_id is not None and tx_id != "":
                tx_id = str(tx_id).strip()
                if tx_id in existing_ids:
                    duplicates_ignored += 1
                    continue
                if tx_id in seen_in_file:
                    duplicates_ignored += 1
                    continue
            extra_fields = row.pop("_extra", None)
            t = AcquirerTransaction(
                acquirer_file_import_id=file_import.id,
                acquirer_id=acquirer_id,
                settlement_date=row.get("settlement_date"),
                transaction_date=row.get("transaction_date"),
                payment_type=row.get("payment_type"),
                gross_amount=float(row.get("gross_amount") or 0),
                fee_amount=float(row.get("fee_amount") or 0),
                net_amount=float(row.get("net_amount") or 0),
                reference_code=row.get("reference"),
                acquirer_transaction_id=row.get("acquirer_transaction_id"),
                status=row.get("status"),
            )
            db.add(t)
            db.flush()
            if tx_id:
                existing_ids.add(tx_id)
                seen_in_file.add(tx_id)
            if extra_fields:
                for field_name, value in extra_fields.items():
                    if not field_name:
                        continue
                    val = None if value is None else (str(value).strip() or None)
                    db.add(
                        AcquirerTransactionExtra(
                            acquirer_transaction_id=t.id,
                            acquirer_id=acquirer_id,
                            field_name=field_name,
                            value=val,
                        )
                    )
            count += 1
        except Exception as e:
            errors.append(f"Row: {e}")
            if len(errors) >= 20:
                errors.append("...")
                break

    file_import.records_count = count
    file_import.status = "completed" if not errors else "partial"
    db.commit()

    msg = f"Imported {count} records."
    if duplicates_ignored:
        msg += f" {duplicates_ignored} duplicate(s) ignored."
    return AcquirerImportResult(
        success=True,
        message=msg,
        file_import_id=file_import.id,
        records_imported=count,
        duplicates_ignored=duplicates_ignored,
        errors=errors[:10],
    )


@router.get("/{acquirer_id}/imports", response_model=List[AcquirerFileImportResponse])
def list_acquirer_imports(
    acquirer_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    acquirer = db.query(Acquirer).filter(Acquirer.id == acquirer_id).first()
    if not acquirer:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Acquirer not found")
    return db.query(AcquirerFileImport).filter(AcquirerFileImport.acquirer_id == acquirer_id).order_by(AcquirerFileImport.imported_at.desc()).limit(50).all()
