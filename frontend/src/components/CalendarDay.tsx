import React from 'react';
import { DailySettlement } from '../types/calendar';

interface CalendarDayProps {
  settlement: DailySettlement | null;
  onSelect: (settlement: DailySettlement) => void;
}

const CalendarDay: React.FC<CalendarDayProps> = ({ settlement, onSelect }) => {
  if (!settlement) {
    return <div className="border border-gray-200 rounded-lg p-2 bg-gray-50 min-h-[100px]"></div>;
  }

  const formatCurrency = (value: number) => {
    return new Intl.NumberFormat('pt-BR', {
      style: 'currency',
      currency: 'BRL',
      minimumFractionDigits: 0,
      maximumFractionDigits: 0,
    }).format(value);
  };

  const getStatusColor = () => {
    if (settlement.status === 'settled') {
      return 'bg-green-50 border-green-300 hover:bg-green-100';
    }
    return 'bg-orange-50 border-orange-300 hover:bg-orange-100';
  };

  const getStatusBadge = () => {
    if (settlement.status === 'settled') {
      return (
        <span className="inline-block px-2 py-0.5 text-xs font-semibold rounded-full bg-green-200 text-green-800">
          Settled
        </span>
      );
    }
    return (
      <span className="inline-block px-2 py-0.5 text-xs font-semibold rounded-full bg-orange-200 text-orange-800">
        Pending
      </span>
    );
  };

  const formatDate = (dateStr: string) => {
    const date = new Date(dateStr + 'T00:00:00');
    return date.getDate();
  };

  const getDayOfWeek = (dateStr: string) => {
    const date = new Date(dateStr + 'T00:00:00');
    const days = ['Sun', 'Mon', 'Tue', 'Wed', 'Thu', 'Fri', 'Sat'];
    return days[date.getDay()];
  };

  const isWeekend = (dateStr: string) => {
    const date = new Date(dateStr + 'T00:00:00');
    const day = date.getDay();
    return day === 0 || day === 6;
  };

  return (
    <div
      onClick={() => onSelect(settlement)}
      className={`border rounded-lg p-2 cursor-pointer transition-all min-h-[100px] ${getStatusColor()} ${
        isWeekend(settlement.date) ? 'opacity-75' : ''
      }`}
    >
      <div className="flex justify-between items-start mb-1">
        <div>
          <div className="text-lg font-bold text-gray-800">{formatDate(settlement.date)}</div>
          <div className="text-xs text-gray-500">{getDayOfWeek(settlement.date)}</div>
        </div>
        {getStatusBadge()}
      </div>
      
      <div className="mt-2 space-y-1">
        <div className="text-sm font-semibold text-gray-700">
          {formatCurrency(settlement.total_net_amount)}
        </div>
        <div className="text-xs text-gray-600">
          {settlement.transaction_count} transaction{settlement.transaction_count !== 1 ? 's' : ''}
        </div>
        {settlement.by_payment_method.length > 0 && (
          <div className="text-xs text-gray-500 truncate">
            {settlement.by_payment_method.length} method{settlement.by_payment_method.length !== 1 ? 's' : ''}
          </div>
        )}
      </div>
    </div>
  );
};

export default CalendarDay;

