import React, { useState, useEffect } from 'react';
import { Link } from 'react-router-dom';
import {
  Users,
  ShieldCheck,
  Search,
  Filter,
  RefreshCw,
  ArrowLeft,
  Mail,
  Calendar,
  Landmark,
  Trees,
  BrainCircuit,
  UserCheck,
  FileDown,
  Activity,
  CheckCircle2,
  AlertCircle
} from 'lucide-react';
import api from '../api';

export default function AdminUsers() {
  const [users, setUsers] = useState([]);
  const [loading, setLoading] = useState(true);
  const [downloading, setDownloading] = useState(false);
  const [search, setSearch] = useState('');
  const [roleFilter, setRoleFilter] = useState('All');
  const [downloadMsg, setDownloadMsg] = useState(null);

  useEffect(() => {
    fetchUsers();
  }, []);

  const fetchUsers = async () => {
    try {
      setLoading(true);
      const res = await api.get('/admin/users');
      setUsers(res.data || []);
    } catch (err) {
      console.error('Error fetching admin user list:', err);
    } finally {
      setLoading(false);
    }
  };

  const handleDownloadReport = async () => {
    try {
      setDownloading(true);
      setDownloadMsg({ type: 'info', text: 'Generating report...' });
      const res = await api.get('/api/admin/farmers/report', {
        responseType: 'blob'
      });

      // Create blob link and trigger download
      const blob = new Blob([res.data], { type: 'application/pdf' });
      const url = window.URL.createObjectURL(blob);
      const link = document.createElement('a');
      link.href = url;
      link.setAttribute('download', 'YieldSense_AI_Farmer_Report.pdf');
      document.body.appendChild(link);
      link.click();
      link.remove();
      window.URL.revokeObjectURL(url);

      setDownloadMsg({ type: 'success', text: 'Report downloaded successfully.' });
      setTimeout(() => setDownloadMsg(null), 6000);
    } catch (err) {
      console.error('Failed to download PDF report:', err);
      setDownloadMsg({ type: 'error', text: 'Unable to generate report.' });
    } finally {
      setDownloading(false);
    }
  };

  const filteredUsers = users.filter((u) => {
    const matchSearch =
      u.name.toLowerCase().includes(search.toLowerCase()) ||
      u.email.toLowerCase().includes(search.toLowerCase());
    const matchRole = roleFilter === 'All' || u.role === roleFilter;
    return matchSearch && matchRole;
  });

  // Calculate high-level summary KPIs
  const totalFarmers = users.filter((u) => u.role === 'Farmer').length;
  const totalFarms = users.reduce((acc, u) => acc + (u.farms_count || 0), 0);
  const totalCrops = users.reduce((acc, u) => acc + (u.crops_count || 0), 0);
  const totalPredictions = users.reduce((acc, u) => acc + (u.predictions_count || 0), 0);

  return (
    <div className="max-w-6xl mx-auto space-y-6">
      {/* Header */}
      <div className="bg-white p-6 md:p-8 rounded-3xl border border-[#e3ecd9] flex flex-col md:flex-row justify-between items-start md:items-center gap-4 shadow-sm">
        <div className="flex items-center gap-4">
          <Link
            to="/admin"
            className="p-2.5 bg-slate-100 hover:bg-slate-200 text-slate-600 rounded-2xl transition-all"
            title="Back to Admin Dashboard"
          >
            <ArrowLeft size={18} />
          </Link>
          <div>
            <div className="flex items-center gap-2 text-brand-600 font-semibold text-xs uppercase tracking-wider mb-1">
              <ShieldCheck size={16} />
              <span>Administrator Governance</span>
            </div>
            <h2 className="text-2xl md:text-3xl font-bold text-slate-800">Farmer Records & User Directory 👥</h2>
            <p className="text-slate-500 text-sm mt-0.5">
              Comprehensive registry of verified farmers, registered land holdings, logged crops, and yield forecasts.
            </p>
          </div>
        </div>

        <div className="flex items-center gap-3 w-full md:w-auto">
          <button
            id="download-farmer-report-btn"
            onClick={handleDownloadReport}
            disabled={downloading}
            className="flex-1 md:flex-none flex items-center justify-center gap-2 px-5 py-2.5 bg-brand-600 hover:bg-brand-700 active:scale-95 text-white rounded-2xl text-xs font-bold shadow-md shadow-brand-600/20 transition-all disabled:opacity-50"
            title="Download formatted PDF Farmer Report"
          >
            <FileDown size={16} className={downloading ? 'animate-bounce' : ''} />
            <span>{downloading ? 'Generating report...' : 'Download Report'}</span>
          </button>

          <button
            onClick={fetchUsers}
            disabled={loading}
            className="flex items-center justify-center gap-2 px-4 py-2.5 bg-slate-100 hover:bg-slate-200 text-slate-700 rounded-2xl text-xs font-semibold transition-all"
            title="Refresh database records"
          >
            <RefreshCw size={14} className={loading ? 'animate-spin' : ''} />
            <span className="hidden sm:inline">Refresh</span>
          </button>
        </div>
      </div>

      {/* Download Alert Notification */}
      {downloadMsg && (
        <div
          id="report-status-alert"
          className={`p-4 rounded-2xl border flex items-center gap-3 text-xs font-semibold animate-in fade-in slide-in-from-top-2 ${
            downloadMsg.type === 'success'
              ? 'bg-emerald-50 text-emerald-800 border-emerald-200'
              : downloadMsg.type === 'info'
              ? 'bg-blue-50 text-blue-800 border-blue-200'
              : 'bg-red-50 text-red-800 border-red-200'
          }`}
        >
          {downloadMsg.type === 'success' ? (
            <CheckCircle2 size={16} />
          ) : downloadMsg.type === 'info' ? (
            <RefreshCw size={16} className="animate-spin" />
          ) : (
            <AlertCircle size={16} />
          )}
          <span>{downloadMsg.text}</span>
        </div>
      )}

      {/* Summary KPI Cards */}
      <div className="grid grid-cols-2 lg:grid-cols-4 gap-4">
        <div className="bg-white p-5 rounded-2xl border border-[#e3ecd9] shadow-sm flex items-center gap-4">
          <div className="w-12 h-12 rounded-2xl bg-emerald-50 text-emerald-600 flex items-center justify-center font-bold">
            <UserCheck size={24} />
          </div>
          <div>
            <div className="text-xl font-extrabold text-slate-800">{totalFarmers}</div>
            <div className="text-xs text-slate-400 font-semibold uppercase tracking-wider">Total Farmers</div>
          </div>
        </div>

        <div className="bg-white p-5 rounded-2xl border border-[#e3ecd9] shadow-sm flex items-center gap-4">
          <div className="w-12 h-12 rounded-2xl bg-blue-50 text-blue-600 flex items-center justify-center font-bold">
            <Landmark size={24} />
          </div>
          <div>
            <div className="text-xl font-extrabold text-slate-800">{totalFarms}</div>
            <div className="text-xs text-slate-400 font-semibold uppercase tracking-wider">Total Farms</div>
          </div>
        </div>

        <div className="bg-white p-5 rounded-2xl border border-[#e3ecd9] shadow-sm flex items-center gap-4">
          <div className="w-12 h-12 rounded-2xl bg-amber-50 text-amber-600 flex items-center justify-center font-bold">
            <Trees size={24} />
          </div>
          <div>
            <div className="text-xl font-extrabold text-slate-800">{totalCrops}</div>
            <div className="text-xs text-slate-400 font-semibold uppercase tracking-wider">Logged Crops</div>
          </div>
        </div>

        <div className="bg-white p-5 rounded-2xl border border-[#e3ecd9] shadow-sm flex items-center gap-4">
          <div className="w-12 h-12 rounded-2xl bg-purple-50 text-purple-600 flex items-center justify-center font-bold">
            <BrainCircuit size={24} />
          </div>
          <div>
            <div className="text-xl font-extrabold text-slate-800">{totalPredictions}</div>
            <div className="text-xs text-slate-400 font-semibold uppercase tracking-wider">Yield Forecasts</div>
          </div>
        </div>
      </div>

      {/* Filter and Search Bar */}
      <div className="bg-white p-4 rounded-3xl border border-[#e3ecd9] shadow-sm flex flex-col sm:flex-row justify-between items-center gap-4">
        <div className="relative w-full sm:w-80">
          <Search className="absolute left-3.5 top-1/2 -translate-y-1/2 text-slate-400" size={16} />
          <input
            type="text"
            value={search}
            onChange={(e) => setSearch(e.target.value)}
            placeholder="Search farmer name or email..."
            className="w-full pl-10 pr-4 py-2.5 bg-slate-50 border border-slate-200 rounded-2xl text-xs sm:text-sm text-slate-800 placeholder-slate-400 focus:outline-none focus:ring-2 focus:ring-brand-500/20"
          />
        </div>

        <div className="flex items-center gap-2 w-full sm:w-auto">
          <span className="text-xs text-slate-400 font-semibold uppercase tracking-wider">Filter:</span>
          {['All', 'Farmer', 'Administrator'].map((r) => (
            <button
              key={r}
              onClick={() => setRoleFilter(r)}
              className={`px-3.5 py-1.5 rounded-xl text-xs font-semibold transition-all ${
                roleFilter === r
                  ? 'bg-brand-600 text-white shadow-sm'
                  : 'bg-slate-100 text-slate-600 hover:bg-slate-200'
              }`}
            >
              {r}
            </button>
          ))}
        </div>
      </div>

      {/* Farmer & User Records Table */}
      <div className="bg-white rounded-3xl border border-[#e3ecd9] shadow-sm overflow-hidden">
        {loading ? (
          <div className="flex flex-col justify-center items-center py-20 gap-3">
            <RefreshCw className="animate-spin text-brand-500" size={28} />
            <span className="text-xs text-slate-400 font-semibold">Loading real records from database...</span>
          </div>
        ) : filteredUsers.length === 0 ? (
          <div className="text-center py-16 text-slate-400 text-sm">
            No farmer records matching your criteria.
          </div>
        ) : (
          <div className="overflow-x-auto">
            <table className="w-full text-left text-sm text-slate-600">
              <thead className="bg-slate-50/80 text-[11px] uppercase tracking-wider font-bold text-slate-400 border-b border-slate-100">
                <tr>
                  <th className="py-4 px-5">ID</th>
                  <th className="py-4 px-5">Farmer Name & Email</th>
                  <th className="py-4 px-5">Role</th>
                  <th className="py-4 px-5 text-center">Farms</th>
                  <th className="py-4 px-5 text-center">Crops</th>
                  <th className="py-4 px-5 text-center">Predictions</th>
                  <th className="py-4 px-5">Registration Date</th>
                  <th className="py-4 px-5">Status & Activity</th>
                </tr>
              </thead>
              <tbody className="divide-y divide-slate-100">
                {filteredUsers.map((u) => {
                  const isAdmin = u.role === 'Administrator';
                  const isActive = u.status === 'Active' || (u.predictions_count > 0 || u.farms_count > 0);
                  return (
                    <tr key={u.id} className="hover:bg-slate-50/60 transition-colors">
                      <td className="py-4 px-5 font-mono text-xs font-semibold text-slate-400">
                        #{u.id}
                      </td>
                      <td className="py-4 px-5">
                        <div className="font-bold text-slate-800">{u.name}</div>
                        <div className="text-xs text-slate-400 flex items-center gap-1 mt-0.5">
                          <Mail size={12} />
                          <span>{u.email}</span>
                        </div>
                      </td>
                      <td className="py-4 px-5">
                        <span
                          className={`inline-flex items-center gap-1 px-3 py-1 rounded-full text-xs font-bold border ${
                            isAdmin
                              ? 'bg-purple-50 text-purple-700 border-purple-200'
                              : 'bg-emerald-50 text-emerald-700 border-emerald-200'
                          }`}
                        >
                          <ShieldCheck size={12} />
                          <span>{u.role}</span>
                        </span>
                      </td>
                      <td className="py-4 px-5 text-center font-semibold text-slate-700">
                        <span className="inline-block px-2.5 py-0.5 bg-slate-100 rounded-lg text-xs">
                          {u.farms_count}
                        </span>
                      </td>
                      <td className="py-4 px-5 text-center font-semibold text-slate-700">
                        <span className="inline-block px-2.5 py-0.5 bg-slate-100 rounded-lg text-xs">
                          {u.crops_count}
                        </span>
                      </td>
                      <td className="py-4 px-5 text-center font-semibold text-slate-700">
                        <span className="inline-block px-2.5 py-0.5 bg-brand-50 text-brand-700 font-bold rounded-lg text-xs">
                          {u.predictions_count}
                        </span>
                      </td>
                      <td className="py-4 px-5 text-xs text-slate-500 font-mono">
                        {new Date(u.created_at).toLocaleDateString(undefined, {
                          year: 'numeric',
                          month: 'short',
                          day: 'numeric'
                        })}
                      </td>
                      <td className="py-4 px-5">
                        <div className="flex flex-col gap-1">
                          <span
                            className={`inline-flex items-center gap-1 text-[11px] font-bold ${
                              isActive ? 'text-emerald-600' : 'text-slate-400'
                            }`}
                          >
                            <span
                              className={`w-2 h-2 rounded-full ${
                                isActive ? 'bg-emerald-500 animate-pulse' : 'bg-slate-300'
                              }`}
                            />
                            {isActive ? 'Active' : 'Registered'}
                          </span>
                          {u.recent_activity && (
                            <span className="text-[11px] text-slate-400 truncate max-w-[160px]" title={u.recent_activity}>
                              {u.recent_activity}
                            </span>
                          )}
                        </div>
                      </td>
                    </tr>
                  );
                })}
              </tbody>
            </table>
          </div>
        )}
      </div>
    </div>
  );
}
