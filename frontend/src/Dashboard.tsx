import { Camera, Users, Activity, AlertCircle, RefreshCw } from 'lucide-react';
import './index.css';

interface DashboardProps {
  stats: any;
  videoSourceKey: number;
}

export function Dashboard({ stats, videoSourceKey }: DashboardProps) {
  const isConnected = stats.status === "connected";
  const statusColors = {
    connected: "success",
    connecting: "warning",
    reconnecting: "warning",
    error: "danger",
    disconnected: "muted",
    waiting_for_source: "warning"
  };

  const statusIcons = {
    connected: <Activity />,
    connecting: <RefreshCw className="animate-spin" />,
    reconnecting: <RefreshCw className="animate-spin" />,
    error: <AlertCircle />,
    disconnected: <AlertCircle />,
    waiting_for_source: <Camera />
  };

  // @ts-ignore
  const color = statusColors[stats.status] || "muted";
  // @ts-ignore
  const icon = statusIcons[stats.status] || <AlertCircle />;

  return (
    <div className="dashboard-grid">
      {/* Main Video Section */}
      <div className="video-section">
        <div className="glass-panel" style={{ padding: '1.5rem' }}>
          <h2 style={{ fontSize: '1.25rem', marginBottom: '1rem', display: 'flex', alignItems: 'center', gap: '0.5rem' }}>
            <Camera className="text-primary" />
            Live DVR Feed
          </h2>
          
          <div className="video-container">
            {isConnected ? (
              <>
                <div className="video-overlay">
                  <span className="badge live">LIVE</span>
                  <span className="badge">
                    <Users size={12} /> {stats.person_count} Detected
                  </span>
                </div>
                <img 
                  key={videoSourceKey}
                  src={`http://localhost:8000/video_feed?key=${videoSourceKey}`} 
                  alt="Live CCTV Feed" 
                  className="video-feed"
                  onError={(e) => {
                    // Try to reload on err
                    e.currentTarget.style.display = 'none';
                    e.currentTarget.parentElement?.classList.add('error-state');
                  }}
                  onLoad={(e) => {
                    e.currentTarget.style.display = 'block';
                    e.currentTarget.parentElement?.classList.remove('error-state');
                  }}
                />
              </>
            ) : (
              <div className="loader-container">
                {stats.status === "waiting_for_source" ? (
                  <>
                    <Camera size={48} style={{ marginBottom: '1rem', opacity: 0.5 }} />
                    <p>Enter an RTSP URL to begin streaming</p>
                  </>
                ) : stats.status === "error" ? (
                  <>
                    <AlertCircle size={48} className="text-danger" style={{ marginBottom: '1rem' }} />
                    <p style={{ color: 'var(--danger)', fontWeight: 500, marginBottom: '0.5rem' }}>Failed to connect to video source.</p>
                    {stats.error_message && (
                      <p style={{ fontSize: '0.875rem', maxWidth: '80%', textAlign: 'center' }}>
                        Error: {stats.error_message}
                      </p>
                    )}
                  </>
                ) : (
                  <>
                    <div className="spinner"></div>
                    <p>Connecting to stream...</p>
                  </>
                )}
              </div>
            )}
          </div>
        </div>
      </div>

      {/* Stats Sidebar Section */}
      <div className="stats-section">
        <div className="glass-panel stat-card">
          <div className={`stat-icon ${color}`}>
            {icon}
          </div>
          <div className="stat-content">
            <div className="stat-label">Connection Status</div>
            <div className="stat-value" style={{ fontSize: '1.5rem', textTransform: 'capitalize' }}>
              {stats.status.replace(/_/g, " ")}
            </div>
            {isConnected && (
              <div className="stat-subtext">Receiving frames...</div>
            )}
          </div>
        </div>

        <div className="glass-panel stat-card">
          <div className="stat-icon" style={{ background: 'rgba(59, 130, 246, 0.1)', color: 'var(--primary)' }}>
            <Users size={32} />
          </div>
          <div className="stat-content">
            <div className="stat-label">People Detected</div>
            <div className="stat-value">{stats.person_count}</div>
            <div className="stat-subtext">Current frame count</div>
          </div>
        </div>

        {isConnected && stats.latency_ms !== undefined && (
          <div className="glass-panel stat-card" style={{ animation: 'slideIn 0.3s ease-out' }}>
            <div className="stat-icon" style={{ background: 'rgba(245, 158, 11, 0.1)', color: 'var(--warning)' }}>
              <Activity size={24} />
            </div>
            <div className="stat-content">
              <div className="stat-label">AI Processing Latency</div>
              <div className="stat-value">{stats.latency_ms} ms</div>
              <div className="stat-subtext">Time to detect objects</div>
            </div>
          </div>
        )}
      </div>
    </div>
  );
}
