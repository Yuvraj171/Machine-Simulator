import React from 'react';
import { AlertTriangle, Zap, Thermometer, Droplets, Activity } from 'lucide-react';
import { clsx } from 'clsx';

const FaultControl = ({ onInjectFault, disabled }) => {

    const faults = [
        { id: 'hose_burst', label: 'Hose Burst', icon: Activity, color: 'text-red-400', border: 'border-red-500/50', bg: 'bg-red-500/10' },
        { id: 'power_surge', label: 'Power Surge', icon: Zap, color: 'text-yellow-400', border: 'border-yellow-500/50', bg: 'bg-yellow-500/10' },
        { id: 'servo_jam', label: 'Servo Jam', icon: AlertTriangle, color: 'text-orange-400', border: 'border-orange-500/50', bg: 'bg-orange-500/10' },
        { id: 'cooling_fail', label: 'Cooling Fail', icon: Thermometer, color: 'text-rose-400', border: 'border-rose-500/50', bg: 'bg-rose-500/10' },
        { id: 'pump_failure', label: 'Pump Fail', icon: Droplets, color: 'text-blue-400', border: 'border-blue-500/50', bg: 'bg-blue-500/10' },
    ];

    return (
        <div className="mt-4 border-t border-slate-700 pt-4">
            <h4 className="text-slate-500 text-xs font-semibold uppercase mb-3 flex items-center gap-2">
                <AlertTriangle size={12} />
                Targeted Fault Injection
            </h4>
            <div className="grid grid-cols-2 md:grid-cols-5 gap-2">
                {faults.map((f) => {
                    const Icon = f.icon;
                    return (
                        <button
                            key={f.id}
                            onClick={() => onInjectFault(f.id)}
                            disabled={disabled}
                            className={clsx(
                                "flex flex-col items-center justify-center p-2 rounded-lg border transition-all active:scale-95 disabled:opacity-50 disabled:cursor-not-allowed",
                                f.bg, f.border, "hover:bg-opacity-20"
                            )}
                            title={`Simulate ${f.label}`}
                        >
                            <Icon size={16} className={clsx("mb-1", f.color)} />
                            <span className={clsx("text-[10px] font-bold uppercase", f.color)}>{f.label}</span>
                        </button>
                    );
                })}
            </div>
        </div>
    );
};

export default FaultControl;
