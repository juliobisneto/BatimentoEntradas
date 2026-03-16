"""
Script para recriar o banco de dados com a nova constraint de unicidade.
ATENÇÃO: Este script irá DELETAR todos os dados existentes!
"""
import os
from app.database import Base, engine
from app.models.payment_method import PaymentMethod
from app.models.transaction import TransactionModel

def recreate_database():
    """Recria o banco de dados com as novas constraints"""
    
    # Verificar se o banco de dados existe
    db_path = "batimento_entradas.db"
    if os.path.exists(db_path):
        print(f"⚠️  ATENÇÃO: O banco de dados '{db_path}' será deletado!")
        response = input("Deseja continuar? (sim/não): ")
        
        if response.lower() not in ['sim', 's', 'yes', 'y']:
            print("❌ Operação cancelada.")
            return
        
        # Deletar banco de dados antigo
        os.remove(db_path)
        print(f"✅ Banco de dados antigo deletado.")
    
    # Criar todas as tabelas com as novas constraints
    Base.metadata.create_all(bind=engine)
    print("✅ Novo banco de dados criado com constraints de unicidade.")
    print("\n📋 Próximos passos:")
    print("   1. Execute: python init_payment_methods.py")
    print("   2. Importe novamente seus arquivos CSV")

if __name__ == "__main__":
    print("="*60)
    print("RECRIAR BANCO DE DADOS COM CONSTRAINTS DE UNICIDADE")
    print("="*60)
    print()
    recreate_database()




