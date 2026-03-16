from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List
from app.database import get_db
from app.models.payment_method import PaymentMethod
from app.models.user import User
from app.schemas.payment_method import (
    PaymentMethodCreate,
    PaymentMethodUpdate,
    PaymentMethodResponse
)
from app.core.security import get_current_user

router = APIRouter(prefix="/payment-methods", tags=["Payment Methods"])

@router.post("/", response_model=PaymentMethodResponse, status_code=status.HTTP_201_CREATED)
def create_payment_method(
    payment_method: PaymentMethodCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Cadastrar novo método de pagamento"""
    # Verificar se já existe
    existing = db.query(PaymentMethod).filter(
        (PaymentMethod.name == payment_method.name) | 
        (PaymentMethod.code == payment_method.code)
    ).first()
    
    if existing:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Método de pagamento já cadastrado"
        )
    
    db_payment_method = PaymentMethod(**payment_method.dict())
    db.add(db_payment_method)
    db.commit()
    db.refresh(db_payment_method)
    return db_payment_method

@router.get("/", response_model=List[PaymentMethodResponse])
def list_payment_methods(
    skip: int = 0,
    limit: int = 100,
    is_active: bool = None,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Listar métodos de pagamento"""
    query = db.query(PaymentMethod)
    
    if is_active is not None:
        query = query.filter(PaymentMethod.is_active == is_active)
    
    return query.offset(skip).limit(limit).all()

@router.get("/{payment_method_id}", response_model=PaymentMethodResponse)
def get_payment_method(
    payment_method_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Buscar método de pagamento por ID"""
    payment_method = db.query(PaymentMethod).filter(
        PaymentMethod.id == payment_method_id
    ).first()
    
    if not payment_method:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Método de pagamento não encontrado"
        )
    
    return payment_method

@router.put("/{payment_method_id}", response_model=PaymentMethodResponse)
def update_payment_method(
    payment_method_id: int,
    payment_method_update: PaymentMethodUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Atualizar método de pagamento"""
    db_payment_method = db.query(PaymentMethod).filter(
        PaymentMethod.id == payment_method_id
    ).first()
    
    if not db_payment_method:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Método de pagamento não encontrado"
        )
    
    update_data = payment_method_update.dict(exclude_unset=True)
    for field, value in update_data.items():
        setattr(db_payment_method, field, value)
    
    db.commit()
    db.refresh(db_payment_method)
    return db_payment_method

@router.delete("/{payment_method_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_payment_method(
    payment_method_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Deletar método de pagamento"""
    db_payment_method = db.query(PaymentMethod).filter(
        PaymentMethod.id == payment_method_id
    ).first()
    
    if not db_payment_method:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Método de pagamento não encontrado"
        )
    
    db.delete(db_payment_method)
    db.commit()
    return None


