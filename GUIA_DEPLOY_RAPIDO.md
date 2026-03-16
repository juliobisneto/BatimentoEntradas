# 🚀 Guia Rápido de Deploy - Batimento de Entradas

Este é um guia simplificado para subir sua aplicação web. Para o guia completo, veja `DEPLOY_GUIDE.md`.

---

## 📋 Status Atual do Projeto

✅ Repositório Git inicializado
✅ SECRET_KEY gerada: `a9ec8e9beb31ba613d7ec1096dc54a323893801b9c5220264144e8f4ea757b78`
✅ Arquivos de configuração prontos
✅ Backend e Frontend configurados

---

## 🎯 Próximos Passos para Deploy

### 1️⃣ **Criar conta no GitHub e fazer push do código**

```bash
# No terminal, na pasta do projeto:
cd /Users/juliobisneto/temp/BatimentoEntradas

# Adicionar arquivos ao Git
git add .
git commit -m "Initial commit - Ready for deployment"

# Criar repositório no GitHub:
# - Vá para https://github.com/new
# - Nome: batimento-entradas (ou o nome que preferir)
# - Deixe PRIVADO se preferir
# - NÃO inicialize com README

# Conectar e enviar código
git remote add origin https://github.com/SEU-USUARIO/batimento-entradas.git
git branch -M main
git push -u origin main
```

---

### 2️⃣ **Escolher a Plataforma de Deploy**

Você tem 2 opções principais:

#### **Opção A: Deploy Completo (Recomendado)**
- **Backend**: Render.com (grátis)
- **Frontend**: Vercel.com (grátis)
- **Database**: Render PostgreSQL (grátis)
- **Storage**: Supabase (grátis)

**Tempo estimado**: 30-40 minutos
**Custo**: $0/mês
**Guia**: Siga o `DEPLOY_GUIDE.md`

#### **Opção B: Deploy Simplificado**
- **Tudo em um**: Railway.app ou Render.com
- **Database**: Incluído
- **Storage**: Local (sem Supabase)

**Tempo estimado**: 15-20 minutos
**Custo**: $0/mês (com limitações)

---

### 3️⃣ **Variáveis de Ambiente Necessárias**

#### **Backend (Render/Railway)**

| Variável | Valor | Onde Obter |
|----------|-------|------------|
| `DATABASE_URL` | `postgresql://...` | Copiado do Render Database |
| `SECRET_KEY` | `a9ec8e9beb31ba613d7ec1096dc54a323893801b9c5220264144e8f4ea757b78` | ✅ Já gerado |
| `FRONTEND_URL` | `https://seu-app.vercel.app` | Após deploy do frontend |
| `SUPABASE_URL` | `https://xxx.supabase.co` | Opcional - ver passo 4 |
| `SUPABASE_KEY` | `eyJhbG...` | Opcional - ver passo 4 |
| `PYTHON_VERSION` | `3.11.0` | ✅ Já configurado |

#### **Frontend (Vercel)**

| Variável | Valor | Onde Obter |
|----------|-------|------------|
| `VITE_API_URL` | `https://seu-backend.onrender.com` | Após deploy do backend |

---

### 4️⃣ **Deploy do Backend (Render.com)**

1. **Criar conta no Render**: https://render.com
2. **Criar PostgreSQL Database**:
   - Clique em "New +" → "PostgreSQL"
   - Nome: `batimento-db`
   - Região: `Oregon (US West)` (grátis)
   - Plano: **Free**
   - Copie o **Internal Database URL**

3. **Criar Web Service**:
   - Clique em "New +" → "Web Service"
   - Conecte seu repositório GitHub
   - Configure:
     - **Name**: `batimento-backend`
     - **Runtime**: Python 3
     - **Build Command**: `pip install -r requirements.txt`
     - **Start Command**: `uvicorn app.main:app --host 0.0.0.0 --port $PORT`
     - **Plan**: Free

4. **Adicionar Variáveis de Ambiente** (na seção Environment):
   - `DATABASE_URL`: (cole o Internal Database URL)
   - `SECRET_KEY`: `a9ec8e9beb31ba613d7ec1096dc54a323893801b9c5220264144e8f4ea757b78`
   - `FRONTEND_URL`: `http://localhost:3000` (temporário, atualize depois)
   - `PYTHON_VERSION`: `3.11.0`

5. **Deploy**: Clique em "Create Web Service"
6. **Aguarde** ~5 minutos para o deploy
7. **Copie a URL**: `https://seu-backend.onrender.com`

8. **Inicializar Database** (no Shell do Render):
   ```bash
   python scripts/init_db.py
   python scripts/create_admin.py
   ```

---

### 5️⃣ **Deploy do Frontend (Vercel.com)**

1. **Criar conta no Vercel**: https://vercel.com
2. **Importar Projeto**:
   - Clique em "Add New..." → "Project"
   - Selecione seu repositório GitHub
   - Configure:
     - **Framework**: Vite
     - **Root Directory**: `frontend`
     - **Build Command**: `npm run build`
     - **Output Directory**: `dist`

3. **Adicionar Variável de Ambiente**:
   - `VITE_API_URL`: `https://seu-backend.onrender.com`

4. **Deploy**: Clique em "Deploy"
5. **Aguarde** ~3 minutos
6. **Copie a URL**: `https://seu-app.vercel.app`

---

### 6️⃣ **Atualizar CORS do Backend**

1. Volte ao **Render**
2. Vá para seu Web Service
3. Atualize a variável `FRONTEND_URL` com a URL do Vercel
4. Clique em "Manual Deploy" → "Deploy latest commit"

---

### 7️⃣ **Testar a Aplicação**

1. **Acesse o frontend**: `https://seu-app.vercel.app`
2. **Faça login**:
   - Email: `admin@admin.com`
   - Password: `admin`
3. **Teste as funcionalidades**:
   - Dashboard
   - Payment Calendar
   - Payment Methods
   - Importação de CSV

---

## 🔧 Comandos Úteis

### Testar localmente antes do deploy

```bash
# Backend
cd /Users/juliobisneto/temp/BatimentoEntradas
python -m venv venv
source venv/bin/activate
pip install -r requirements.txt
uvicorn app.main:app --reload

# Frontend (em outro terminal)
cd /Users/juliobisneto/temp/BatimentoEntradas/frontend
npm install
npm run dev
```

### Verificar logs no Render

```bash
# No dashboard do Render, clique em "Logs" para ver erros
```

### Fazer redeploy após mudanças

```bash
# Fazer alterações no código
git add .
git commit -m "Sua mensagem"
git push

# Render e Vercel farão redeploy automático!
```

---

## 🆘 Troubleshooting Rápido

### ❌ Erro: "Database connection failed"
- Verifique se o `DATABASE_URL` está correto no Render
- Confirme que o database foi criado
- Execute `python scripts/test_connection.py` no Shell do Render

### ❌ Erro: "CORS policy error"
- Verifique se `FRONTEND_URL` no backend é EXATAMENTE a URL do Vercel
- Inclua `https://` no início
- Redeploy o backend após mudar

### ❌ Frontend mostra página em branco
- Verifique se `VITE_API_URL` está configurado no Vercel
- Abra o Console do navegador (F12) para ver erros
- Verifique os logs de build no Vercel

### ❌ Erro ao fazer login
- Certifique-se de que executou `python scripts/create_admin.py`
- Verifique se o backend está respondendo em `/health`

---

## 🎉 Aplicação no Ar!

Após seguir todos os passos, sua aplicação estará acessível de qualquer lugar!

**URLs importantes**:
- 🌐 **Frontend**: https://seu-app.vercel.app
- 🔌 **API Backend**: https://seu-backend.onrender.com
- 📚 **Documentação API**: https://seu-backend.onrender.com/docs

**Credenciais padrão**:
- 📧 Email: `admin@admin.com`
- 🔑 Senha: `admin`

⚠️ **IMPORTANTE**: Altere a senha do admin após o primeiro login!

---

## 📊 Recursos

- ✅ **100% Gratuito** - Todas as plataformas usam planos free
- ✅ **Auto-deploy** - Atualizações automáticas ao fazer push no Git
- ✅ **SSL/HTTPS** - Incluído gratuitamente
- ✅ **Domínio personalizado** - Pode configurar depois (opcional)

---

## 📞 Precisa de Ajuda?

1. Veja o guia completo: `DEPLOY_GUIDE.md`
2. Confira o checklist: `DEPLOY_CHECKLIST.md`
3. Leia o README: `README.md`

**Boa sorte com o deploy! 🚀**
