import React, { useState, useEffect } from 'react';
import { useToast } from '../hooks/use-toast';

const Settings = () => {
  const [settings, setSettings] = useState({
    // Application Settings
    app_name: 'ProjectHosting',
    app_description: 'A comprehensive project hosting platform',
    app_url: 'https://projecthosting.local',
    maintenance_mode: false,
    
    // Database Settings
    database_url: '',
    database_pool_size: 10,
    database_timeout: 30,
    
    // Redis Settings
    redis_url: '',
    redis_timeout: 5,
    
    // JWT Settings
    jwt_secret: '',
    jwt_expiration: 3600,
    
    // Email Settings
    smtp_host: '',
    smtp_port: 587,
    smtp_username: '',
    smtp_password: '',
    smtp_use_tls: true,
    
    // Monitoring Settings
    prometheus_enabled: true,
    grafana_enabled: true,
    log_level: 'INFO',
    metrics_retention: '30d',
    
    // VPN Settings
    tailscale_enabled: false,
    tailscale_hostname: 'projecthosting-vpn',
    tailscale_routes: '10.0.0.0/8,172.16.0.0/12,192.168.0.0/16',
    
    // Security Settings
    rate_limit_enabled: true,
    rate_limit_requests: 100,
    rate_limit_window: 60,
    cors_origins: '*',
    
    // File Upload Settings
    max_file_size: 5242880, // 5MB
    allowed_file_types: 'jpg,jpeg,png,gif,webp,pdf,doc,docx',
    upload_path: '/app/uploads',
    
    // Backup Settings
    backup_enabled: true,
    backup_schedule: '0 2 * * *',
    backup_retention: 7,
    backup_location: '/app/backups'
  });

  const [loading, setLoading] = useState(true);
  const [saving, setSaving] = useState(false);
  const [activeTab, setActiveTab] = useState('application');
  const [systemStatus, setSystemStatus] = useState({});
  const { toast } = useToast();

  const tabs = [
    { id: 'application', name: 'Application', icon: '🏠' },
    { id: 'database', name: 'Database', icon: '🗄️' },
    { id: 'monitoring', name: 'Monitoring', icon: '📊' },
    { id: 'security', name: 'Security', icon: '🔒' },
    { id: 'files', name: 'Files', icon: '📁' },
    { id: 'backup', name: 'Backup', icon: '💾' },
    { id: 'system', name: 'System', icon: '⚙️' }
  ];

  useEffect(() => {
    fetchSettings();
    fetchSystemStatus();
  }, []);

  const fetchSettings = async () => {
    try {
      const response = await fetch('/api/admin/settings');
      if (response.ok) {
        const data = await response.json();
        setSettings(prev => ({ ...prev, ...data.settings }));
      }
    } catch (error) {
      console.error('Error fetching settings:', error);
      toast({
        title: "Error",
        description: "Failed to load settings",
        variant: "destructive"
      });
    } finally {
      setLoading(false);
    }
  };

  const fetchSystemStatus = async () => {
    try {
      const response = await fetch('/api/admin/system/status');
      if (response.ok) {
        const data = await response.json();
        setSystemStatus(data);
      }
    } catch (error) {
      console.error('Error fetching system status:', error);
    }
  };

  const handleSettingChange = (key, value) => {
    setSettings(prev => ({
      ...prev,
      [key]: value
    }));
  };

  const saveSettings = async () => {
    setSaving(true);
    try {
      const response = await fetch('/api/admin/settings', {
        method: 'PUT',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({ settings }),
      });

      if (response.ok) {
        toast({
          title: "Success",
          description: "Settings saved successfully",
        });
      } else {
        throw new Error('Failed to save settings');
      }
    } catch (error) {
      console.error('Error saving settings:', error);
      toast({
        title: "Error",
        description: "Failed to save settings",
        variant: "destructive"
      });
    } finally {
      setSaving(false);
    }
  };

  const testConnection = async (type) => {
    try {
      const response = await fetch(`/api/admin/test/${type}`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({ settings }),
      });

      const result = await response.json();
      
      if (result.success) {
        toast({
          title: "Success",
          description: `${type} connection test passed`,
        });
      } else {
        toast({
          title: "Error",
          description: `${type} connection test failed: ${result.error}`,
          variant: "destructive"
        });
      }
    } catch (error) {
      toast({
        title: "Error",
        description: `Failed to test ${type} connection`,
        variant: "destructive"
      });
    }
  };

  const restartService = async (service) => {
    try {
      const response = await fetch(`/api/admin/services/${service}/restart`, {
        method: 'POST',
      });

      if (response.ok) {
        toast({
          title: "Success",
          description: `${service} service restarted successfully`,
        });
        fetchSystemStatus();
      } else {
        throw new Error('Failed to restart service');
      }
    } catch (error) {
      toast({
        title: "Error",
        description: `Failed to restart ${service} service`,
        variant: "destructive"
      });
    }
  };

  const triggerBackup = async () => {
    try {
      const response = await fetch('/api/admin/backup/trigger', {
        method: 'POST',
      });

      if (response.ok) {
        toast({
          title: "Success",
          description: "Backup started successfully",
        });
      } else {
        throw new Error('Failed to start backup');
      }
    } catch (error) {
      toast({
        title: "Error",
        description: "Failed to start backup",
        variant: "destructive"
      });
    }
  };

  if (loading) {
    return (
      <div className="flex items-center justify-center min-h-64">
        <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-600"></div>
      </div>
    );
  }

  const renderApplicationSettings = () => (
    <div className="space-y-6">
      <div>
        <label className="block text-sm font-medium text-gray-700 mb-2">
          Application Name
        </label>
        <input
          type="text"
          value={settings.app_name}
          onChange={(e) => handleSettingChange('app_name', e.target.value)}
          className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
        />
      </div>

      <div>
        <label className="block text-sm font-medium text-gray-700 mb-2">
          Application Description
        </label>
        <textarea
          value={settings.app_description}
          onChange={(e) => handleSettingChange('app_description', e.target.value)}
          rows={3}
          className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
        />
      </div>

      <div>
        <label className="block text-sm font-medium text-gray-700 mb-2">
          Application URL
        </label>
        <input
          type="url"
          value={settings.app_url}
          onChange={(e) => handleSettingChange('app_url', e.target.value)}
          className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
        />
      </div>

      <div className="flex items-center">
        <input
          type="checkbox"
          id="maintenance_mode"
          checked={settings.maintenance_mode}
          onChange={(e) => handleSettingChange('maintenance_mode', e.target.checked)}
          className="h-4 w-4 text-blue-600 focus:ring-blue-500 border-gray-300 rounded"
        />
        <label htmlFor="maintenance_mode" className="ml-2 block text-sm text-gray-700">
          Enable Maintenance Mode
        </label>
      </div>
    </div>
  );

  const renderDatabaseSettings = () => (
    <div className="space-y-6">
      <div>
        <label className="block text-sm font-medium text-gray-700 mb-2">
          Database URL
        </label>
        <input
          type="text"
          value={settings.database_url}
          onChange={(e) => handleSettingChange('database_url', e.target.value)}
          placeholder="postgresql://user:password@host:port/database"
          className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
        />
        <button
          onClick={() => testConnection('database')}
          className="mt-2 bg-blue-600 text-white px-4 py-2 rounded hover:bg-blue-700 transition-colors"
        >
          Test Connection
        </button>
      </div>

      <div className="grid grid-cols-2 gap-4">
        <div>
          <label className="block text-sm font-medium text-gray-700 mb-2">
            Pool Size
          </label>
          <input
            type="number"
            value={settings.database_pool_size}
            onChange={(e) => handleSettingChange('database_pool_size', parseInt(e.target.value))}
            min="1"
            max="100"
            className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
          />
        </div>

        <div>
          <label className="block text-sm font-medium text-gray-700 mb-2">
            Timeout (seconds)
          </label>
          <input
            type="number"
            value={settings.database_timeout}
            onChange={(e) => handleSettingChange('database_timeout', parseInt(e.target.value))}
            min="1"
            max="300"
            className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
          />
        </div>
      </div>

      <div>
        <label className="block text-sm font-medium text-gray-700 mb-2">
          Redis URL
        </label>
        <input
          type="text"
          value={settings.redis_url}
          onChange={(e) => handleSettingChange('redis_url', e.target.value)}
          placeholder="redis://host:port/db"
          className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
        />
        <button
          onClick={() => testConnection('redis')}
          className="mt-2 bg-blue-600 text-white px-4 py-2 rounded hover:bg-blue-700 transition-colors"
        >
          Test Connection
        </button>
      </div>
    </div>
  );

  const renderSystemTab = () => (
    <div className="space-y-6">
      <div className="bg-gray-50 p-4 rounded-lg">
        <h3 className="text-lg font-semibold mb-4">System Status</h3>
        <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
          {Object.entries(systemStatus).map(([service, status]) => (
            <div key={service} className="text-center">
              <div className={`w-4 h-4 rounded-full mx-auto mb-2 ${
                status === 'healthy' ? 'bg-green-500' : 'bg-red-500'
              }`}></div>
              <div className="text-sm font-medium capitalize">{service}</div>
              <div className="text-xs text-gray-600">{status}</div>
            </div>
          ))}
        </div>
      </div>

      <div className="bg-gray-50 p-4 rounded-lg">
        <h3 className="text-lg font-semibold mb-4">Service Management</h3>
        <div className="grid grid-cols-2 md:grid-cols-3 gap-4">
          {['frontend', 'backend', 'bridge', 'watchdog'].map((service) => (
            <button
              key={service}
              onClick={() => restartService(service)}
              className="bg-yellow-600 text-white px-4 py-2 rounded hover:bg-yellow-700 transition-colors"
            >
              Restart {service}
            </button>
          ))}
        </div>
      </div>

      <div className="bg-gray-50 p-4 rounded-lg">
        <h3 className="text-lg font-semibold mb-4">Backup Management</h3>
        <button
          onClick={triggerBackup}
          className="bg-green-600 text-white px-4 py-2 rounded hover:bg-green-700 transition-colors"
        >
          Trigger Manual Backup
        </button>
      </div>
    </div>
  );

  return (
    <div className="max-w-6xl mx-auto p-6">
      <div className="flex justify-between items-center mb-6">
        <div>
          <h1 className="text-3xl font-bold text-gray-900">Settings</h1>
          <p className="text-gray-600 mt-1">Configure your application settings</p>
        </div>
        <button
          onClick={saveSettings}
          disabled={saving}
          className="bg-blue-600 text-white px-6 py-2 rounded-lg hover:bg-blue-700 transition-colors disabled:opacity-50"
        >
          {saving ? 'Saving...' : 'Save Settings'}
        </button>
      </div>

      <div className="bg-white rounded-lg shadow-md">
        {/* Tabs */}
        <div className="border-b border-gray-200">
          <nav className="flex space-x-8 px-6">
            {tabs.map((tab) => (
              <button
                key={tab.id}
                onClick={() => setActiveTab(tab.id)}
                className={`py-4 px-1 border-b-2 font-medium text-sm ${
                  activeTab === tab.id
                    ? 'border-blue-500 text-blue-600'
                    : 'border-transparent text-gray-500 hover:text-gray-700 hover:border-gray-300'
                }`}
              >
                <span className="mr-2">{tab.icon}</span>
                {tab.name}
              </button>
            ))}
          </nav>
        </div>

        {/* Tab Content */}
        <div className="p-6">
          {activeTab === 'application' && renderApplicationSettings()}
          {activeTab === 'database' && renderDatabaseSettings()}
          {activeTab === 'system' && renderSystemTab()}
          {/* Add other tab renderers here */}
        </div>
      </div>
    </div>
  );
};

export default Settings;

