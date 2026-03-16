# Sistema de Batimento de Entradas

Sistema completo para gerenciamento de pagamentos e transações financeiras com dashboard analítico.

## 📋 Funcionalidades

### Backend (FastAPI + PostgreSQL)
- ✅ **Cadastro de métodos de pagamento** com regras de liquidação
  - Taxa de desconto
  - Tempo de liquidação
  - Taxa de antecipação
- ✅ **Importação de arquivos CSV** com validações completas
  - Validação de nome do arquivo (`transactions_YYYYMMDD.csv`)
  - Validação de headers
  - Batimento de número de registros
  - Validação de tipos de dados
- ✅ **Cálculos automáticos**
  - Valor líquido após taxas
  - Data de liquidação
  - Descontos aplicados
- ✅ **API REST completa** com documentação automática (Swagger)

### Frontend (React + TypeScript + Tailwind CSS)
- ✅ **Dashboard analítico** com filtros
  - Filtros por sponsor, venue, evento e data
  - Cards estatísticos (vendas, reembolsos, receita líquida)
  - Estatísticas por método de pagamento
  - Tabela detalhada de transações
- ✅ **Gerenciamento de métodos de pagamento**
  - Criar, editar e deletar métodos
  - Ativar/desativar métodos
  - Validação de formulários
- ✅ **Interface moderna e responsiva**

## 🚀 Instalação

### Pré-requisitos

- Python 3.8+
- Node.js 18+
- PostgreSQL 12+

### 1. Configurar Banco de Dados

Crie um banco de dados PostgreSQL:

```bash
createdb batimento_entradas
```

Ou via psql:

```sql
CREATE DATABASE batimento_entradas;
```

### 2. Configurar Backend

```bash
# Instalar dependências
pip install -r requirements.txt

# Criar arquivo .env (se não foi bloqueado)
cat > .env << EOF
DATABASE_URL=postgresql://seu_usuario:sua_senha@localhost:5432/batimento_entradas
SECRET_KEY=sua-chave-secreta-aqui
UPLOAD_DIR=./uploads
EOF

# Criar diretório de uploads
mkdir -p uploads

# Inicializar métodos de pagamento padrão
python init_payment_methods.py
```

### 3. Configurar Frontend

```bash
cd frontend

# Instalar dependências
npm install

# Voltar para a raiz
cd ..
```

## ▶️ Executar o Sistema

### Iniciar o Backend

```bash
# Na raiz do projeto
uvicorn app.main:app --reload
```

O backend estará disponível em: `http://localhost:8000`

Documentação da API: `http://localhost:8000/docs`

### Iniciar o Frontend

Em outro terminal:

```bash
cd frontend
npm run dev
```

O frontend estará disponível em: `http://localhost:3000`

## 📁 Formato do Arquivo de Importação

### Nome do arquivo

O arquivo deve seguir o formato: `transactions_YYYYMMDD.csv`

**Exemplos válidos:**
- `transactions_20251031.csv`
- `transactions_20251115.csv`

### Estrutura do CSV

O arquivo deve conter os seguintes campos **na ordem exata**:

| Campo | Tipo | Descrição |
|-------|------|-----------|
| `#register` | integer | Número do registro |
| `order_timestamp` | timestamp | Data e hora do pedido (YYYY-MM-DD HH:MM:SS) |
| `payment_method_id` | integer | ID do método de pagamento |
| `event_sponsor` | string(100) | Patrocinador do evento |
| `venue` | string(100) | Local do evento |
| `event` | string(255) | Nome do evento |
| `#of_items_in_order` | integer | Número de itens no pedido |
| `total_order_value` | float | Valor total do pedido |
| `type_transaction` | string(10) | Tipo da transação (venda/reembolso) |

### Última Linha

A **última linha** do arquivo deve conter **apenas o número total de registros** no campo `#register` (para validação/batimento).

### Exemplo de arquivo CSV válido

```csv
#register,order_timestamp,payment_method_id,event_sponsor,venue,event,#of_items_in_order,total_order_value,type_transaction
1,2025-10-31 10:30:00,1,Empresa A,Estádio Municipal,Show de Rock,2,150.50,venda
2,2025-10-31 11:45:00,4,Empresa B,Teatro Nacional,Peça de Teatro,1,80.00,venda
3,2025-10-31 14:20:00,2,Empresa A,Arena Sports,Jogo de Futebol,4,320.00,venda
4,2025-10-31 16:00:00,3,Empresa C,Centro de Convenções,Festival de Música,3,210.75,venda
5,2025-10-31 18:30:00,1,Empresa A,Estádio Municipal,Show de Rock,1,75.25,reembolso
5
```

**Nota:** A última linha contém apenas o número `5` (total de registros).

## 📊 Usando o Sistema

### 1. Cadastrar Métodos de Pagamento

1. Acesse `http://localhost:3000`
2. Clique na aba **"Payment Methods"**
3. Preencha o formulário:
   - **Payment Method**: Nome do método (ex: "Crédito à Vista")
   - **Payment Terms**: Dias para liquidação (ex: 30)
   - **Tax**: Taxa de desconto em % (ex: 2.5)
4. Clique em **"Create"**

### 2. Importar Transações

#### Via API (Backend)

```bash
curl -X POST "http://localhost:8000/transactions/import" \
  -H "accept: application/json" \
  -H "Content-Type: multipart/form-data" \
  -F "file=@transactions_20251031.csv"
```

#### Via Interface (Swagger)

1. Acesse `http://localhost:8000/docs`
2. Encontre o endpoint **POST /transactions/import**
3. Clique em **"Try it out"**
4. Faça upload do arquivo CSV
5. Clique em **"Execute"**

### 3. Visualizar Dashboard

1. Acesse `http://localhost:3000`
2. A aba **"Dashboard"** é a página inicial
3. Use os filtros para:
   - Selecionar intervalo de datas
   - Filtrar por sponsor, venue ou evento
4. Visualize:
   - Cards com totalizações
   - Estatísticas por método de pagamento
   - Tabela detalhada de transações

## 🗂️ Estrutura do Projeto

```
BatimentoEntradas/
├── app/                          # Backend
│   ├── api/                      # Endpoints da API
│   │   ├── payment_methods.py   # CRUD de métodos de pagamento
│   │   └── transactions.py      # Transações e dashboard
│   ├── models/                   # Modelos do banco de dados
│   │   ├── payment_method.py
│   │   └── transaction.py
│   ├── schemas/                  # Schemas Pydantic
│   │   ├── payment_method.py
│   │   └── transaction.py
│   ├── services/                 # Lógica de negócio
│   │   └── file_import.py       # Importação de arquivos
│   ├── database.py               # Configuração do banco
│   └── main.py                   # App FastAPI
├── frontend/                     # Frontend
│   ├── src/
│   │   ├── components/          # Componentes React
│   │   │   ├── Layout.tsx
│   │   │   ├── PaymentMethodForm.tsx
│   │   │   ├── PaymentMethodList.tsx
│   │   │   ├── DashboardFilters.tsx
│   │   │   ├── StatCard.tsx
│   │   │   └── TransactionsTable.tsx
│   │   ├── pages/               # Páginas
│   │   │   ├── Dashboard.tsx
│   │   │   └── PaymentMethodsPage.tsx
│   │   ├── services/            # API client
│   │   │   └── api.ts
│   │   ├── types/               # TypeScript types
│   │   │   ├── paymentMethod.ts
│   │   │   └── dashboard.ts
│   │   ├── App.tsx              # App principal
│   │   └── index.tsx            # Entry point
│   ├── package.json
│   └── vite.config.ts
├── requirements.txt              # Dependências Python
├── init_payment_methods.py      # Script de inicialização
└── README.md
```

## 🔗 Endpoints da API

### Métodos de Pagamento

- `POST /payment-methods/` - Criar método de pagamento
- `GET /payment-methods/` - Listar métodos
- `GET /payment-methods/{id}` - Buscar por ID
- `PUT /payment-methods/{id}` - Atualizar
- `DELETE /payment-methods/{id}` - Deletar

### Transações

- `POST /transactions/import` - Importar arquivo CSV
- `GET /transactions/` - Listar transações (com filtros)
- `GET /transactions/{id}` - Buscar por ID
- `GET /transactions/summary` - Resumo geral

### Dashboard

- `GET /transactions/dashboard/summary` - Resumo consolidado com filtros
- `GET /transactions/dashboard/filters` - Opções de filtros disponíveis
- `GET /transactions/dashboard/by-payment-method` - Estatísticas por método

## 🧪 Métodos de Pagamento Padrão

Ao executar `init_payment_methods.py`, são criados:

| ID | Nome | Taxa | Liquidação |
|----|------|------|------------|
| 1 | Crédito à Vista | 2.5% | 30 dias |
| 2 | Crédito Parcelado | 3.5% | 30 dias |
| 3 | Débito | 1.5% | 1 dia |
| 4 | PIX | 0.5% | 0 dias |
| 5 | Dinheiro | 0.0% | 0 dias |

## 📈 Cálculos Realizados

Para cada transação importada, o sistema calcula automaticamente:

1. **Valor do Desconto** = `valor_total × (taxa_desconto / 100)`
2. **Valor Líquido** = `valor_total - valor_desconto`
3. **Data de Liquidação** = `data_pedido + dias_liquidação`

### Exemplo:

```
Transação: R$ 1000,00
Método: Crédito (2.5%, 30 dias)
Data: 31/10/2025

Desconto = R$ 1000,00 × 0.025 = R$ 25,00
Líquido = R$ 1000,00 - R$ 25,00 = R$ 975,00
Liquidação = 31/10/2025 + 30 dias = 30/11/2025
```

## ⚠️ Validações Implementadas

### Nome do Arquivo
- Deve seguir o padrão `transactions_YYYYMMDD.csv`
- Data deve ser válida

### Headers
- Todos os campos obrigatórios devem estar presentes
- Ordem dos campos deve ser respeitada

### Batimento de Registros
- Última linha deve conter o total de registros
- Número de linhas deve bater com o total informado

### Tipos de Dados
- `#register`: inteiro
- `order_timestamp`: timestamp válido
- `payment_method_id`: inteiro (deve existir no banco)
- Strings: respeitam tamanhos máximos
- `total_order_value`: número positivo
- `#of_items_in_order`: inteiro maior que 0

## 🛠️ Tecnologias Utilizadas

### Backend
- **FastAPI** - Framework web moderno
- **SQLAlchemy** - ORM
- **PostgreSQL** - Banco de dados
- **Pydantic** - Validação de dados
- **Pandas** - Processamento de CSV
- **Uvicorn** - Servidor ASGI

### Frontend
- **React 18** - UI Library
- **TypeScript** - Type safety
- **Vite** - Build tool
- **Tailwind CSS** - Styling
- **Axios** - HTTP client
- **React Icons** - Ícones
- **React Toastify** - Notificações

## 🐛 Troubleshooting

### Erro de conexão com banco de dados

Verifique se o PostgreSQL está rodando e se as credenciais no `.env` estão corretas.

### Erro ao importar arquivo

- Verifique o formato do nome do arquivo
- Confira se todos os headers estão presentes
- Valide a última linha com o total de registros
- Certifique-se de que os métodos de pagamento existem

### Frontend não conecta ao backend

- Verifique se o backend está rodando na porta 8000
- Confira o proxy configurado no `vite.config.ts`

## 📝 Licença

Este projeto foi desenvolvido para fins educacionais e de demonstração.

## 👨‍💻 Autor

Sistema desenvolvido para gerenciamento financeiro de eventos.

---

**Versão:** 1.0.0  
**Data:** Outubro 2025




