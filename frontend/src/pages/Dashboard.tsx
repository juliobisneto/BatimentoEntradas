import React, { useState, useEffect } from 'react';
import { toast } from 'react-toastify';
import {
  FaShoppingCart,
  FaMoneyBillWave,
  FaUndo,
  FaChartLine,
  FaPercentage,
  FaBox,
} from 'react-icons/fa';
import DashboardFilters from '../components/DashboardFilters';
import StatCard from '../components/StatCard';
import TransactionsTable from '../components/TransactionsTable';
import { dashboardAPI } from '../services/api';
import {
  DashboardData,
  DashboardFilters as Filters,
  FilterOptions,
  PaymentMethodStats,
} from '../types/dashboard';

const Dashboard: React.FC = () => {
  const [data, setData] = useState<DashboardData | null>(null);
  const [paymentMethodStats, setPaymentMethodStats] = useState<PaymentMethodStats[]>([]);
  const [filterOptions, setFilterOptions] = useState<FilterOptions>({
    sponsors: [],
    venues: [],
    events: [],
  });
  const [filters, setFilters] = useState<Filters>({});
  const [loading, setLoading] = useState(true);

  // Load filter options
  useEffect(() => {
    loadFilterOptions();
  }, []);

  // Load data when filters change
  useEffect(() => {
    loadData();
  }, [filters]);

  const loadFilterOptions = async () => {
    try {
      const options = await dashboardAPI.getFilterOptions();
      setFilterOptions(options);
    } catch (error) {
      console.error('Error loading filter options:', error);
    }
  };

  const loadData = async () => {
    try {
      setLoading(true);
      
      // Prepare filters for API
      const apiFilters: any = {};
      
      if (filters.start_date) {
        apiFilters.start_date = `${filters.start_date}T00:00:00`;
      }
      if (filters.end_date) {
        apiFilters.end_date = `${filters.end_date}T23:59:59`;
      }
      if (filters.event_sponsor) {
        apiFilters.event_sponsor = filters.event_sponsor;
      }
      if (filters.venue) {
        apiFilters.venue = filters.venue;
      }
      if (filters.event) {
        apiFilters.event = filters.event;
      }

      const [summaryData, paymentStats] = await Promise.all([
        dashboardAPI.getSummary(apiFilters),
        dashboardAPI.getByPaymentMethod(apiFilters),
      ]);

      setData(summaryData);
      setPaymentMethodStats(paymentStats);
    } catch (error: any) {
      toast.error('Error loading dashboard data');
      console.error(error);
    } finally {
      setLoading(false);
    }
  };

  const handleFilterChange = (newFilters: Filters) => {
    setFilters(newFilters);
  };

  const handleResetFilters = () => {
    setFilters({});
  };

  const formatCurrency = (value: number) => {
    return new Intl.NumberFormat('pt-BR', {
      style: 'currency',
      currency: 'BRL',
    }).format(value);
  };

  if (loading && !data) {
    return (
      <div className="flex items-center justify-center h-64">
        <p className="text-gray-500 text-lg">Loading dashboard...</p>
      </div>
    );
  }

  return (
    <>
      <div className="mb-6">
        <h1 className="text-3xl font-bold text-gray-800">Dashboard</h1>
        <p className="text-gray-600 mt-1">Transaction overview and analytics</p>
      </div>

      {/* Filters */}
      <DashboardFilters
        filters={filters}
        filterOptions={filterOptions}
        onFilterChange={handleFilterChange}
        onReset={handleResetFilters}
      />

      {data && (
        <>
          {/* Statistics Cards */}
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6 mb-6">
            <StatCard
              title="Total Transactions"
              value={data.summary.total_transactions}
              subtitle={`${data.summary.total_sales_count} sales / ${data.summary.total_refunds_count} refunds`}
              icon={FaShoppingCart}
              bgColor="bg-blue-500"
              textColor="text-white"
            />

            <StatCard
              title="Total Sales"
              value={formatCurrency(data.summary.total_sales_value)}
              subtitle={`${data.summary.total_sales_count} transactions`}
              icon={FaMoneyBillWave}
              bgColor="bg-green-500"
              textColor="text-white"
            />

            <StatCard
              title="Total Refunds"
              value={formatCurrency(data.summary.total_refunds_value)}
              subtitle={`${data.summary.total_refunds_count} transactions`}
              icon={FaUndo}
              bgColor="bg-red-500"
              textColor="text-white"
            />

            <StatCard
              title="Net Revenue"
              value={formatCurrency(data.summary.net_revenue)}
              subtitle="Sales - Refunds"
              icon={FaChartLine}
              bgColor="bg-purple-500"
              textColor="text-white"
            />

            <StatCard
              title="Net After Tax"
              value={formatCurrency(data.summary.net_revenue_after_tax)}
              subtitle={`Tax: ${formatCurrency(data.summary.total_discount)}\nNet Tax: ${formatCurrency(data.summary.net_revenue - data.summary.net_revenue_after_tax)}`}
              icon={FaPercentage}
              bgColor="bg-indigo-500"
              textColor="text-white"
            />

            <StatCard
              title="Total Items Sold"
              value={data.summary.total_items}
              subtitle={`Avg: ${formatCurrency(data.summary.average_transaction_value)}`}
              icon={FaBox}
              bgColor="bg-orange-500"
              textColor="text-white"
            />
          </div>

          {/* Payment Methods Stats */}
          {paymentMethodStats.length > 0 && (
            <div className="bg-white rounded-lg shadow-md p-6 mb-6">
              <h2 className="text-xl font-bold text-gray-800 mb-4">By Payment Method</h2>
              <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
                {paymentMethodStats.map((stat) => (
                  <div
                    key={stat.payment_method}
                    className="border border-gray-200 rounded-lg p-4"
                  >
                    <h3 className="font-semibold text-gray-700 mb-2">
                      {stat.payment_method}
                    </h3>
                    <p className="text-2xl font-bold text-blue-600 mb-1">
                      {formatCurrency(stat.total_value)}
                    </p>
                    <p className="text-sm text-gray-500">{stat.count} transactions</p>
                    <p className="text-sm text-green-600 mt-1">
                      Net: {formatCurrency(stat.net_value)}
                    </p>
                  </div>
                ))}
              </div>
            </div>
          )}

          {/* Transactions Table */}
          <div>
            <h2 className="text-xl font-bold text-gray-800 mb-4">
              Transaction Details ({data.transactions.length})
            </h2>
            <TransactionsTable transactions={data.transactions} />
          </div>
        </>
      )}
    </>
  );
};

export default Dashboard;


