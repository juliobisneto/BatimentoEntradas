# File Import Feature - Documentação Completa

## 📋 Visão Geral

Nova funcionalidade que permite importar arquivos CSV através de uma interface web dedicada, com verificação de duplicatas, opção de reprocessamento e resumo detalhado dos resultados.

## 🎯 Funcionalidades Implementadas

### 1. Interface de Upload
- Seleção de arquivo CSV através de input file
- Validação de formato (.csv)
- Validação de nome (transactions_YYYYMMDD.csv)
- Feedback visual durante o processo

### 2. Detecção de Duplicatas
- Verificação automática ao selecionar arquivo
- Exibição de informações da importação anterior:
  - Número de registros
  - Data da primeira importação
  - ID da importação
  - Localização do arquivo

### 3. Opção de Reprocessamento
- Modal de confirmação quando arquivo já foi importado
- Opção de deletar registros existentes
- Reimportação automática após deleção
- Opção de cancelar a operação

### 4. Resumo Detalhado
Após a importação, exibe:
- Status geral (sucesso/erro)
- Nome do arquivo
- Localização final do arquivo
- Total de registros no arquivo
- Quantidade de registros importados
- Quantidade de duplicatas encontradas
- Quantidade de erros
- Mensagem descritiva
- Tabela de erros detalhada (se houver)

### 5. Tratamento de Erros
- Validação de formato de arquivo
- Validação de nome do arquivo
- Validação de headers
- Validação de tipos de dados
- Batimento de quantidade de registros
- Mensagens de erro claras e descritivas

## 🔧 Componentes Técnicos

### Backend (FastAPI)

#### Novos Endpoints

1. **GET /transactions/check-file/{filename}**
   - Verifica se um arquivo já foi importado
   - Retorna informações sobre a importação anterior
   
   Resposta quando já importado:
   ```json
   {
     "already_imported": true,
     "file_location": "old_files",
     "records_count": 50,
     "first_import_date": "2026-01-25T20:24:32.966637",
     "file_import_id": "uuid"
   }
   ```
   
   Resposta quando não importado:
   ```json
   {
     "already_imported": false
   }
   ```

2. **DELETE /transactions/delete-by-file/{filename}**
   - Deleta todas as transações de um arquivo
   - Remove o arquivo de old_files (se existir)
   - Usado para reprocessamento
   
   Resposta:
   ```json
   {
     "success": true,
     "message": "Deletadas 50 transações do arquivo 'filename.csv'",
     "deleted_count": 50
   }
   ```

3. **POST /transactions/import**
   - Endpoint de importação (já existente)
   - Atualizado para não requerer autenticação (temporariamente)

### Frontend (React + TypeScript)

#### Nova Página: FileImport.tsx

**Localização**: `frontend/src/pages/FileImport.tsx`

**Principais funcionalidades**:
- Upload de arquivo com validação
- Verificação automática de duplicatas
- Modal de confirmação para reprocessamento
- Exibição de resumo detalhado
- Tabela de erros expandível

**Estados gerenciados**:
```typescript
selectedFile: File | null          // Arquivo selecionado
uploading: boolean                 // Estado de upload
importResult: ImportResult | null  // Resultado da importação
fileCheck: FileCheckResult | null  // Resultado da verificação
showConfirmDialog: boolean         // Exibir modal de confirmação
```

#### Navegação

Adicionada ao menu principal em `App.tsx`:
- Nova opção: "File Import"
- Rota: `currentPage === 'file-import'`

## 📖 Como Usar

### 1. Acessar a Funcionalidade
1. Abra o frontend: http://localhost:3000
2. Faça login (se necessário)
3. Clique em "File Import" no menu superior

### 2. Importar Arquivo Novo
1. Clique em "Choose File"
2. Selecione um arquivo CSV no formato correto
3. Arquivo é automaticamente verificado
4. Clique em "Import File"
5. Aguarde o processamento
6. Visualize o resumo da importação

### 3. Reprocessar Arquivo Já Importado
1. Selecione um arquivo já importado
2. Sistema exibe aviso automático
3. Escolha uma das opções:
   - **"Yes, Delete and Reprocess"**: Deleta registros antigos e reimporta
   - **"Cancel"**: Cancela a operação
4. Se escolher reprocessar, aguarde o processo automático
5. Visualize o resumo da reimportação

### 4. Visualizar Erros
Se houver erros ou duplicatas:
1. Role até a seção "Errors and Warnings"
2. Visualize a tabela com detalhes:
   - Número da linha
   - Número do registro
   - Tipo (Duplicate/Error)
   - Mensagem de erro

## 🔒 Validações Implementadas

### Validações de Frontend
1. **Extensão do arquivo**: Deve ser .csv
2. **Nome do arquivo**: Deve seguir o padrão transactions_YYYYMMDD.csv
3. **Arquivo selecionado**: Não permite upload sem arquivo

### Validações de Backend
1. **Formato do nome**: transactions_YYYYMMDD.csv
2. **Data válida**: YYYYMMDD deve ser uma data válida
3. **Headers**: Devem estar na ordem correta
4. **Batimento de registros**: Última linha deve conter o total
5. **Tipos de dados**: Cada campo deve ter o tipo correto
6. **Métodos de pagamento**: payment_method_id deve existir
7. **Arquivo duplicado**: Verifica se já foi importado

### Validações de Dados
```
#register          → integer
order_timestamp    → timestamp
payment_method_id  → integer
event_sponsor      → string(100)
venue              → string(100)
event              → string(255)
#of_items_in_order → integer
total_order_value  → float
type_transaction   → string(10)
```

## 📊 Fluxo de Arquivos

```
new_files/
    ↓ (selecionar arquivo)
    ↓
[VERIFICAÇÃO]
    ↓
    ├─ Já importado? → [MODAL DE CONFIRMAÇÃO]
    │                      ↓
    │                  Reprocessar?
    │                      ↓
    │                  [DELETE] → [IMPORT]
    │                      
    └─ Novo? → [IMPORT]
                   ↓
                Sucesso?
                   ↓
                   ├─ Sim → old_files/ (movido)
                   │        new_files/ (removido)
                   │
                   └─ Não → uploads/ (temporário)
```

## 🎨 Interface do Usuário

### Elementos Visuais

1. **Cabeçalho**
   - Ícone de upload
   - Título: "File Import"

2. **Seção de Upload**
   - Input de arquivo
   - Informações do arquivo selecionado
   - Botão de importação

3. **Modal de Confirmação** (arquivo duplicado)
   - Ícone de aviso (amarelo)
   - Informações da importação anterior
   - Dois botões:
     - "Yes, Delete and Reprocess" (vermelho)
     - "Cancel" (cinza)

4. **Resumo de Importação**
   - Card com border colorido:
     - Verde: Sucesso
     - Vermelho: Erro
   - Grid com estatísticas:
     - Nome do arquivo
     - Localização
     - Total de registros
     - Importados (verde)
     - Duplicatas (amarelo)
     - Erros (vermelho)
   - Mensagem descritiva
   - Tabela de erros (se houver)
   - Próximos passos (se sucesso)

5. **Caixa de Informações**
   - Requisitos do arquivo
   - Formato esperado
   - Campos obrigatórios

## 🧪 Cenários de Teste

### Teste 1: Importação Normal
**Arquivo**: transactions_20250118.csv (disponível em new_files/)
**Resultado Esperado**: 
- ✅ 50 registros importados
- ✅ 0 duplicatas
- ✅ 0 erros
- ✅ Arquivo movido para old_files/

### Teste 2: Arquivo Duplicado
**Arquivo**: transactions_20250110.csv (já importado)
**Resultado Esperado**:
- ⚠️ Modal de confirmação exibido
- ℹ️ Informações da importação anterior
- 🔄 Opção de reprocessar ou cancelar

### Teste 3: Reprocessamento
**Ação**: Escolher "Delete and Reprocess" no teste 2
**Resultado Esperado**:
- 🗑️ 50 registros deletados
- 📥 50 novos registros importados
- ✅ Processo concluído com sucesso

### Teste 4: Arquivo com Nome Inválido
**Arquivo**: test.csv
**Resultado Esperado**:
- ❌ Erro de validação
- 💬 "Invalid filename format. Use: transactions_YYYYMMDD.csv"

### Teste 5: Arquivo Não-CSV
**Arquivo**: documento.txt
**Resultado Esperado**:
- ❌ Erro de validação
- 💬 "Only CSV files are allowed"

## 🔄 Integração com Sistema Existente

### Compatibilidade
- ✅ Usa mesma lógica de importação do sistema
- ✅ Mantém controle de duplicatas
- ✅ Preserva histórico de importações
- ✅ Movimentação de arquivos consistente

### Banco de Dados
Nenhuma alteração necessária:
- Usa campos existentes em TransactionModel
- Usa relacionamentos existentes
- Mantém constraints de unicidade

### API
- Novos endpoints não conflitam com existentes
- Endpoint de importação continua funcionando via API direta
- Documentação automática atualizada em /docs

## 📝 Notas Importantes

### Segurança
- Endpoint de importação temporariamente sem autenticação
- Recomendado reativar autenticação para produção
- Validações de dados impedem injeção de código

### Performance
- Upload de arquivo é bloqueante (por design)
- Processamento é síncrono
- Adequado para arquivos pequenos/médios (< 1000 registros)

### Arquivos
- Arquivos em old_files/ são permanentes
- Arquivos em new_files/ são removidos após importação
- Arquivos em uploads/ são temporários (durante processamento)

### Duplicatas
Detectadas por combinação de campos:
- register
- order_timestamp
- event_sponsor
- venue
- event
- total_order_value

## 🚀 Próximas Melhorias Sugeridas

1. **Upload em Lote**
   - Permitir seleção de múltiplos arquivos
   - Processamento sequencial automático

2. **Histórico de Importações**
   - Tela com lista de todas as importações
   - Filtros por data, status, arquivo

3. **Preview de Arquivo**
   - Exibir primeiras linhas antes de importar
   - Validação prévia sem processar

4. **Agendamento**
   - Importação automática em horários definidos
   - Monitoramento de pasta new_files/

5. **Notificações**
   - Email ao concluir importação
   - Alertas de erros críticos

6. **Logs Detalhados**
   - Registro de todas as operações
   - Auditoria completa

## 📞 Suporte

Para problemas ou dúvidas:
1. Verifique os logs do backend
2. Acesse a documentação da API: http://localhost:8000/docs
3. Revise este documento
4. Teste os endpoints diretamente via API

## ✅ Checklist de Deploy

Antes de fazer deploy para produção:

- [ ] Reativar autenticação no endpoint de importação
- [ ] Configurar limite de tamanho de arquivo
- [ ] Implementar rate limiting
- [ ] Configurar backup automático de old_files/
- [ ] Testar com volumes maiores de dados
- [ ] Documentar processo de rollback
- [ ] Configurar monitoramento de erros
- [ ] Revisar permissões de pasta
- [ ] Testar recuperação de falhas
- [ ] Atualizar documentação de usuário

---

**Versão**: 1.0  
**Data**: 26/01/2026  
**Status**: ✅ Implementado e Testado
