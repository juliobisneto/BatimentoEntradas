#!/usr/bin/env python3
"""
Script para gerar arquivos de teste de transações para janeiro de 2025
"""
import random
import csv
from datetime import datetime, timedelta
import os

# Configurações
START_DATE = datetime(2025, 1, 10)  # 10 de janeiro de 2025
NUM_FILES = 10
RECORDS_PER_FILE = 50
OUTPUT_DIR = "new_files"

# Dados para geração aleatória
SPONSORS = ["Empresa A", "Empresa B", "Empresa C", "Empresa D", "Empresa E", "Empresa F"]
VENUES = [
    "Teatro Nacional",
    "Estádio Municipal", 
    "Centro de Convenções",
    "Auditório Central",
    "Ginásio Coberto",
    "Parque de Exposições"
]
EVENTS = [
    "Festival de Música",
    "Jogo de Futebol",
    "Concerto Sinfônico",
    "Peça de Teatro",
    "Show de Rock",
    "Festival de Jazz",
    "Conferência Tech",
    "Show de Stand-up"
]
PAYMENT_METHODS = [1, 2, 3, 4, 5]  # IDs dos métodos de pagamento
TRANSACTION_TYPES = ["venda", "reembolso"]

def generate_transactions(date, num_records):
    """Gera transações aleatórias para uma data específica"""
    transactions = []
    
    for i in range(1, num_records + 1):
        # Gerar timestamp aleatório no dia (08:00 - 23:00)
        hour = random.randint(8, 22)
        minute = random.randint(0, 59)
        second = random.randint(0, 59)
        timestamp = date.replace(hour=hour, minute=minute, second=second)
        
        # Tipo de transação (85% vendas, 15% reembolsos)
        transaction_type = random.choices(
            TRANSACTION_TYPES, 
            weights=[85, 15]
        )[0]
        
        # Gerar valores aleatórios
        num_items = random.randint(1, 8)
        total_value = round(random.uniform(100.0, 3000.0), 2)
        
        transaction = {
            '#register': i,
            'order_timestamp': timestamp.strftime('%Y-%m-%d %H:%M:%S'),
            'payment_method_id': random.choice(PAYMENT_METHODS),
            'event_sponsor': random.choice(SPONSORS),
            'venue': random.choice(VENUES),
            'event': random.choice(EVENTS),
            '#of_items_in_order': num_items,
            'total_order_value': total_value,
            'type_transaction': transaction_type
        }
        
        transactions.append(transaction)
    
    return transactions

def create_csv_file(date, transactions):
    """Cria arquivo CSV para a data especificada"""
    # Nome do arquivo
    filename = f"transactions_{date.strftime('%Y%m%d')}.csv"
    filepath = os.path.join(OUTPUT_DIR, filename)
    
    # Criar diretório se não existir
    os.makedirs(OUTPUT_DIR, exist_ok=True)
    
    # Headers
    headers = [
        '#register',
        'order_timestamp',
        'payment_method_id',
        'event_sponsor',
        'venue',
        'event',
        '#of_items_in_order',
        'total_order_value',
        'type_transaction'
    ]
    
    # Escrever arquivo
    with open(filepath, 'w', newline='', encoding='utf-8') as csvfile:
        writer = csv.DictWriter(csvfile, fieldnames=headers)
        
        # Header
        writer.writeheader()
        
        # Dados
        writer.writerows(transactions)
        
        # Última linha com o total
        csvfile.write(f"{len(transactions)}\n")
    
    return filename, filepath

def main():
    print("=" * 70)
    print("📁 GERADOR DE ARQUIVOS DE TESTE - JANEIRO 2025")
    print("=" * 70)
    print()
    
    created_files = []
    total_records = 0
    
    for day_offset in range(NUM_FILES):
        current_date = START_DATE + timedelta(days=day_offset)
        
        # Gerar transações
        transactions = generate_transactions(current_date, RECORDS_PER_FILE)
        
        # Criar arquivo
        filename, filepath = create_csv_file(current_date, transactions)
        
        # Estatísticas
        sales = sum(1 for t in transactions if t['type_transaction'] == 'venda')
        refunds = sum(1 for t in transactions if t['type_transaction'] == 'reembolso')
        total_value = sum(t['total_order_value'] for t in transactions)
        
        created_files.append({
            'filename': filename,
            'date': current_date.strftime('%d/%m/%Y'),
            'records': len(transactions),
            'sales': sales,
            'refunds': refunds,
            'total_value': total_value
        })
        
        total_records += len(transactions)
        
        print(f"✅ {filename}")
        print(f"   Data: {current_date.strftime('%d/%m/%Y')}")
        print(f"   Registros: {len(transactions)} ({sales} vendas, {refunds} reembolsos)")
        print(f"   Valor Total: R$ {total_value:,.2f}")
        print()
    
    print("=" * 70)
    print("📊 RESUMO DA GERAÇÃO")
    print("=" * 70)
    print(f"Total de Arquivos:    {len(created_files)}")
    print(f"Total de Registros:   {total_records}")
    print(f"Período:              {created_files[0]['date']} até {created_files[-1]['date']}")
    print(f"Registros por Arquivo: {RECORDS_PER_FILE}")
    print(f"Diretório:            {OUTPUT_DIR}/")
    print()
    print("✅ Todos os arquivos foram criados com sucesso!")
    print("=" * 70)

if __name__ == "__main__":
    main()
