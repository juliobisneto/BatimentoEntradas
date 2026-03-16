from fastapi import APIRouter, Depends, HTTPException, status, UploadFile, File
from sqlalchemy.orm import Session
from sqlalchemy import func
from typing import List, Optional
from datetime import datetime
from app.database import get_db
from app.models.transaction import TransactionModel
from app.models.payment_method import PaymentMethod
from app.models.user import User
from app.schemas.transaction import (
    TransactionCreate, 
    TransactionResponse, 
    TransactionWithPaymentMethod,
    ImportResult
)
from app.services.file_import import FileImportService
from app.core.security import get_current_user

router = APIRouter(prefix="/transactions", tags=["Transactions"])

@router.get("/check-file/{filename}")
async def check_file_imported(
    filename: str,
    db: Session = Depends(get_db)
):
    """
    Verificar se um arquivo já foi importado anteriormente.
    Retorna informações sobre a importação se existir.
    """
    service = FileImportService(db)
    result = service.check_file_already_imported(filename)
    return result

@router.delete("/delete-by-file/{filename}")
async def delete_transactions_by_file(
    filename: str,
    db: Session = Depends(get_db)
):
    """
    Deletar todas as transações importadas de um arquivo específico.
    Usado para reprocessamento de arquivos.
    """
    import os
    from pathlib import Path
    
    # Verificar se existem transações desse arquivo
    transactions = db.query(TransactionModel).filter(
        TransactionModel.file_name == filename
    ).all()
    
    if not transactions:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Nenhuma transação encontrada para o arquivo '{filename}'"
        )
    
    count = len(transactions)
    
    # Deletar transações
    db.query(TransactionModel).filter(
        TransactionModel.file_name == filename
    ).delete()
    db.commit()
    
    # Mover arquivo de old_files de volta para uploads (se existir)
    old_file_path = Path("old_files") / filename
    if old_file_path.exists():
        old_file_path.unlink()
    
    return {
        "success": True,
        "message": f"Deletadas {count} transações do arquivo '{filename}'",
        "deleted_count": count
    }

@router.post("/import", response_model=ImportResult, status_code=status.HTTP_201_CREATED)
async def import_transactions(
    file: UploadFile = File(...),
    db: Session = Depends(get_db)
):
    """
    Importar transações de arquivo CSV.
    
    O arquivo deve seguir o formato:
    - Nome: transactions_YYYYMMDD.csv
    - Headers: #register, order_timestamp, payment_method_id, event_sponsor, 
               venue, event, #of_items_in_order, total_order_value, type_transaction
    - Última linha: total de registros no campo #register
    """
    service = FileImportService(db)
    
    try:
        result = await service.import_file(file)
        
        if not result["success"]:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=result
            )
        
        return result
    
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error processing file: {str(e)}" if str(e) else "Unexpected error processing file. Check that the file format and payment method IDs are correct.",
        )

@router.get("/", response_model=List[TransactionWithPaymentMethod])
def list_transactions(
    skip: int = 0,
    limit: int = 100,
    start_date: Optional[datetime] = None,
    end_date: Optional[datetime] = None,
    payment_method_id: Optional[int] = None,
    transaction_type: Optional[str] = None,
    event: Optional[str] = None,
    venue: Optional[str] = None,
    db: Session = Depends(get_db)
):
    """Listar transações com filtros"""
    query = db.query(TransactionModel)
    
    if start_date:
        query = query.filter(TransactionModel.order_timestamp >= start_date)
    
    if end_date:
        query = query.filter(TransactionModel.order_timestamp <= end_date)
    
    if payment_method_id:
        query = query.filter(TransactionModel.payment_method_id == payment_method_id)
    
    if transaction_type:
        query = query.filter(TransactionModel.transaction_type == transaction_type)
    
    if event:
        query = query.filter(TransactionModel.event.ilike(f"%{event}%"))
    
    if venue:
        query = query.filter(TransactionModel.venue.ilike(f"%{venue}%"))
    
    transactions = query.order_by(TransactionModel.order_timestamp.desc()).offset(skip).limit(limit).all()
    return transactions

@router.get("/summary")
def get_transactions_summary(
    start_date: Optional[datetime] = None,
    end_date: Optional[datetime] = None,
    db: Session = Depends(get_db)
):
    """Obter resumo de transações"""
    query = db.query(
        func.count(TransactionModel.id).label('total_transactions'),
        func.sum(TransactionModel.total_order_value).label('total_amount'),
        func.sum(TransactionModel.net_amount).label('total_net_amount'),
        func.sum(TransactionModel.discount_amount).label('total_discount'),
        func.sum(TransactionModel.number_of_items).label('total_items')
    )
    
    if start_date:
        query = query.filter(TransactionModel.order_timestamp >= start_date)
    
    if end_date:
        query = query.filter(TransactionModel.order_timestamp <= end_date)
    
    result = query.first()
    
    return {
        "total_transactions": result.total_transactions or 0,
        "total_amount": float(result.total_amount or 0),
        "total_net_amount": float(result.total_net_amount or 0),
        "total_discount": float(result.total_discount or 0),
        "total_items": int(result.total_items or 0)
    }

@router.get("/dashboard/summary")
def get_dashboard_summary(
    start_date: Optional[datetime] = None,
    end_date: Optional[datetime] = None,
    event_sponsor: Optional[str] = None,
    venue: Optional[str] = None,
    event: Optional[str] = None,
    db: Session = Depends(get_db)
):
    """
    Obter resumo consolidado para dashboard com filtros
    """
    # Query base
    query = db.query(TransactionModel)
    
    # Aplicar filtros
    if start_date:
        query = query.filter(TransactionModel.order_timestamp >= start_date)
    
    if end_date:
        query = query.filter(TransactionModel.order_timestamp <= end_date)
    
    if event_sponsor:
        query = query.filter(TransactionModel.event_sponsor.ilike(f"%{event_sponsor}%"))
    
    if venue:
        query = query.filter(TransactionModel.venue.ilike(f"%{venue}%"))
    
    if event:
        query = query.filter(TransactionModel.event.ilike(f"%{event}%"))
    
    # Obter todas as transações filtradas
    transactions = query.all()
    
    # Calcular estatísticas
    total_transactions = len(transactions)
    
    sales = [t for t in transactions if t.transaction_type.lower() in ['venda', 'sale']]
    refunds = [t for t in transactions if t.transaction_type.lower() in ['reembolso', 'refund']]
    
    total_sales_value = sum(t.total_order_value for t in sales)
    total_sales_count = len(sales)
    
    total_refunds_value = sum(t.total_order_value for t in refunds)
    total_refunds_count = len(refunds)
    
    # Total arrecadado = vendas - reembolsos
    net_revenue = total_sales_value - total_refunds_value
    
    # Total líquido (após taxas)
    net_sales_after_tax = sum(t.net_amount for t in sales)
    net_refunds_after_tax = sum(t.net_amount for t in refunds)
    net_revenue_after_tax = net_sales_after_tax - net_refunds_after_tax
    
    # Total de descontos
    total_discount = sum(t.discount_amount for t in transactions)
    
    # Total de itens
    total_items = sum(t.number_of_items for t in transactions)
    
    return {
        "summary": {
            "total_transactions": total_transactions,
            "total_sales_count": total_sales_count,
            "total_refunds_count": total_refunds_count,
            "total_sales_value": float(total_sales_value),
            "total_refunds_value": float(total_refunds_value),
            "net_revenue": float(net_revenue),
            "net_revenue_after_tax": float(net_revenue_after_tax),
            "total_discount": float(total_discount),
            "total_items": total_items,
            "average_transaction_value": float(total_sales_value / total_sales_count) if total_sales_count > 0 else 0
        },
        "transactions": [
            {
                "id": t.id,
                "register": t.register,
                "order_timestamp": t.order_timestamp.isoformat(),
                "event_sponsor": t.event_sponsor,
                "venue": t.venue,
                "event": t.event,
                "number_of_items": t.number_of_items,
                "total_order_value": float(t.total_order_value),
                "net_amount": float(t.net_amount),
                "discount_amount": float(t.discount_amount),
                "transaction_type": t.transaction_type,
                "payment_method": {
                    "id": t.payment_method.id,
                    "name": t.payment_method.name
                }
            }
            for t in transactions
        ]
    }

@router.get("/dashboard/filters")
def get_dashboard_filters(db: Session = Depends(get_db)):
    """
    Obter listas únicas de sponsors, venues e events para filtros
    """
    sponsors = db.query(TransactionModel.event_sponsor).distinct().all()
    venues = db.query(TransactionModel.venue).distinct().all()
    events = db.query(TransactionModel.event).distinct().all()
    
    return {
        "sponsors": sorted([s[0] for s in sponsors if s[0]]),
        "venues": sorted([v[0] for v in venues if v[0]]),
        "events": sorted([e[0] for e in events if e[0]])
    }

@router.get("/dashboard/by-payment-method")
def get_by_payment_method(
    start_date: Optional[datetime] = None,
    end_date: Optional[datetime] = None,
    event_sponsor: Optional[str] = None,
    venue: Optional[str] = None,
    event: Optional[str] = None,
    db: Session = Depends(get_db)
):
    """
    Obter resumo por método de pagamento
    """
    query = db.query(
        PaymentMethod.name,
        PaymentMethod.id,
        func.count(TransactionModel.id).label('count'),
        func.sum(TransactionModel.total_order_value).label('total_value'),
        func.sum(TransactionModel.net_amount).label('net_value')
    ).join(TransactionModel.payment_method)
    
    # Aplicar filtros
    if start_date:
        query = query.filter(TransactionModel.order_timestamp >= start_date)
    if end_date:
        query = query.filter(TransactionModel.order_timestamp <= end_date)
    if event_sponsor:
        query = query.filter(TransactionModel.event_sponsor.ilike(f"%{event_sponsor}%"))
    if venue:
        query = query.filter(TransactionModel.venue.ilike(f"%{venue}%"))
    if event:
        query = query.filter(TransactionModel.event.ilike(f"%{event}%"))
    
    results = query.group_by(PaymentMethod.id, PaymentMethod.name).all()
    
    return [
        {
            "payment_method": r.name,
            "count": r.count,
            "total_value": float(r.total_value or 0),
            "net_value": float(r.net_value or 0)
        }
        for r in results
    ]

@router.get("/payment-calendar")
def get_payment_calendar(
    start_date: Optional[str] = None,
    end_date: Optional[str] = None,
    payment_method_id: Optional[int] = None,
    db: Session = Depends(get_db)
):
    """
    Obter calendário de pagamentos agrupado por data de liquidação
    """
    from collections import defaultdict
    from datetime import date
    
    # Converter strings para datetime se fornecidas
    start_dt = None
    end_dt = None
    
    if start_date:
        try:
            start_dt = datetime.fromisoformat(start_date)
        except (ValueError, TypeError):
            pass
    
    if end_date:
        try:
            end_dt = datetime.fromisoformat(end_date)
        except (ValueError, TypeError):
            pass
    
    # Query base
    query = db.query(TransactionModel).filter(
        TransactionModel.settlement_date.isnot(None)
    )
    
    # Filtros
    if start_dt:
        query = query.filter(TransactionModel.settlement_date >= start_dt)
    if end_dt:
        query = query.filter(TransactionModel.settlement_date <= end_dt)
    if payment_method_id:
        query = query.filter(TransactionModel.payment_method_id == payment_method_id)
    
    # Buscar transações
    transactions = query.all()
    
    # Agrupar por data de liquidação
    daily_settlements = defaultdict(lambda: {
        'date': None,
        'total_amount': 0.0,
        'total_net_amount': 0.0,
        'transaction_count': 0,
        'by_payment_method': defaultdict(lambda: {
            'method_id': 0,
            'method_name': '',
            'count': 0,
            'total': 0.0,
            'net': 0.0,
            'transactions': []
        }),
        'status': 'pending'
    })
    
    # Processar transações
    today = datetime.now().date()
    
    for t in transactions:
        settlement_date = t.settlement_date.date()
        date_key = settlement_date.isoformat()
        
        # Dados do dia
        daily_settlements[date_key]['date'] = date_key
        daily_settlements[date_key]['total_amount'] += float(t.total_order_value)
        daily_settlements[date_key]['total_net_amount'] += float(t.net_amount)
        daily_settlements[date_key]['transaction_count'] += 1
        
        # Status (se já passou a data de liquidação)
        if settlement_date <= today:
            daily_settlements[date_key]['status'] = 'settled'
        
        # Dados por método de pagamento
        pm = daily_settlements[date_key]['by_payment_method'][t.payment_method_id]
        pm['method_id'] = t.payment_method.id
        pm['method_name'] = t.payment_method.name
        pm['count'] += 1
        pm['total'] += float(t.total_order_value)
        pm['net'] += float(t.net_amount)
        pm['transactions'].append({
            'id': t.id,
            'register': t.register,
            'order_timestamp': t.order_timestamp.isoformat(),
            'event': t.event,
            'venue': t.venue,
            'event_sponsor': t.event_sponsor,
            'total_order_value': float(t.total_order_value),
            'net_amount': float(t.net_amount),
            'discount_amount': float(t.discount_amount),
            'transaction_type': t.transaction_type
        })
    
    # Converter para lista e ordenar
    daily_list = []
    total_amount = 0.0
    settled_amount = 0.0
    pending_amount = 0.0
    
    for date_key, data in sorted(daily_settlements.items()):
        # Converter by_payment_method de dict para lista
        data['by_payment_method'] = list(data['by_payment_method'].values())
        daily_list.append(data)
        
        total_amount += data['total_net_amount']
        if data['status'] == 'settled':
            settled_amount += data['total_net_amount']
        else:
            pending_amount += data['total_net_amount']
    
    # Calcular estatísticas
    summary = {
        'total_amount': total_amount,
        'settled_amount': settled_amount,
        'pending_amount': pending_amount,
        'settled_percentage': (settled_amount / total_amount * 100) if total_amount > 0 else 0,
        'total_days': len(daily_list),
        'average_daily': total_amount / len(daily_list) if daily_list else 0
    }
    
    # Maior e menor liquidação
    if daily_list:
        sorted_by_amount = sorted(daily_list, key=lambda x: x['total_net_amount'])
        summary['min_settlement'] = {
            'date': sorted_by_amount[0]['date'],
            'amount': sorted_by_amount[0]['total_net_amount']
        }
        summary['max_settlement'] = {
            'date': sorted_by_amount[-1]['date'],
            'amount': sorted_by_amount[-1]['total_net_amount']
        }
    
    return {
        'period': {
            'start': start_date if start_date else None,
            'end': end_date if end_date else None
        },
        'daily_settlements': daily_list,
        'summary': summary
    }

@router.get("/{transaction_id}", response_model=TransactionWithPaymentMethod)
def get_transaction(transaction_id: int, db: Session = Depends(get_db)):
    """Buscar transação por ID"""
    transaction = db.query(TransactionModel).filter(
        TransactionModel.id == transaction_id
    ).first()
    
    if not transaction:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Transação não encontrada"
        )
    
    return transaction

