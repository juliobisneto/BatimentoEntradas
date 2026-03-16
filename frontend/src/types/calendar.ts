export interface CalendarTransaction {
  id: number;
  register: number;
  order_timestamp: string;
  event: string;
  venue: string;
  event_sponsor: string;
  total_order_value: number;
  net_amount: number;
  discount_amount: number;
  transaction_type: string;
}

export interface PaymentMethodSummary {
  method_id: number;
  method_name: string;
  count: number;
  total: number;
  net: number;
  transactions: CalendarTransaction[];
}

export interface DailySettlement {
  date: string;
  total_amount: number;
  total_net_amount: number;
  transaction_count: number;
  by_payment_method: PaymentMethodSummary[];
  status: 'settled' | 'pending';
}

export interface CalendarSummary {
  total_amount: number;
  settled_amount: number;
  pending_amount: number;
  settled_percentage: number;
  total_days: number;
  average_daily: number;
  min_settlement?: {
    date: string;
    amount: number;
  };
  max_settlement?: {
    date: string;
    amount: number;
  };
}

export interface PaymentCalendarData {
  period: {
    start: string | null;
    end: string | null;
  };
  daily_settlements: DailySettlement[];
  summary: CalendarSummary;
}




