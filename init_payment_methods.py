from app.database import SessionLocal, Base, engine
from app.models.payment_method import PaymentMethod
from app.models.transaction import TransactionModel  # Import necessário para resolver relacionamentos

# Criar todas as tabelas
Base.metadata.create_all(bind=engine)

def init_payment_methods():
    db = SessionLocal()
    
    payment_methods = [
        {
            "name": "Crédito à Vista",
            "code": "CREDIT_CASH",
            "discount_rate": 2.5,
            "settlement_days": 30,
            "anticipation_rate": 3.0
        },
        {
            "name": "Crédito Parcelado",
            "code": "CREDIT_INSTALLMENT",
            "discount_rate": 3.5,
            "settlement_days": 30,
            "anticipation_rate": 4.0
        },
        {
            "name": "Débito",
            "code": "DEBIT",
            "discount_rate": 1.5,
            "settlement_days": 1,
            "anticipation_rate": 1.5
        },
        {
            "name": "PIX",
            "code": "PIX",
            "discount_rate": 0.5,
            "settlement_days": 0,
            "anticipation_rate": 0.0
        },
        {
            "name": "Dinheiro",
            "code": "CASH",
            "discount_rate": 0.0,
            "settlement_days": 0,
            "anticipation_rate": 0.0
        }
    ]
    
    for pm_data in payment_methods:
        existing = db.query(PaymentMethod).filter(
            PaymentMethod.code == pm_data["code"]
        ).first()
        
        if not existing:
            pm = PaymentMethod(**pm_data)
            db.add(pm)
            print(f"✓ Criado: {pm_data['name']}")
        else:
            print(f"✗ Já existe: {pm_data['name']}")
    
    db.commit()
    db.close()
    print("\nInicialização concluída!")

if __name__ == "__main__":
    init_payment_methods()

