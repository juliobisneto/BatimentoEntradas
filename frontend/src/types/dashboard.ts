export interface DashboardSummary {
  total_transactions: number;
  total_sales_count: number;
  total_refunds_count: number;
  total_sales_value: number;
  total_refunds_value: number;
  net_revenue: number;
  net_revenue_after_tax: number;
  total_discount: number;
  total_items: number;
  average_transaction_value: number;
}

export interface DashboardTransaction {
  id: number;
  register: number;
  order_timestamp: string;
  event_sponsor: string;
  venue: string;
  event: string;
  number_of_items: number;
  total_order_value: number;
  net_amount: number;
  discount_amount: number;
  transaction_type: string;
  payment_method: {
    id: number;
    name: string;
  };
}

export interface DashboardData {
  summary: DashboardSummary;
  transactions: DashboardTransaction[];
}

export interface DashboardFilters {
  start_date?: string;
  end_date?: string;
  event_sponsor?: string;
  venue?: string;
  event?: string;
}

export interface FilterOptions {
  sponsors: string[];
  venues: string[];
  events: string[];
}

export interface PaymentMethodStats {
  payment_method: string;
  count: number;
  total_value: number;
  net_value: number;
}




