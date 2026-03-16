import React, { useState } from 'react';
import { FaFileUpload, FaCheckCircle, FaExclamationTriangle, FaTimesCircle, FaRedo } from 'react-icons/fa';
import { toast } from 'react-toastify';
import api from '../services/api';

interface ImportResult {
  success: boolean;
  message: string;
  total_records_in_file: number;
  total_imported: number;
  total_duplicates: number;
  total_errors: number;
  file_import_id: string;
  file_name: string;
  file_location: string;
  errors: Array<{
    row: number;
    register: string | number;
    error: string;
    type: string;
  }>;
}

interface FileCheckResult {
  already_imported: boolean;
  file_location?: string;
  records_count?: number;
  first_import_date?: string;
  file_import_id?: string;
  message?: string;
}

const FileImport: React.FC = () => {
  const [selectedFile, setSelectedFile] = useState<File | null>(null);
  const [uploading, setUploading] = useState(false);
  const [importResult, setImportResult] = useState<ImportResult | null>(null);
  const [fileCheck, setFileCheck] = useState<FileCheckResult | null>(null);
  const [showConfirmDialog, setShowConfirmDialog] = useState(false);

  const handleFileSelect = async (event: React.ChangeEvent<HTMLInputElement>) => {
    const file = event.target.files?.[0];
    if (!file) return;

    // Validar extensão
    if (!file.name.endsWith('.csv')) {
      toast.error('Only CSV files are allowed');
      return;
    }

    setSelectedFile(file);
    setImportResult(null);
    setFileCheck(null);
    setShowConfirmDialog(false);

    // Verificar se arquivo já foi importado
    try {
      const response = await api.get(`/transactions/check-file/${file.name}`);
      const checkResult: FileCheckResult = response.data;
      
      if (checkResult.already_imported) {
        setFileCheck(checkResult);
        setShowConfirmDialog(true);
      }
    } catch (error) {
      console.error('Error checking file:', error);
    }
  };

  const handleDeleteAndReprocess = async () => {
    if (!selectedFile) return;

    try {
      setUploading(true);
      
      // Deletar registros existentes
      await api.delete(`/transactions/delete-by-file/${selectedFile.name}`);
      
      toast.success('Previous records deleted. Starting reprocessing...');
      setShowConfirmDialog(false);
      setFileCheck(null);
      
      // Aguardar um pouco e então importar
      setTimeout(() => {
        handleUpload();
      }, 500);
      
    } catch (error: any) {
      console.error('Error deleting records:', error);
      toast.error(error.response?.data?.detail || 'Error deleting previous records');
      setUploading(false);
    }
  };

  const handleUpload = async () => {
    if (!selectedFile) {
      toast.error('Please select a file');
      return;
    }

    // Se arquivo já foi importado e usuário não confirmou reprocessamento
    if (showConfirmDialog) {
      toast.warning('Please confirm if you want to reprocess the file');
      return;
    }

    setUploading(true);
    setImportResult(null);

    try {
      const formData = new FormData();
      formData.append('file', selectedFile);

      const response = await api.post<ImportResult>('/transactions/import', formData, {
        headers: {
          'Content-Type': 'multipart/form-data',
        },
      });

      setImportResult(response.data);
      
      if (response.data.success) {
        toast.success('File imported successfully!');
      } else {
        toast.warning('File imported with errors');
      }
      
    } catch (error: any) {
      console.error('Error importing file:', error);
      
      const errorDetail = error.response?.data?.detail;
      
      if (typeof errorDetail === 'string') {
        toast.error(errorDetail);
      } else if (errorDetail?.message) {
        toast.error(errorDetail.message);
      } else {
        toast.error('Error importing file');
      }
      
      // Se houver detalhes do erro, exibir como resultado
      if (errorDetail && typeof errorDetail === 'object') {
        setImportResult(errorDetail as ImportResult);
      }
    } finally {
      setUploading(false);
    }
  };

  const handleCancelReprocess = () => {
    setShowConfirmDialog(false);
    setSelectedFile(null);
    setFileCheck(null);
    // Reset file input
    const fileInput = document.getElementById('file-input') as HTMLInputElement;
    if (fileInput) fileInput.value = '';
  };

  const formatDateTime = (dateString?: string) => {
    if (!dateString) return 'N/A';
    return new Intl.DateTimeFormat('en-US', {
      year: 'numeric',
      month: '2-digit',
      day: '2-digit',
      hour: '2-digit',
      minute: '2-digit',
      second: '2-digit',
    }).format(new Date(dateString));
  };

  const getStatusIcon = (success: boolean) => {
    return success ? (
      <FaCheckCircle className="text-green-500 text-3xl" />
    ) : (
      <FaTimesCircle className="text-red-500 text-3xl" />
    );
  };

  return (
    <div className="max-w-4xl mx-auto py-6">
        <div className="flex items-center gap-3 mb-6">
          <FaFileUpload className="text-3xl text-blue-600" />
          <h1 className="text-2xl font-bold text-gray-800">File Import</h1>
        </div>

        {/* Upload Section */}
        <div className="bg-white shadow-md rounded-lg p-6 mb-6">
          <h2 className="text-lg font-semibold text-gray-800 mb-4">Select CSV File</h2>
          
          <div className="mb-4">
            <label className="block text-sm font-medium text-gray-700 mb-2">
              File (format: transactions_YYYYMMDD.csv)
            </label>
            <input
              id="file-input"
              type="file"
              accept=".csv"
              onChange={handleFileSelect}
              disabled={uploading}
              className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
            />
          </div>

          {selectedFile && !showConfirmDialog && (
            <div className="bg-blue-50 border border-blue-200 rounded-md p-4 mb-4">
              <p className="text-sm text-blue-800">
                <strong>Selected file:</strong> {selectedFile.name}
              </p>
              <p className="text-sm text-blue-600">
                Size: {(selectedFile.size / 1024).toFixed(2)} KB
              </p>
            </div>
          )}

          {!showConfirmDialog && (
            <button
              onClick={handleUpload}
              disabled={!selectedFile || uploading}
              className="w-full px-4 py-3 bg-blue-600 text-white rounded-md hover:bg-blue-700 transition-colors disabled:bg-gray-400 disabled:cursor-not-allowed flex items-center justify-center gap-2"
            >
              {uploading ? (
                <>
                  <div className="animate-spin rounded-full h-5 w-5 border-b-2 border-white"></div>
                  Processing...
                </>
              ) : (
                <>
                  <FaFileUpload /> Import File
                </>
              )}
            </button>
          )}
        </div>

        {/* Confirmation Dialog */}
        {showConfirmDialog && fileCheck && (
          <div className="bg-yellow-50 border-2 border-yellow-400 rounded-lg p-6 mb-6">
            <div className="flex items-start gap-3 mb-4">
              <FaExclamationTriangle className="text-yellow-600 text-3xl flex-shrink-0 mt-1" />
              <div>
                <h3 className="text-lg font-bold text-yellow-800 mb-2">
                  File Already Imported
                </h3>
                <p className="text-yellow-700 mb-2">
                  The file <strong>{selectedFile?.name}</strong> has already been imported.
                </p>
                {fileCheck.records_count && (
                  <p className="text-yellow-700 mb-2">
                    <strong>Records:</strong> {fileCheck.records_count} transactions
                  </p>
                )}
                {fileCheck.first_import_date && (
                  <p className="text-yellow-700 mb-2">
                    <strong>First import:</strong> {formatDateTime(fileCheck.first_import_date)}
                  </p>
                )}
                <p className="text-yellow-800 font-semibold mt-4">
                  Do you want to delete the existing records and reprocess the file?
                </p>
              </div>
            </div>

            <div className="flex gap-3">
              <button
                onClick={handleDeleteAndReprocess}
                disabled={uploading}
                className="flex-1 px-4 py-3 bg-red-600 text-white rounded-md hover:bg-red-700 transition-colors disabled:bg-gray-400 flex items-center justify-center gap-2"
              >
                {uploading ? (
                  <>
                    <div className="animate-spin rounded-full h-5 w-5 border-b-2 border-white"></div>
                    Reprocessing...
                  </>
                ) : (
                  <>
                    <FaRedo /> Yes, Delete and Reprocess
                  </>
                )}
              </button>
              <button
                onClick={handleCancelReprocess}
                disabled={uploading}
                className="flex-1 px-4 py-3 bg-gray-300 text-gray-700 rounded-md hover:bg-gray-400 transition-colors disabled:bg-gray-200 flex items-center justify-center gap-2"
              >
                <FaTimesCircle /> Cancel
              </button>
            </div>
          </div>
        )}

        {/* Import Result */}
        {importResult && (
          <div className={`rounded-lg shadow-md p-6 ${
            importResult.success ? 'bg-green-50 border-2 border-green-300' : 'bg-red-50 border-2 border-red-300'
          }`}>
            <div className="flex items-center gap-3 mb-4">
              {getStatusIcon(importResult.success)}
              <h2 className="text-xl font-bold text-gray-800">
                {importResult.success ? 'Import Successful!' : 'Import Failed'}
              </h2>
            </div>

            <div className="bg-white rounded-md p-4 mb-4">
              <h3 className="font-semibold text-gray-800 mb-3">Summary</h3>
              
              <div className="grid grid-cols-2 gap-4">
                <div>
                  <p className="text-sm text-gray-600">File Name</p>
                  <p className="font-semibold text-gray-800">{importResult.file_name}</p>
                </div>
                <div>
                  <p className="text-sm text-gray-600">Location</p>
                  <p className="font-semibold text-gray-800">{importResult.file_location}</p>
                </div>
                <div>
                  <p className="text-sm text-gray-600">Total Records</p>
                  <p className="font-semibold text-gray-800">{importResult.total_records_in_file}</p>
                </div>
                <div>
                  <p className="text-sm text-gray-600">Imported</p>
                  <p className="font-semibold text-green-600">{importResult.total_imported}</p>
                </div>
                <div>
                  <p className="text-sm text-gray-600">Duplicates</p>
                  <p className="font-semibold text-yellow-600">{importResult.total_duplicates}</p>
                </div>
                <div>
                  <p className="text-sm text-gray-600">Errors</p>
                  <p className="font-semibold text-red-600">{importResult.total_errors}</p>
                </div>
              </div>

              {importResult.message && (
                <div className="mt-4 p-3 bg-blue-50 rounded-md">
                  <p className="text-sm text-blue-800">{importResult.message}</p>
                </div>
              )}
            </div>

            {/* Errors Details */}
            {importResult.errors && importResult.errors.length > 0 && (
              <div className="bg-white rounded-md p-4">
                <h3 className="font-semibold text-gray-800 mb-3 flex items-center gap-2">
                  <FaExclamationTriangle className="text-yellow-600" />
                  Errors and Warnings ({importResult.errors.length})
                </h3>
                
                <div className="max-h-96 overflow-y-auto">
                  <table className="min-w-full divide-y divide-gray-200">
                    <thead className="bg-gray-50 sticky top-0">
                      <tr>
                        <th className="px-4 py-2 text-left text-xs font-medium text-gray-500 uppercase">Row</th>
                        <th className="px-4 py-2 text-left text-xs font-medium text-gray-500 uppercase">Register</th>
                        <th className="px-4 py-2 text-left text-xs font-medium text-gray-500 uppercase">Type</th>
                        <th className="px-4 py-2 text-left text-xs font-medium text-gray-500 uppercase">Error</th>
                      </tr>
                    </thead>
                    <tbody className="bg-white divide-y divide-gray-200">
                      {importResult.errors.map((error, index) => (
                        <tr key={index} className={error.type === 'duplicate' ? 'bg-yellow-50' : 'bg-red-50'}>
                          <td className="px-4 py-2 text-sm text-gray-900">{error.row}</td>
                          <td className="px-4 py-2 text-sm text-gray-900">{error.register}</td>
                          <td className="px-4 py-2 text-sm">
                            <span className={`px-2 py-1 rounded-full text-xs font-semibold ${
                              error.type === 'duplicate' 
                                ? 'bg-yellow-200 text-yellow-800' 
                                : 'bg-red-200 text-red-800'
                            }`}>
                              {error.type === 'duplicate' ? 'Duplicate' : 'Error'}
                            </span>
                          </td>
                          <td className="px-4 py-2 text-sm text-gray-700">{error.error}</td>
                        </tr>
                      ))}
                    </tbody>
                  </table>
                </div>
              </div>
            )}

            {/* Success message with next steps */}
            {importResult.success && importResult.total_imported > 0 && (
              <div className="bg-white rounded-md p-4 mt-4">
                <h3 className="font-semibold text-green-700 mb-2">✅ Next Steps</h3>
                <ul className="list-disc list-inside text-sm text-gray-700 space-y-1">
                  <li>View imported data in the Dashboard</li>
                  <li>Check payment schedule in the Payment Calendar</li>
                  <li>The file has been moved to old_files/ directory</li>
                </ul>
              </div>
            )}
          </div>
        )}

        {/* Information Box */}
        <div className="bg-blue-50 border border-blue-200 rounded-lg p-6 mt-6">
          <h3 className="font-semibold text-blue-800 mb-3">📋 File Requirements</h3>
          <ul className="text-sm text-blue-700 space-y-2">
            <li><strong>Format:</strong> CSV file</li>
            <li><strong>Filename:</strong> transactions_YYYYMMDD.csv (e.g., transactions_20250115.csv)</li>
            <li><strong>Required fields (in order):</strong></li>
            <li className="ml-4">
              #register, order_timestamp, payment_method_id, event_sponsor, venue, event, 
              #of_items_in_order, total_order_value, type_transaction
            </li>
            <li><strong>Last line:</strong> Must contain the total number of records in #register field</li>
          </ul>
        </div>
    </div>
  );
};

export default FileImport;
