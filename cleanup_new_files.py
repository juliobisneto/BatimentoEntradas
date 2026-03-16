#!/usr/bin/env python3
"""
Script para limpar arquivos já importados de new_files/

Remove de new_files/ os arquivos CSV que já foram importados com sucesso
(presentes em old_files/).
"""
import os
import sys

def cleanup_imported_files():
    """Remove de new_files/ os arquivos já importados (presentes em old_files/)"""
    new_files_dir = "new_files"
    old_files_dir = "old_files"
    
    # Validar diretórios
    if not os.path.exists(old_files_dir):
        print("❌ Diretório old_files/ não encontrado")
        return False
    
    if not os.path.exists(new_files_dir):
        print("❌ Diretório new_files/ não encontrado")
        return False
    
    # Obter lista de arquivos já importados
    old_files = set(f for f in os.listdir(old_files_dir) if f.endswith('.csv'))
    
    if not old_files:
        print("ℹ️  Nenhum arquivo encontrado em old_files/")
        return True
    
    print(f"📊 Encontrados {len(old_files)} arquivo(s) importado(s) em old_files/\n")
    
    # Processar arquivos em new_files
    removed_count = 0
    skipped_count = 0
    
    for filename in os.listdir(new_files_dir):
        if not filename.endswith('.csv'):
            continue
            
        if filename in old_files:
            file_path = os.path.join(new_files_dir, filename)
            try:
                # Obter tamanho do arquivo antes de remover
                file_size = os.path.getsize(file_path)
                file_size_kb = file_size / 1024
                
                os.remove(file_path)
                print(f"✅ Removido: {filename} ({file_size_kb:.1f} KB)")
                removed_count += 1
            except Exception as e:
                print(f"⚠️  Erro ao remover {filename}: {str(e)}")
                skipped_count += 1
        else:
            print(f"⏭️  Mantido: {filename} (ainda não importado)")
            skipped_count += 1
    
    # Resumo
    print(f"\n{'═'*60}")
    print(f"📋 RESUMO DA LIMPEZA")
    print(f"{'═'*60}")
    print(f"✅ Removidos:  {removed_count} arquivo(s)")
    print(f"⏭️  Mantidos:   {skipped_count} arquivo(s)")
    print(f"{'═'*60}\n")
    
    return True

def main():
    print("╔════════════════════════════════════════════════════════════╗")
    print("║  🗑️  LIMPEZA DE ARQUIVOS JÁ IMPORTADOS                    ║")
    print("╚════════════════════════════════════════════════════════════╝")
    print()
    print("Este script irá remover de new_files/ os arquivos CSV que")
    print("já foram importados com sucesso (presentes em old_files/).")
    print()
    
    # Confirmar ação
    response = input("Deseja continuar? (s/n): ").lower().strip()
    
    if response not in ['s', 'sim', 'y', 'yes']:
        print("\n❌ Operação cancelada pelo usuário.")
        sys.exit(0)
    
    print("\n🚀 Iniciando limpeza...\n")
    
    success = cleanup_imported_files()
    
    if success:
        print("✅ Limpeza concluída com sucesso!")
        sys.exit(0)
    else:
        print("❌ Limpeza finalizada com erros.")
        sys.exit(1)

if __name__ == "__main__":
    main()




