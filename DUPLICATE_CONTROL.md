# Sistema de Controle de Duplicatas

## Visão Geral

O sistema agora possui um controle robusto de duplicatas que previne a importação de:
1. **Arquivos duplicados**: Impede que o mesmo arquivo seja importado mais de uma vez
2. **Registros duplicados**: Impede que transações idênticas sejam inseridas no banco de dados

## Como Funciona

### 1. Verificação de Arquivo Duplicado

Antes de processar qualquer arquivo CSV, o sistema:

- Verifica se um arquivo com o mesmo nome já foi importado anteriormente
- Checa tanto o diretório `old_files/` quanto o banco de dados
- Se encontrado, retorna erro HTTP 409 (Conflict) com informações sobre a importação anterior

**Resposta em caso de arquivo duplicado:**
```json
{
  "error": "Arquivo já foi importado anteriormente",
  "filename": "transactions_20251002.csv",
  "import_info": {
    "already_imported": true,
    "file_location": "old_files",
    "records_count": 100,
    "first_import_date": "2025-10-31T15:30:00",
    "file_import_id": "abc123..."
  }
}
```

### 2. Constraint de Unicidade no Banco de Dados

Foi adicionada uma constraint única composta pelos seguintes campos:

- `register` - Número do registro
- `order_timestamp` - Data e hora do pedido
- `event_sponsor` - Patrocinador do evento
- `venue` - Local do evento
- `event` - Nome do evento
- `total_order_value` - Valor total do pedido

**Nome da constraint:** `uq_transaction_record`

Esta combinação garante que a mesma transação não seja inserida duas vezes no banco de dados.

### 3. Detecção de Duplicatas Durante Importação

Durante a importação, o sistema:

1. Tenta inserir cada registro
2. Se detectar uma violação da constraint de unicidade:
   - Marca o registro como duplicata
   - Continua processando os demais registros
   - Não considera duplicatas como erros de validação

**Resultado da importação com duplicatas:**
```json
{
  "success": true,
  "message": "Arquivo processado: 50 registros importados, 50 duplicatas ignoradas. Movido para old_files.",
  "total_records_in_file": 100,
  "total_imported": 50,
  "total_duplicates": 50,
  "total_errors": 0,
  "file_import_id": "xyz789...",
  "file_name": "transactions_20251031.csv",
  "file_location": "old_files",
  "errors": [
    {
      "row": 5,
      "register": 12345,
      "error": "Registro duplicado (já existe no banco de dados)",
      "type": "duplicate"
    }
  ]
}
```

## Tipos de Erros

O sistema agora diferencia três tipos de problemas:

1. **duplicate**: Registro já existe no banco (não é erro crítico)
2. **validation_error**: Erro de validação de dados (erro crítico)
3. **integrity_error**: Outro erro de integridade do banco (erro crítico)

## Critérios de Sucesso

A importação é considerada bem-sucedida quando:

- **Todos os registros foram importados**, OU
- **Todos os registros foram processados e os únicos "erros" foram duplicatas**

Apenas erros de validação e integridade impedem que o arquivo seja movido para `old_files/`.

## Fluxo de Trabalho

### Primeira Importação de um Arquivo
```
1. Upload: transactions_20251002.csv
2. Validação: ✅ Nome correto, headers OK, batimento OK
3. Processamento: 100 registros novos
4. Resultado: ✅ 100 importados, 0 duplicatas
5. Arquivo movido para: old_files/
```

### Tentativa de Reimportação do Mesmo Arquivo
```
1. Upload: transactions_20251002.csv
2. Verificação: ❌ Arquivo já foi importado
3. Resposta: HTTP 409 Conflict
4. Arquivo: Rejeitado (não salvo)
```

### Importação de Arquivo com Dados Parcialmente Duplicados
```
1. Upload: transactions_20251031.csv (100 registros)
2. Validação: ✅ Tudo OK
3. Processamento:
   - 50 registros novos → importados
   - 50 registros duplicados → ignorados
4. Resultado: ✅ 50 importados, 50 duplicatas
5. Arquivo movido para: old_files/
```

## Recriando o Banco de Dados

Para aplicar as novas constraints em um banco existente, execute:

```bash
python recreate_database.py
```

⚠️ **ATENÇÃO**: Este comando irá deletar todos os dados existentes!

Após recriar o banco:

```bash
# 1. Reiniciar métodos de pagamento
python init_payment_methods.py

# 2. Reimportar arquivos CSV (na ordem correta)
```

## Verificando Duplicatas Manualmente

### No Dashboard
- Registros duplicados aparecerão na lista de erros do resultado da importação
- Serão marcados com `type: "duplicate"`

### Via API
```bash
# Verificar se um arquivo já foi importado
curl -X POST http://localhost:8000/transactions/import \
  -F "file=@transactions_20251002.csv"

# Se já importado, retornará 409 Conflict
```

## Vantagens do Sistema

1. ✅ **Idempotência**: Pode-se tentar importar o mesmo arquivo múltiplas vezes sem problemas
2. ✅ **Integridade**: Garante que não há dados duplicados no banco
3. ✅ **Rastreabilidade**: Todas as duplicatas são registradas e reportadas
4. ✅ **Flexibilidade**: Permite importar arquivos com dados parcialmente duplicados
5. ✅ **Transparência**: Mensagens claras sobre o que foi importado, duplicado ou erro

## Resolução de Problemas

### "Arquivo já foi importado anteriormente"
**Causa**: O arquivo CSV com este nome já foi processado com sucesso anteriormente.

**Solução**: 
- Se realmente precisa reimportar, primeiro remova os registros antigos do banco
- Ou renomeie o arquivo para uma data diferente (se apropriado)

### "Registro duplicado (já existe no banco de dados)"
**Causa**: A transação já está no banco de dados (mesma combinação de campos únicos).

**Solução**: 
- Isto é normal e esperado
- O registro duplicado é simplesmente ignorado
- Se o arquivo inteiro contém apenas duplicatas, ele será movido para `old_files/` normalmente

### Muitos erros de integridade
**Causa**: Pode haver inconsistência nos dados ou problema com métodos de pagamento.

**Solução**:
- Verifique se todos os `payment_method_id` existem no cadastro
- Revise os dados no CSV para garantir que estão no formato correto
- Consulte os logs de erro detalhados na resposta da API

## Implementação Técnica

### Model (transaction.py)
```python
__table_args__ = (
    UniqueConstraint(
        'register', 
        'order_timestamp', 
        'event_sponsor',
        'venue',
        'event',
        'total_order_value',
        name='uq_transaction_record'
    ),
)
```

### Service (file_import.py)
- `check_file_already_imported()`: Verifica se arquivo foi importado
- Tratamento de `IntegrityError` durante flush
- Diferenciação entre duplicatas e erros reais

### API Response
- Campo `total_duplicates` adicionado
- Erros agora têm campo `type` para classificação
- Mensagens mais descritivas sobre o resultado




