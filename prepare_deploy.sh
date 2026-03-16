#!/bin/bash

# 🚀 Script de Deploy Simplificado
# Execute este script para preparar o código para deploy

echo "================================================"
echo "🚀 Preparando Aplicação para Deploy"
echo "================================================"
echo ""

# Verificar se está no diretório correto
if [ ! -f "requirements.txt" ]; then
    echo "❌ Erro: Execute este script na raiz do projeto!"
    exit 1
fi

# 1. Verificar Git
echo "📦 [1/5] Verificando Git..."
if [ ! -d ".git" ]; then
    echo "   Inicializando repositório Git..."
    git init
else
    echo "   ✅ Git já inicializado"
fi
echo ""

# 2. Preparar .gitignore
echo "🔒 [2/5] Verificando .gitignore..."
if [ -f ".gitignore" ]; then
    echo "   ✅ .gitignore presente"
else
    echo "   ❌ .gitignore não encontrado!"
fi
echo ""

# 3. Adicionar arquivos ao Git
echo "📝 [3/5] Adicionando arquivos ao Git..."
git add -A
echo "   ✅ Arquivos adicionados"
echo ""

# 4. Mostrar status
echo "📊 [4/5] Status do repositório:"
git status --short
echo ""

# 5. Instruções finais
echo "================================================"
echo "✅ Preparação Concluída!"
echo "================================================"
echo ""
echo "📋 PRÓXIMOS PASSOS:"
echo ""
echo "1️⃣  Criar repositório no GitHub:"
echo "    → https://github.com/new"
echo "    → Nome sugerido: batimento-entradas"
echo ""
echo "2️⃣  Fazer primeiro commit e push:"
echo "    git commit -m \"Initial commit - Ready for deployment\""
echo "    git remote add origin https://github.com/SEU-USUARIO/batimento-entradas.git"
echo "    git branch -M main"
echo "    git push -u origin main"
echo ""
echo "3️⃣  Seguir o guia de deploy:"
echo "    → Leia: GUIA_DEPLOY_RAPIDO.md"
echo "    → Ou: DEPLOY_GUIDE.md (guia completo)"
echo ""
echo "================================================"
echo "🔑 CREDENCIAIS GERADAS:"
echo "================================================"
echo ""
echo "SECRET_KEY (para o backend):"
echo "a9ec8e9beb31ba613d7ec1096dc54a323893801b9c5220264144e8f4ea757b78"
echo ""
echo "⚠️  GUARDE ESTA CHAVE EM LOCAL SEGURO!"
echo ""
echo "================================================"
echo "🌐 PLATAFORMAS NECESSÁRIAS:"
echo "================================================"
echo ""
echo "Backend:  https://render.com (Free)"
echo "Frontend: https://vercel.com (Free)"
echo "Database: Render PostgreSQL (Free)"
echo "Storage:  https://supabase.com (Opcional, Free)"
echo ""
echo "💰 Custo Total: \$0/mês"
echo ""
echo "================================================"
echo "📚 DOCUMENTAÇÃO:"
echo "================================================"
echo ""
echo "→ GUIA_DEPLOY_RAPIDO.md     - Guia simplificado"
echo "→ PRE_DEPLOY_CHECKLIST.md   - Checklist de preparação"
echo "→ DEPLOY_GUIDE.md           - Guia completo passo a passo"
echo "→ DEPLOY_CHECKLIST.md       - Checklist durante deploy"
echo ""
echo "Boa sorte com o deploy! 🚀"
echo ""
