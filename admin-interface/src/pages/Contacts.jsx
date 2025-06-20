import React, { useState, useEffect } from 'react';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { Badge } from '@/components/ui/badge';
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from '@/components/ui/select';
import { Dialog, DialogContent, DialogHeader, DialogTitle, DialogTrigger } from '@/components/ui/dialog';
import { Table, TableBody, TableCell, TableHead, TableHeader, TableRow } from '@/components/ui/table';
import { MessageSquare, Mail, Calendar, Eye, CheckCircle, Clock, Archive } from 'lucide-react';
import { useApi } from '../contexts/ApiContext';
import { useToast } from '@/hooks/use-toast';

const Contacts = () => {
  const [contacts, setContacts] = useState([]);
  const [loading, setLoading] = useState(true);
  const [selectedContact, setSelectedContact] = useState(null);
  const [dialogOpen, setDialogOpen] = useState(false);
  const [statusFilter, setStatusFilter] = useState('all');

  const { getContacts, updateContactStatus } = useApi();
  const { toast } = useToast();

  useEffect(() => {
    fetchContacts();
  }, [statusFilter]);

  const fetchContacts = async () => {
    try {
      const params = statusFilter !== 'all' ? { status: statusFilter } : {};
      const data = await getContacts(params);
      setContacts(data.contacts || []);
    } catch (error) {
      toast({
        title: "Erreur",
        description: "Impossible de charger les contacts",
        variant: "destructive"
      });
    } finally {
      setLoading(false);
    }
  };

  const handleStatusChange = async (contactId, newStatus) => {
    try {
      await updateContactStatus(contactId, newStatus);
      toast({
        title: "Succès",
        description: "Statut mis à jour avec succès"
      });
      fetchContacts();
    } catch (error) {
      toast({
        title: "Erreur",
        description: "Impossible de mettre à jour le statut",
        variant: "destructive"
      });
    }
  };

  const handleViewContact = (contact) => {
    setSelectedContact(contact);
    setDialogOpen(true);
    
    // Mark as read if it's new
    if (contact.status === 'new') {
      handleStatusChange(contact.id, 'read');
    }
  };

  const getStatusBadge = (status) => {
    const variants = {
      new: { variant: "destructive", icon: MessageSquare, label: "Nouveau" },
      read: { variant: "secondary", icon: Eye, label: "Lu" },
      replied: { variant: "default", icon: CheckCircle, label: "Répondu" },
      archived: { variant: "outline", icon: Archive, label: "Archivé" }
    };

    const config = variants[status] || variants.new;
    const Icon = config.icon;

    return (
      <Badge variant={config.variant} className="flex items-center gap-1">
        <Icon className="w-3 h-3" />
        {config.label}
      </Badge>
    );
  };

  const formatDate = (dateString) => {
    return new Date(dateString).toLocaleDateString('fr-FR', {
      year: 'numeric',
      month: 'short',
      day: 'numeric',
      hour: '2-digit',
      minute: '2-digit'
    });
  };

  if (loading) {
    return (
      <div className="flex items-center justify-center h-64">
        <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-blue-600"></div>
      </div>
    );
  }

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-3xl font-bold text-gray-900">Gestion des Contacts</h1>
          <p className="text-gray-600">Messages reçus via le formulaire de contact</p>
        </div>
        <div className="flex items-center space-x-4">
          <Select value={statusFilter} onValueChange={setStatusFilter}>
            <SelectTrigger className="w-48">
              <SelectValue />
            </SelectTrigger>
            <SelectContent>
              <SelectItem value="all">Tous les statuts</SelectItem>
              <SelectItem value="new">Nouveaux</SelectItem>
              <SelectItem value="read">Lus</SelectItem>
              <SelectItem value="replied">Répondus</SelectItem>
              <SelectItem value="archived">Archivés</SelectItem>
            </SelectContent>
          </Select>
        </div>
      </div>

      {/* Stats Cards */}
      <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
        {[
          { label: 'Total', count: contacts.length, icon: MessageSquare, color: 'text-blue-600' },
          { label: 'Nouveaux', count: contacts.filter(c => c.status === 'new').length, icon: MessageSquare, color: 'text-red-600' },
          { label: 'Lus', count: contacts.filter(c => c.status === 'read').length, icon: Eye, color: 'text-yellow-600' },
          { label: 'Répondus', count: contacts.filter(c => c.status === 'replied').length, icon: CheckCircle, color: 'text-green-600' }
        ].map((stat, index) => (
          <Card key={index}>
            <CardContent className="p-4">
              <div className="flex items-center justify-between">
                <div>
                  <p className="text-sm font-medium text-gray-600">{stat.label}</p>
                  <p className="text-2xl font-bold">{stat.count}</p>
                </div>
                <stat.icon className={`w-8 h-8 ${stat.color}`} />
              </div>
            </CardContent>
          </Card>
        ))}
      </div>

      {/* Contacts Table */}
      <Card>
        <CardHeader>
          <CardTitle className="flex items-center">
            <MessageSquare className="w-5 h-5 mr-2" />
            Messages de contact ({contacts.length})
          </CardTitle>
        </CardHeader>
        <CardContent>
          <Table>
            <TableHeader>
              <TableRow>
                <TableHead>Contact</TableHead>
                <TableHead>Sujet</TableHead>
                <TableHead>Date</TableHead>
                <TableHead>Statut</TableHead>
                <TableHead>Actions</TableHead>
              </TableRow>
            </TableHeader>
            <TableBody>
              {contacts.map((contact) => (
                <TableRow key={contact.id} className={contact.status === 'new' ? 'bg-blue-50' : ''}>
                  <TableCell>
                    <div>
                      <div className="font-medium">{contact.name}</div>
                      <div className="text-sm text-gray-500 flex items-center">
                        <Mail className="w-3 h-3 mr-1" />
                        {contact.email}
                      </div>
                      {contact.company && (
                        <div className="text-sm text-gray-500">{contact.company}</div>
                      )}
                    </div>
                  </TableCell>
                  <TableCell>
                    <div className="max-w-xs">
                      <div className="font-medium">{contact.subject || 'Sans sujet'}</div>
                      <div className="text-sm text-gray-500 truncate">
                        {contact.message}
                      </div>
                    </div>
                  </TableCell>
                  <TableCell>
                    <div className="flex items-center text-sm text-gray-500">
                      <Calendar className="w-3 h-3 mr-1" />
                      {formatDate(contact.created_at)}
                    </div>
                  </TableCell>
                  <TableCell>
                    {getStatusBadge(contact.status)}
                  </TableCell>
                  <TableCell>
                    <div className="flex space-x-2">
                      <Button
                        variant="ghost"
                        size="sm"
                        onClick={() => handleViewContact(contact)}
                      >
                        <Eye className="w-4 h-4" />
                      </Button>
                      <Select
                        value={contact.status}
                        onValueChange={(value) => handleStatusChange(contact.id, value)}
                      >
                        <SelectTrigger className="w-32">
                          <SelectValue />
                        </SelectTrigger>
                        <SelectContent>
                          <SelectItem value="new">Nouveau</SelectItem>
                          <SelectItem value="read">Lu</SelectItem>
                          <SelectItem value="replied">Répondu</SelectItem>
                          <SelectItem value="archived">Archivé</SelectItem>
                        </SelectContent>
                      </Select>
                    </div>
                  </TableCell>
                </TableRow>
              ))}
            </TableBody>
          </Table>
          {contacts.length === 0 && (
            <div className="text-center py-8 text-gray-500">
              Aucun message trouvé pour ce filtre.
            </div>
          )}
        </CardContent>
      </Card>

      {/* Contact Detail Dialog */}
      <Dialog open={dialogOpen} onOpenChange={setDialogOpen}>
        <DialogContent className="max-w-2xl">
          <DialogHeader>
            <DialogTitle>Détails du message</DialogTitle>
          </DialogHeader>
          {selectedContact && (
            <div className="space-y-4">
              <div className="grid grid-cols-2 gap-4">
                <div>
                  <h4 className="font-medium text-gray-900">Nom</h4>
                  <p className="text-gray-600">{selectedContact.name}</p>
                </div>
                <div>
                  <h4 className="font-medium text-gray-900">Email</h4>
                  <p className="text-gray-600">{selectedContact.email}</p>
                </div>
              </div>

              {selectedContact.company && (
                <div>
                  <h4 className="font-medium text-gray-900">Entreprise</h4>
                  <p className="text-gray-600">{selectedContact.company}</p>
                </div>
              )}

              <div>
                <h4 className="font-medium text-gray-900">Sujet</h4>
                <p className="text-gray-600">{selectedContact.subject || 'Sans sujet'}</p>
              </div>

              <div>
                <h4 className="font-medium text-gray-900">Message</h4>
                <div className="bg-gray-50 p-4 rounded-lg">
                  <p className="text-gray-700 whitespace-pre-wrap">{selectedContact.message}</p>
                </div>
              </div>

              <div className="grid grid-cols-2 gap-4 text-sm text-gray-500">
                <div>
                  <h4 className="font-medium text-gray-900">Date de réception</h4>
                  <p>{formatDate(selectedContact.created_at)}</p>
                </div>
                <div>
                  <h4 className="font-medium text-gray-900">Statut</h4>
                  <div className="mt-1">
                    {getStatusBadge(selectedContact.status)}
                  </div>
                </div>
              </div>

              <div className="flex justify-end space-x-2 pt-4 border-t">
                <Button
                  variant="outline"
                  onClick={() => setDialogOpen(false)}
                >
                  Fermer
                </Button>
                <Button
                  onClick={() => {
                    window.location.href = `mailto:${selectedContact.email}?subject=Re: ${selectedContact.subject || 'Votre message'}`;
                    handleStatusChange(selectedContact.id, 'replied');
                  }}
                >
                  <Mail className="w-4 h-4 mr-2" />
                  Répondre
                </Button>
              </div>
            </div>
          )}
        </DialogContent>
      </Dialog>
    </div>
  );
};

export default Contacts;

