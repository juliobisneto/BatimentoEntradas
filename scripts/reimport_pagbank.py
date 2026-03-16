#!/usr/bin/env python3
"""
Clear all PagBank acquirer imports and re-import the XML file.
Run from project root: python scripts/reimport_pagbank.py
"""
import json
import os
import sys

# Add project root to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.database import SessionLocal
from app.models.acquirer import (
    Acquirer,
    AcquirerFileImport,
    AcquirerTransaction,
    AcquirerTransactionExtra,
)
from app.services.acquirer_parser import parse_xml_with_config

FILE_PATH = os.path.join(
    os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
    "AcqImports",
    "Relatório O que vendi - PagBank.xml",
)


def main():
    db = SessionLocal()
    try:
        acquirer = db.query(Acquirer).filter(Acquirer.code.ilike("%PAGBANK%")).first()
        if not acquirer:
            print("PagBank acquirer not found. Create it in the Acquirers screen first.")
            return 1
        if not acquirer.parser_config:
            print("PagBank acquirer has no parser config. Configure it in the UI first.")
            return 1

        # Delete in order to respect FK (extras -> transactions -> file_imports)
        file_imports = db.query(AcquirerFileImport).filter(
            AcquirerFileImport.acquirer_id == acquirer.id
        ).all()
        for fi in file_imports:
            for t in db.query(AcquirerTransaction).filter(
                AcquirerTransaction.acquirer_file_import_id == fi.id
            ).all():
                db.query(AcquirerTransactionExtra).filter(
                    AcquirerTransactionExtra.acquirer_transaction_id == t.id
                ).delete()
            db.query(AcquirerTransaction).filter(
                AcquirerTransaction.acquirer_file_import_id == fi.id
            ).delete()
        db.query(AcquirerFileImport).filter(
            AcquirerFileImport.acquirer_id == acquirer.id
        ).delete()
        db.commit()
        print(f"Cleared all imports for acquirer '{acquirer.name}' (id={acquirer.id}).")

        if not os.path.isfile(FILE_PATH):
            print(f"File not found: {FILE_PATH}")
            return 1

        config = json.loads(acquirer.parser_config)
        with open(FILE_PATH, "rb") as f:
            content = f.read()
        rows = parse_xml_with_config(content, config, encoding=config.get("encoding"))
        print(f"Parsed {len(rows)} transactions.")

        file_import = AcquirerFileImport(
            acquirer_id=acquirer.id,
            file_name=os.path.basename(FILE_PATH),
            status="processing",
            records_count=0,
        )
        db.add(file_import)
        db.commit()
        db.refresh(file_import)

        count = 0
        for row in rows:
            try:
                extra_fields = row.pop("_extra", None)
                t = AcquirerTransaction(
                    acquirer_file_import_id=file_import.id,
                    acquirer_id=acquirer.id,
                    settlement_date=row.get("settlement_date"),
                    transaction_date=row.get("transaction_date"),
                    payment_type=row.get("payment_type"),
                    gross_amount=float(row.get("gross_amount") or 0),
                    fee_amount=float(row.get("fee_amount") or 0),
                    net_amount=float(row.get("net_amount") or 0),
                    reference_code=row.get("reference"),
                    acquirer_transaction_id=row.get("acquirer_transaction_id"),
                    status=row.get("status"),
                )
                db.add(t)
                db.flush()
                if extra_fields:
                    for field_name, value in extra_fields.items():
                        if not field_name:
                            continue
                        val = None if value is None else (str(value).strip() or None)
                        db.add(
                            AcquirerTransactionExtra(
                                acquirer_transaction_id=t.id,
                                acquirer_id=acquirer.id,
                                field_name=field_name,
                                value=val,
                            )
                        )
                count += 1
            except Exception as e:
                print(f"Row error: {e}")
                break

        file_import.records_count = count
        file_import.status = "completed"
        db.commit()
        print(f"Re-imported {count} records. File import id={file_import.id}")
        return 0
    finally:
        db.close()


if __name__ == "__main__":
    sys.exit(main())
