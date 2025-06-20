import React, { useState, useEffect } from 'react';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { Badge } from '@/components/ui/badge';
import { Progress } from '@/components/ui/progress';
import {
  BarChart,
  Bar,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  ResponsiveContainer,
  LineChart,
  Line,
  PieChart,
  Pie,
  Cell
} from 'recharts';
import {
  Server,
  Database,
  Cpu,
  MemoryStick,
  HardDrive,
  Wifi,
  Shield,
  Download,
  Activity,
  AlertTriangle,
  CheckCircle
} from 'lucide-react';
import { useApi } from '../contexts/ApiContext';
import { useToast } from '@/hooks/use-toast';

const System = () => {
  const [systemInfo, setSystemInfo] = useState(null);
  const [loading, setLoading] = useState(true);
  const [backupLoading, setBackupLoading] = useState(false);

  const { getSystemInfo, createBackup } = useApi();
  const { toast } = useToast();

  useEffect(() => {
    fetchSystemInfo();
    
    // Refresh system info every 30 seconds
    const interval = setInterval(fetchSystemInfo, 30000);
    return () => clearInterval(interval);
  }, []);

  const fetchSystemInfo = async () => {
    try {
      const data = await getSystemInfo();
      setSystemInfo(data.system_info);
    } catch (error) {
      console.error('Failed to fetch system info:', error);
    } finally {
      setLoading(false);
    }
  };

  const handleBackup = async () => {
    setBackupLoading(true);
    try {
      const result = await createBackup();
      toast({
        title: "Succès",
        description: `Sauvegarde créée: ${result.backup_file}`
      });
    } catch (error) {
      toast({
        title: "Erreur",
        description: "Impossible de créer la sauvegarde",
        variant: "destructive"
      });
    } finally {
      setBackupLoading(false);
    }
  };

  const formatBytes = (bytes) => {
    if (bytes === 0) return '0 Bytes';
    const k = 1024;
    const sizes = ['Bytes', 'KB', 'MB', 'GB', 'TB'];
    const i = Math.floor(Math.log(bytes) / Math.log(k));
    return parseFloat((bytes / Math.pow(k, i)).toFixed(2)) + ' ' + sizes[i];
  };

  const getStatusColor = (percentage) => {
    if (percentage < 60) return 'text-green-600';
    if (percentage < 80) return 'text-yellow-600';
    return 'text-red-600';
  };

  const getStatusBadge = (status, label) => {
    return (
      <Badge variant={status ? "default" : "destructive"} className="flex items-center gap-1">
        {status ? <CheckCircle className="w-3 h-3" /> : <AlertTriangle className="w-3 h-3" />}
        {label}
      </Badge>
    );
  };

  // Mock data for charts
  const performanceData = [
    { time: '00:00', cpu: 45, memory: 62, disk: 78 },
    { time: '04:00', cpu: 32, memory: 58, disk: 78 },
    { time: '08:00', cpu: 67, memory: 71, disk: 79 },
    { time: '12:00', cpu: 89, memory: 85, disk: 80 },
    { time: '16:00', cpu: 76, memory: 79, disk: 81 },
    { time: '20:00', cpu: 54, memory: 68, disk: 82 },
  ];

  const serviceStatusData = [
    { name: 'En ligne', value: 8, color: '#10B981' },
    { name: 'Maintenance', value: 1, color: '#F59E0B' },
    { name: 'Hors ligne', value: 0, color: '#EF4444' }
  ];

  if (loading) {
    return (
      <div className="flex items-center justify-center h-64">
        <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-blue-600"></div>
      </div>
    );
  }

  const cpuPercent = systemInfo?.cpu_percent || 0;
  const memoryPercent = systemInfo?.memory?.percent || 0;
  const diskPercent = systemInfo?.disk?.percent || 0;

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-3xl font-bold text-gray-900">Système & Monitoring</h1>
          <p className="text-gray-600">Surveillance de l'infrastructure et des performances</p>
        </div>
        <div className="flex space-x-2">
          <Button
            onClick={handleBackup}
            disabled={backupLoading}
            variant="outline"
          >
            {backupLoading ? (
              <div className="animate-spin rounded-full h-4 w-4 border-b-2 border-blue-600 mr-2"></div>
            ) : (
              <Download className="w-4 h-4 mr-2" />
            )}
            Créer une sauvegarde
          </Button>
          <Button onClick={fetchSystemInfo} variant="outline">
            <Activity className="w-4 h-4 mr-2" />
            Actualiser
          </Button>
        </div>
      </div>

      {/* System Status Cards */}
      <div className="grid grid-cols-1 md:grid-cols-4 gap-6">
        <Card>
          <CardContent className="p-6">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-sm font-medium text-gray-600">CPU</p>
                <p className={`text-2xl font-bold ${getStatusColor(cpuPercent)}`}>
                  {cpuPercent.toFixed(1)}%
                </p>
              </div>
              <Cpu className="w-8 h-8 text-blue-600" />
            </div>
            <Progress value={cpuPercent} className="mt-2" />
          </CardContent>
        </Card>

        <Card>
          <CardContent className="p-6">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-sm font-medium text-gray-600">Mémoire</p>
                <p className={`text-2xl font-bold ${getStatusColor(memoryPercent)}`}>
                  {memoryPercent.toFixed(1)}%
                </p>
              </div>
              <MemoryStick className="w-8 h-8 text-green-600" />
            </div>
            <Progress value={memoryPercent} className="mt-2" />
            <p className="text-xs text-gray-500 mt-1">
              {formatBytes(systemInfo?.memory?.available || 0)} disponible
            </p>
          </CardContent>
        </Card>

        <Card>
          <CardContent className="p-6">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-sm font-medium text-gray-600">Disque</p>
                <p className={`text-2xl font-bold ${getStatusColor(diskPercent)}`}>
                  {diskPercent.toFixed(1)}%
                </p>
              </div>
              <HardDrive className="w-8 h-8 text-purple-600" />
            </div>
            <Progress value={diskPercent} className="mt-2" />
            <p className="text-xs text-gray-500 mt-1">
              {formatBytes(systemInfo?.disk?.free || 0)} libre
            </p>
          </CardContent>
        </Card>

        <Card>
          <CardContent className="p-6">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-sm font-medium text-gray-600">Uptime</p>
                <p className="text-lg font-bold text-gray-900">24h 15m</p>
              </div>
              <Server className="w-8 h-8 text-orange-600" />
            </div>
            <div className="flex items-center mt-2">
              <div className="w-2 h-2 bg-green-500 rounded-full mr-2"></div>
              <span className="text-sm text-gray-600">Système stable</span>
            </div>
          </CardContent>
        </Card>
      </div>

      {/* Charts Row */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        {/* Performance Chart */}
        <Card>
          <CardHeader>
            <CardTitle className="flex items-center">
              <Activity className="w-5 h-5 mr-2" />
              Performance des dernières 24h
            </CardTitle>
          </CardHeader>
          <CardContent>
            <ResponsiveContainer width="100%" height={300}>
              <LineChart data={performanceData}>
                <CartesianGrid strokeDasharray="3 3" />
                <XAxis dataKey="time" />
                <YAxis />
                <Tooltip />
                <Line type="monotone" dataKey="cpu" stroke="#3B82F6" strokeWidth={2} name="CPU %" />
                <Line type="monotone" dataKey="memory" stroke="#10B981" strokeWidth={2} name="Mémoire %" />
                <Line type="monotone" dataKey="disk" stroke="#8B5CF6" strokeWidth={2} name="Disque %" />
              </LineChart>
            </ResponsiveContainer>
          </CardContent>
        </Card>

        {/* Service Status Chart */}
        <Card>
          <CardHeader>
            <CardTitle className="flex items-center">
              <Server className="w-5 h-5 mr-2" />
              État des services
            </CardTitle>
          </CardHeader>
          <CardContent>
            <ResponsiveContainer width="100%" height={300}>
              <PieChart>
                <Pie
                  data={serviceStatusData}
                  cx="50%"
                  cy="50%"
                  outerRadius={80}
                  fill="#8884d8"
                  dataKey="value"
                  label={({ name, value }) => `${name}: ${value}`}
                >
                  {serviceStatusData.map((entry, index) => (
                    <Cell key={`cell-${index}`} fill={entry.color} />
                  ))}
                </Pie>
                <Tooltip />
              </PieChart>
            </ResponsiveContainer>
          </CardContent>
        </Card>
      </div>

      {/* Services Status */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        {/* Infrastructure Services */}
        <Card>
          <CardHeader>
            <CardTitle className="flex items-center">
              <Database className="w-5 h-5 mr-2" />
              Services d'infrastructure
            </CardTitle>
          </CardHeader>
          <CardContent>
            <div className="space-y-4">
              {[
                { name: 'API Backend', status: true, port: '5000' },
                { name: 'Base de données', status: true, port: '5432' },
                { name: 'Redis Cache', status: true, port: '6379' },
                { name: 'Nginx Proxy', status: true, port: '80/443' }
              ].map((service, index) => (
                <div key={index} className="flex items-center justify-between p-3 bg-gray-50 rounded-lg">
                  <div className="flex items-center space-x-3">
                    <div className={`w-3 h-3 rounded-full ${service.status ? 'bg-green-500' : 'bg-red-500'}`}></div>
                    <div>
                      <h4 className="font-medium">{service.name}</h4>
                      <p className="text-sm text-gray-500">Port {service.port}</p>
                    </div>
                  </div>
                  {getStatusBadge(service.status, service.status ? 'En ligne' : 'Hors ligne')}
                </div>
              ))}
            </div>
          </CardContent>
        </Card>

        {/* Security & Monitoring */}
        <Card>
          <CardHeader>
            <CardTitle className="flex items-center">
              <Shield className="w-5 h-5 mr-2" />
              Sécurité & Monitoring
            </CardTitle>
          </CardHeader>
          <CardContent>
            <div className="space-y-4">
              {[
                { name: 'Tailscale VPN', status: true, description: 'Tunnel sécurisé actif' },
                { name: 'Firewall', status: true, description: 'Règles appliquées' },
                { name: 'SSL/TLS', status: true, description: 'Certificats valides' },
                { name: 'Monitoring', status: true, description: 'Prometheus + Grafana' }
              ].map((item, index) => (
                <div key={index} className="flex items-center justify-between p-3 bg-gray-50 rounded-lg">
                  <div className="flex items-center space-x-3">
                    <div className={`w-3 h-3 rounded-full ${item.status ? 'bg-green-500' : 'bg-red-500'}`}></div>
                    <div>
                      <h4 className="font-medium">{item.name}</h4>
                      <p className="text-sm text-gray-500">{item.description}</p>
                    </div>
                  </div>
                  {getStatusBadge(item.status, item.status ? 'Actif' : 'Inactif')}
                </div>
              ))}
            </div>
          </CardContent>
        </Card>
      </div>

      {/* Network & Connectivity */}
      <Card>
        <CardHeader>
          <CardTitle className="flex items-center">
            <Wifi className="w-5 h-5 mr-2" />
            Réseau & Connectivité
          </CardTitle>
        </CardHeader>
        <CardContent>
          <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
            <div className="text-center p-4 bg-green-50 rounded-lg">
              <div className="w-12 h-12 bg-green-100 rounded-full flex items-center justify-center mx-auto mb-2">
                <Wifi className="w-6 h-6 text-green-600" />
              </div>
              <h3 className="font-medium text-green-900">Tailscale</h3>
              <p className="text-sm text-green-700">100.64.1.42</p>
              <Badge variant="default" className="mt-2">Connecté</Badge>
            </div>
            
            <div className="text-center p-4 bg-blue-50 rounded-lg">
              <div className="w-12 h-12 bg-blue-100 rounded-full flex items-center justify-center mx-auto mb-2">
                <Server className="w-6 h-6 text-blue-600" />
              </div>
              <h3 className="font-medium text-blue-900">Load Balancer</h3>
              <p className="text-sm text-blue-700">34.77.123.45</p>
              <Badge variant="default" className="mt-2">Actif</Badge>
            </div>
            
            <div className="text-center p-4 bg-purple-50 rounded-lg">
              <div className="w-12 h-12 bg-purple-100 rounded-full flex items-center justify-center mx-auto mb-2">
                <Database className="w-6 h-6 text-purple-600" />
              </div>
              <h3 className="font-medium text-purple-900">Base de données</h3>
              <p className="text-sm text-purple-700">10.0.1.10</p>
              <Badge variant="default" className="mt-2">Connectée</Badge>
            </div>
          </div>
        </CardContent>
      </Card>

      {/* Quick Actions */}
      <Card>
        <CardHeader>
          <CardTitle>Actions rapides</CardTitle>
        </CardHeader>
        <CardContent>
          <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
            <Button variant="outline" className="h-auto p-4 flex flex-col items-center">
              <Download className="w-6 h-6 mb-2" />
              <span>Télécharger les logs</span>
            </Button>
            <Button variant="outline" className="h-auto p-4 flex flex-col items-center">
              <Activity className="w-6 h-6 mb-2" />
              <span>Redémarrer services</span>
            </Button>
            <Button variant="outline" className="h-auto p-4 flex flex-col items-center">
              <Shield className="w-6 h-6 mb-2" />
              <span>Audit sécurité</span>
            </Button>
            <Button variant="outline" className="h-auto p-4 flex flex-col items-center">
              <Server className="w-6 h-6 mb-2" />
              <span>Maintenance</span>
            </Button>
          </div>
        </CardContent>
      </Card>
    </div>
  );
};

export default System;

