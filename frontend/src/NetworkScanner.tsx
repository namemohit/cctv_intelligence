import { useState } from 'react';
import { Wifi, Search, CheckCircle, Monitor, AlertTriangle, ChevronRight, RefreshCw, Tv2 } from 'lucide-react';

interface Device {
  ip: string;
  port: number;
  hostname: string;
}

interface ScanResult {
  subnet: string;
  devices: Device[];
  total_scanned: number;
}

interface NetworkScannerProps {
  onSelectDevice: (ip: string) => void;
}

export function NetworkScanner({ onSelectDevice }: NetworkScannerProps) {
  const [scanning, setScanning] = useState(false);
  const [result, setResult] = useState<ScanResult | null>(null);
  const [error, setError] = useState<string | null>(null);
  const [selectedIp, setSelectedIp] = useState<string | null>(null);

  const runScan = async () => {
    setScanning(true);
    setResult(null);
    setError(null);
    setSelectedIp(null);

    try {
      const res = await fetch('http://localhost:8000/api/scan_network');
      if (!res.ok) throw new Error('Scan failed');
      const data: ScanResult = await res.json();
      setResult(data);
    } catch (e) {
      setError('Could not reach the backend. Make sure the Python server is running.');
    } finally {
      setScanning(false);
    }
  };

  const handleSelect = (ip: string) => {
    setSelectedIp(ip);
    onSelectDevice(ip);
  };

  return (
    <div className="scanner-wrapper">
      {/* Header */}
      <div className="scanner-header">
        <div className="scanner-header-left">
          <div className="scanner-icon-bg">
            <Wifi size={22} color="white" />
          </div>
          <div>
            <h3 className="scanner-title">Network Scanner</h3>
            <p className="scanner-subtitle">
              Find DVRs &amp; cameras on your local WiFi
            </p>
          </div>
        </div>
        <button
          className={`btn scan-btn ${scanning ? 'scanning' : ''}`}
          onClick={runScan}
          disabled={scanning}
          style={{ width: 'auto', minWidth: '160px' }}
        >
          {scanning
            ? <><RefreshCw size={16} className="spin-icon" /> Scanning…</>
            : <><Search size={16} /> Scan Network</>
          }
        </button>
      </div>

      {/* How it works info bar */}
      {!result && !scanning && !error && (
        <div className="scanner-info-bar">
          <AlertTriangle size={14} style={{ flexShrink: 0, color: 'var(--warning)' }} />
          <span>
            Scans all 254 hosts on your subnet for open RTSP port <strong>554</strong>.
            Takes about 3–5 seconds. DVRs and IP cameras will appear below.
          </span>
        </div>
      )}

      {/* Scanning progress */}
      {scanning && (
        <div className="scanner-progress">
          <div className="scanner-progress-bar">
            <div className="scanner-progress-fill" />
          </div>
          <p className="scanner-progress-text">Probing all devices on your WiFi…</p>
        </div>
      )}

      {/* Error */}
      {error && (
        <div className="scanner-error">
          <AlertTriangle size={16} />
          {error}
        </div>
      )}

      {/* Results */}
      {result && (
        <div className="scanner-results">
          <div className="scanner-results-header">
            <span className="scanner-results-label">
              Scanned <strong>{result.total_scanned}</strong> hosts on <code>{result.subnet}.0/24</code>
            </span>
            <span className={`scanner-badge ${result.devices.length > 0 ? 'found' : 'empty'}`}>
              {result.devices.length > 0
                ? `${result.devices.length} device${result.devices.length > 1 ? 's' : ''} found`
                : 'No devices found'}
            </span>
          </div>

          {result.devices.length === 0 ? (
            <div className="scanner-empty">
              <Monitor size={40} style={{ opacity: 0.3, marginBottom: '0.75rem' }} />
              <p>No devices with port 554 open found on your network.</p>
              <p style={{ fontSize: '0.8rem', marginTop: '0.4rem', color: 'var(--text-muted)' }}>
                Make sure your DVR is powered on and connected to WiFi.
              </p>
            </div>
          ) : (
            <div className="device-list">
              {result.devices.map((device) => {
                const isSelected = selectedIp === device.ip;
                return (
                  <div
                    key={device.ip}
                    className={`device-row ${isSelected ? 'selected' : ''}`}
                    onClick={() => handleSelect(device.ip)}
                  >
                    <div className="device-icon">
                      <Tv2 size={20} />
                    </div>
                    <div className="device-info">
                      <div className="device-ip">{device.ip}</div>
                      <div className="device-hostname">
                        {device.hostname !== device.ip ? device.hostname : 'Unknown device'} · Port {device.port}
                      </div>
                    </div>
                    <div className="device-action">
                      {isSelected
                        ? <CheckCircle size={18} color="var(--success)" />
                        : <ChevronRight size={18} color="var(--text-muted)" />
                      }
                    </div>
                    {isSelected && (
                      <div className="device-selected-tag">IP filled ✓</div>
                    )}
                  </div>
                );
              })}
            </div>
          )}

          <p className="scanner-hint">
            Click a device to auto-fill its IP in the <strong>Connect Your Camera</strong> form below.
          </p>
        </div>
      )}
    </div>
  );
}
