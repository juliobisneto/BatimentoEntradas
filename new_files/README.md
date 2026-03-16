# Arquivos de Teste - Transações

Esta pasta contém 5 arquivos CSV de teste com dados aleatórios para importação.

## Arquivos Disponíveis

| Arquivo | Data | Registros | Descrição |
|---------|------|-----------|-----------|
| `transactions_20251002.csv` | 02/10/2025 | 100 | Transações do dia 02 de outubro |
| `transactions_20251010.csv` | 10/10/2025 | 100 | Transações do dia 10 de outubro |
| `transactions_20251011.csv` | 11/10/2025 | 100 | Transações do dia 11 de outubro |
| `transactions_20251021.csv` | 21/10/2025 | 100 | Transações do dia 21 de outubro |
| `transactions_20251031.csv` | 31/10/2025 | 100 | Transações do dia 31 de outubro |

**Total: 500 registros**

## Características dos Dados

- **Timestamps**: Aleatórios entre 08:00 e 22:59 da data correspondente
- **Métodos de Pagamento**: IDs 1-5 (todos os métodos cadastrados)
- **Sponsors**: 6 empresas diferentes (A-F)
- **Venues**: 7 locais diferentes
- **Eventos**: 10 tipos de eventos variados
- **Itens por Pedido**: 1 a 10 itens
- **Valores**: R$ 50 a R$ 5000 (variável conforme número de itens)
- **Tipo de Transação**: 90% vendas, 10% reembolsos

## Como Importar

### Via Terminal (importar todos)

```bash
cd /Users/juliobisneto/temp/BatimentoEntradas

# Importar arquivo por arquivo
for file in new_files/transactions_*.csv; do
  echo "Importando $file..."
  curl -X POST "http://localhost:8000/transactions/import" \
    -F "file=@$file"
  echo ""
done
```

### Via Swagger UI (importar individualmente)

1. Acesse http://localhost:8000/docs
2. Endpoint **POST /transactions/import**
3. Selecione o arquivo desejado
4. Execute

### Validações Implementadas

Cada arquivo:
- ✅ Segue o formato `transactions_YYYYMMDD.csv`
- ✅ Possui os 9 campos obrigatórios na ordem correta
- ✅ Última linha contém o total de registros (100)
- ✅ Todos os payment_method_id existem no banco
- ✅ Tipos de dados corretos
- ✅ Timestamps válidos

## Estrutura do CSV

```
#register,order_timestamp,payment_method_id,event_sponsor,venue,event,#of_items_in_order,total_order_value,type_transaction
1,2025-10-02 08:24:27,5,Empresa F,Centro de Convenções,Festival de Música,4,1755.0,venda
...
100,2025-10-02 12:46:30,4,Empresa A,Arena Sports,Festival de Música,7,977.62,venda
100
```

## Após Importação

Você verá no dashboard:
- 500 transações no total
- Distribuição por data
- Estatísticas por método de pagamento
- Filtros funcionando por sponsor, venue, evento e data




