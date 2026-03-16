import React, { useState, useEffect } from 'react';
import { toast } from 'react-toastify';
import PaymentMethodForm from '../components/PaymentMethodForm';
import PaymentMethodList from '../components/PaymentMethodList';
import { paymentMethodsAPI } from '../services/api';
import { PaymentMethod, PaymentMethodFormData } from '../types/paymentMethod';

const PaymentMethodsPage: React.FC = () => {
  const [paymentMethods, setPaymentMethods] = useState<PaymentMethod[]>([]);
  const [loading, setLoading] = useState(true);
  const [editingMethod, setEditingMethod] = useState<PaymentMethod | null>(null);

  const loadPaymentMethods = async () => {
    try {
      setLoading(true);
      const data = await paymentMethodsAPI.getAll();
      setPaymentMethods(data);
    } catch (error) {
      toast.error('Error loading payment methods');
      console.error(error);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    loadPaymentMethods();
  }, []);

  const handleCreate = async (data: PaymentMethodFormData) => {
    try {
      await paymentMethodsAPI.create(data);
      toast.success('Payment method created successfully!');
      loadPaymentMethods();
    } catch (error: any) {
      toast.error(error.response?.data?.detail || 'Error creating payment method');
      throw error;
    }
  };

  const handleUpdate = async (data: PaymentMethodFormData) => {
    if (!editingMethod?.id) return;
    try {
      console.log('Updating payment method:', editingMethod.id, data);
      await paymentMethodsAPI.update(editingMethod.id, data);
      toast.success('Payment method updated successfully!');
      setEditingMethod(null);
      loadPaymentMethods();
    } catch (error: any) {
      console.error('Update error:', error);
      toast.error(error.response?.data?.detail || 'Error updating payment method');
      throw error;
    }
  };

  const handleDelete = async (id: number) => {
    try {
      await paymentMethodsAPI.delete(id);
      toast.success('Payment method deleted successfully!');
      loadPaymentMethods();
    } catch (error: any) {
      toast.error(error.response?.data?.detail || 'Error deleting payment method');
    }
  };

  const handleToggleActive = async (id: number, isActive: boolean) => {
    try {
      await paymentMethodsAPI.toggleActive(id, isActive);
      toast.success(`Payment method ${isActive ? 'activated' : 'deactivated'} successfully!`);
      loadPaymentMethods();
    } catch (error: any) {
      toast.error(error.response?.data?.detail || 'Error updating payment method');
    }
  };

  const handleEdit = (method: PaymentMethod) => {
    console.log('Editing method:', method);
    setEditingMethod(method);
    window.scrollTo({ top: 0, behavior: 'smooth' });
  };

  const handleCancelEdit = () => {
    console.log('Canceling edit - clearing form');
    setEditingMethod(null);
  };

  return (
    <>
      {editingMethod ? (
        <PaymentMethodForm
          onSubmit={handleUpdate}
          onCancel={handleCancelEdit}
          initialData={{
            payment_method: editingMethod.name,
            payment_terms: editingMethod.settlement_days,
            tax: editingMethod.discount_rate,
          }}
          isEdit
        />
      ) : (
        <PaymentMethodForm onSubmit={handleCreate} />
      )}

      <div className="mt-8">
        <h2 className="text-2xl font-bold mb-4 text-gray-800">Registered Payment Methods</h2>
        {loading ? (
          <div className="bg-white rounded-lg shadow-md p-8 text-center">
            <p className="text-gray-500">Loading...</p>
          </div>
        ) : (
          <PaymentMethodList
            paymentMethods={paymentMethods}
            onEdit={handleEdit}
            onDelete={handleDelete}
            onToggleActive={handleToggleActive}
          />
        )}
      </div>
    </>
  );
};

export default PaymentMethodsPage;


