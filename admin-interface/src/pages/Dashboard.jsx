import React, { useState, useEffect } from 'react';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { Badge } from '@/components/ui/badge';
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
  Activity,
  Users,
  FolderOpen,
  Store,
  MessageSquare,
  TrendingUp,
  Server,
  Database,
  Wifi
} from 'lucide-react';
import { useApi } from '../contexts/ApiContext';

const Dashboard = () => {
  const [dashboardData, setDashboardData] = useState(null);
  const [loading, setLoading] = useState(true);
  const { getDashboard } = useApi();

  useEffect(() => {
    const fetchDashboard = async () => {
      try {
        const data = await getDashboard();
        setDashboardData(data.dashboard);
      } catch (error) {
        console.error('Failed to fetch dashboard:', error);
      } finally {
        setLoading(false);
      }
    };

    fetchDashboard();
  }, [getDashboard]);

  if (loading) {
    return (
      <div className="flex items-center justify-center h-64">
        <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-blue-600"></div>
      </div>
    );
  }

  const stats = dashboardData?.stats || {};
  
  const statsCards = [
    {
      title: 'Projets Total',
      value: stats.total_projects || 0,
      icon: FolderOpen,
      color: 'text-blue-600',
      bgColor: 'bg-blue-50'
    },
    {
      title: 'Projets En Ligne',
      value: stats.online_projects || 0,
      icon: Activity,
      color: 'text-green-600',
      bgColor: 'bg-green-50'
    },
    {
      title: 'Articles Store',
      value: stats.total_store_items || 0,
      icon: Store,
      color: 'text-purple-600',
      bgColor: 'bg-purple-50'
    },
    {
      title: 'Messages',
      value: stats.total_contacts || 0,
      icon: MessageSquare,
      color: 'text-orange-600',
      bgColor: 'bg-orange-50'
    }
  ];

  const recentProjects = dashboardData?.recent_projects || [];
  const recentContacts = dashboardData?.recent_contacts || [];

  // Mock data for charts
  const projectStatusData = [
    { name: 'En ligne', value: stats.online_projects || 0, color: '#10B981' },
    { name: 'Maintenance', value: (stats.total_projects - stats.online_projects) || 0, color: '#F59E0B' },
    { name: 'Hors ligne', value: 1, color: '#EF4444' }
  ];

  const activityData = [
    { name: 'Lun', visits: 120, contacts: 5 },
    { name: 'Mar', visits: 150, contacts: 8 },
    { name: 'Mer', visits: 180, contacts: 12 },
    { name: 'Jeu', visits: 200, contacts: 15 },
    { name: 'Ven', visits: 250, contacts: 10 },
    { name: 'Sam', visits: 180, contacts: 6 },
    { name: 'Dim', visits: 160, contacts: 4 }
  ];

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-3xl font-bold text-gray-900">Tableau de bord</h1>
          <p className="text-gray-600">Vue d'ensemble de votre startup</p>
        </div>
        <div className="flex items-center space-x-2">
          <div className="flex items-center space-x-1">
            <Wifi className="w-4 h-4 text-green-500" />
            <span className="text-sm text-gray-600">Tailscale connecté</span>
          </div>
        </div>
      </div>

      {/* Stats Cards */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
        {statsCards.map((stat, index) => (
          <Card key={index} className="hover:shadow-lg transition-shadow">
            <CardContent className="p-6">
              <div className="flex items-center justify-between">
                <div>
                  <p className="text-sm font-medium text-gray-600">{stat.title}</p>
                  <p className="text-3xl font-bold text-gray-900">{stat.value}</p>
                </div>
                <div className={`p-3 rounded-full ${stat.bgColor}`}>
                  <stat.icon className={`w-6 h-6 ${stat.color}`} />
                </div>
              </div>
            </CardContent>
          </Card>
        ))}
      </div>

      {/* Charts Row */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        {/* Activity Chart */}
        <Card>
          <CardHeader>
            <CardTitle className="flex items-center">
              <TrendingUp className="w-5 h-5 mr-2" />
              Activité de la semaine
            </CardTitle>
          </CardHeader>
          <CardContent>
            <ResponsiveContainer width="100%" height={300}>
              <LineChart data={activityData}>
                <CartesianGrid strokeDasharray="3 3" />
                <XAxis dataKey="name" />
                <YAxis />
                <Tooltip />
                <Line type="monotone" dataKey="visits" stroke="#3B82F6" strokeWidth={2} />
                <Line type="monotone" dataKey="contacts" stroke="#10B981" strokeWidth={2} />
              </LineChart>
            </ResponsiveContainer>
          </CardContent>
        </Card>

        {/* Project Status Chart */}
        <Card>
          <CardHeader>
            <CardTitle className="flex items-center">
              <Activity className="w-5 h-5 mr-2" />
              Statut des projets
            </CardTitle>
          </CardHeader>
          <CardContent>
            <ResponsiveContainer width="100%" height={300}>
              <PieChart>
                <Pie
                  data={projectStatusData}
                  cx="50%"
                  cy="50%"
                  outerRadius={80}
                  fill="#8884d8"
                  dataKey="value"
                  label={({ name, value }) => `${name}: ${value}`}
                >
                  {projectStatusData.map((entry, index) => (
                    <Cell key={`cell-${index}`} fill={entry.color} />
                  ))}
                </Pie>
                <Tooltip />
              </PieChart>
            </ResponsiveContainer>
          </CardContent>
        </Card>
      </div>

      {/* Recent Activity */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        {/* Recent Projects */}
        <Card>
          <CardHeader>
            <CardTitle>Projets récents</CardTitle>
          </CardHeader>
          <CardContent>
            <div className="space-y-4">
              {recentProjects.length > 0 ? (
                recentProjects.map((project) => (
                  <div key={project.id} className="flex items-center justify-between p-3 bg-gray-50 rounded-lg">
                    <div>
                      <h4 className="font-medium">{project.name}</h4>
                      <p className="text-sm text-gray-600">{project.description}</p>
                    </div>
                    <Badge variant={project.status === 'online' ? 'default' : 'secondary'}>
                      {project.status}
                    </Badge>
                  </div>
                ))
              ) : (
                <p className="text-gray-500 text-center py-4">Aucun projet récent</p>
              )}
            </div>
          </CardContent>
        </Card>

        {/* Recent Contacts */}
        <Card>
          <CardHeader>
            <CardTitle>Messages récents</CardTitle>
          </CardHeader>
          <CardContent>
            <div className="space-y-4">
              {recentContacts.length > 0 ? (
                recentContacts.map((contact) => (
                  <div key={contact.id} className="flex items-center justify-between p-3 bg-gray-50 rounded-lg">
                    <div>
                      <h4 className="font-medium">{contact.name}</h4>
                      <p className="text-sm text-gray-600">{contact.email}</p>
                      <p className="text-xs text-gray-500">{contact.subject}</p>
                    </div>
                    <Badge variant={contact.status === 'new' ? 'destructive' : 'secondary'}>
                      {contact.status}
                    </Badge>
                  </div>
                ))
              ) : (
                <p className="text-gray-500 text-center py-4">Aucun message récent</p>
              )}
            </div>
          </CardContent>
        </Card>
      </div>

      {/* System Status */}
      <Card>
        <CardHeader>
          <CardTitle className="flex items-center">
            <Server className="w-5 h-5 mr-2" />
            État du système
          </CardTitle>
        </CardHeader>
        <CardContent>
          <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
            <div className="flex items-center space-x-3">
              <div className="w-3 h-3 bg-green-500 rounded-full"></div>
              <span className="text-sm">API Backend</span>
              <Badge variant="outline" className="text-green-600">En ligne</Badge>
            </div>
            <div className="flex items-center space-x-3">
              <div className="w-3 h-3 bg-green-500 rounded-full"></div>
              <span className="text-sm">Base de données</span>
              <Badge variant="outline" className="text-green-600">Connectée</Badge>
            </div>
            <div className="flex items-center space-x-3">
              <div className="w-3 h-3 bg-green-500 rounded-full"></div>
              <span className="text-sm">Tailscale VPN</span>
              <Badge variant="outline" className="text-green-600">Actif</Badge>
            </div>
          </div>
        </CardContent>
      </Card>
    </div>
  );
};

export default Dashboard;

