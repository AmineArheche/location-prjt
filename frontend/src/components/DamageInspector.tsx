import React, { useState } from 'react';
import type { DamagePin, DamageType, DamageSeverity, DamageReport } from '../types';
import { AlertTriangle, Trash2, ShieldAlert, Layers } from 'lucide-react';

export type CarView = 'Top' | 'Left Side' | 'Right Side' | 'Front' | 'Back' | 'Windshield';

interface DamageInspectorProps {
  value?: DamageReport | DamagePin[] | Record<string, any>;
  onChange?: (report: DamageReport) => void;
  readOnly?: boolean;
  title?: string;
}

export const DamageInspector: React.FC<DamageInspectorProps> = ({
  value,
  onChange,
  readOnly = false,
  title = 'Vehicle Damage Inspection Map',
}) => {
  // Parse initial pins from value
  const initialPins: DamagePin[] = Array.isArray(value)
    ? value
    : (value as DamageReport)?.pins || [];

  const [pins, setPins] = useState<DamagePin[]>(initialPins);
  const [activeView, setActiveView] = useState<CarView>('Top');
  const [selectedPinId, setSelectedPinId] = useState<string | null>(null);

  const views: CarView[] = ['Top', 'Left Side', 'Right Side', 'Front', 'Back', 'Windshield'];

  // Handle click on the SVG map to add a pin
  const handleMapClick = (e: React.MouseEvent<SVGSVGElement, MouseEvent>) => {
    if (readOnly) return;
    const rect = e.currentTarget.getBoundingClientRect();
    const x = Math.round(((e.clientX - rect.left) / rect.width) * 100);
    const y = Math.round(((e.clientY - rect.top) / rect.height) * 100);

    const newPin: DamagePin = {
      id: 'pin_' + Math.random().toString(36).substring(2, 9),
      view: activeView,
      x,
      y,
      type: 'Scratch',
      severity: 'Minor',
      notes: '',
      photoUrl: '',
    };

    const updatedPins = [...pins, newPin];
    setPins(updatedPins);
    setSelectedPinId(newPin.id);
    notifyChange(updatedPins);
  };

  const notifyChange = (updatedPins: DamagePin[]) => {
    if (onChange) {
      onChange({
        pins: updatedPins,
        timestamp: new Date().toISOString(),
      });
    }
  };

  const updatePin = (id: string, updates: Partial<DamagePin>) => {
    const updated = pins.map((p) => (p.id === id ? { ...p, ...updates } : p));
    setPins(updated);
    notifyChange(updated);
  };

  const deletePin = (id: string) => {
    const updated = pins.filter((p) => p.id !== id);
    setPins(updated);
    if (selectedPinId === id) setSelectedPinId(null);
    notifyChange(updated);
  };

  const selectedPin = pins.find((p) => p.id === selectedPinId);

  const getSeverityBadgeColor = (sev: DamageSeverity) => {
    switch (sev) {
      case 'Minor':
        return 'bg-amber-100 dark:bg-amber-500/20 text-amber-700 dark:text-amber-400 border-amber-300 dark:border-amber-500/30';
      case 'Moderate':
        return 'bg-orange-100 dark:bg-orange-500/20 text-orange-700 dark:text-orange-400 border-orange-300 dark:border-orange-500/30';
      case 'Severe':
        return 'bg-rose-100 dark:bg-rose-500/20 text-rose-700 dark:text-rose-400 border-rose-300 dark:border-rose-500/30';
      default:
        return 'bg-slate-100 dark:bg-slate-700 text-slate-700 dark:text-slate-300';
    }
  };

  return (
    <div className="w-full glass-panel rounded-2xl p-5 border border-slate-200 dark:border-slate-800 space-y-4">
      {/* Header */}
      <div className="flex items-center justify-between">
        <div className="flex items-center gap-2.5">
          <div className="p-2 rounded-xl bg-amber-500/10 border border-amber-500/30 text-amber-600 dark:text-amber-400">
            <ShieldAlert className="w-5 h-5" />
          </div>
          <div>
            <h3 className="text-sm font-bold text-slate-900 dark:text-white uppercase tracking-wider">{title}</h3>
            <p className="text-xs text-slate-500 dark:text-slate-400">Click outline diagram to place or edit damage pins</p>
          </div>
        </div>

        <div className="flex items-center gap-2">
          <span className="px-3 py-1 rounded-full text-xs font-semibold bg-slate-100 dark:bg-slate-800 border border-slate-200 dark:border-slate-700 text-slate-700 dark:text-slate-300">
            Total Damage Pins: <strong className="text-emerald-600 dark:text-emerald-400 font-mono">{pins.length}</strong>
          </span>
        </div>
      </div>

      {/* View Switcher Tabs */}
      <div className="flex items-center gap-1.5 p-1.5 rounded-xl bg-slate-100 dark:bg-slate-900/80 border border-slate-200 dark:border-slate-800 overflow-x-auto">
        {views.map((v) => {
          const count = pins.filter((p) => p.view === v).length;
          return (
            <button
              key={v}
              type="button"
              onClick={() => setActiveView(v)}
              className={`flex items-center gap-1.5 px-3 py-1.5 rounded-lg text-xs font-semibold transition-all whitespace-nowrap ${
                activeView === v
                  ? 'bg-gradient-to-r from-emerald-600 to-teal-600 text-white shadow-md'
                  : 'text-slate-600 dark:text-slate-400 hover:text-slate-900 dark:hover:text-white hover:bg-slate-200/70 dark:hover:bg-slate-800/60'
              }`}
            >
              <span>{v}</span>
              {count > 0 && (
                <span className="w-4 h-4 rounded-full bg-rose-500 text-white text-[10px] flex items-center justify-center font-bold">
                  {count}
                </span>
              )}
            </button>
          );
        })}
      </div>

      {/* 2D Vector Outline Map Container */}
      <div className="grid grid-cols-1 md:grid-cols-3 gap-4 items-start">
        <div className="md:col-span-2 relative rounded-xl bg-slate-100 dark:bg-slate-950 border border-slate-200 dark:border-slate-800 p-4 min-h-[320px] flex items-center justify-center overflow-hidden group">
          {/* Subtle Grid Background */}
          <div className="absolute inset-0 bg-[radial-gradient(#94a3b8_1px,transparent_1px)] dark:bg-[radial-gradient(#1e293b_1px,transparent_1px)] [background-size:16px_16px] opacity-40 pointer-events-none" />

          {/* SVG Outline for selected view */}
          <svg
            viewBox="0 0 500 300"
            className="w-full h-auto max-h-[300px] cursor-crosshair relative z-10 select-none"
            onClick={handleMapClick}
          >
            <defs>
              <linearGradient id="carGrad" x1="0%" y1="0%" x2="100%" y2="100%">
                <stop offset="0%" stopColor="#1e293b" stopOpacity="0.8" />
                <stop offset="100%" stopColor="#0f172a" stopOpacity="0.9" />
              </linearGradient>
            </defs>

            {/* Render 2D Vector Outline per activeView */}
            {activeView === 'Top' && (
              <g stroke="#38bdf8" strokeWidth="2.5" fill="url(#carGrad)" strokeLinejoin="round">
                {/* Car Roof & Hood Top Outline */}
                <path d="M 120 70 Q 250 50 380 70 Q 420 100 420 150 Q 420 200 380 230 Q 250 250 120 230 Q 80 200 80 150 Q 80 100 120 70 Z" />
                {/* Hood Line */}
                <path d="M 140 85 Q 250 75 360 85" stroke="#0284c7" strokeWidth="1.5" fill="none" />
                {/* Windshield Front */}
                <path d="M 160 100 Q 250 90 340 100 L 330 130 Q 250 125 170 130 Z" stroke="#38bdf8" strokeWidth="1.5" fill="#0284c7" fillOpacity="0.2" />
                {/* Roof Box */}
                <rect x="170" y="135" width="160" height="70" rx="8" stroke="#38bdf8" strokeWidth="1.5" fill="none" />
                {/* Rear Window */}
                <path d="M 180 210 Q 250 215 320 210 L 330 220 Q 250 225 170 220 Z" stroke="#38bdf8" strokeWidth="1.5" fill="#0284c7" fillOpacity="0.2" />
                {/* Side Mirrors */}
                <ellipse cx="140" cy="95" rx="10" ry="6" fill="#38bdf8" />
                <ellipse cx="360" cy="95" rx="10" ry="6" fill="#38bdf8" />
              </g>
            )}

            {activeView === 'Left Side' && (
              <g stroke="#38bdf8" strokeWidth="2.5" fill="url(#carGrad)" strokeLinejoin="round">
                {/* Sedan Side Outline */}
                <path d="M 50 200 L 90 200 Q 110 140 170 140 L 320 140 Q 380 160 440 200 L 460 200 Q 470 220 460 230 L 40 230 Z" />
                {/* Windows */}
                <path d="M 175 148 L 245 148 L 245 185 L 140 185 Z" fill="#0284c7" fillOpacity="0.25" stroke="#38bdf8" strokeWidth="1.5" />
                <path d="M 255 148 L 315 148 L 360 185 L 255 185 Z" fill="#0284c7" fillOpacity="0.25" stroke="#38bdf8" strokeWidth="1.5" />
                {/* Wheels */}
                <circle cx="110" cy="225" r="28" fill="#090d16" stroke="#38bdf8" strokeWidth="3" />
                <circle cx="110" cy="225" r="12" fill="#38bdf8" />
                <circle cx="370" cy="225" r="28" fill="#090d16" stroke="#38bdf8" strokeWidth="3" />
                <circle cx="370" cy="225" r="12" fill="#38bdf8" />
                {/* Door Handles */}
                <rect x="210" y="192" width="20" height="4" rx="2" fill="#38bdf8" />
                <rect x="280" y="192" width="20" height="4" rx="2" fill="#38bdf8" />
              </g>
            )}

            {activeView === 'Right Side' && (
              <g stroke="#38bdf8" strokeWidth="2.5" fill="url(#carGrad)" strokeLinejoin="round">
                {/* Reversed Side Silhouette */}
                <path d="M 450 200 L 410 200 Q 390 140 330 140 L 180 140 Q 120 160 60 200 L 40 200 Q 30 220 40 230 L 460 230 Z" />
                {/* Windows */}
                <path d="M 325 148 L 255 148 L 255 185 L 360 185 Z" fill="#0284c7" fillOpacity="0.25" stroke="#38bdf8" strokeWidth="1.5" />
                <path d="M 245 148 L 185 148 L 140 185 L 245 185 Z" fill="#0284c7" fillOpacity="0.25" stroke="#38bdf8" strokeWidth="1.5" />
                {/* Wheels */}
                <circle cx="390" cy="225" r="28" fill="#090d16" stroke="#38bdf8" strokeWidth="3" />
                <circle cx="390" cy="225" r="12" fill="#38bdf8" />
                <circle cx="130" cy="225" r="28" fill="#090d16" stroke="#38bdf8" strokeWidth="3" />
                <circle cx="130" cy="225" r="12" fill="#38bdf8" />
                {/* Door Handles */}
                <rect x="270" y="192" width="20" height="4" rx="2" fill="#38bdf8" />
                <rect x="200" y="192" width="20" height="4" rx="2" fill="#38bdf8" />
              </g>
            )}

            {activeView === 'Front' && (
              <g stroke="#38bdf8" strokeWidth="2.5" fill="url(#carGrad)" strokeLinejoin="round">
                {/* Car Front View */}
                <path d="M 120 230 L 130 150 Q 140 100 250 100 Q 360 100 370 150 L 380 230 Q 250 245 120 230 Z" />
                {/* Windshield */}
                <path d="M 150 115 Q 250 105 350 115 L 340 155 Q 250 150 160 155 Z" fill="#0284c7" fillOpacity="0.3" stroke="#38bdf8" strokeWidth="1.5" />
                {/* Headlights */}
                <polygon points="135,180 175,180 165,200 135,195" fill="#fef08a" stroke="#eab308" strokeWidth="2" />
                <polygon points="365,180 325,180 335,200 365,195" fill="#fef08a" stroke="#eab308" strokeWidth="2" />
                {/* Grille */}
                <rect x="190" y="180" width="120" height="25" rx="4" fill="#090d16" stroke="#38bdf8" strokeWidth="1.5" />
                {/* License Plate */}
                <rect x="210" y="210" width="80" height="16" rx="2" fill="#ffffff" stroke="#000000" strokeWidth="1" />
                <text x="250" y="222" fontSize="9" fontWeight="bold" textAnchor="middle" fill="#000000" stroke="none">12345 | A | 15</text>
              </g>
            )}

            {activeView === 'Back' && (
              <g stroke="#38bdf8" strokeWidth="2.5" fill="url(#carGrad)" strokeLinejoin="round">
                {/* Rear View Silhouette */}
                <path d="M 120 230 L 130 150 Q 140 100 250 100 Q 360 100 370 150 L 380 230 Q 250 245 120 230 Z" />
                {/* Rear Glass */}
                <path d="M 150 115 Q 250 108 350 115 L 340 155 Q 250 152 160 155 Z" fill="#0284c7" fillOpacity="0.25" stroke="#38bdf8" strokeWidth="1.5" />
                {/* Taillights */}
                <polygon points="135,180 175,180 165,200 135,195" fill="#ef4444" stroke="#b91c1c" strokeWidth="2" />
                <polygon points="365,180 325,180 335,200 365,195" fill="#ef4444" stroke="#b91c1c" strokeWidth="2" />
                {/* Trunk Plate Area */}
                <rect x="210" y="185" width="80" height="20" rx="3" fill="#ffffff" stroke="#000000" strokeWidth="1" />
                <text x="250" y="199" fontSize="9" fontWeight="bold" textAnchor="middle" fill="#000000" stroke="none">12345 | A | 15</text>
              </g>
            )}

            {activeView === 'Windshield' && (
              <g stroke="#38bdf8" strokeWidth="2.5" fill="url(#carGrad)" strokeLinejoin="round">
                {/* Glass Close-Up Trapeze */}
                <path d="M 100 80 L 400 80 L 450 240 L 50 240 Z" fill="#0284c7" fillOpacity="0.3" />
                <path d="M 250 80 L 250 240" stroke="#38bdf8" strokeDasharray="4 4" strokeWidth="1.5" />
                <circle cx="250" cy="90" r="10" fill="#1e293b" stroke="#38bdf8" strokeWidth="1.5" />
              </g>
            )}

            {/* Pins on Active View */}
            {pins
              .filter((p) => p.view === activeView)
              .map((p) => {
                const isSelected = p.id === selectedPinId;
                return (
                  <g
                    key={p.id}
                    className="cursor-pointer transition-transform hover:scale-125"
                    onClick={(e) => {
                      e.stopPropagation();
                      setSelectedPinId(p.id);
                    }}
                  >
                    {/* Pulsing ring if selected */}
                    {isSelected && (
                      <circle
                        cx={`${p.x}%`}
                        cy={`${p.y}%`}
                        r="18"
                        className="animate-ping fill-rose-500/30"
                      />
                    )}

                    {/* Outer Pin Body */}
                    <circle
                      cx={`${p.x}%`}
                      cy={`${p.y}%`}
                      r={isSelected ? '12' : '10'}
                      className={`${
                        isSelected ? 'fill-rose-500 stroke-white' : 'fill-amber-500 stroke-slate-900'
                      } stroke-2 drop-shadow-md`}
                    />

                    {/* Pin Center Dot */}
                    <circle
                      cx={`${p.x}%`}
                      cy={`${p.y}%`}
                      r="4"
                      fill="#ffffff"
                    />
                  </g>
                );
              })}
          </svg>
        </div>

        {/* Pin Details & Editor Panel */}
        <div className="rounded-xl bg-white dark:bg-slate-900/90 border border-slate-200 dark:border-slate-800 p-4 space-y-4">
          <div className="flex items-center justify-between border-b border-slate-200 dark:border-slate-800 pb-2">
            <h4 className="text-xs font-bold text-slate-900 dark:text-white uppercase tracking-wider flex items-center gap-1.5">
              <Layers className="w-4 h-4 text-emerald-600 dark:text-emerald-400" />
              {selectedPin ? 'Edit Damage Pin' : 'Select or Add Pin'}
            </h4>
            {selectedPin && !readOnly && (
              <button
                type="button"
                onClick={() => deletePin(selectedPin.id)}
                className="p-1 rounded-lg text-rose-500 hover:bg-rose-50 dark:hover:bg-rose-500/10 transition-colors"
                title="Remove Pin"
              >
                <Trash2 className="w-4 h-4" />
              </button>
            )}
          </div>

          {selectedPin ? (
            <div className="space-y-3">
              <div>
                <label className="block text-[11px] font-semibold text-slate-700 dark:text-slate-300 uppercase tracking-wider mb-1">
                  Damage Type
                </label>
                <select
                  disabled={readOnly}
                  value={selectedPin.type}
                  onChange={(e) => updatePin(selectedPin.id, { type: e.target.value as DamageType })}
                  className="w-full glass-input rounded-lg px-3 py-2 text-xs bg-white dark:bg-slate-900 text-slate-800 dark:text-slate-200 border-slate-300 dark:border-slate-700"
                >
                  <option value="Scratch">Scratch (Rayure)</option>
                  <option value="Dent">Dent (Bosse / Enfoncement)</option>
                  <option value="Crack">Crack (Fissure)</option>
                  <option value="Broken Light">Broken Light (Feu Cassé)</option>
                </select>
              </div>

              <div>
                <label className="block text-[11px] font-semibold text-slate-700 dark:text-slate-300 uppercase tracking-wider mb-1">
                  Severity Level
                </label>
                <div className="grid grid-cols-3 gap-1.5">
                  {(['Minor', 'Moderate', 'Severe'] as DamageSeverity[]).map((sev) => (
                    <button
                      key={sev}
                      type="button"
                      disabled={readOnly}
                      onClick={() => updatePin(selectedPin.id, { severity: sev })}
                      className={`px-2 py-1.5 rounded-lg text-[11px] font-semibold border transition-all ${
                        selectedPin.severity === sev
                          ? getSeverityBadgeColor(sev) + ' ring-1 ring-emerald-500/40'
                          : 'bg-slate-100 dark:bg-slate-800 border-slate-200 dark:border-slate-700 text-slate-600 dark:text-slate-400 hover:text-slate-900 dark:hover:text-slate-200'
                      }`}
                    >
                      {sev}
                    </button>
                  ))}
                </div>
              </div>

              <div>
                <label className="block text-[11px] font-semibold text-slate-700 dark:text-slate-300 uppercase tracking-wider mb-1">
                  Photo URL / Evidence Link
                </label>
                <div className="flex items-center gap-1.5">
                  <input
                    type="url"
                    disabled={readOnly}
                    placeholder="https://..."
                    value={selectedPin.photoUrl || ''}
                    onChange={(e) => updatePin(selectedPin.id, { photoUrl: e.target.value })}
                    className="w-full glass-input rounded-lg px-2.5 py-1.5 text-xs bg-white dark:bg-slate-900 text-slate-800 dark:text-slate-200 border-slate-300 dark:border-slate-700"
                  />
                </div>
              </div>

              <div>
                <label className="block text-[11px] font-semibold text-slate-700 dark:text-slate-300 uppercase tracking-wider mb-1">
                  Agent Inspection Notes
                </label>
                <textarea
                  disabled={readOnly}
                  rows={2}
                  placeholder="e.g. 5cm scratch on front bumper right side..."
                  value={selectedPin.notes || ''}
                  onChange={(e) => updatePin(selectedPin.id, { notes: e.target.value })}
                  className="w-full glass-input rounded-lg p-2 text-xs bg-white dark:bg-slate-900 text-slate-800 dark:text-slate-200 border-slate-300 dark:border-slate-700"
                />
              </div>
            </div>
          ) : (
            <div className="text-center py-8 text-slate-500 text-xs space-y-2">
              <AlertTriangle className="w-8 h-8 mx-auto stroke-1 text-slate-400 dark:text-slate-600" />
              <p>Select an existing pin from the map or list, or click on the car map to drop a new damage pin.</p>
            </div>
          )}
        </div>
      </div>

      {/* Pins Summary Table */}
      {pins.length > 0 && (
        <div className="pt-2 border-t border-slate-200 dark:border-slate-800">
          <div className="text-xs font-semibold text-slate-700 dark:text-slate-300 mb-2 uppercase tracking-wider">
            Recorded Damage Log ({pins.length})
          </div>
          <div className="grid grid-cols-1 sm:grid-cols-2 md:grid-cols-3 gap-2">
            {pins.map((p, idx) => (
              <div
                key={p.id}
                onClick={() => {
                  setActiveView(p.view);
                  setSelectedPinId(p.id);
                }}
                className={`p-2.5 rounded-xl border text-xs cursor-pointer transition-all flex items-center justify-between ${
                  selectedPinId === p.id
                    ? 'bg-slate-100 dark:bg-slate-800 border-cyan-500 shadow-sm'
                    : 'bg-white dark:bg-slate-900/60 border-slate-200 dark:border-slate-800 hover:border-slate-300 dark:hover:border-slate-700'
                }`}
              >
                <div>
                  <div className="font-semibold text-slate-900 dark:text-white flex items-center gap-1.5">
                    <span>#{idx + 1} {p.type}</span>
                    <span className="text-[10px] text-slate-500 dark:text-slate-400">({p.view})</span>
                  </div>
                  <div className="text-[11px] text-slate-500 dark:text-slate-400 truncate max-w-[150px]">
                    {p.notes || 'No description'}
                  </div>
                </div>
                <span className={`px-2 py-0.5 rounded text-[10px] font-bold border ${getSeverityBadgeColor(p.severity)}`}>
                  {p.severity}
                </span>
              </div>
            ))}
          </div>
        </div>
      )}
    </div>
  );
};
