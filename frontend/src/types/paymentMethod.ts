export interface PaymentMethod {
  id?: number;
  name: string;
  code: string;
  discount_rate: number;
  settlement_days: number;
  anticipation_rate: number;
  is_active: boolean;
  created_at?: string;
  updated_at?: string;
}

export interface PaymentMethodFormData {
  payment_method: string;
  payment_terms: number;
  tax: number;
}




