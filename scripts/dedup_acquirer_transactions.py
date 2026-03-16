#!/usr/bin/env python3
"""
Find duplicate acquirer transactions (same acquirer_id + acquirer_transaction_id)
and delete duplicates, keeping one record per pair.
Run from project root: python scripts/dedup_acquirer_transactions.py
"""
import os
import sys
from collections import defaultdict

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.database import SessionLocal
from app.models.acquirer import AcquirerTransaction


def main():
    db = SessionLocal()
    try:
        # All transactions with a non-empty acquirer_transaction_id
        rows = (
            db.query(AcquirerTransaction)
            .filter(
                AcquirerTransaction.acquirer_transaction_id.isnot(None),
                AcquirerTransaction.acquirer_transaction_id != "",
            )
            .order_by(AcquirerTransaction.id)
            .all()
        )

        # Group by (acquirer_id, acquirer_transaction_id); normalize id as string
        groups = defaultdict(list)
        for t in rows:
            key = (t.acquirer_id, str(t.acquirer_transaction_id).strip())
            groups[key].append(t)

        duplicates_to_delete = []
        for key, tx_list in groups.items():
            if len(tx_list) > 1:
                # Keep the first (smallest id), delete the rest
                for t in tx_list[1:]:
                    duplicates_to_delete.append(t)

        if not duplicates_to_delete:
            print("No duplicate acquirer transactions found.")
            return

        print(f"Found {len(duplicates_to_delete)} duplicate transaction(s) to remove (keeping first of each group).")

        for t in duplicates_to_delete:
            db.delete(t)
        db.commit()
        print(f"Deleted {len(duplicates_to_delete)} duplicate transaction(s). (Extras removed by cascade.)")
    finally:
        db.close()


if __name__ == "__main__":
    main()
