import React from 'react';
import { DailySettlement } from '../types/calendar';
import { FaTimes, FaCreditCard, FaCalendarAlt, FaMoneyBillWave, FaReceipt } from 'react-icons/fa';

interface DayDetailModalProps {
  settlement: DailySettlement;
  onClose: () => void;
}

const DayDetailModal: React.FC<DayDetailModalProps> = ({ settlement, onClose }) => {
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
      month: 'long',
      year: 'numeric',
      weekday: 'long'
    }).format(date);
  };

  const formatDateTime = (timestamp: string) => {
    const date = new Date(timestamp);
    return new Intl.DateTimeFormat('en-US', {
      day: '2-digit',
      month: '2-digit',
      year: 'numeric',
      hour: '2-digit',
      minute: '2-digit'
    }).format(date);
  };

  const getStatusBadge = () => {
    if (settlement.status === 'settled') {
      return (
          <span className="inline-flex items-center px-3 py-1 rounded-full text-sm font-medium bg-green-100 text-green-800">
          Settled
        </span>
      );
    }
    return (
      <span className="inline-flex items-center px-3 py-1 rounded-full text-sm font-medium bg-orange-100 text-orange-800">
        Pending
      </span>
    );
  };

  return (
    <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50 p-4">
      <div className="bg-white rounded-lg shadow-xl max-w-6xl w-full max-h-[90vh] overflow-hidden">
        {/* Header */}
        <div className="bg-gradient-to-r from-blue-600 to-blue-700 text-white p-6 flex justify-between items-start">
          <div>
            <div className="flex items-center gap-3 mb-2">
              <FaCalendarAlt className="text-2xl" />
              <h2 className="text-2xl font-bold">Day Details</h2>
            </div>
            <p className="text-blue-100 text-lg">{formatDate(settlement.date)}</p>
          </div>
          <button
            onClick={onClose}
            className="text-white hover:bg-white hover:bg-opacity-20 rounded-full p-2 transition-colors"
          >
            <FaTimes className="text-xl" />
          </button>
        </div>

        {/* Summary Cards */}
        <div className="p-6 bg-gray-50 border-b border-gray-200">
          <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
            <div className="bg-white rounded-lg p-4 shadow-sm">
              <div className="flex items-center gap-2 text-gray-600 mb-1">
                <FaMoneyBillWave />
                <div className="text-sm">Total Amount</div>
              </div>
              <div className="text-xl font-bold text-gray-800">
                {formatCurrency(settlement.total_amount)}
              </div>
            </div>
            
            <div className="bg-white rounded-lg p-4 shadow-sm">
              <div className="flex items-center gap-2 text-gray-600 mb-1">
                <FaReceipt />
                <div className="text-sm">Net Amount</div>
              </div>
              <div className="text-xl font-bold text-green-600">
                {formatCurrency(settlement.total_net_amount)}
              </div>
            </div>
            
            <div className="bg-white rounded-lg p-4 shadow-sm">
              <div className="flex items-center gap-2 text-gray-600 mb-1">
                <FaCreditCard />
                <div className="text-sm">Transactions</div>
              </div>
              <div className="text-xl font-bold text-gray-800">
                {settlement.transaction_count}
              </div>
            </div>
            
            <div className="bg-white rounded-lg p-4 shadow-sm">
              <div className="flex items-center gap-2 text-gray-600 mb-1">
                <FaCalendarAlt />
                <div className="text-sm">Status</div>
              </div>
              <div className="mt-1">
                {getStatusBadge()}
              </div>
            </div>
          </div>
        </div>

        {/* Payment Methods Details */}
        <div className="p-6 overflow-y-auto max-h-[calc(90vh-340px)]">
          <h3 className="text-lg font-bold text-gray-800 mb-4">Breakdown by Payment Method</h3>
          
          <div className="space-y-6">
            {settlement.by_payment_method.map((method) => (
              <div key={method.method_id} className="border border-gray-200 rounded-lg overflow-hidden">
                {/* Method Header */}
                <div className="bg-gray-100 p-4 border-b border-gray-200">
                  <div className="flex justify-between items-center">
                    <div>
                      <h4 className="text-lg font-semibold text-gray-800">{method.method_name}</h4>
                      <p className="text-sm text-gray-600">{method.count} transaction{method.count !== 1 ? 's' : ''}</p>
                    </div>
                    <div className="text-right">
                      <div className="text-sm text-gray-600">Net</div>
                      <div className="text-xl font-bold text-green-600">{formatCurrency(method.net)}</div>
                      <div className="text-xs text-gray-500">Total: {formatCurrency(method.total)}</div>
                    </div>
                  </div>
                </div>

                {/* Transactions Table */}
                <div className="overflow-x-auto">
                  <table className="w-full">
                    <thead className="bg-gray-50 border-b border-gray-200">
                      <tr>
                        <th className="px-4 py-3 text-left text-xs font-medium text-gray-600 uppercase tracking-wider">
                          #Reg
                        </th>
                        <th className="px-4 py-3 text-left text-xs font-medium text-gray-600 uppercase tracking-wider">
                          Date/Time
                        </th>
                        <th className="px-4 py-3 text-left text-xs font-medium text-gray-600 uppercase tracking-wider">
                          Event
                        </th>
                        <th className="px-4 py-3 text-left text-xs font-medium text-gray-600 uppercase tracking-wider">
                          Sponsor
                        </th>
                        <th className="px-4 py-3 text-left text-xs font-medium text-gray-600 uppercase tracking-wider">
                          Venue
                        </th>
                        <th className="px-4 py-3 text-right text-xs font-medium text-gray-600 uppercase tracking-wider">
                          Total Value
                        </th>
                        <th className="px-4 py-3 text-right text-xs font-medium text-gray-600 uppercase tracking-wider">
                          Discount
                        </th>
                        <th className="px-4 py-3 text-right text-xs font-medium text-gray-600 uppercase tracking-wider">
                          Net
                        </th>
                        <th className="px-4 py-3 text-center text-xs font-medium text-gray-600 uppercase tracking-wider">
                          Type
                        </th>
                      </tr>
                    </thead>
                    <tbody className="bg-white divide-y divide-gray-200">
                      {method.transactions.map((transaction) => (
                        <tr key={transaction.id} className="hover:bg-gray-50">
                          <td className="px-4 py-3 whitespace-nowrap text-sm text-gray-900">
                            {transaction.register}
                          </td>
                          <td className="px-4 py-3 whitespace-nowrap text-sm text-gray-600">
                            {formatDateTime(transaction.order_timestamp)}
                          </td>
                          <td className="px-4 py-3 text-sm text-gray-900 max-w-xs truncate">
                            {transaction.event}
                          </td>
                          <td className="px-4 py-3 text-sm text-gray-600">
                            {transaction.event_sponsor}
                          </td>
                          <td className="px-4 py-3 text-sm text-gray-600">
                            {transaction.venue}
                          </td>
                          <td className="px-4 py-3 whitespace-nowrap text-sm text-right text-gray-900">
                            {formatCurrency(transaction.total_order_value)}
                          </td>
                          <td className="px-4 py-3 whitespace-nowrap text-sm text-right text-red-600">
                            -{formatCurrency(transaction.discount_amount)}
                          </td>
                          <td className="px-4 py-3 whitespace-nowrap text-sm text-right font-semibold text-green-600">
                            {formatCurrency(transaction.net_amount)}
                          </td>
                          <td className="px-4 py-3 whitespace-nowrap text-center">
                            {transaction.transaction_type === 'venda' ? (
                              <span className="inline-flex px-2 py-1 text-xs font-semibold rounded-full bg-blue-100 text-blue-800">
                                Sale
                              </span>
                            ) : (
                              <span className="inline-flex px-2 py-1 text-xs font-semibold rounded-full bg-red-100 text-red-800">
                                Refund
                              </span>
                            )}
                          </td>
                        </tr>
                      ))}
                    </tbody>
                  </table>
                </div>
              </div>
            ))}
          </div>
        </div>

        {/* Footer */}
        <div className="bg-gray-50 px-6 py-4 border-t border-gray-200">
          <button
            onClick={onClose}
            className="w-full md:w-auto px-6 py-2 bg-blue-600 text-white rounded-md hover:bg-blue-700 transition-colors font-medium"
          >
            Close
          </button>
        </div>
      </div>
    </div>
  );
};

export default DayDetailModal;

