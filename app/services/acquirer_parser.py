"""
Parser genérico de arquivo XML e Excel do adquirente baseado em parser_config.
XML: root_element > repeating_element com campos mapeados.
Excel: planilha com header row e field_mappings (internal_key -> nome da coluna).
"""
import io
from datetime import datetime
from typing import Dict, Any, List, Optional
import xml.etree.ElementTree as ET

import pandas as pd


def _parse_br_decimal(value: str, decimal_separator: str = ",") -> float:
    """Converte string numérica BR (ex: 33,00) para float."""
    if not value or not value.strip():
        return 0.0
    s = value.strip().replace(".", "").replace(",", ".")
    try:
        return float(s)
    except ValueError:
        return 0.0


def _parse_date(value: str, date_format: str) -> Optional[datetime]:
    """Converte string de data conforme date_format."""
    if not value or not value.strip():
        return None
    try:
        return datetime.strptime(value.strip(), date_format)
    except (ValueError, TypeError):
        return None


def parse_xml_with_config(
    content: bytes,
    config: Dict[str, Any],
    encoding: Optional[str] = None,
) -> List[Dict[str, Any]]:
    """
    Parse XML usando parser_config.
    config esperado:
      - root_element: str
      - repeating_element: str
      - field_mappings: dict internal_key -> xml_tag_name
      - date_format: str (ex: %d/%m/%Y %H:%M)
      - decimal_separator: str (ex: ,)
      - encoding: str (ex: ISO-8859-1)
    Retorna lista de dicts com chaves internas (settlement_date, net_amount, etc).
    """
    enc = encoding or config.get("encoding") or "utf-8"
    try:
        text = content.decode(enc)
    except Exception:
        text = content.decode("utf-8", errors="replace")

    root_name = config.get("root_element") or "root"
    repeat_name = config.get("repeating_element") or "item"
    mappings = config.get("field_mappings") or {}
    mapped_xml_tags = set(mappings.values())  # tags that go to AcquirerTransaction
    date_fmt = config.get("date_format") or "%Y-%m-%d %H:%M:%S"
    dec_sep = config.get("decimal_separator") or ","

    date_fields = {"settlement_date", "transaction_date"}
    decimal_fields = {"net_amount", "gross_amount", "fee_amount"}

    root = ET.fromstring(text)

    def local_tag(elem):
        return elem.tag.split("}")[-1] if "}" in elem.tag else elem.tag

    # Filhos diretos do root que são o bloco repetido (ex.: Transaction)
    items = [c for c in root if local_tag(c) == repeat_name]
    if not items:
        # fallback: todos os elementos com esse nome na árvore
        items = [e for e in root.iter() if local_tag(e) == repeat_name]

    result = []
    for item in items:
        row = {}
        for internal_key, xml_tag in mappings.items():
            # Encontrar filho por tag (pode ter namespace)
            child = None
            for c in item:
                if local_tag(c) == xml_tag:
                    child = c
                    break
            if child is not None and child.text is not None:
                raw = child.text.strip()
            else:
                raw = ""

            if internal_key in date_fields and raw:
                row[internal_key] = _parse_date(raw, date_fmt)
            elif internal_key in decimal_fields:
                row[internal_key] = _parse_br_decimal(raw, dec_sep)
            else:
                row[internal_key] = raw if raw else None

        # Campos não mapeados: guardar em _extra como field_name -> value (string)
        extra = {}
        for c in item:
            tag = local_tag(c)
            if tag not in mapped_xml_tags:
                val = (c.text or "").strip()
                extra[tag] = val if val else None
        if extra:
            row["_extra"] = extra

        # Garantir net_amount como float para não quebrar
        if "net_amount" not in row or row["net_amount"] is None:
            row["net_amount"] = 0.0
        result.append(row)

    return result


def parse_xlsx_with_config(
    content: bytes,
    config: Dict[str, Any],
) -> List[Dict[str, Any]]:
    """
    Read Excel (.xlsx) with parser_config.
    config expected:
      - sheet: 0 or sheet name (str)
      - header_row: 0-based row index for column names (default 0)
      - field_mappings: dict internal_key -> column name (as in Excel header)
      - date_format: str (e.g. %d/%m/%Y %H:%M)
      - decimal_separator: str (e.g. ,)
    Returns list of dicts with internal keys; unmapped columns go to _extra.
    """
    mappings = config.get("field_mappings") or {}
    mapped_columns = set(mappings.values())
    date_fmt = config.get("date_format") or "%Y-%m-%d %H:%M:%S"
    dec_sep = config.get("decimal_separator") or ","
    sheet = config.get("sheet", 0)
    header_row = config.get("header_row", 0)

    date_fields = {"settlement_date", "transaction_date"}
    decimal_fields = {"net_amount", "gross_amount", "fee_amount"}

    df = pd.read_excel(io.BytesIO(content), sheet_name=sheet, header=header_row)

    result = []
    for _, series in df.iterrows():
        row = {}
        for internal_key, col_name in mappings.items():
            raw = ""
            val = None
            if col_name in df.columns:
                val = series.get(col_name)
                if pd.notna(val):
                    raw = str(val).strip()
            if internal_key in date_fields:
                if isinstance(val, pd.Timestamp):
                    row[internal_key] = val.to_pydatetime()
                elif raw:
                    row[internal_key] = _parse_date(raw, date_fmt)
                else:
                    row[internal_key] = None
            elif internal_key in decimal_fields:
                if isinstance(val, (int, float)) and not pd.isna(val):
                    row[internal_key] = float(val)
                else:
                    row[internal_key] = _parse_br_decimal(raw, dec_sep)
            else:
                row[internal_key] = raw if raw else None

        extra = {}
        for col in df.columns:
            if col not in mapped_columns:
                val = series.get(col)
                if pd.isna(val):
                    extra[col] = None
                else:
                    s = str(val).strip()
                    extra[col] = s if s else None
        if extra:
            row["_extra"] = extra

        if "net_amount" not in row or row["net_amount"] is None:
            row["net_amount"] = 0.0
        result.append(row)

    return result


def inspect_xlsx(content: bytes) -> Dict[str, Any]:
    """
    Inspect an xlsx file: return sheet names and, per sheet, column names
    and optionally the first data row. Use this to configure field_mappings.
    """
    xl = pd.ExcelFile(io.BytesIO(content))
    sheets = {}
    for name in xl.sheet_names:
        df = pd.read_excel(xl, sheet_name=name, header=0)
        columns = list(df.columns.astype(str))
        first_row = None
        if len(df) > 0:
            first_row = df.iloc[0].astype(str).replace("nan", "").to_dict()
        sheets[name] = {"columns": columns, "first_row": first_row, "row_count": len(df)}
    return {"sheet_names": xl.sheet_names, "sheets": sheets}
