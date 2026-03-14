import React, { useState, useEffect } from 'react';
import { Shield, Settings, Play, Link as LinkIcon, Eye, EyeOff, Wifi } from 'lucide-react';
import { Dashboard } from './Dashboard';
import { NetworkScanner } from './NetworkScanner';
import './index.css';

function App() {
  const [stats, setStats] = useState({
    person_count: 0,
    status: "disconnected",
    last_update: Date.now(),
    error_message: null as string | null
  });
  
  // New comprehensive state for granular RTSP inputs
  const [inputType, setInputType] = useState<'granular' | 'raw'>('granular');
  const [rtspUrl, setRtspUrl] = useState('');
  
  const [showPassword, setShowPassword] = useState(false);
  
  // New State for Persistent Logging
  const [logHistory, setLogHistory] = useState<{time: string, msg: string, type: string}[]>([]);
  
  const [dvrConfig, setDvrConfig] = useState({
    username: 'admin',
    password: '',
    ipAddress: '',
    port: '554',
    channel: '1',
    streamType: 'main' // main or sub
  });

  const [isSubmitting, setIsSubmitting] = useState(false);
  const [videoSourceKey, setVideoSourceKey] = useState(0);
  const [activeTab, setActiveTab] = useState<'connect' | 'scan'>('connect');

  // Poll for stats every second
  useEffect(() => {
    let lastStatus = "";
    let lastError = "";
    
    const fetchStats = async () => {
      try {
        const res = await fetch('http://localhost:8000/api/stats');
        if (res.ok) {
          const data = await res.json();
          setStats(data);
          
          if (data.status !== lastStatus || (data.error_message && data.error_message !== lastError)) {
             let type = "info";
             let msg = data.error_message || `System status: ${data.status}`;
             if (data.status === "error") type = "error";
             if (data.status === "connected") type = "success";
             if (data.status === "connecting" && !data.error_message) msg = "Dialing camera stream...";
             
             // Check if it's genuinely a new message or status change
             // We use a stronger check: ignore if the exact same message was logged within the last 10 seconds.
             setLogHistory(logs => {
               // Get recent logs (last 5)
               const recentLogs = logs.slice(-5);
               const isDuplicate = recentLogs.some(l => l.msg === msg);
               
               if (isDuplicate) return logs; // skip duplicate
               
               return [...logs, {
                 time: new Date().toLocaleTimeString(),
                 msg: msg,
                 type: type
               }];
             });
             
             lastStatus = data.status;
             lastError = data.error_message;
          }
        }
      } catch (err) {
        setStats(prev => ({ ...prev, status: "error" }));
      }
    };

    const interval = setInterval(fetchStats, 1000);
    return () => clearInterval(interval);
  }, []);

  // Construct RTSP URL from granular inputs
  const constructRtspUrl = () => {
    const { username, password, ipAddress, port, channel, streamType } = dvrConfig;
    if (!ipAddress) return '';
    
    const encUser = encodeURIComponent(username);
    const encPass = encodeURIComponent(password);
    
    const ch = channel.padStart(1, '1'); // Convert 1 -> 1
    const stream = streamType === 'main' ? '1' : '2';
    
    return `rtsp://${encUser}:${encPass}@${ipAddress}:${port}/Streaming/Channels/${ch}0${stream}`;
  };

  const handleConnect = async (e: React.FormEvent) => {
    e.preventDefault();
    
    const finalUrl = inputType === 'granular' ? constructRtspUrl() : rtspUrl;
    
    if (!finalUrl) {
      alert("Please provide the connection details.");
      return;
    }

    setIsSubmitting(true);
    try {
      const controller = new AbortController();
      const timeoutId = setTimeout(() => controller.abort(), 5000);
      
      const res = await fetch('http://localhost:8000/api/set_source', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json'
        },
        body: JSON.stringify({ url: finalUrl }),
        signal: controller.signal
      });
      clearTimeout(timeoutId);
      
      setLogHistory([{ time: new Date().toLocaleTimeString(), msg: `Connecting to ${finalUrl.replace(/:([^:@]+)@/, ':***@')}...`, type: 'info' }]);
      
      if (res.ok) {
        setVideoSourceKey(prev => prev + 1); // Force image reload
        setStats(prev => ({ ...prev, status: "connecting" }));
      }
    } catch (err) {
      console.error("Failed to connect:", err);
    } finally {
      setIsSubmitting(false);
    }
  };

  const useSampleVideo = async () => {
    const sampleUrl = "/Users/mohit/Desktop/name.mohit/dvr_yolo_integration_codebase/ForBiggerFun.mp4";
    setRtspUrl(sampleUrl);
    setInputType('raw');
    
    setIsSubmitting(true);
    try {
      await fetch('http://localhost:8000/api/set_source', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json'},
        body: JSON.stringify({ url: sampleUrl })
      });
      
      setLogHistory([{ time: new Date().toLocaleTimeString(), msg: "Connecting to sample video...", type: 'info' }]);
      
      setVideoSourceKey(prev => prev + 1);
    } finally {
      setIsSubmitting(false);
    }
  };

  const handleConfigChange = (e: React.ChangeEvent<HTMLInputElement | HTMLSelectElement>) => {
    const { name, value } = e.target;
    setDvrConfig(prev => ({ ...prev, [name]: value }));
  };

  const handleDeviceSelected = (ip: string) => {
    setDvrConfig(prev => ({ ...prev, ipAddress: ip }));
    setInputType('granular');
    setActiveTab('connect');
  };

  return (
    <div className="app-container">
      <header className="header glass-panel">
        <div className="header-title">
          <div style={{ background: 'var(--primary)', padding: '0.5rem', borderRadius: '12px' }}>
            <Shield size={24} color="white" />
          </div>
          <h1>YOLO Surveillance Hub</h1>
        </div>
        
        <div style={{ display: 'flex', alignItems: 'center', gap: '1rem' }}>
          {stats.status === "connected" && (
            <div style={{ display: 'flex', alignItems: 'center', gap: '0.5rem', fontSize: '0.875rem' }}>
              <div style={{ width: 8, height: 8, borderRadius: '50%', background: 'var(--success)' }}></div>
              System Active
            </div>
          )}
        </div>
      </header>

      <main>
        <Dashboard stats={stats} videoSourceKey={videoSourceKey} />
      </main>
      
      <section className="glass-panel settings-panel" style={{ marginTop: '1rem', animation: 'fadeIn 1s ease-out' }}>
        {/* Tab Switcher */}
        <div style={{ display: 'flex', gap: '0.5rem', marginBottom: '1.5rem', background: 'rgba(0,0,0,0.2)', padding: '0.25rem', borderRadius: '10px', width: 'fit-content' }}>
          <button
            onClick={() => setActiveTab('connect')}
            style={{
              padding: '0.6rem 1.25rem',
              background: activeTab === 'connect' ? 'var(--primary)' : 'transparent',
              border: 'none', borderRadius: '8px', color: 'white',
              cursor: 'pointer', fontSize: '0.875rem', fontWeight: 500,
              display: 'flex', alignItems: 'center', gap: '0.4rem',
              transition: 'all 0.2s'
            }}
          >
            <Settings size={15} /> Connect Camera
          </button>
          <button
            onClick={() => setActiveTab('scan')}
            style={{
              padding: '0.6rem 1.25rem',
              background: activeTab === 'scan' ? '#7c3aed' : 'transparent',
              border: 'none', borderRadius: '8px', color: 'white',
              cursor: 'pointer', fontSize: '0.875rem', fontWeight: 500,
              display: 'flex', alignItems: 'center', gap: '0.4rem',
              transition: 'all 0.2s'
            }}
          >
            <Wifi size={15} /> Find DVR on Network
          </button>
        </div>

        {/* Tab: Connect Camera */}
        {activeTab === 'connect' && (<>
        <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '1.5rem' }}>
          <h3 style={{ display: 'flex', alignItems: 'center', gap: '0.5rem', fontSize: '1.25rem', margin: 0 }}>
            <Settings className="text-primary" />
            Connect Your Camera
          </h3>
          
          <div style={{ display: 'flex', gap: '0.5rem', background: 'rgba(0,0,0,0.2)', padding: '0.25rem', borderRadius: '8px' }}>
            <button 
              className={`toggle-btn ${inputType === 'granular' ? 'active' : ''}`}
              onClick={() => setInputType('granular')}
              style={{
                padding: '0.5rem 1rem',
                background: inputType === 'granular' ? 'var(--primary)' : 'transparent',
                border: 'none',
                borderRadius: '6px',
                color: 'white',
                cursor: 'pointer',
                fontSize: '0.875rem',
                transition: 'all 0.2s'
              }}
            >
              Easy Setup
            </button>
            <button 
              className={`toggle-btn ${inputType === 'raw' ? 'active' : ''}`}
              onClick={() => setInputType('raw')}
              style={{
                padding: '0.5rem 1rem',
                background: inputType === 'raw' ? 'var(--primary)' : 'transparent',
                border: 'none',
                borderRadius: '6px',
                color: 'white',
                cursor: 'pointer',
                fontSize: '0.875rem',
                transition: 'all 0.2s'
              }}
            >
              Advanced (URL)
            </button>
          </div>
        </div>
        
        <div style={{ display: 'grid', gridTemplateColumns: '1fr auto', gap: '2rem', alignItems: 'flex-start' }}>
          <form onSubmit={handleConnect} style={{ display: 'flex', flexDirection: 'column', gap: '1.5rem', flex: 1 }}>
            
            {inputType === 'granular' ? (
              <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(200px, 1fr))', gap: '1rem' }}>
                <div className="form-group" style={{ marginBottom: 0 }}>
                  <label className="form-label">Public IP / DDNS Address</label>
                  <input 
                    type="text" 
                    name="ipAddress"
                    className="form-input" 
                    placeholder="e.g. 182.xx.xx.xx or mydvr.ddns.net"
                    value={dvrConfig.ipAddress}
                    onChange={handleConfigChange}
                    required
                  />
                  <small style={{ color: 'var(--text-muted)', fontSize: '0.75rem', marginTop: '4px', display: 'block' }}>Your router's public internet address</small>
                </div>

                <div className="form-group" style={{ marginBottom: 0 }}>
                  <label className="form-label">RTSP Port</label>
                  <input 
                    type="text" 
                    name="port"
                    className="form-input" 
                    placeholder="554"
                    value={dvrConfig.port}
                    onChange={handleConfigChange}
                  />
                  <small style={{ color: 'var(--text-muted)', fontSize: '0.75rem', marginTop: '4px', display: 'block' }}>Default is 554. Needs port-forwarding.</small>
                </div>

                <div className="form-group" style={{ marginBottom: 0 }}>
                  <label className="form-label">Username</label>
                  <input 
                    type="text" 
                    name="username"
                    className="form-input" 
                    placeholder="admin"
                    value={dvrConfig.username}
                    onChange={handleConfigChange}
                  />
                </div>

                <div className="form-group" style={{ marginBottom: 0 }}>
                  <label className="form-label">Password</label>
                  <div style={{ position: 'relative' }}>
                    <input 
                      type={showPassword ? "text" : "password"}
                      name="password"
                      className="form-input" 
                      placeholder="DVR Password"
                      value={dvrConfig.password}
                      onChange={handleConfigChange}
                      style={{ paddingRight: '2.5rem' }}
                    />
                    <button 
                      type="button"
                      onClick={() => setShowPassword(!showPassword)}
                      style={{
                        position: 'absolute',
                        right: '0.75rem',
                        top: '50%',
                        transform: 'translateY(-50%)',
                        background: 'none',
                        border: 'none',
                        color: 'var(--text-muted)',
                        cursor: 'pointer',
                        display: 'flex',
                        alignItems: 'center'
                      }}
                    >
                      {showPassword ? <EyeOff size={18} /> : <Eye size={18} />}
                    </button>
                  </div>
                </div>

                <div className="form-group" style={{ marginBottom: 0 }}>
                  <label className="form-label">Camera Channel</label>
                  <input 
                    type="number" 
                    name="channel"
                    className="form-input" 
                    min="1"
                    value={dvrConfig.channel}
                    onChange={handleConfigChange}
                  />
                </div>

                <div className="form-group" style={{ marginBottom: 0 }}>
                  <label className="form-label">Stream Quality</label>
                  <select 
                    name="streamType" 
                    className="form-input"
                    value={dvrConfig.streamType}
                    onChange={handleConfigChange}
                    style={{ height: '44px' }}
                  >
                    <option value="main">Main Stream (High Quality)</option>
                    <option value="sub">Sub Stream (Better for internet)</option>
                  </select>
                </div>
              </div>
            ) : (
              <div className="form-group" style={{ marginBottom: 0 }}>
                <label className="form-label">Complete RTSP URL or Local Video Path</label>
                <div style={{ display: 'flex', alignItems: 'center', background: 'rgba(0,0,0,0.2)', border: '1px solid var(--card-border)', borderRadius: '8px', paddingRight: '0.5rem' }}>
                  <div style={{ padding: '0 1rem', color: 'var(--text-muted)' }}>
                    <LinkIcon size={16} />
                  </div>
                  <input 
                    type="text" 
                    className="form-input" 
                    style={{ border: 'none', background: 'transparent', paddingLeft: 0 }}
                    placeholder="rtsp://username:password@ip:554/Streaming/Channels/101"
                    value={rtspUrl}
                    onChange={(e) => setRtspUrl(e.target.value)}
                  />
                </div>
              </div>
            )}

            {inputType === 'granular' && (
              <div style={{ marginTop: '0.5rem', padding: '0.75rem', background: 'rgba(0,0,0,0.2)', borderRadius: '8px', border: '1px solid rgba(255,255,255,0.05)' }}>
                <p style={{ fontSize: '0.75rem', color: 'var(--text-muted)', marginBottom: '0.25rem', textTransform: 'uppercase', letterSpacing: '0.05em' }}>Generated Connection String</p>
                <div style={{ fontFamily: 'monospace', fontSize: '0.875rem', color: 'var(--text-main)', wordBreak: 'break-all' }}>
                  {constructRtspUrl() ? (
                    <>
                      rtsp://<span style={{ color: 'var(--primary)' }}>{encodeURIComponent(dvrConfig.username)}</span>:
                      <span style={{ color: 'var(--danger)' }}>{showPassword ? encodeURIComponent(dvrConfig.password) : '********'}</span>@
                      <span style={{ color: 'var(--success)' }}>{dvrConfig.ipAddress || 'IP'}</span>:
                      <span style={{ color: 'var(--warning)' }}>{dvrConfig.port || '554'}</span>
                      /Streaming/Channels/{dvrConfig.channel.padStart(1, '1')}0{dvrConfig.streamType === 'main' ? '1' : '2'}
                    </>
                  ) : <span style={{ color: 'var(--text-muted)' }}>Waiting for IP address...</span>}
                </div>
              </div>
            )}

            <div style={{ borderTop: '1px solid var(--card-border)', paddingTop: '1.5rem', display: 'flex', justifyContent: 'flex-start' }}>
               <button type="submit" className="btn" disabled={isSubmitting || (inputType === 'granular' && !dvrConfig.ipAddress) || (inputType === 'raw' && !rtspUrl)} style={{ width: 'auto', minWidth: '200px' }}>
                {isSubmitting ? 'Connecting...' : 'Connect to Camera'}
              </button>
            </div>
          </form>
          
          <div style={{ borderLeft: '1px solid var(--card-border)', paddingLeft: '2rem', height: '100%', display: 'flex', flexDirection: 'column', justifyContent: 'center' }}>
            <div style={{ background: 'rgba(59, 130, 246, 0.1)', padding: '1rem', borderRadius: '12px', marginBottom: '1rem', maxWidth: '250px' }}>
              <p style={{ fontSize: '0.875rem', color: 'var(--text-muted)', marginBottom: '0', lineHeight: 1.5 }}>
                Don't have your router setup yet? You can still test the YOLO AI.
              </p>
            </div>
            <button 
              onClick={useSampleVideo} 
              className="btn" 
              style={{ background: 'var(--card-bg)', border: '1px solid var(--card-border)' }}
              disabled={isSubmitting}
            >
              <Play size={16} /> Play Sample Video
            </button>
          </div>
        </div>
        
        {/* Diagnostic Logs Section */}
        {logHistory.length > 0 && (
          <div style={{ marginTop: '2rem', padding: '1rem', background: 'rgba(0,0,0,0.3)', borderRadius: '12px', border: '1px solid var(--card-border)' }}>
            <h4 style={{ fontSize: '0.875rem', textTransform: 'uppercase', letterSpacing: '0.05em', color: 'var(--text-muted)', marginBottom: '0.5rem' }}>Connection History</h4>
            <div style={{ 
              fontFamily: 'monospace', 
              fontSize: '0.875rem', 
              maxHeight: '150px', 
              overflowY: 'auto',
              padding: '0.5rem',
              background: 'rgba(0,0,0,0.5)',
              borderRadius: '6px',
              userSelect: 'text'
            }}>
              {logHistory.map((log, i) => (
                <div key={i} style={{ marginBottom: '4px', borderBottom: '1px solid rgba(255,255,255,0.05)', paddingBottom: '4px' }}>
                  <span style={{ color: 'var(--text-muted)', marginRight: '8px' }}>[{log.time}]</span>
                  <span style={{ 
                    color: log.type === 'error' ? 'var(--danger)' : 
                           log.type === 'success' ? 'var(--success)' : 
                           'var(--warning)' 
                  }}>
                    {log.type === 'error' ? '[FAILED]' : log.type === 'success' ? '[SUCCESS]' : '[WORKING]'} {log.msg}
                  </span>
                </div>
              ))}
            </div>
          </div>
        )}
        </>)}

        {/* Tab: Network Scanner */}
        {activeTab === 'scan' && (
          <NetworkScanner onSelectDevice={handleDeviceSelected} />
        )}
      </section>
    </div>
  );
}

export default App;
