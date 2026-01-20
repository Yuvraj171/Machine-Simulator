import React, { useState } from 'react';
import { Play, Square, AlertTriangle, RotateCcw, Download } from 'lucide-react';
import { clsx } from 'clsx';
import axios from 'axios';

const ControlPanel = ({ status, onStart, onStop, onInjectFault, onReset, onRepair }) => {
    const isRunning = status === 'HEATING' || status === 'QUENCH';
    const isDown = status === 'DOWN';

    // Export Filter State
    const [exportFilter, setExportFilter] = useState('all');

    const handleDownload = async () => {
        try {
            // Build URL with filter query params
            let url = 'http://127.0.0.1:8000/export/excel/1';
            const params = new URLSearchParams();

            switch (exportFilter) {
                case 'last_50':
                    params.append('last_n', '50');
                    break;
                case 'last_100':
                    params.append('last_n', '100');
                    break;
                case 'last_1h':
                    params.append('hours', '1');
                    break;
                case 'last_24h':
                    params.append('hours', '24');
                    break;
                case 'session':
                    params.append('session_only', 'true');
                    break;
                case 'since_export':
                    params.append('since_export', 'true');
                    break;
                default:
                    // 'all' - no params needed
                    break;
            }

            if (params.toString()) {
                url += '?' + params.toString();
            }

            console.log('Exporting with URL:', url);

            const response = await axios.get(url, {
                responseType: 'blob',
            });

            const blobUrl = window.URL.createObjectURL(new Blob([response.data]));
            const link = document.createElement('a');
            link.href = blobUrl;
            link.setAttribute('download', `Simulation_Report_${new Date().toISOString().slice(0, 10)}.xlsx`);
            document.body.appendChild(link);
            link.click();
            link.remove();
        } catch (error) {
            console.error("Export failed", error);
            alert("Failed to download report.");
        }
    };

    const handleStartClick = () => {
        console.log("ControlPanel: Start Clicked");
        if (onStart) onStart();
    };

    const handleStopClick = () => {
        console.log("ControlPanel: Stop Clicked");
        if (onStop) onStop();
    };

    const handleFaultClick = () => {
        console.log("ControlPanel: Inject Fault Clicked");
        if (onInjectFault) onInjectFault();
    };

    const handleResetClick = () => {
        console.log("ControlPanel: Reset Clicked");
        if (onReset) onReset();
    };

    return (
        <div className="w-full bg-industrial-card rounded-xl border border-slate-700 shadow-lg p-6">
            <div className="flex justify-between items-center mb-6">
                <div className="flex items-center gap-4">
                    <h3 className="text-slate-400 text-sm font-semibold uppercase tracking-wider">Machine Control</h3>

                    {/* Export Filter Dropdown */}
                    <select
                        value={exportFilter}
                        onChange={(e) => setExportFilter(e.target.value)}
                        className="text-xs bg-slate-800 text-slate-300 border border-slate-600 rounded px-2 py-1 focus:outline-none focus:border-industrial-accent"
                    >
                        <option value="all">All Data</option>
                        <option value="last_50">Last 50 Parts</option>
                        <option value="last_100">Last 100 Parts</option>
                        <option value="last_1h">Last 1 Hour</option>
                        <option value="last_24h">Last 24 Hours</option>
                        <option value="session">Current Session</option>
                        <option value="since_export">Since Last Export</option>
                    </select>

                    <button
                        onClick={handleDownload}
                        className="text-xs flex items-center gap-1 text-industrial-accent hover:text-white transition-colors border border-industrial-accent/30 rounded px-2 py-1"
                        title="Download Data Log"
                    >
                        <Download size={12} />
                        EXPORT EXCEL
                    </button>
                </div>

                <div className="flex items-center gap-2">
                    <span className={clsx("w-3 h-3 rounded-full animate-pulse", {
                        'bg-industrial-success': status === 'IDLE' || status === 'COMPLETED',
                        'bg-industrial-warning': isRunning,
                        'bg-industrial-danger': isDown,
                    })} />
                    <span className="font-mono text-industrial-text font-bold">{status || 'OFFLINE'}</span>
                </div>
            </div>

            <div className="grid grid-cols-2 md:grid-cols-5 gap-4">
                <button
                    onClick={onStart}
                    disabled={isRunning || isDown}
                    className="flex items-center justify-center gap-2 bg-industrial-success/10 hover:bg-industrial-success/20 text-industrial-success border border-industrial-success/50 py-3 rounded-lg transition-all disabled:opacity-50 disabled:cursor-not-allowed group"
                >
                    <Play size={18} className="group-active:scale-95 transition-transform" />
                    <span className="font-medium">START CYCLE</span>
                </button>

                <button
                    onClick={handleStopClick} // "Stop" in this sim just means finish/reset for now, or we can add a stop endpoint later
                    disabled={!isRunning}
                    className="flex items-center justify-center gap-2 bg-slate-700/50 hover:bg-slate-700 text-slate-300 border border-slate-600 py-3 rounded-lg transition-all disabled:opacity-50 disabled:cursor-not-allowed group"
                >
                    <Square size={18} className="group-active:scale-95 transition-transform" />
                    <span className="font-medium">STOP</span>
                </button>

                <button
                    onClick={handleFaultClick}
                    disabled={isDown}
                    className="flex items-center justify-center gap-2 bg-industrial-danger/10 hover:bg-industrial-danger/20 text-industrial-danger border border-industrial-danger/50 py-3 rounded-lg transition-all disabled:opacity-50 disabled:cursor-not-allowed group"
                >
                    <AlertTriangle size={18} className="group-active:scale-95 transition-transform" />
                    <span className="font-medium">INJECT FAULT</span>
                </button>

                <button
                    onClick={handleResetClick}
                    className="flex items-center justify-center gap-2 bg-slate-500/10 hover:bg-slate-500/20 text-slate-400 border border-slate-500/50 py-3 rounded-lg transition-all group"
                >
                    <RotateCcw size={18} className="group-active:-rotate-180 transition-transform duration-500" />
                    <span className="font-medium">RESET</span>
                </button>

                <button
                    onClick={() => onRepair && onRepair()}
                    className="flex items-center justify-center gap-2 bg-blue-500/10 hover:bg-blue-500/20 text-blue-400 border border-blue-500/50 py-3 rounded-lg transition-all group col-span-2 md:col-span-1"
                >
                    <div className="flex items-center gap-2">
                        <span className="text-lg">🔧</span>
                        <span className="font-medium">REPAIR</span>
                    </div>
                </button>
            </div>
        </div>
    );
};

export default ControlPanel;
