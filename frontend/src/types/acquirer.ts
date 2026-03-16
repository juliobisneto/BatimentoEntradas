export interface Acquirer {
  id: number;
  name: string;
  code: string;
  file_format: string;
  parser_config: ParserConfig | null;
  is_active: boolean;
  created_at: string;
  updated_at: string;
}

export interface ParserConfig {
  root_element?: string;
  repeating_element?: string;
  field_mappings?: Record<string, string>;
  date_format?: string;
  decimal_separator?: string;
  encoding?: string;
}

export interface AcquirerPaymentMethod {
  id: number;
  acquirer_id: number;
  name: string;
  code: string;
  discount_rate: number;
  settlement_days: number;
  anticipation_rate: number;
  is_active: boolean;
  payment_method_id: number | null;
  created_at: string;
  updated_at: string;
}

export interface AcquirerFileImport {
  id: number;
  acquirer_id: number;
  file_name: string;
  imported_at: string;
  status: string;
  records_count: number;
  error_message: string | null;
}

export interface AcquirerImportResult {
  success: boolean;
  message: string;
  file_import_id?: number;
  records_imported: number;
  duplicates_ignored?: number;
  errors: string[];
}
