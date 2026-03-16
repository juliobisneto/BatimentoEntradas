import React from 'react';
import { FaFilter, FaRedo } from 'react-icons/fa';
import { DashboardFilters as Filters, FilterOptions } from '../types/dashboard';

interface DashboardFiltersProps {
  filters: Filters;
  filterOptions: FilterOptions;
  onFilterChange: (filters: Filters) => void;
  onReset: () => void;
}

const DashboardFilters: React.FC<DashboardFiltersProps> = ({
  filters,
  filterOptions,
  onFilterChange,
  onReset,
}) => {
  const handleChange = (field: keyof Filters, value: string) => {
    onFilterChange({
      ...filters,
      [field]: value || undefined,
    });
  };

  return (
    <div className="bg-white rounded-lg shadow-md p-6 mb-6">
      <div className="flex items-center justify-between mb-4">
        <h2 className="text-xl font-bold text-gray-800 flex items-center gap-2">
          <FaFilter /> Filters
        </h2>
        <button
          onClick={onReset}
          className="flex items-center gap-2 text-blue-600 hover:text-blue-800 text-sm"
        >
          <FaRedo /> Reset
        </button>
      </div>

      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-5 gap-4">
        {/* Date Range */}
        <div>
          <label className="block text-sm font-medium text-gray-700 mb-1">
            Start Date
          </label>
          <input
            type="date"
            value={filters.start_date || ''}
            onChange={(e) => handleChange('start_date', e.target.value)}
            className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500"
          />
        </div>

        <div>
          <label className="block text-sm font-medium text-gray-700 mb-1">
            End Date
          </label>
          <input
            type="date"
            value={filters.end_date || ''}
            onChange={(e) => handleChange('end_date', e.target.value)}
            className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500"
          />
        </div>

        {/* Sponsor */}
        <div>
          <label className="block text-sm font-medium text-gray-700 mb-1">
            Sponsor
          </label>
          <select
            value={filters.event_sponsor || ''}
            onChange={(e) => handleChange('event_sponsor', e.target.value)}
            className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500"
          >
            <option value="">All Sponsors</option>
            {filterOptions.sponsors.map((sponsor) => (
              <option key={sponsor} value={sponsor}>
                {sponsor}
              </option>
            ))}
          </select>
        </div>

        {/* Venue */}
        <div>
          <label className="block text-sm font-medium text-gray-700 mb-1">
            Venue
          </label>
          <select
            value={filters.venue || ''}
            onChange={(e) => handleChange('venue', e.target.value)}
            className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500"
          >
            <option value="">All Venues</option>
            {filterOptions.venues.map((venue) => (
              <option key={venue} value={venue}>
                {venue}
              </option>
            ))}
          </select>
        </div>

        {/* Event */}
        <div>
          <label className="block text-sm font-medium text-gray-700 mb-1">
            Event
          </label>
          <select
            value={filters.event || ''}
            onChange={(e) => handleChange('event', e.target.value)}
            className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500"
          >
            <option value="">All Events</option>
            {filterOptions.events.map((event) => (
              <option key={event} value={event}>
                {event}
              </option>
            ))}
          </select>
        </div>
      </div>
    </div>
  );
};

export default DashboardFilters;




