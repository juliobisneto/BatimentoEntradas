import pandas as pd
import re
import os
import shutil
from datetime import datetime, timedelta
from typing import Dict, List
from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError
from fastapi import UploadFile
import uuid
import io
from app.models.transaction import TransactionModel
from app.models.payment_method import PaymentMethod

class FileImportService:
    # Campos esperados na ordem correta
    EXPECTED_HEADERS = [
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
    
    def __init__(self, db: Session):
        self.db = db
    
    def check_file_already_imported(self, filename: str) -> Dict:
        """
        Verifica se o arquivo já foi importado anteriormente.
        Retorna informações sobre importação anterior se existir.
        """
        # Verificar se existe no diretório old_files
        old_files_dir = "old_files"
        old_file_path = os.path.join(old_files_dir, filename)
        
        if os.path.exists(old_file_path):
            # Buscar registros no banco de dados
            existing_records = self.db.query(TransactionModel).filter(
                TransactionModel.file_name == filename
            ).all()
            
            if existing_records:
                return {
                    "already_imported": True,
                    "file_location": "old_files",
                    "records_count": len(existing_records),
                    "first_import_date": min(r.created_at for r in existing_records),
                    "file_import_id": existing_records[0].file_import_id
                }
        
        # Verificar se existem registros no banco mesmo que o arquivo não esteja em old_files
        existing_records = self.db.query(TransactionModel).filter(
            TransactionModel.file_name == filename
        ).first()
        
        if existing_records:
            return {
                "already_imported": True,
                "file_location": "database",
                "message": "Arquivo já foi importado anteriormente (registros encontrados no banco)"
            }
        
        return {"already_imported": False}
    
    def validate_filename(self, filename: str) -> datetime:
        """Valida o formato do nome do arquivo e retorna a data"""
        pattern = r'^transactions_(\d{8})\.csv$'
        match = re.match(pattern, filename)
        
        if not match:
            raise ValueError(
                "Invalid filename. Expected format: transactions_YYYYMMDD.csv"
            )
        
        date_str = match.group(1)
        try:
            file_date = datetime.strptime(date_str, '%Y%m%d')
            return file_date
        except ValueError:
            raise ValueError(
                f"Invalid date in filename: {date_str}. Use YYYYMMDD format."
            )
    
    def validate_headers(self, df: pd.DataFrame) -> None:
        """Valida se os headers do arquivo estão corretos"""
        actual_headers = df.columns.tolist()
        
        if actual_headers != self.EXPECTED_HEADERS:
            raise ValueError(
                f"File headers do not match expected format.\n"
                f"Expected: {self.EXPECTED_HEADERS}\n"
                f"Found: {actual_headers}"
            )
    
    def validate_record_count(self, df: pd.DataFrame) -> tuple:
        """
        Valida o batimento do número de registros.
        A última linha deve conter o total de registros.
        Retorna: (dataframe sem última linha, total esperado)
        """
        if len(df) < 2:
            raise ValueError("File must have at least 2 lines (header + 1 record + total row)")
        
        last_row = df.iloc[-1]
        
        try:
            total_expected = int(last_row['#register'])
        except (ValueError, TypeError):
            raise ValueError(
                f"Last row must contain the total record count in '#register'. "
                f"Value found: {last_row['#register']}"
            )
        
        df_data = df.iloc[:-1]
        
        actual_records = len(df_data)
        if actual_records != total_expected:
            raise ValueError(
                f"Record count mismatch. Expected: {total_expected}, Found: {actual_records}"
            )
        
        return df_data, total_expected
    
    def validate_data_types(self, row: pd.Series, row_num: int) -> Dict:
        """Valida os tipos de dados de uma linha"""
        errors = []
        
        # Validar #register (integer)
        try:
            register = int(row['#register'])
        except (ValueError, TypeError):
            errors.append(f"#register must be an integer: {row['#register']}")
        
        # Validar order_timestamp (timestamp)
        try:
            if isinstance(row['order_timestamp'], str):
                order_timestamp = pd.to_datetime(row['order_timestamp'])
            else:
                order_timestamp = row['order_timestamp']
        except Exception as e:
            errors.append(f"Invalid order_timestamp: {row['order_timestamp']} - {str(e)}")
        
        # Validar payment_method_id (integer)
        try:
            payment_method_id = int(row['payment_method_id'])
        except (ValueError, TypeError):
            errors.append(f"payment_method_id must be an integer: {row['payment_method_id']}")
        
        # Validar strings
        event_sponsor = str(row['event_sponsor'])[:100]
        venue = str(row['venue'])[:100]
        event = str(row['event'])[:255]
        
        # Validar #of_items_in_order (integer)
        try:
            number_of_items = int(row['#of_items_in_order'])
            if number_of_items < 1:
                errors.append(f"#of_items_in_order must be greater than 0: {number_of_items}")
        except (ValueError, TypeError):
            errors.append(f"#of_items_in_order must be an integer: {row['#of_items_in_order']}")
        
        # Validar total_order_value (float)
        try:
            total_order_value = float(row['total_order_value'])
            if total_order_value <= 0:
                errors.append(f"total_order_value must be greater than 0: {total_order_value}")
        except (ValueError, TypeError):
            errors.append(f"total_order_value must be a number: {row['total_order_value']}")
        
        # Validar type_transaction (string 10)
        transaction_type = str(row['type_transaction'])[:10]
        
        if errors:
            raise ValueError("; ".join(errors))
        
        return {
            'register': register,
            'order_timestamp': order_timestamp,
            'payment_method_id': payment_method_id,
            'event_sponsor': event_sponsor,
            'venue': venue,
            'event': event,
            'number_of_items': number_of_items,
            'total_order_value': total_order_value,
            'transaction_type': transaction_type
        }
    
    async def import_file(self, file: UploadFile) -> Dict:
        """Importar arquivo CSV"""
        
        # 1. Validar nome do arquivo
        file_date = self.validate_filename(file.filename)
        
        # 2. Verificar se arquivo já foi importado
        import_check = self.check_file_already_imported(file.filename)
        if import_check["already_imported"]:
            import_info = import_check.get("records_count", "informação não disponível")
            import_date = import_check.get("first_import_date", "desconhecida")
            raise ValueError(
                f"Arquivo '{file.filename}' já foi importado anteriormente. "
                f"Importação original continha {import_info} registros. "
                f"Data da primeira importação: {import_date}"
            )
        
        file_import_id = str(uuid.uuid4())
        
        # 3. Salvar arquivo temporariamente em uploads
        uploads_dir = "uploads"
        old_files_dir = "old_files"
        os.makedirs(uploads_dir, exist_ok=True)
        os.makedirs(old_files_dir, exist_ok=True)
        
        temp_file_path = os.path.join(uploads_dir, file.filename)
        
        # Salvar arquivo
        contents = await file.read()
        with open(temp_file_path, "wb") as f:
            f.write(contents)
        
        # 3. Ler arquivo CSV
        try:
            df = pd.read_csv(io.BytesIO(contents))
        except Exception as e:
            # Remover arquivo em caso de erro
            if os.path.exists(temp_file_path):
                os.remove(temp_file_path)
            raise ValueError(f"Erro ao ler arquivo CSV: {str(e)}")
        
        # 4. Validar headers
        try:
            self.validate_headers(df)
        except Exception as e:
            # Remover arquivo em caso de erro de validação
            if os.path.exists(temp_file_path):
                os.remove(temp_file_path)
            raise
        
        # 5. Validar e fazer batimento do número de registros
        try:
            df_data, total_expected = self.validate_record_count(df)
        except Exception as e:
            # Remover arquivo em caso de erro de validação
            if os.path.exists(temp_file_path):
                os.remove(temp_file_path)
            raise
        
        # 6. Processar registros
        imported = 0
        duplicates = 0
        errors = []
        
        for index, row in df_data.iterrows():
            try:
                # Validar tipos de dados
                validated_data = self.validate_data_types(row, index + 2)
                
                # Verificar se método de pagamento existe
                payment_method = self.db.query(PaymentMethod).filter(
                    PaymentMethod.id == validated_data['payment_method_id']
                ).first()
                
                if not payment_method:
                    raise ValueError(
                        f"Payment method ID {validated_data['payment_method_id']} not found. "
                        f"Please register it in Payment Methods before importing."
                    )
                
                # Adicionar informações de controle
                validated_data['file_import_id'] = file_import_id
                validated_data['file_name'] = file.filename
                
                # Verificar se o registro já existe no banco (prevenir duplicata)
                existing = self.db.query(TransactionModel).filter(
                    TransactionModel.register == validated_data['register'],
                    TransactionModel.order_timestamp == validated_data['order_timestamp'],
                    TransactionModel.event_sponsor == validated_data['event_sponsor'],
                    TransactionModel.venue == validated_data['venue'],
                    TransactionModel.event == validated_data['event'],
                    TransactionModel.total_order_value == validated_data['total_order_value']
                ).first()
                
                if existing:
                    # Registro duplicado
                    duplicates += 1
                    errors.append({
                        "row": index + 2,
                        "register": row.get('#register', 'N/A'),
                        "error": "Registro duplicado (já existe no banco de dados)",
                        "type": "duplicate"
                    })
                else:
                    # Criar transação com cálculos
                    self.create_transaction_with_calculations(validated_data, payment_method)
                    imported += 1
                
            except Exception as e:
                errors.append({
                    "row": index + 2,  # +2 porque: +1 para índice base-1, +1 para header
                    "register": row.get('#register', 'N/A'),
                    "error": str(e),
                    "type": "validation_error"
                })
        
        # 7. Commit se houver registros importados
        if imported > 0:
            self.db.commit()
        
        # 8. Se importação foi bem-sucedida (todos os registros importados ou apenas duplicatas), mover para old_files
        # Considera sucesso se: importou todos OU se só teve duplicatas (registros já existiam)
        total_processed = imported + duplicates
        validation_errors = [e for e in errors if e.get('type') != 'duplicate']
        
        success = total_processed == total_expected and len(validation_errors) == 0
        
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
            
            if duplicates > 0:
                message = f"Arquivo processado: {imported} registros importados, {duplicates} duplicatas ignoradas. Movido para old_files."
            else:
                message = "Arquivo importado com sucesso e movido para old_files"
        else:
            # Manter em uploads se houver erros de validação
            file_location = "uploads"
            message = f"Arquivo importado com erros: {imported} importados, {duplicates} duplicatas, {len(validation_errors)} erros. Mantido em uploads."
        
        # 9. Retornar resultado
        return {
            "success": success,
            "message": message,
            "total_records_in_file": total_expected,
            "total_imported": imported,
            "total_duplicates": duplicates,
            "total_errors": len(validation_errors),
            "file_import_id": file_import_id,
            "file_name": file.filename,
            "file_location": file_location,
            "errors": errors
        }
    
    def create_transaction_with_calculations(
        self, 
        transaction_data: Dict, 
        payment_method: PaymentMethod
    ) -> TransactionModel:
        """Criar transação com cálculos automáticos"""
        
        # Calcular valores
        amount = transaction_data['total_order_value']
        discount_amount = amount * (payment_method.discount_rate / 100)
        net_amount = amount - discount_amount
        
        # Calcular data de liquidação
        order_timestamp = transaction_data['order_timestamp']
        settlement_date = order_timestamp + timedelta(days=payment_method.settlement_days)
        
        # Criar transação
        transaction = TransactionModel(
            **transaction_data,
            discount_amount=discount_amount,
            net_amount=net_amount,
            settlement_date=settlement_date
        )
        
        self.db.add(transaction)
        return transaction

