import axios from 'axios';
import { PaymentMethod } from '../types/paymentMethod';

// Get API URL from environment variable or use localhost as fallback
const API_URL = import.meta.env.VITE_API_URL || 'http://localhost:8000';

const api = axios.create({
  baseURL: API_URL,
  headers: {
    'Content-Type': 'application/json',
  },
});

// Add auth token to requests
api.interceptors.request.use(
  (config) => {
    const token = localStorage.getItem('access_token');
    if (token) {
      config.headers.Authorization = `Bearer ${token}`;
    }
    return config;
  },
  (error) => {
    return Promise.reject(error);
  }
);

// Handle auth errors
api.interceptors.response.use(
  (response) => response,
  (error) => {
    if (error.response?.status === 401) {
      // Unauthorized - clear token and redirect to login
      localStorage.removeItem('access_token');
      window.location.href = '/';
    }
    return Promise.reject(error);
  }
);

export const paymentMethodsAPI = {
  // Listar todos os métodos de pagamento
  getAll: async (): Promise<PaymentMethod[]> => {
    const response = await api.get('/payment-methods/');
    return response.data;
  },

  // Buscar método de pagamento por ID
  getById: async (id: number): Promise<PaymentMethod> => {
    const response = await api.get(`/payment-methods/${id}`);
    return response.data;
  },

  // Criar novo método de pagamento
  create: async (data: {
    payment_method: string;
    payment_terms: number;
    tax: number;
  }): Promise<PaymentMethod> => {
    // Converter os dados do formulário para o formato da API
    const apiData = {
      name: data.payment_method,
      code: data.payment_method.toUpperCase().replace(/\s+/g, '_'),
      discount_rate: data.tax,
      settlement_days: data.payment_terms,
      anticipation_rate: data.tax * 1.2, // Taxa de antecipação = taxa + 20%
      is_active: true,
    };
    
    const response = await api.post('/payment-methods/', apiData);
    return response.data;
  },

  // Atualizar método de pagamento
  update: async (
    id: number,
    data: {
      payment_method?: string;
      payment_terms?: number;
      tax?: number;
    }
  ): Promise<PaymentMethod> => {
    const apiData: any = {};
    
    if (data.payment_method) {
      apiData.name = data.payment_method;
    }
    if (data.payment_terms !== undefined) {
      apiData.settlement_days = data.payment_terms;
    }
    if (data.tax !== undefined) {
      apiData.discount_rate = data.tax;
      apiData.anticipation_rate = data.tax * 1.2;
    }
    
    console.log('API update call:', { id, data, apiData });
    const response = await api.put(`/payment-methods/${id}`, apiData);
    console.log('API update response:', response.data);
    return response.data;
  },

  // Deletar método de pagamento
  delete: async (id: number): Promise<void> => {
    await api.delete(`/payment-methods/${id}`);
  },

  // Ativar/Desativar método de pagamento
  toggleActive: async (id: number, isActive: boolean): Promise<PaymentMethod> => {
    const response = await api.put(`/payment-methods/${id}`, { is_active: isActive });
    return response.data;
  },
};

export const dashboardAPI = {
  // Obter resumo do dashboard
  getSummary: async (filters: {
    start_date?: string;
    end_date?: string;
    event_sponsor?: string;
    venue?: string;
    event?: string;
  }): Promise<any> => {
    const params = new URLSearchParams();
    
    if (filters.start_date) params.append('start_date', filters.start_date);
    if (filters.end_date) params.append('end_date', filters.end_date);
    if (filters.event_sponsor) params.append('event_sponsor', filters.event_sponsor);
    if (filters.venue) params.append('venue', filters.venue);
    if (filters.event) params.append('event', filters.event);
    
    const response = await api.get(`/transactions/dashboard/summary?${params.toString()}`);
    return response.data;
  },

  // Obter opções de filtros
  getFilterOptions: async (): Promise<any> => {
    const response = await api.get('/transactions/dashboard/filters');
    return response.data;
  },

  // Obter estatísticas por método de pagamento
  getByPaymentMethod: async (filters: {
    start_date?: string;
    end_date?: string;
    event_sponsor?: string;
    venue?: string;
    event?: string;
  }): Promise<any> => {
    const params = new URLSearchParams();
    
    if (filters.start_date) params.append('start_date', filters.start_date);
    if (filters.end_date) params.append('end_date', filters.end_date);
    if (filters.event_sponsor) params.append('event_sponsor', filters.event_sponsor);
    if (filters.venue) params.append('venue', filters.venue);
    if (filters.event) params.append('event', filters.event);
    
    const response = await api.get(`/transactions/dashboard/by-payment-method?${params.toString()}`);
    return response.data;
  },

  // Obter calendário de pagamentos
  getPaymentCalendar: async (filters: {
    start_date?: string;
    end_date?: string;
    payment_method_id?: number;
  }): Promise<any> => {
    const params = new URLSearchParams();
    
    if (filters.start_date) params.append('start_date', filters.start_date);
    if (filters.end_date) params.append('end_date', filters.end_date);
    if (filters.payment_method_id) params.append('payment_method_id', filters.payment_method_id.toString());
    
    const response = await api.get(`/transactions/payment-calendar?${params.toString()}`);
    return response.data;
  },
};

export const acquirersAPI = {
  getAll: async (isActive?: boolean): Promise<any[]> => {
    const response = await api.get('/acquirers/', { params: isActive !== undefined ? { is_active: isActive } : {} });
    return response.data;
  },
  getById: async (id: number): Promise<any> => {
    const response = await api.get(`/acquirers/${id}`);
    return response.data;
  },
  create: async (data: { name: string; code: string; file_format?: string; parser_config?: any; is_active?: boolean }) => {
    const response = await api.post('/acquirers/', data);
    return response.data;
  },
  update: async (id: number, data: Partial<{ name: string; code: string; file_format: string; parser_config: any; is_active: boolean }>) => {
    const response = await api.put(`/acquirers/${id}`, data);
    return response.data;
  },
  delete: async (id: number): Promise<void> => {
    await api.delete(`/acquirers/${id}`);
  },
  getParserConfig: async (id: number): Promise<{ parser_config: any }> => {
    const response = await api.get(`/acquirers/${id}/parser-config`);
    return response.data;
  },
  updateParserConfig: async (id: number, parser_config: object) => {
    const response = await api.put(`/acquirers/${id}/parser-config`, { parser_config });
    return response.data;
  },
  getPaymentMethods: async (acquirerId: number): Promise<any[]> => {
    const response = await api.get(`/acquirers/${acquirerId}/payment-methods`);
    return response.data;
  },
  createPaymentMethod: async (acquirerId: number, data: any) => {
    const response = await api.post(`/acquirers/${acquirerId}/payment-methods`, data);
    return response.data;
  },
  updatePaymentMethod: async (acquirerId: number, pmId: number, data: any) => {
    const response = await api.put(`/acquirers/${acquirerId}/payment-methods/${pmId}`, data);
    return response.data;
  },
  deletePaymentMethod: async (acquirerId: number, pmId: number): Promise<void> => {
    await api.delete(`/acquirers/${acquirerId}/payment-methods/${pmId}`);
  },
  importFile: async (acquirerId: number, file: File): Promise<any> => {
    const formData = new FormData();
    formData.append('file', file);
    const response = await api.post(`/acquirers/${acquirerId}/import`, formData, {
      headers: { 'Content-Type': 'multipart/form-data' },
    });
    return response.data;
  },
  listImports: async (acquirerId: number): Promise<any[]> => {
    const response = await api.get(`/acquirers/${acquirerId}/imports`);
    return response.data;
  },
};

export default api;

