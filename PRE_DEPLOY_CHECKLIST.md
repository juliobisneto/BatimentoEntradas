# ✅ CHECKLIST DE PRÉ-DEPLOY

Antes de fazer o deploy, verifique:

## 📦 Código e Repositório

- [x] Repositório Git inicializado
- [ ] Código commitado (sem arquivos pendentes)
- [ ] Repositório criado no GitHub
- [ ] Código enviado para GitHub (`git push`)
- [x] Arquivo `.gitignore` presente (não sobe .env, uploads, node_modules, etc)

## 🔐 Segurança e Credenciais

- [x] SECRET_KEY gerada (NÃO use a padrão em produção!)
  - Valor gerado: `a9ec8e9beb31ba613d7ec1096dc54a323893801b9c5220264144e8f4ea757b78`
- [ ] Arquivos `.env` NÃO commitados (devem estar em .gitignore)
- [ ] Senhas e tokens salvos em local seguro

## 📋 Arquivos de Configuração

- [x] `requirements.txt` - Dependências Python
- [x] `runtime.txt` - Versão do Python (3.11.0)
- [x] `Procfile` - Comando de start
- [x] `render.yaml` - Configuração do Render (opcional)
- [x] `frontend/package.json` - Dependências Node.js
- [x] `frontend/vercel.json` - Configuração do Vercel

## 🧪 Testes Locais (Opcional mas Recomendado)

- [ ] Backend rodando localmente (`uvicorn app.main:app --reload`)
- [ ] Frontend rodando localmente (`npm run dev`)
- [ ] Login funcionando
- [ ] Dashboard carregando
- [ ] Importação de CSV funcionando

## 🌐 Contas Criadas

- [ ] Conta no GitHub (para hospedar código)
- [ ] Conta no Render (para backend + database)
- [ ] Conta no Vercel (para frontend)
- [ ] Conta no Supabase (opcional - para storage de arquivos)

## 📝 Informações que Você Vai Precisar

### Para o Backend (Render):
- [ ] Database URL (será gerado pelo Render)
- [x] SECRET_KEY (já gerado)
- [ ] Frontend URL (será gerado pelo Vercel)

### Para o Frontend (Vercel):
- [ ] Backend URL (será gerado pelo Render)

---

## 🚀 Próximos Passos

Se todos os itens acima estiverem ✅, você está pronto para:

1. **Criar repositório no GitHub** e fazer push do código
2. **Seguir o GUIA_DEPLOY_RAPIDO.md** para deploy

Tempo estimado total: **30-40 minutos**

Custo total: **$0/mês** 💰

---

## 📞 Comandos Rápidos

### Commitar e enviar código para GitHub

```bash
cd /Users/juliobisneto/temp/BatimentoEntradas

git add .
git commit -m "Ready for deployment"

# Criar repositório no GitHub primeiro, depois:
git remote add origin https://github.com/SEU-USUARIO/batimento-entradas.git
git branch -M main
git push -u origin main
```

### Testar localmente (opcional)

```bash
# Terminal 1 - Backend
cd /Users/juliobisneto/temp/BatimentoEntradas
python -m venv venv
source venv/bin/activate
pip install -r requirements.txt

# Copiar configurações locais
cp .env.local.example .env

# Inicializar database
python scripts/init_db.py
python scripts/create_admin.py

# Rodar backend
uvicorn app.main:app --reload

# Terminal 2 - Frontend
cd /Users/juliobisneto/temp/BatimentoEntradas/frontend
npm install

# Copiar configurações locais
cp .env.local.example .env

# Rodar frontend
npm run dev
```

Acesse: http://localhost:3000

Login: `admin@admin.com` / `admin`

---

**Boa sorte! 🚀**
