# 🗑️ Limpeza Automática de Arquivos

## Visão Geral

O sistema agora possui **limpeza automática** dos arquivos CSV após importação bem-sucedida, evitando duplicação de armazenamento e facilitando o gerenciamento de arquivos.

---

## Como Funciona

### Fluxo de Importação

```
1. Upload do arquivo → salvado temporariamente em uploads/
2. Validação e processamento dos registros
3. ✅ Se sucesso:
   ├─ Arquivo movido de uploads/ para old_files/
   └─ Arquivo REMOVIDO de new_files/ (se existir)
4. ❌ Se erro:
   └─ Arquivo mantido em uploads/ para análise
```

### Remoção Automática

Após uma importação bem-sucedida, o sistema:

1. **Move** o arquivo de `uploads/` para `old_files/`
2. **Verifica** se existe uma cópia em `new_files/`
3. **Remove** automaticamente a cópia de `new_files/`
4. **Registra** aviso em caso de erro (mas não falha a importação)

---

## Estrutura de Diretórios

```
BatimentoEntradas/
│
├── new_files/              # 📥 Arquivos aguardando importação
│   ├── README.md           #    (apenas arquivos não importados)
│   └── (vazio após importação)
│
├── uploads/                # 🔄 Armazenamento temporário
│   └── (arquivos com erro de validação)
│
└── old_files/              # 📦 Arquivos importados (arquivo)
    ├── transactions_20251002.csv
    ├── transactions_20251010.csv
    ├── transactions_20251011.csv
    ├── transactions_20251021.csv
    ├── transactions_20251031.csv
    └── transactions_20251101.csv
```

---

## Teste da Funcionalidade

### ✅ Resultado do Teste

**Arquivo de teste:** `transactions_20251101.csv` (30 registros)

**Antes da importação:**
```
new_files/transactions_20251101.csv  ✓ Presente
```

**Após importação bem-sucedida:**
```
new_files/transactions_20251101.csv  ✗ Removido automaticamente
old_files/transactions_20251101.csv  ✓ Movido para arquivo
```

**Status:** ✅ Funcionando perfeitamente!

---

## Script de Limpeza Manual

Para limpar arquivos já importados anteriormente, use o script `cleanup_new_files.py`:

```bash
python3 cleanup_new_files.py
```

### Funcionalidades do Script

- ✅ Lista todos os arquivos em `old_files/`
- ✅ Compara com arquivos em `new_files/`
- ✅ Remove duplicatas de `new_files/`
- ✅ Exibe relatório detalhado
- ✅ Solicita confirmação antes de executar

### Exemplo de Uso

```bash
$ python3 cleanup_new_files.py

╔════════════════════════════════════════════════════════════╗
║  🗑️  LIMPEZA DE ARQUIVOS JÁ IMPORTADOS                    ║
╚════════════════════════════════════════════════════════════╝

Este script irá remover de new_files/ os arquivos CSV que
já foram importados com sucesso (presentes em old_files/).

Deseja continuar? (s/n): s

🚀 Iniciando limpeza...

📊 Encontrados 6 arquivo(s) importado(s) em old_files/

✅ Removido: transactions_20251002.csv (8.7 KB)
✅ Removido: transactions_20251010.csv (8.8 KB)
✅ Removido: transactions_20251011.csv (8.6 KB)
✅ Removido: transactions_20251021.csv (8.8 KB)

════════════════════════════════════════════════════════════
📋 RESUMO DA LIMPEZA
════════════════════════════════════════════════════════════
✅ Removidos:  4 arquivo(s)
⏭️  Mantidos:   0 arquivo(s)
════════════════════════════════════════════════════════════

✅ Limpeza concluída com sucesso!
```

---

## Vantagens

### 🎯 Economia de Espaço
- Evita duplicação de arquivos CSV
- Mantém apenas cópias necessárias
- Reduz uso de disco

### 📋 Organização
- `new_files/` contém apenas arquivos pendentes
- `old_files/` contém arquivo completo
- Fácil identificar o que falta importar

### 🔒 Segurança
- Arquivo preservado em `old_files/`
- Backup completo de todas as importações
- Rastreabilidade mantida no banco de dados

### ⚙️ Automação
- Sem necessidade de intervenção manual
- Limpeza acontece automaticamente
- Menos chance de erro humano

---

## Comportamento em Diferentes Cenários

### Cenário 1: Importação Bem-Sucedida
```
✅ Arquivo movido para old_files/
✅ Arquivo removido de new_files/
✅ Registros no banco de dados
```

### Cenário 2: Importação com Duplicatas
```
✅ Arquivo movido para old_files/ (sucesso)
✅ Arquivo removido de new_files/
ℹ️  Duplicatas ignoradas, sem erro
```

### Cenário 3: Erro de Validação
```
❌ Arquivo mantido em uploads/
✅ Arquivo permanece em new_files/
ℹ️  Permite correção e reimportação
```

### Cenário 4: Arquivo Não Existe em new_files/
```
✅ Importação normal
ℹ️  Nenhuma ação adicional necessária
⚠️  Nenhum erro gerado
```

---

## Implementação Técnica

### Código em `app/services/file_import.py`

```python
if success:
    # Mover arquivo para old_files
    old_file_path = os.path.join(old_files_dir, file.filename)
    shutil.move(temp_file_path, old_file_path)
    file_location = "old_files"
    
    # Apagar arquivo de new_files se existir
    new_files_path = os.path.join("new_files", file.filename)
    if os.path.exists(new_files_path):
        try:
            os.remove(new_files_path)
        except Exception as e:
            # Log do erro mas não falha a importação
            print(f"⚠️  Aviso: Não foi possível remover {new_files_path}: {str(e)}")
```

### Características da Implementação

- ✅ **Segura**: Não falha se o arquivo não existir
- ✅ **Robusta**: Captura exceções de remoção
- ✅ **Não-intrusiva**: Não afeta o resultado da importação
- ✅ **Transparente**: Registra avisos em caso de problema

---

## Boas Práticas

### Para Novos Arquivos

1. **Adicione** arquivos CSV em `new_files/`
2. **Importe** via API ou dashboard
3. **Aguarde** - limpeza é automática
4. **Verifique** `old_files/` para confirmar

### Para Arquivos Existentes

1. **Execute** `python3 cleanup_new_files.py`
2. **Confirme** a limpeza quando solicitado
3. **Verifique** o relatório de remoção

### Backup

- `old_files/` serve como **arquivo master**
- Faça backup regular de `old_files/`
- Banco de dados contém todos os registros
- Dupla segurança de dados

---

## Solução de Problemas

### Arquivo não foi removido de new_files/

**Possíveis causas:**
- Permissões de arquivo/diretório
- Arquivo em uso por outro processo
- Sistema de arquivos somente leitura

**Solução:**
1. Verificar permissões: `ls -l new_files/`
2. Remover manualmente: `rm new_files/arquivo.csv`
3. Ou usar script: `python3 cleanup_new_files.py`

### Erro durante remoção

**O que acontece:**
- Importação **NÃO é afetada**
- Aviso é registrado no console
- Arquivo permanece em `new_files/`

**Ação:**
- Remover manualmente quando possível
- Ou ignorar (apenas usa espaço extra)

---

## Estatísticas

### Teste Realizado

- **Arquivo:** transactions_20251101.csv
- **Tamanho:** 2.7 KB
- **Registros:** 30 (todos duplicatas)
- **Resultado:** ✅ Sucesso
- **Remoção:** ✅ Automática
- **Tempo:** < 1 segundo

### Economia de Espaço

Com 5 arquivos de ~8.7 KB cada:
- **Antes:** ~43.5 KB duplicados
- **Depois:** 0 KB duplicados
- **Economia:** ~43.5 KB por ciclo de importação

---

## Conclusão

A limpeza automática de arquivos após importação:

✅ **Economiza** espaço em disco  
✅ **Organiza** o fluxo de trabalho  
✅ **Automatiza** tarefas manuais  
✅ **Preserva** segurança dos dados  
✅ **Mantém** rastreabilidade completa  

O sistema agora está ainda mais robusto e profissional! 🚀

---

**Implementado em:** 31/10/2025  
**Versão:** 1.1  
**Status:** ✅ Produção




