import React, { useState } from 'react';
import { FaSave, FaTimes } from 'react-icons/fa';
import { PaymentMethodFormData } from '../types/paymentMethod';

interface PaymentMethodFormProps {
  onSubmit: (data: PaymentMethodFormData) => Promise<void>;
  onCancel?: () => void;
  initialData?: PaymentMethodFormData;
  isEdit?: boolean;
}

const PaymentMethodForm: React.FC<PaymentMethodFormProps> = ({
  onSubmit,
  onCancel,
  initialData,
  isEdit = false,
}) => {
  const [formData, setFormData] = useState<PaymentMethodFormData>(
    initialData || {
      payment_method: '',
      payment_terms: 0,
      tax: 0,
    }
  );
  const [loading, setLoading] = useState(false);
  const [errors, setErrors] = useState<{ [key: string]: string }>({});

  // Update form data when initialData changes or when mode changes
  React.useEffect(() => {
    if (initialData && isEdit) {
      console.log('Initial data changed:', initialData);
      setFormData(initialData);
    } else if (!isEdit) {
      // Clear form when not in edit mode
      console.log('Clearing form - not in edit mode');
      setFormData({
        payment_method: '',
        payment_terms: 0,
        tax: 0,
      });
      setErrors({});
    }
  }, [initialData, isEdit]);

  const validateForm = (): boolean => {
    const newErrors: { [key: string]: string } = {};

    if (!formData.payment_method.trim()) {
      newErrors.payment_method = 'Payment method is required';
    }

    if (formData.payment_terms < 0) {
      newErrors.payment_terms = 'Payment terms must be 0 or greater';
    }

    if (formData.tax < 0 || formData.tax > 100) {
      newErrors.tax = 'Tax must be between 0 and 100';
    }

    setErrors(newErrors);
    return Object.keys(newErrors).length === 0;
  };

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();

    console.log('Form submitted:', { isEdit, formData });

    if (!validateForm()) {
      console.log('Form validation failed');
      return;
    }

    setLoading(true);
    try {
      console.log('Calling onSubmit with:', formData);
      await onSubmit(formData);
      console.log('onSubmit completed successfully');
      if (!isEdit) {
        setFormData({ payment_method: '', payment_terms: 0, tax: 0 });
      }
    } catch (error) {
      console.error('Error submitting form:', error);
    } finally {
      setLoading(false);
    }
  };

  const handleChange = (field: keyof PaymentMethodFormData, value: string | number) => {
    setFormData((prev) => ({ ...prev, [field]: value }));
    // Clear field error when user starts typing
    if (errors[field]) {
      setErrors((prev) => ({ ...prev, [field]: '' }));
    }
  };

  return (
    <form onSubmit={handleSubmit} className="bg-white rounded-lg shadow-md p-6 mb-6">
      <h2 className="text-2xl font-bold mb-6 text-gray-800">
        {isEdit ? 'Edit Payment Method' : 'New Payment Method'}
      </h2>

      {/* Payment Method */}
      <div className="mb-4">
        <label htmlFor="payment_method" className="block text-gray-700 font-semibold mb-2">
          Payment Method <span className="text-red-500">*</span>
        </label>
        <input
          type="text"
          id="payment_method"
          value={formData.payment_method}
          onChange={(e) => handleChange('payment_method', e.target.value)}
          placeholder="e.g., Credit Card, Debit, PIX, Cash"
          className={`w-full px-4 py-2 border rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500 ${
            errors.payment_method ? 'border-red-500' : 'border-gray-300'
          }`}
        />
        {errors.payment_method && (
          <p className="text-red-500 text-sm mt-1">{errors.payment_method}</p>
        )}
      </div>

      {/* Payment Terms */}
      <div className="mb-4">
        <label htmlFor="payment_terms" className="block text-gray-700 font-semibold mb-2">
          Payment Terms (days) <span className="text-red-500">*</span>
        </label>
        <input
          type="number"
          id="payment_terms"
          value={formData.payment_terms}
          onChange={(e) => handleChange('payment_terms', parseInt(e.target.value) || 0)}
          placeholder="Number of days for settlement"
          min="0"
          className={`w-full px-4 py-2 border rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500 ${
            errors.payment_terms ? 'border-red-500' : 'border-gray-300'
          }`}
        />
        {errors.payment_terms && (
          <p className="text-red-500 text-sm mt-1">{errors.payment_terms}</p>
        )}
        <p className="text-gray-500 text-sm mt-1">
          Number of days until payment is settled
        </p>
      </div>

      {/* Tax */}
      <div className="mb-6">
        <label htmlFor="tax" className="block text-gray-700 font-semibold mb-2">
          Tax (%) <span className="text-red-500">*</span>
        </label>
        <input
          type="number"
          id="tax"
          value={formData.tax}
          onChange={(e) => handleChange('tax', parseFloat(e.target.value) || 0)}
          placeholder="Discount rate percentage"
          min="0"
          max="100"
          step="0.01"
          className={`w-full px-4 py-2 border rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500 ${
            errors.tax ? 'border-red-500' : 'border-gray-300'
          }`}
        />
        {errors.tax && <p className="text-red-500 text-sm mt-1">{errors.tax}</p>}
        <p className="text-gray-500 text-sm mt-1">
          Discount rate applied to transactions (0-100%)
        </p>
      </div>

      {/* Buttons */}
      <div className="flex gap-3">
        <button
          type="submit"
          disabled={loading}
          className="flex items-center gap-2 bg-blue-600 text-white px-6 py-2 rounded-lg hover:bg-blue-700 disabled:bg-gray-400 disabled:cursor-not-allowed transition-colors"
        >
          <FaSave />
          {loading ? 'Saving...' : isEdit ? 'Update' : 'Create'}
        </button>
        
        {onCancel && (
          <button
            type="button"
            onClick={onCancel}
            className="flex items-center gap-2 bg-gray-300 text-gray-700 px-6 py-2 rounded-lg hover:bg-gray-400 transition-colors"
          >
            <FaTimes />
            Cancel
          </button>
        )}
      </div>
    </form>
  );
};

export default PaymentMethodForm;


