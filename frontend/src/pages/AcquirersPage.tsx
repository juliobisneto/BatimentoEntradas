import React, { useState, useEffect } from 'react';
import { toast } from 'react-toastify';
import {
  FaBuilding,
  FaPlus,
  FaArrowLeft,
  FaCog,
  FaCreditCard,
  FaFileUpload,
  FaSave,
  FaTrash,
  FaEdit,
} from 'react-icons/fa';
import { acquirersAPI } from '../services/api';
import type { Acquirer, AcquirerPaymentMethod, ParserConfig } from '../types/acquirer';

const DEFAULT_PARSER_CONFIG: ParserConfig = {
  root_element: 'SummaryReport',
  repeating_element: 'Transaction',
  field_mappings: {
    settlement_date: 'data_prevista_liberacao',
    transaction_date: 'data_transacao',
    payment_type: 'forma_pagamento',
    net_amount: 'valor_liquido',
    gross_amount: 'valor_bruto',
    fee_amount: 'valor_taxa',
    reference: 'codigo_refencia',
    status: 'status',
    acquirer_transaction_id: 'codigo_transacao',
  },
  date_format: '%d/%m/%Y %H:%M',
  decimal_separator: ',',
  encoding: 'ISO-8859-1',
};

/** Parse JSON, allowing trailing commas (e.g. "key": "value", }) */
function parseParserConfigJson(raw: string): ParserConfig {
  let s = raw.trim();
  if (!s) return {} as ParserConfig;
  try {
    return JSON.parse(s) as ParserConfig;
  } catch {
    s = s.replace(/,(\s*[}\]])/g, '$1');
    return JSON.parse(s) as ParserConfig;
  }
}

const AcquirersPage: React.FC = () => {
  const [acquirers, setAcquirers] = useState<Acquirer[]>([]);
  const [loading, setLoading] = useState(true);
  const [selectedId, setSelectedId] = useState<number | null>(null);
  const [acquirer, setAcquirer] = useState<Acquirer | null>(null);
  const [paymentMethods, setPaymentMethods] = useState<AcquirerPaymentMethod[]>([]);
  const [imports, setImports] = useState<any[]>([]);
  const [form, setForm] = useState({ name: '', code: '', file_format: 'xml_generic', is_active: true });
  const [parserConfigJson, setParserConfigJson] = useState('');
  const [pmForm, setPmForm] = useState({ name: '', code: '', discount_rate: 0, settlement_days: 0, anticipation_rate: 0 });
  const [editingPmId, setEditingPmId] = useState<number | null>(null);
  const [importFile, setImportFile] = useState<File | null>(null);
  const [importing, setImporting] = useState(false);
  const [saving, setSaving] = useState(false);

  const loadAcquirers = async () => {
    try {
      setLoading(true);
      const data = await acquirersAPI.getAll();
      setAcquirers(data);
    } catch (e: any) {
      toast.error(e.response?.data?.detail || 'Error loading acquirers');
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    loadAcquirers();
  }, []);

  useEffect(() => {
    if (selectedId == null || selectedId === 0) {
      if (selectedId === null) {
        setAcquirer(null);
        setPaymentMethods([]);
        setImports([]);
      }
      return;
    }
    (async () => {
      try {
        const a = await acquirersAPI.getById(selectedId);
        setAcquirer(a);
        setForm({ name: a.name, code: a.code, file_format: a.file_format || 'xml_generic', is_active: a.is_active });
        setParserConfigJson(a.parser_config ? JSON.stringify(a.parser_config, null, 2) : JSON.stringify(DEFAULT_PARSER_CONFIG, null, 2));
        const pms = await acquirersAPI.getPaymentMethods(selectedId);
        setPaymentMethods(pms);
        const imps = await acquirersAPI.listImports(selectedId);
        setImports(imps);
      } catch (e: any) {
        toast.error(e.response?.data?.detail || 'Error loading acquirer');
        setSelectedId(null);
      }
    })();
  }, [selectedId]);

  const handleSaveAcquirer = async () => {
    if (!selectedId || !acquirer) return;
    setSaving(true);
    try {
      let parserConfig: ParserConfig | undefined;
      try {
        parserConfig = parseParserConfigJson(parserConfigJson);
      } catch {
        toast.error('Invalid parser JSON');
        setSaving(false);
        return;
      }
      await acquirersAPI.update(selectedId, { ...form, parser_config: parserConfig });
      toast.success('Acquirer updated');
      const a = await acquirersAPI.getById(selectedId);
      setAcquirer(a);
      loadAcquirers();
    } catch (e: any) {
      toast.error(e.response?.data?.detail || 'Error saving');
    } finally {
      setSaving(false);
    }
  };

  const handleCreateAcquirer = async () => {
    if (!form.name.trim() || !form.code.trim()) {
      toast.error('Name and code are required');
      return;
    }
    setSaving(true);
    try {
      let parserConfig: ParserConfig | undefined;
      try {
        parserConfig = parseParserConfigJson(parserConfigJson || '{}');
      } catch {
        parserConfig = DEFAULT_PARSER_CONFIG;
      }
      const created = await acquirersAPI.create({
        name: form.name.trim(),
        code: form.code.trim().toUpperCase(),
        file_format: form.file_format,
        is_active: form.is_active,
        parser_config: Object.keys(parserConfig).length ? parserConfig : undefined,
      });
      toast.success('Acquirer created');
      setAcquirers((prev) => [...prev, created]);
      setSelectedId(created.id);
      setAcquirer(created);
    } catch (e: any) {
      toast.error(e.response?.data?.detail || 'Error creating');
    } finally {
      setSaving(false);
    }
  };

  const handleDeleteAcquirer = async (id: number) => {
    if (!window.confirm('Delete this acquirer? This action cannot be undone.')) return;
    try {
      await acquirersAPI.delete(id);
      toast.success('Acquirer deleted');
      if (selectedId === id) setSelectedId(null);
      loadAcquirers();
    } catch (e: any) {
      toast.error(e.response?.data?.detail || 'Error deleting');
    }
  };

  const handleSavePm = async () => {
    if (!selectedId) return;
    if (!pmForm.name.trim() || !pmForm.code.trim()) {
      toast.error('Payment method name and code are required');
      return;
    }
    try {
      if (editingPmId) {
        await acquirersAPI.updatePaymentMethod(selectedId, editingPmId, pmForm);
        toast.success('Payment method updated');
        setEditingPmId(null);
      } else {
        await acquirersAPI.createPaymentMethod(selectedId, pmForm);
        toast.success('Payment method created');
      }
      setPmForm({ name: '', code: '', discount_rate: 0, settlement_days: 0, anticipation_rate: 0 });
      const pms = await acquirersAPI.getPaymentMethods(selectedId);
      setPaymentMethods(pms);
    } catch (e: any) {
      toast.error(e.response?.data?.detail || 'Error saving payment method');
    }
  };

  const handleDeletePm = async (pmId: number) => {
    if (!selectedId || !window.confirm('Delete this payment method?')) return;
    try {
      await acquirersAPI.deletePaymentMethod(selectedId, pmId);
      toast.success('Deleted');
      setPaymentMethods((prev) => prev.filter((p) => p.id !== pmId));
      if (editingPmId === pmId) setEditingPmId(null);
    } catch (e: any) {
      toast.error(e.response?.data?.detail || 'Error deleting');
    }
  };

  const handleImport = async () => {
    if (!selectedId || !importFile) {
      toast.error('Please select a file');
      return;
    }
    setImporting(true);
    try {
      const result = await acquirersAPI.importFile(selectedId, importFile);
      if (result.success) {
        toast.success(result.message);
        setImportFile(null);
        const imps = await acquirersAPI.listImports(selectedId);
        setImports(imps);
      } else {
        toast.error(result.message);
        if (result.errors?.length) result.errors.forEach((e: string) => toast.error(e));
      }
    } catch (e: any) {
      toast.error(e.response?.data?.detail || 'Import error');
    } finally {
      setImporting(false);
    }
  };

  return (
    <div className="space-y-8">
      <h1 className="text-3xl font-bold text-gray-800">Acquirers</h1>

      {selectedId == null ? (
        <>
          <div className="flex justify-between items-center">
            <p className="text-gray-600">Register acquirers and configure the file parser for reconciliation.</p>
            <button
              type="button"
              onClick={() => {
                setSelectedId(0);
                setAcquirer(null);
                setForm({ name: '', code: '', file_format: 'xml_generic', is_active: true });
                setParserConfigJson(JSON.stringify(DEFAULT_PARSER_CONFIG, null, 2));
                setPaymentMethods([]);
                setImports([]);
              }}
              className="px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 flex items-center gap-2"
            >
              <FaPlus /> New acquirer
            </button>
          </div>
          {loading ? (
            <div className="bg-white rounded-lg shadow p-8 text-center text-gray-500">Loading...</div>
          ) : (
            <div className="grid gap-4 md:grid-cols-2 lg:grid-cols-3">
              {acquirers.map((a) => (
                <div
                  key={a.id}
                  className="bg-white rounded-lg shadow-md p-6 border border-gray-200 hover:border-blue-400 cursor-pointer transition-colors"
                  onClick={() => setSelectedId(a.id)}
                >
                  <div className="flex items-center gap-3 mb-2">
                    <FaBuilding className="text-blue-600 text-2xl" />
                    <div>
                      <h2 className="text-xl font-semibold text-gray-800">{a.name}</h2>
                      <p className="text-sm text-gray-500">{a.code}</p>
                    </div>
                  </div>
                  <p className="text-sm text-gray-600">Format: {a.file_format}</p>
                  {!a.is_active && <span className="text-xs text-red-600">Inactive</span>}
                </div>
              ))}
            </div>
          )}
        </>
      ) : (
        <div className="space-y-6">
          <button
            type="button"
            onClick={() => {
              setSelectedId(null);
              setEditingPmId(null);
            }}
            className="text-blue-600 hover:underline flex items-center gap-2"
          >
            <FaArrowLeft /> Back to list
          </button>

          {/* Form: name, code, format (new or edit) */}
          <div className="bg-white rounded-lg shadow-md p-6">
            <h2 className="text-xl font-bold text-gray-800 mb-4 flex items-center gap-2">
              <FaBuilding /> {selectedId === 0 ? 'New acquirer' : 'Acquirer details'}
            </h2>
            <div className="grid gap-4 md:grid-cols-2">
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">Name</label>
                <input
                  type="text"
                  value={form.name}
                  onChange={(e) => setForm((f) => ({ ...f, name: e.target.value }))}
                  className="w-full border border-gray-300 rounded-lg px-3 py-2"
                  placeholder="Ex.: PagBank"
                />
              </div>
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">Code</label>
                <input
                  type="text"
                  value={form.code}
                  onChange={(e) => setForm((f) => ({ ...f, code: e.target.value.toUpperCase() }))}
                  className="w-full border border-gray-300 rounded-lg px-3 py-2"
                  placeholder="PAGBANK"
                  disabled={!!acquirer}
                />
              </div>
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">File format</label>
                <select
                  value={form.file_format}
                  onChange={(e) => setForm((f) => ({ ...f, file_format: e.target.value }))}
                  className="w-full border border-gray-300 rounded-lg px-3 py-2"
                >
                  <option value="xml_generic">Generic XML</option>
                  <option value="pagbank_xml">PagBank XML</option>
                  <option value="xlsx_generic">Generic XLSX (Excel)</option>
                  <option value="csv_generic">Generic CSV</option>
                </select>
              </div>
              <div className="flex items-center gap-2">
                <input
                  type="checkbox"
                  id="is_active"
                  checked={form.is_active}
                  onChange={(e) => setForm((f) => ({ ...f, is_active: e.target.checked }))}
                  className="rounded"
                />
                <label htmlFor="is_active" className="text-sm text-gray-700">Active</label>
              </div>
            </div>
            <div className="mt-4">
              {selectedId === 0 ? (
                <button type="button" onClick={handleCreateAcquirer} disabled={saving} className="px-4 py-2 bg-green-600 text-white rounded-lg hover:bg-green-700 disabled:opacity-50 flex items-center gap-2">
                  <FaSave /> Create acquirer
                </button>
              ) : (
                <div className="flex gap-2">
                  <button type="button" onClick={handleSaveAcquirer} disabled={saving} className="px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 disabled:opacity-50 flex items-center gap-2">
                    <FaSave /> Save changes
                  </button>
                  <button type="button" onClick={() => handleDeleteAcquirer(selectedId)} className="px-4 py-2 bg-red-600 text-white rounded-lg hover:bg-red-700 flex items-center gap-2">
                    <FaTrash /> Delete
                  </button>
                </div>
              )}
            </div>
          </div>

          {selectedId !== 0 && acquirer && (
            <>
              {/* Parser config */}
              <div className="bg-white rounded-lg shadow-md p-6">
                <h2 className="text-xl font-bold text-gray-800 mb-4 flex items-center gap-2">
                  <FaCog /> Parser configuration
                </h2>
                <p className="text-sm text-gray-600 mb-2">JSON with root_element, repeating_element, field_mappings, date_format, decimal_separator, encoding.</p>
                <textarea
                  value={parserConfigJson}
                  onChange={(e) => setParserConfigJson(e.target.value)}
                  rows={14}
                  className="w-full border border-gray-300 rounded-lg px-3 py-2 font-mono text-sm"
                  spellCheck={false}
                />
              </div>

              {/* Payment methods */}
              <div className="bg-white rounded-lg shadow-md p-6">
                <h2 className="text-xl font-bold text-gray-800 mb-4 flex items-center gap-2">
                  <FaCreditCard /> Acquirer payment methods
                </h2>
                <div className="grid gap-3 md:grid-cols-5 mb-4">
                  <input type="text" placeholder="Name (e.g. Pix)" value={pmForm.name} onChange={(e) => setPmForm((f) => ({ ...f, name: e.target.value }))} className="border rounded px-2 py-1.5" />
                  <input type="text" placeholder="Code (PIX)" value={pmForm.code} onChange={(e) => setPmForm((f) => ({ ...f, code: e.target.value }))} className="border rounded px-2 py-1.5" />
                  <input type="number" step="0.01" placeholder="Rate %" value={pmForm.discount_rate || ''} onChange={(e) => setPmForm((f) => ({ ...f, discount_rate: parseFloat(e.target.value) || 0 }))} className="border rounded px-2 py-1.5" />
                  <input type="number" placeholder="Settlement days" value={pmForm.settlement_days || ''} onChange={(e) => setPmForm((f) => ({ ...f, settlement_days: parseInt(e.target.value, 10) || 0 }))} className="border rounded px-2 py-1.5" />
                  <button type="button" onClick={handleSavePm} className="px-3 py-1.5 bg-blue-600 text-white rounded hover:bg-blue-700">
                    {editingPmId ? 'Update' : 'Add'}
                  </button>
                </div>
                <ul className="divide-y">
                  {paymentMethods.map((pm) => (
                    <li key={pm.id} className="py-2 flex items-center justify-between">
                      <span><strong>{pm.name}</strong> ({pm.code}) — Rate: {pm.discount_rate}%, Days: {pm.settlement_days}</span>
                      <div className="flex gap-2">
                        <button type="button" onClick={() => { setEditingPmId(pm.id); setPmForm({ name: pm.name, code: pm.code, discount_rate: pm.discount_rate, settlement_days: pm.settlement_days, anticipation_rate: pm.anticipation_rate }); }} className="text-blue-600 hover:underline"><FaEdit /></button>
                        <button type="button" onClick={() => handleDeletePm(pm.id)} className="text-red-600 hover:underline"><FaTrash /></button>
                      </div>
                    </li>
                  ))}
                </ul>
              </div>

              {/* Import file */}
              <div className="bg-white rounded-lg shadow-md p-6">
                <h2 className="text-xl font-bold text-gray-800 mb-4 flex items-center gap-2">
                  <FaFileUpload /> Import acquirer file
                </h2>
                <div className="flex flex-wrap items-end gap-4">
                  <div>
                    <label className="block text-sm font-medium text-gray-700 mb-1">File (XML/CSV)</label>
                    <input type="file" accept=".xml,.csv,.xlsx" onChange={(e) => setImportFile(e.target.files?.[0] || null)} className="border rounded px-2 py-1.5" />
                  </div>
                  <button type="button" onClick={handleImport} disabled={!importFile || importing} className="px-4 py-2 bg-green-600 text-white rounded-lg hover:bg-green-700 disabled:opacity-50">
                    {importing ? 'Importing...' : 'Import'}
                  </button>
                </div>
                {imports.length > 0 && (
                  <div className="mt-4">
                    <h3 className="font-semibold text-gray-700 mb-2">Recent imports</h3>
                    <ul className="text-sm text-gray-600 space-y-1">
                      {imports.slice(0, 10).map((imp) => (
                        <li key={imp.id}>{imp.file_name} — {imp.records_count} records — {new Date(imp.imported_at).toLocaleString()}</li>
                      ))}
                    </ul>
                  </div>
                )}
              </div>
            </>
          )}
        </div>
      )}
    </div>
  );
};

export default AcquirersPage;
