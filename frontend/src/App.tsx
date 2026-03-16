import React, { useState, useEffect } from 'react';
import { ToastContainer } from 'react-toastify';
import 'react-toastify/dist/ReactToastify.css';
import PaymentMethodsPage from './pages/PaymentMethodsPage';
import Dashboard from './pages/Dashboard';
import PaymentCalendar from './pages/PaymentCalendar';
import FileImport from './pages/FileImport';
import AcquirersPage from './pages/AcquirersPage';
import Login from './pages/Login';
import NewCSportLogo from './components/NewCSportLogo';
import { FaSignOutAlt, FaUser } from 'react-icons/fa';
import api from './services/api';

interface User {
  name: string;
  email: string;
}

function App() {
  const [currentPage, setCurrentPage] = useState<'dashboard' | 'payment-methods' | 'payment-calendar' | 'file-import' | 'acquirers'>('dashboard');
  const [isAuthenticated, setIsAuthenticated] = useState(false);
  const [loading, setLoading] = useState(true);
  const [currentUser, setCurrentUser] = useState<User | null>(null);

  useEffect(() => {
    // Check if user is already authenticated
    const token = localStorage.getItem('access_token');
    setIsAuthenticated(!!token);
    if (token) {
      loadCurrentUser();
    }
    setLoading(false);
  }, []);

  const loadCurrentUser = async () => {
    try {
      const response = await api.get('/auth/me');
      setCurrentUser(response.data);
    } catch (error) {
      console.error('Error loading user:', error);
    }
  };

  const handleLoginSuccess = (token: string) => {
    setIsAuthenticated(true);
    loadCurrentUser();
  };

  const handleLogout = () => {
    localStorage.removeItem('access_token');
    setIsAuthenticated(false);
    setCurrentUser(null);
    setCurrentPage('dashboard');
  };

  if (loading) {
    return (
      <div className="min-h-screen flex items-center justify-center">
        <div className="text-gray-500 text-lg">Loading...</div>
      </div>
    );
  }

  if (!isAuthenticated) {
    return (
      <>
        <ToastContainer position="top-right" autoClose={3000} />
        <Login onLoginSuccess={handleLoginSuccess} />
      </>
    );
  }

  return (
    <div className="min-h-screen bg-gray-100">
      <ToastContainer position="top-right" autoClose={3000} />
      
      {/* Header Bar */}
      <header className="bg-blue-600 text-white shadow-lg">
        <div className="container mx-auto px-4 py-4">
          <div className="flex justify-between items-center">
            <div className="flex items-center gap-4">
              <NewCSportLogo size="small" color="white" />
              <div className="border-l border-blue-400 h-12 mx-2"></div>
              <h1 className="text-2xl font-bold">Ticket Revenue Reconciliation System</h1>
            </div>
            <div className="flex items-center gap-4">
              {currentUser && (
                <div className="flex items-center gap-2 text-sm bg-blue-700 px-3 py-2 rounded">
                  <FaUser className="text-blue-200" />
                  <span className="font-semibold">{currentUser.name}</span>
                </div>
              )}
              <button
                onClick={handleLogout}
                className="px-4 py-2 text-white hover:bg-blue-700 rounded transition-colors flex items-center gap-2"
              >
                <FaSignOutAlt />
                Logout
              </button>
            </div>
          </div>
        </div>
      </header>

      {/* Navigation Menu */}
      <nav className="bg-white shadow-md">
        <div className="container mx-auto px-4">
          <div className="flex space-x-4">
            <button
              onClick={() => setCurrentPage('dashboard')}
              className={`px-4 py-4 font-medium border-b-2 transition-colors ${
                currentPage === 'dashboard'
                  ? 'border-blue-600 text-blue-600'
                  : 'border-transparent text-gray-600 hover:text-blue-600'
              }`}
            >
              Dashboard
            </button>
            <button
              onClick={() => setCurrentPage('payment-calendar')}
              className={`px-4 py-4 font-medium border-b-2 transition-colors ${
                currentPage === 'payment-calendar'
                  ? 'border-blue-600 text-blue-600'
                  : 'border-transparent text-gray-600 hover:text-blue-600'
              }`}
            >
              Payment Calendar
            </button>
            <button
              onClick={() => setCurrentPage('file-import')}
              className={`px-4 py-4 font-medium border-b-2 transition-colors ${
                currentPage === 'file-import'
                  ? 'border-blue-600 text-blue-600'
                  : 'border-transparent text-gray-600 hover:text-blue-600'
              }`}
            >
              File Import
            </button>
            <button
              onClick={() => setCurrentPage('payment-methods')}
              className={`px-4 py-4 font-medium border-b-2 transition-colors ${
                currentPage === 'payment-methods'
                  ? 'border-blue-600 text-blue-600'
                  : 'border-transparent text-gray-600 hover:text-blue-600'
              }`}
            >
              Payment Methods
            </button>
            <button
              onClick={() => setCurrentPage('acquirers')}
              className={`px-4 py-4 font-medium border-b-2 transition-colors ${
                currentPage === 'acquirers'
                  ? 'border-blue-600 text-blue-600'
                  : 'border-transparent text-gray-600 hover:text-blue-600'
              }`}
            >
              Acquirers
            </button>
          </div>
        </div>
      </nav>

      {/* Main Content */}
      <main className="container mx-auto px-4 py-8">
        {currentPage === 'dashboard' && <Dashboard />}
        {currentPage === 'payment-calendar' && <PaymentCalendar />}
        {currentPage === 'file-import' && <FileImport />}
        {currentPage === 'payment-methods' && <PaymentMethodsPage />}
        {currentPage === 'acquirers' && <AcquirersPage />}
      </main>

      {/* Footer */}
      <footer className="bg-gray-800 text-gray-300 mt-12">
        <div className="container mx-auto px-4 py-4 text-center">
          <p>&copy; 2025 Ticket Revenue Reconciliation System</p>
        </div>
      </footer>
    </div>
  );
}

export default App;


