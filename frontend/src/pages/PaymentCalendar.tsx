import React, { useState, useEffect } from 'react';
import { toast } from 'react-toastify';
import { dashboardAPI, paymentMethodsAPI } from '../services/api';
import { PaymentCalendarData, DailySettlement } from '../types/calendar';
import { PaymentMethod } from '../types/paymentMethod';
import { FaCalendarAlt, FaChevronLeft, FaChevronRight, FaFilter, FaTimes } from 'react-icons/fa';
import CalendarDay from '../components/CalendarDay';
import DayDetailModal from '../components/DayDetailModal';

const PaymentCalendar: React.FC = () => {
  const [calendarData, setCalendarData] = useState<PaymentCalendarData | null>(null);
  const [paymentMethods, setPaymentMethods] = useState<PaymentMethod[]>([]);
  const [loading, setLoading] = useState(false);
  const [selectedDay, setSelectedDay] = useState<DailySettlement | null>(null);
  
  // Filters
  const [startDate, setStartDate] = useState<string>('');
  const [endDate, setEndDate] = useState<string>('');
  const [selectedPaymentMethod, setSelectedPaymentMethod] = useState<number | undefined>(undefined);
  
  // Initialize dates (current month, first 15 days)
  useEffect(() => {
    const now = new Date();
    const start = new Date(now.getFullYear(), now.getMonth(), 1);
    const end = new Date(now.getFullYear(), now.getMonth(), 15);
    
    setStartDate(start.toISOString().split('T')[0]);
    setEndDate(end.toISOString().split('T')[0]);
  }, []);
  
  // Load payment methods
  useEffect(() => {
    loadPaymentMethods();
  }, []);
  
  // Load calendar data when filters change
  useEffect(() => {
    if (startDate && endDate) {
      loadCalendarData();
    }
  }, [startDate, endDate, selectedPaymentMethod]);
  
  const loadPaymentMethods = async () => {
    try {
      const data = await paymentMethodsAPI.getAll();
      setPaymentMethods(data);
    } catch (error) {
      console.error('Error loading payment methods:', error);
    }
  };
  
  const loadCalendarData = async () => {
    setLoading(true);
    try {
      const data = await dashboardAPI.getPaymentCalendar({
        start_date: startDate,
        end_date: endDate,
        payment_method_id: selectedPaymentMethod
      });
      setCalendarData(data);
    } catch (error) {
      toast.error('Error loading payment calendar');
      console.error('Error loading calendar:', error);
    } finally {
      setLoading(false);
    }
  };
  
  const navigatePeriod = (direction: 'prev' | 'next') => {
    const start = new Date(startDate);
    const end = new Date(endDate);
    const days = Math.ceil((end.getTime() - start.getTime()) / (1000 * 60 * 60 * 24));
    
    if (direction === 'prev') {
      start.setDate(start.getDate() - days);
      end.setDate(end.getDate() - days);
    } else {
      start.setDate(start.getDate() + days);
      end.setDate(end.getDate() + days);
    }
    
    setStartDate(start.toISOString().split('T')[0]);
    setEndDate(end.toISOString().split('T')[0]);
  };
  
  const clearFilters = () => {
    const now = new Date();
    const start = new Date(now.getFullYear(), now.getMonth(), 1);
    const end = new Date(now.getFullYear(), now.getMonth(), 15);
    
    setStartDate(start.toISOString().split('T')[0]);
    setEndDate(end.toISOString().split('T')[0]);
    setSelectedPaymentMethod(undefined);
  };
  
  const formatCurrency = (value: number) => {
    return new Intl.NumberFormat('pt-BR', {
      style: 'currency',
      currency: 'BRL'
    }).format(value);
  };
  
  const formatDate = (dateStr: string) => {
    const date = new Date(dateStr + 'T00:00:00');
    return new Intl.DateTimeFormat('en-US', {
      day: '2-digit',
      month: 'short',
      year: 'numeric'
    }).format(date);
  };
  
  // Generate calendar grid
  const generateCalendarGrid = () => {
    if (!calendarData || calendarData.daily_settlements.length === 0) {
      return [];
    }
    
    const start = new Date(calendarData.daily_settlements[0].date + 'T00:00:00');
    const end = new Date(calendarData.daily_settlements[calendarData.daily_settlements.length - 1].date + 'T00:00:00');
    
    const grid: (DailySettlement | null)[] = [];
    const settlementMap = new Map(
      calendarData.daily_settlements.map(s => [s.date, s])
    );
    
    // Fill grid from start to end
    const current = new Date(start);
    while (current <= end) {
      const dateKey = current.toISOString().split('T')[0];
      grid.push(settlementMap.get(dateKey) || null);
      current.setDate(current.getDate() + 1);
    }
    
    return grid;
  };
  
  const calendarGrid = generateCalendarGrid();
  
  return (
    <div className="min-h-screen bg-gray-100 p-6">
      <div className="max-w-7xl mx-auto">
        {/* Header */}
        <div className="bg-white rounded-lg shadow-md p-6 mb-6">
          <div className="flex items-center justify-between mb-6">
            <div className="flex items-center gap-3">
              <FaCalendarAlt className="text-3xl text-blue-600" />
              <h1 className="text-2xl font-bold text-gray-800">Payment Calendar</h1>
            </div>
          </div>
          
          {/* Filters */}
          <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-2">
                Start Date
              </label>
              <input
                type="date"
                value={startDate}
                onChange={(e) => setStartDate(e.target.value)}
                className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
              />
            </div>
            
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-2">
                End Date
              </label>
              <input
                type="date"
                value={endDate}
                onChange={(e) => setEndDate(e.target.value)}
                className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
              />
            </div>
            
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-2">
                Payment Method
              </label>
              <select
                value={selectedPaymentMethod || ''}
                onChange={(e) => setSelectedPaymentMethod(e.target.value ? parseInt(e.target.value) : undefined)}
                className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
              >
                <option value="">All</option>
                {paymentMethods.map(pm => (
                  <option key={pm.id} value={pm.id}>{pm.name}</option>
                ))}
              </select>
            </div>
            
            <div className="flex items-end gap-2">
              <button
                onClick={clearFilters}
                className="flex-1 px-4 py-2 bg-gray-200 text-gray-700 rounded-md hover:bg-gray-300 transition-colors flex items-center justify-center gap-2"
              >
                <FaTimes /> Clear
              </button>
            </div>
          </div>
          
          {/* Period Navigation */}
          <div className="flex items-center justify-between mt-4 pt-4 border-t border-gray-200">
            <button
              onClick={() => navigatePeriod('prev')}
              className="px-4 py-2 bg-blue-600 text-white rounded-md hover:bg-blue-700 transition-colors flex items-center gap-2"
            >
              <FaChevronLeft /> Previous
            </button>
            
            <div className="text-lg font-semibold text-gray-700">
              {startDate && endDate && `${formatDate(startDate)} - ${formatDate(endDate)}`}
            </div>
            
            <button
              onClick={() => navigatePeriod('next')}
              className="px-4 py-2 bg-blue-600 text-white rounded-md hover:bg-blue-700 transition-colors flex items-center gap-2"
            >
              Next <FaChevronRight />
            </button>
          </div>
          
          {/* Summary */}
          {calendarData && (
            <div className="mt-4 pt-4 border-t border-gray-200">
              <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
                <div>
                  <div className="text-sm text-gray-600">Total Receivable</div>
                  <div className="text-xl font-bold text-blue-600">
                    {formatCurrency(calendarData.summary.total_amount)}
                  </div>
                </div>
                <div>
                  <div className="text-sm text-gray-600">Settled</div>
                  <div className="text-xl font-bold text-green-600">
                    {formatCurrency(calendarData.summary.settled_amount)}
                    <span className="text-sm ml-2">({calendarData.summary.settled_percentage.toFixed(1)}%)</span>
                  </div>
                </div>
                <div>
                  <div className="text-sm text-gray-600">Pending</div>
                  <div className="text-xl font-bold text-orange-600">
                    {formatCurrency(calendarData.summary.pending_amount)}
                  </div>
                </div>
                <div>
                  <div className="text-sm text-gray-600">Daily Average</div>
                  <div className="text-xl font-bold text-gray-700">
                    {formatCurrency(calendarData.summary.average_daily)}
                  </div>
                </div>
              </div>
            </div>
          )}
        </div>
        
        {/* Calendar Grid */}
        {loading ? (
          <div className="bg-white rounded-lg shadow-md p-12 text-center">
            <div className="text-gray-500">Loading calendar...</div>
          </div>
        ) : calendarGrid.length === 0 ? (
          <div className="bg-white rounded-lg shadow-md p-12 text-center">
            <div className="text-gray-500">No payments found in the selected period</div>
          </div>
        ) : (
          <div className="bg-white rounded-lg shadow-md p-6">
            <div className="grid grid-cols-7 gap-3">
              {['Sun', 'Mon', 'Tue', 'Wed', 'Thu', 'Fri', 'Sat'].map(day => (
                <div key={day} className="text-center font-bold text-gray-700 py-2">
                  {day}
                </div>
              ))}
              
              {calendarGrid.map((settlement, index) => (
                <CalendarDay
                  key={index}
                  settlement={settlement}
                  onSelect={setSelectedDay}
                />
              ))}
            </div>
          </div>
        )}
      </div>
      
      {/* Day Detail Modal */}
      {selectedDay && (
        <DayDetailModal
          settlement={selectedDay}
          onClose={() => setSelectedDay(null)}
        />
      )}
    </div>
  );
};

export default PaymentCalendar;


