import React, { useState, useEffect } from 'react';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Badge } from '@/components/ui/badge';
import { Button } from '@/components/ui/button';
import { ExternalLink, Activity, AlertCircle, Clock } from 'lucide-react';

const ProjectList = () => {
  const [projects, setProjects] = useState([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    fetchProjects();
  }, []);

  const fetchProjects = async () => {
    try {
      const response = await fetch('/api/projects');
      const data = await response.json();
      
      if (data.success) {
        const fixedProjects = data.projects.map(project => ({
            ...project,
            technologies: typeof project.technologies === 'string'
              ? JSON.parse(project.technologies)
              : project.technologies
          }));

        setProjects(fixedProjects);
      }
    } catch (error) {
      console.error('Failed to fetch projects:', error);
    } finally {
      setLoading(false);
    }
  };

  const getStatusBadge = (status) => {
    const variants = {
      online: { variant: "default", icon: Activity, color: "text-green-600", label: "En ligne" },
      maintenance: { variant: "secondary", icon: Clock, color: "text-yellow-600", label: "Maintenance" },
      offline: { variant: "destructive", icon: AlertCircle, color: "text-red-600", label: "Hors ligne" }
    };

    const config = variants[status] || variants.offline;
    const Icon = config.icon;

    return (
      <Badge variant={config.variant} className="flex items-center gap-1">
        <Icon className="w-3 h-3" />
        {config.label}
      </Badge>
    );
  };

  if (loading) {
    return (
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
        {[...Array(6)].map((_, i) => (
          <Card key={i} className="animate-pulse">
            <CardContent className="p-6">
              <div className="h-4 bg-gray-200 rounded w-3/4 mb-2"></div>
              <div className="h-3 bg-gray-200 rounded w-1/2 mb-4"></div>
              <div className="h-20 bg-gray-200 rounded mb-4"></div>
              <div className="h-8 bg-gray-200 rounded w-1/3"></div>
            </CardContent>
          </Card>
        ))}
      </div>
    );
  }

  return (
    <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
      {projects.map((project) => (
        <Card key={project.id} className="hover:shadow-lg transition-shadow">
          <CardHeader className="pb-3">
            <div className="flex items-start justify-between">
              <div>
                <CardTitle className="text-lg">{project.name}</CardTitle>
                {project.category && (
                  <Badge variant="outline" className="mt-1">
                    {project.category}
                  </Badge>
                )}
              </div>
              {getStatusBadge(project.status)}
            </div>
          </CardHeader>
          <CardContent>
            {project.image_url && (
              <img
                src={project.image_url}
                alt={project.name}
                className="w-full h-32 object-cover rounded-lg mb-4"
              />
            )}
            
            <p className="text-gray-600 text-sm mb-4 line-clamp-3">
              {project.description}
            </p>

            {project.technologies && project.technologies.length > 0 && (
              <div className="flex flex-wrap gap-1 mb-4">
                {project.technologies.slice(0, 3).map((tech, index) => (
                  <Badge key={index} variant="secondary" className="text-xs">
                    {tech}
                  </Badge>
                ))}
                {project.technologies.length > 3 && (
                  <Badge variant="secondary" className="text-xs">
                    +{project.technologies.length - 3}
                  </Badge>
                )}
              </div>
            )}

            {project.url && (
              <Button
                variant="outline"
                size="sm"
                className="w-full"
                asChild
              >
                <a
                  href={project.url}
                  target="_blank"
                  rel="noopener noreferrer"
                  className="flex items-center justify-center"
                >
                  <ExternalLink className="w-4 h-4 mr-2" />
                  Voir le projet
                </a>
              </Button>
            )}
          </CardContent>
        </Card>
      ))}

      {projects.length === 0 && !loading && (
        <div className="col-span-full text-center py-12">
          <div className="text-gray-500">
            <Activity className="w-12 h-12 mx-auto mb-4 opacity-50" />
            <h3 className="text-lg font-medium mb-2">Aucun projet disponible</h3>
            <p>Les projets seront bientôt disponibles.</p>
          </div>
        </div>
      )}
    </div>
  );
};

export default ProjectList;

