import React, { useState, useEffect } from 'react';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { Badge } from '@/components/ui/badge';
import { Input } from '@/components/ui/input';
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from '@/components/ui/select';
import { Tabs, TabsContent, TabsList, TabsTrigger } from '@/components/ui/tabs';
import {
  Table,
  TableBody,
  TableCell,
  TableHead,
  TableHeader,
  TableRow,
} from '@/components/ui/table';
import {
  Search,
  Filter,
  Download,
  RefreshCw,
  AlertTriangle,
  Info,
  CheckCircle,
  XCircle,
  Clock,
  Server,
  Database,
  Globe,
  User,
  Calendar,
  Eye,
  EyeOff
} from 'lucide-react';
import { useApi } from '../contexts/ApiContext';
import { useToast } from '@/hooks/use-toast';

const Logs = () => {
  const [logs, setLogs] = useState([]);
  const [filteredLogs, setFilteredLogs] = useState([]);
  const [loading, setLoading] = useState(true);
  const [searchTerm, setSearchTerm] = useState('');
  const [selectedService, setSelectedService] = useState('all');
  const [selectedLevel, setSelectedLevel] = useState('all');
  const [selectedTimeRange, setSelectedTimeRange] = useState('24h');
  const [autoRefresh, setAutoRefresh] = useState(false);
  const [expandedRows, setExpandedRows] = useState(new Set());

  const { getLogs, getLogStats } = useApi();
  const { toast } = useToast();

  useEffect(() => {
    fetchLogs();
    
    let interval;
    if (autoRefresh) {
      interval = setInterval(fetchLogs, 10000); // Refresh every 10 seconds
    }
    
    return () => {
      if (interval) clearInterval(interval);
    };
  }, [autoRefresh, selectedTimeRange]);

  useEffect(() => {
    filterLogs();
  }, [logs, searchTerm, selectedService, selectedLevel]);

  const fetchLogs = async () => {
    try {
      setLoading(true);
      const data = await getLogs({
        timeRange: selectedTimeRange,
        service: selectedService !== 'all' ? selectedService : undefined,
        level: selectedLevel !== 'all' ? selectedLevel : undefined
      });
      setLogs(data.logs || []);
    } catch (error) {
      console.error('Failed to fetch logs:', error);
      toast({
        title: "Erreur",
        description: "Impossible de charger les logs",
        variant: "destructive"
      });
    } finally {
      setLoading(false);
    }
  };

  const filterLogs = () => {
    let filtered = [...logs];

    // Search filter
    if (searchTerm) {
      filtered = filtered.filter(log => 
        log.message.toLowerCase().includes(searchTerm.toLowerCase()) ||
        log.service.toLowerCase().includes(searchTerm.toLowerCase()) ||
        log.user_id?.toLowerCase().includes(searchTerm.toLowerCase())
      );
    }

    // Service filter
    if (selectedService !== 'all') {
      filtered = filtered.filter(log => log.service === selectedService);
    }

    // Level filter
    if (selectedLevel !== 'all') {
      filtered = filtered.filter(log => log.level === selectedLevel);
    }

    setFilteredLogs(filtered);
  };

  const exportLogs = async () => {
    try {
      const data = await getLogs({
        timeRange: selectedTimeRange,
        service: selectedService !== 'all' ? selectedService : undefined,
        level: selectedLevel !== 'all' ? selectedLevel : undefined,
        export: true
      });
      
      const blob = new Blob([data.csv], { type: 'text/csv' });
      const url = window.URL.createObjectURL(blob);
      const a = document.createElement('a');
      a.href = url;
      a.download = `logs-${new Date().toISOString().split('T')[0]}.csv`;
      document.body.appendChild(a);
      a.click();
      document.body.removeChild(a);
      window.URL.revokeObjectURL(url);
      
      toast({
        title: "Succès",
        description: "Logs exportés avec succès"
      });
    } catch (error) {
      toast({
        title: "Erreur",
        description: "Impossible d'exporter les logs",
        variant: "destructive"
      });
    }
  };

  const toggleRowExpansion = (logId) => {
    const newExpanded = new Set(expandedRows);
    if (newExpanded.has(logId)) {
      newExpanded.delete(logId);
    } else {
      newExpanded.add(logId);
    }
    setExpandedRows(newExpanded);
  };

  const getLevelIcon = (level) => {
    switch (level.toLowerCase()) {
      case 'error':
        return <XCircle className="w-4 h-4 text-red-500" />;
      case 'warning':
        return <AlertTriangle className="w-4 h-4 text-yellow-500" />;
      case 'info':
        return <Info className="w-4 h-4 text-blue-500" />;
      case 'success':
        return <CheckCircle className="w-4 h-4 text-green-500" />;
      default:
        return <Info className="w-4 h-4 text-gray-500" />;
    }
  };

  const getLevelBadge = (level) => {
    const variants = {
      error: 'destructive',
      warning: 'secondary',
      info: 'default',
      success: 'default',
      debug: 'outline'
    };
    
    return (
      <Badge variant={variants[level.toLowerCase()] || 'outline'} className="flex items-center gap-1">
        {getLevelIcon(level)}
        {level.toUpperCase()}
      </Badge>
    );
  };

  const getServiceIcon = (service) => {
    switch (service.toLowerCase()) {
      case 'frontend':
        return <Globe className="w-4 h-4" />;
      case 'backend':
      case 'api':
        return <Server className="w-4 h-4" />;
      case 'database':
        return <Database className="w-4 h-4" />;
      default:
        return <Server className="w-4 h-4" />;
    }
  };

  const formatTimestamp = (timestamp) => {
    return new Date(timestamp).toLocaleString('fr-FR', {
      year: 'numeric',
      month: '2-digit',
      day: '2-digit',
      hour: '2-digit',
      minute: '2-digit',
      second: '2-digit'
    });
  };

  const mockLogs = [
    {
      id: 1,
      timestamp: new Date().toISOString(),
      level: 'info',
      service: 'frontend',
      message: 'User logged in successfully',
      user_id: 'user123',
      ip_address: '192.168.1.100',
      request_id: 'req_abc123',
      details: {
        user_agent: 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36',
        session_id: 'sess_xyz789',
        action: 'login'
      }
    },
    {
      id: 2,
      timestamp: new Date(Date.now() - 300000).toISOString(),
      level: 'error',
      service: 'backend',
      message: 'Database connection failed',
      user_id: null,
      ip_address: '10.0.1.5',
      request_id: 'req_def456',
      details: {
        error_code: 'DB_CONNECTION_TIMEOUT',
        retry_count: 3,
        database: 'postgresql'
      }
    },
    {
      id: 3,
      timestamp: new Date(Date.now() - 600000).toISOString(),
      level: 'warning',
      service: 'api',
      message: 'High memory usage detected',
      user_id: null,
      ip_address: '10.0.1.10',
      request_id: 'req_ghi789',
      details: {
        memory_usage: '85%',
        threshold: '80%',
        process: 'api-worker'
      }
    }
  ];

  // Use mock data if no real logs
  const displayLogs = filteredLogs.length > 0 ? filteredLogs : mockLogs;

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-3xl font-bold text-gray-900">Logs & Traces</h1>
          <p className="text-gray-600">Surveillance et analyse des logs système</p>
        </div>
        <div className="flex space-x-2">
          <Button
            onClick={() => setAutoRefresh(!autoRefresh)}
            variant={autoRefresh ? "default" : "outline"}
            size="sm"
          >
            <RefreshCw className={`w-4 h-4 mr-2 ${autoRefresh ? 'animate-spin' : ''}`} />
            Auto-refresh
          </Button>
          <Button onClick={exportLogs} variant="outline" size="sm">
            <Download className="w-4 h-4 mr-2" />
            Exporter
          </Button>
          <Button onClick={fetchLogs} variant="outline" size="sm">
            <RefreshCw className="w-4 h-4 mr-2" />
            Actualiser
          </Button>
        </div>
      </div>

      {/* Filters */}
      <Card>
        <CardHeader>
          <CardTitle className="flex items-center">
            <Filter className="w-5 h-5 mr-2" />
            Filtres
          </CardTitle>
        </CardHeader>
        <CardContent>
          <div className="grid grid-cols-1 md:grid-cols-5 gap-4">
            <div className="relative">
              <Search className="absolute left-3 top-1/2 transform -translate-y-1/2 text-gray-400 w-4 h-4" />
              <Input
                placeholder="Rechercher dans les logs..."
                value={searchTerm}
                onChange={(e) => setSearchTerm(e.target.value)}
                className="pl-10"
              />
            </div>
            
            <Select value={selectedService} onValueChange={setSelectedService}>
              <SelectTrigger>
                <SelectValue placeholder="Service" />
              </SelectTrigger>
              <SelectContent>
                <SelectItem value="all">Tous les services</SelectItem>
                <SelectItem value="frontend">Frontend</SelectItem>
                <SelectItem value="backend">Backend</SelectItem>
                <SelectItem value="api">API</SelectItem>
                <SelectItem value="database">Base de données</SelectItem>
                <SelectItem value="nginx">Nginx</SelectItem>
              </SelectContent>
            </Select>

            <Select value={selectedLevel} onValueChange={setSelectedLevel}>
              <SelectTrigger>
                <SelectValue placeholder="Niveau" />
              </SelectTrigger>
              <SelectContent>
                <SelectItem value="all">Tous les niveaux</SelectItem>
                <SelectItem value="error">Erreur</SelectItem>
                <SelectItem value="warning">Avertissement</SelectItem>
                <SelectItem value="info">Information</SelectItem>
                <SelectItem value="debug">Debug</SelectItem>
              </SelectContent>
            </Select>

            <Select value={selectedTimeRange} onValueChange={setSelectedTimeRange}>
              <SelectTrigger>
                <SelectValue placeholder="Période" />
              </SelectTrigger>
              <SelectContent>
                <SelectItem value="1h">Dernière heure</SelectItem>
                <SelectItem value="24h">Dernières 24h</SelectItem>
                <SelectItem value="7d">7 derniers jours</SelectItem>
                <SelectItem value="30d">30 derniers jours</SelectItem>
              </SelectContent>
            </Select>

            <div className="flex items-center space-x-2">
              <span className="text-sm text-gray-600">
                {displayLogs.length} entrée(s)
              </span>
            </div>
          </div>
        </CardContent>
      </Card>

      {/* Logs Table */}
      <Card>
        <CardHeader>
          <CardTitle className="flex items-center justify-between">
            <span className="flex items-center">
              <Clock className="w-5 h-5 mr-2" />
              Logs en temps réel
            </span>
            {autoRefresh && (
              <Badge variant="default" className="animate-pulse">
                <RefreshCw className="w-3 h-3 mr-1" />
                Live
              </Badge>
            )}
          </CardTitle>
        </CardHeader>
        <CardContent>
          {loading ? (
            <div className="flex items-center justify-center h-32">
              <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-blue-600"></div>
            </div>
          ) : (
            <div className="overflow-x-auto">
              <Table>
                <TableHeader>
                  <TableRow>
                    <TableHead className="w-[50px]"></TableHead>
                    <TableHead>Timestamp</TableHead>
                    <TableHead>Niveau</TableHead>
                    <TableHead>Service</TableHead>
                    <TableHead>Message</TableHead>
                    <TableHead>Utilisateur</TableHead>
                    <TableHead>IP</TableHead>
                    <TableHead>Request ID</TableHead>
                  </TableRow>
                </TableHeader>
                <TableBody>
                  {displayLogs.map((log) => (
                    <React.Fragment key={log.id}>
                      <TableRow className="cursor-pointer hover:bg-gray-50">
                        <TableCell>
                          <Button
                            variant="ghost"
                            size="sm"
                            onClick={() => toggleRowExpansion(log.id)}
                          >
                            {expandedRows.has(log.id) ? (
                              <EyeOff className="w-4 h-4" />
                            ) : (
                              <Eye className="w-4 h-4" />
                            )}
                          </Button>
                        </TableCell>
                        <TableCell className="font-mono text-sm">
                          {formatTimestamp(log.timestamp)}
                        </TableCell>
                        <TableCell>
                          {getLevelBadge(log.level)}
                        </TableCell>
                        <TableCell>
                          <div className="flex items-center space-x-2">
                            {getServiceIcon(log.service)}
                            <span className="capitalize">{log.service}</span>
                          </div>
                        </TableCell>
                        <TableCell className="max-w-md truncate">
                          {log.message}
                        </TableCell>
                        <TableCell>
                          {log.user_id ? (
                            <div className="flex items-center space-x-1">
                              <User className="w-3 h-3" />
                              <span className="text-sm">{log.user_id}</span>
                            </div>
                          ) : (
                            <span className="text-gray-400">-</span>
                          )}
                        </TableCell>
                        <TableCell className="font-mono text-sm">
                          {log.ip_address}
                        </TableCell>
                        <TableCell className="font-mono text-xs">
                          {log.request_id}
                        </TableCell>
                      </TableRow>
                      
                      {expandedRows.has(log.id) && (
                        <TableRow>
                          <TableCell colSpan={8} className="bg-gray-50">
                            <div className="p-4 space-y-3">
                              <h4 className="font-medium text-gray-900">Détails du log</h4>
                              <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                                <div>
                                  <h5 className="text-sm font-medium text-gray-700 mb-2">Informations générales</h5>
                                  <div className="space-y-1 text-sm">
                                    <div><strong>ID:</strong> {log.id}</div>
                                    <div><strong>Timestamp:</strong> {log.timestamp}</div>
                                    <div><strong>Service:</strong> {log.service}</div>
                                    <div><strong>Niveau:</strong> {log.level}</div>
                                  </div>
                                </div>
                                <div>
                                  <h5 className="text-sm font-medium text-gray-700 mb-2">Contexte</h5>
                                  <div className="space-y-1 text-sm">
                                    <div><strong>IP:</strong> {log.ip_address}</div>
                                    <div><strong>Request ID:</strong> {log.request_id}</div>
                                    {log.user_id && <div><strong>Utilisateur:</strong> {log.user_id}</div>}
                                  </div>
                                </div>
                              </div>
                              
                              <div>
                                <h5 className="text-sm font-medium text-gray-700 mb-2">Message complet</h5>
                                <div className="bg-white p-3 rounded border font-mono text-sm">
                                  {log.message}
                                </div>
                              </div>
                              
                              {log.details && (
                                <div>
                                  <h5 className="text-sm font-medium text-gray-700 mb-2">Détails techniques</h5>
                                  <div className="bg-white p-3 rounded border">
                                    <pre className="text-xs text-gray-600 whitespace-pre-wrap">
                                      {JSON.stringify(log.details, null, 2)}
                                    </pre>
                                  </div>
                                </div>
                              )}
                            </div>
                          </TableCell>
                        </TableRow>
                      )}
                    </React.Fragment>
                  ))}
                </TableBody>
              </Table>
            </div>
          )}
        </CardContent>
      </Card>

      {/* Log Statistics */}
      <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
        <Card>
          <CardContent className="p-6">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-sm font-medium text-gray-600">Total Logs</p>
                <p className="text-2xl font-bold text-gray-900">{displayLogs.length}</p>
              </div>
              <Clock className="w-8 h-8 text-blue-600" />
            </div>
          </CardContent>
        </Card>

        <Card>
          <CardContent className="p-6">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-sm font-medium text-gray-600">Erreurs</p>
                <p className="text-2xl font-bold text-red-600">
                  {displayLogs.filter(log => log.level === 'error').length}
                </p>
              </div>
              <XCircle className="w-8 h-8 text-red-600" />
            </div>
          </CardContent>
        </Card>

        <Card>
          <CardContent className="p-6">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-sm font-medium text-gray-600">Avertissements</p>
                <p className="text-2xl font-bold text-yellow-600">
                  {displayLogs.filter(log => log.level === 'warning').length}
                </p>
              </div>
              <AlertTriangle className="w-8 h-8 text-yellow-600" />
            </div>
          </CardContent>
        </Card>

        <Card>
          <CardContent className="p-6">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-sm font-medium text-gray-600">Services Actifs</p>
                <p className="text-2xl font-bold text-green-600">
                  {new Set(displayLogs.map(log => log.service)).size}
                </p>
              </div>
              <Server className="w-8 h-8 text-green-600" />
            </div>
          </CardContent>
        </Card>
      </div>
    </div>
  );
};

export default Logs;

