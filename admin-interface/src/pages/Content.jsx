import React, { useState, useEffect } from 'react';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import { Label } from '@/components/ui/label';
import { Textarea } from '@/components/ui/textarea';
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from '@/components/ui/select';
import { Dialog, DialogContent, DialogHeader, DialogTitle, DialogTrigger } from '@/components/ui/dialog';
import { Table, TableBody, TableCell, TableHead, TableHeader, TableRow } from '@/components/ui/table';
import { Tabs, TabsContent, TabsList, TabsTrigger } from '@/components/ui/tabs';
import { Plus, Edit, Trash2, FileText, Home, FolderOpen, Store as StoreIcon } from 'lucide-react';
import { useApi } from '../contexts/ApiContext';
import { useToast } from '@/hooks/use-toast';

const Content = () => {
  const [contentBlocks, setContentBlocks] = useState([]);
  const [loading, setLoading] = useState(true);
  const [dialogOpen, setDialogOpen] = useState(false);
  const [editingBlock, setEditingBlock] = useState(null);
  const [selectedPage, setSelectedPage] = useState('home');
  const [formData, setFormData] = useState({
    page: 'home',
    section: '',
    key: '',
    value: '',
    content_type: 'text',
    order_index: 0,
    active: true
  });

  const { getContent, createContentBlock, updateContentBlock, deleteContentBlock } = useApi();
  const { toast } = useToast();

  const pages = [
    { id: 'home', name: 'Accueil', icon: Home },
    { id: 'projects', name: 'Projets', icon: FolderOpen },
    { id: 'store', name: 'Store', icon: StoreIcon }
  ];

  useEffect(() => {
    fetchContent();
  }, [selectedPage]);

  const fetchContent = async () => {
    try {
      const data = await getContent(selectedPage);
      // Convert content object to array for table display
      const blocks = [];
      Object.entries(data.content || {}).forEach(([section, sectionContent]) => {
        Object.entries(sectionContent).forEach(([key, contentData]) => {
          blocks.push({
            id: contentData.id,
            page: selectedPage,
            section,
            key,
            value: contentData.value,
            content_type: contentData.type,
            order_index: 0,
            active: true
          });
        });
      });
      setContentBlocks(blocks);
    } catch (error) {
      toast({
        title: "Erreur",
        description: "Impossible de charger le contenu",
        variant: "destructive"
      });
    } finally {
      setLoading(false);
    }
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    try {
      const blockData = {
        ...formData,
        order_index: parseInt(formData.order_index)
      };

      if (editingBlock) {
        await updateContentBlock(editingBlock.id, blockData);
        toast({
          title: "Succès",
          description: "Contenu mis à jour avec succès"
        });
      } else {
        await createContentBlock(blockData);
        toast({
          title: "Succès",
          description: "Contenu créé avec succès"
        });
      }

      setDialogOpen(false);
      setEditingBlock(null);
      resetForm();
      fetchContent();
    } catch (error) {
      toast({
        title: "Erreur",
        description: "Impossible de sauvegarder le contenu",
        variant: "destructive"
      });
    }
  };

  const resetForm = () => {
    setFormData({
      page: selectedPage,
      section: '',
      key: '',
      value: '',
      content_type: 'text',
      order_index: 0,
      active: true
    });
  };

  const handleEdit = (block) => {
    setEditingBlock(block);
    setFormData({
      page: block.page,
      section: block.section,
      key: block.key,
      value: typeof block.value === 'object' ? JSON.stringify(block.value, null, 2) : block.value,
      content_type: block.content_type,
      order_index: block.order_index,
      active: block.active
    });
    setDialogOpen(true);
  };

  const handleDelete = async (id) => {
    if (window.confirm('Êtes-vous sûr de vouloir supprimer ce bloc de contenu ?')) {
      try {
        await deleteContentBlock(id);
        toast({
          title: "Succès",
          description: "Contenu supprimé avec succès"
        });
        fetchContent();
      } catch (error) {
        toast({
          title: "Erreur",
          description: "Impossible de supprimer le contenu",
          variant: "destructive"
        });
      }
    }
  };

  const renderValue = (value, type) => {
    if (type === 'json') {
      return (
        <pre className="text-xs bg-gray-100 p-2 rounded max-w-xs overflow-hidden">
          {JSON.stringify(value, null, 2)}
        </pre>
      );
    }
    
    if (typeof value === 'string' && value.length > 100) {
      return (
        <div className="max-w-xs">
          <p className="truncate">{value}</p>
          <span className="text-xs text-gray-500">({value.length} caractères)</span>
        </div>
      );
    }
    
    return <span className="max-w-xs block truncate">{String(value)}</span>;
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
          <h1 className="text-3xl font-bold text-gray-900">Gestion du Contenu</h1>
          <p className="text-gray-600">Gérez le contenu dynamique de votre site</p>
        </div>
        <Dialog open={dialogOpen} onOpenChange={setDialogOpen}>
          <DialogTrigger asChild>
            <Button onClick={() => {
              setEditingBlock(null);
              resetForm();
            }}>
              <Plus className="w-4 h-4 mr-2" />
              Nouveau Contenu
            </Button>
          </DialogTrigger>
          <DialogContent className="max-w-2xl">
            <DialogHeader>
              <DialogTitle>
                {editingBlock ? 'Modifier le contenu' : 'Nouveau contenu'}
              </DialogTitle>
            </DialogHeader>
            <form onSubmit={handleSubmit} className="space-y-4">
              <div className="grid grid-cols-2 gap-4">
                <div>
                  <Label htmlFor="page">Page</Label>
                  <Select value={formData.page} onValueChange={(value) => setFormData({ ...formData, page: value })}>
                    <SelectTrigger>
                      <SelectValue />
                    </SelectTrigger>
                    <SelectContent>
                      {pages.map((page) => (
                        <SelectItem key={page.id} value={page.id}>
                          {page.name}
                        </SelectItem>
                      ))}
                    </SelectContent>
                  </Select>
                </div>
                <div>
                  <Label htmlFor="section">Section</Label>
                  <Input
                    id="section"
                    value={formData.section}
                    onChange={(e) => setFormData({ ...formData, section: e.target.value })}
                    placeholder="hero, features, testimonials..."
                    required
                  />
                </div>
              </div>

              <div className="grid grid-cols-2 gap-4">
                <div>
                  <Label htmlFor="key">Clé</Label>
                  <Input
                    id="key"
                    value={formData.key}
                    onChange={(e) => setFormData({ ...formData, key: e.target.value })}
                    placeholder="title, description, image_url..."
                    required
                  />
                </div>
                <div>
                  <Label htmlFor="content_type">Type de contenu</Label>
                  <Select value={formData.content_type} onValueChange={(value) => setFormData({ ...formData, content_type: value })}>
                    <SelectTrigger>
                      <SelectValue />
                    </SelectTrigger>
                    <SelectContent>
                      <SelectItem value="text">Texte</SelectItem>
                      <SelectItem value="html">HTML</SelectItem>
                      <SelectItem value="json">JSON</SelectItem>
                      <SelectItem value="url">URL</SelectItem>
                      <SelectItem value="number">Nombre</SelectItem>
                    </SelectContent>
                  </Select>
                </div>
              </div>

              <div>
                <Label htmlFor="value">Valeur</Label>
                <Textarea
                  id="value"
                  value={formData.value}
                  onChange={(e) => setFormData({ ...formData, value: e.target.value })}
                  rows={formData.content_type === 'json' ? 8 : 4}
                  placeholder={
                    formData.content_type === 'json' 
                      ? '{"key": "value", "array": [1, 2, 3]}'
                      : 'Contenu...'
                  }
                  required
                />
              </div>

              <div className="grid grid-cols-2 gap-4">
                <div>
                  <Label htmlFor="order_index">Ordre d'affichage</Label>
                  <Input
                    id="order_index"
                    type="number"
                    value={formData.order_index}
                    onChange={(e) => setFormData({ ...formData, order_index: e.target.value })}
                  />
                </div>
                <div className="flex items-center space-x-2 pt-6">
                  <input
                    type="checkbox"
                    id="active"
                    checked={formData.active}
                    onChange={(e) => setFormData({ ...formData, active: e.target.checked })}
                    className="rounded"
                  />
                  <Label htmlFor="active">Actif</Label>
                </div>
              </div>

              <div className="flex justify-end space-x-2">
                <Button type="button" variant="outline" onClick={() => setDialogOpen(false)}>
                  Annuler
                </Button>
                <Button type="submit">
                  {editingBlock ? 'Mettre à jour' : 'Créer'}
                </Button>
              </div>
            </form>
          </DialogContent>
        </Dialog>
      </div>

      {/* Page Tabs */}
      <Tabs value={selectedPage} onValueChange={setSelectedPage}>
        <TabsList>
          {pages.map((page) => (
            <TabsTrigger key={page.id} value={page.id} className="flex items-center">
              <page.icon className="w-4 h-4 mr-2" />
              {page.name}
            </TabsTrigger>
          ))}
        </TabsList>

        {pages.map((page) => (
          <TabsContent key={page.id} value={page.id}>
            <Card>
              <CardHeader>
                <CardTitle className="flex items-center">
                  <FileText className="w-5 h-5 mr-2" />
                  Contenu de la page {page.name} ({contentBlocks.length})
                </CardTitle>
              </CardHeader>
              <CardContent>
                <Table>
                  <TableHeader>
                    <TableRow>
                      <TableHead>Section</TableHead>
                      <TableHead>Clé</TableHead>
                      <TableHead>Type</TableHead>
                      <TableHead>Valeur</TableHead>
                      <TableHead>Ordre</TableHead>
                      <TableHead>Actions</TableHead>
                    </TableRow>
                  </TableHeader>
                  <TableBody>
                    {contentBlocks.map((block) => (
                      <TableRow key={block.id}>
                        <TableCell>
                          <span className="font-medium">{block.section}</span>
                        </TableCell>
                        <TableCell>
                          <code className="bg-gray-100 px-2 py-1 rounded text-sm">
                            {block.key}
                          </code>
                        </TableCell>
                        <TableCell>
                          <span className="text-sm bg-blue-100 text-blue-800 px-2 py-1 rounded">
                            {block.content_type}
                          </span>
                        </TableCell>
                        <TableCell>
                          {renderValue(block.value, block.content_type)}
                        </TableCell>
                        <TableCell>
                          <span className="text-sm text-gray-500">{block.order_index}</span>
                        </TableCell>
                        <TableCell>
                          <div className="flex space-x-2">
                            <Button
                              variant="ghost"
                              size="sm"
                              onClick={() => handleEdit(block)}
                            >
                              <Edit className="w-4 h-4" />
                            </Button>
                            <Button
                              variant="ghost"
                              size="sm"
                              onClick={() => handleDelete(block.id)}
                              className="text-red-600 hover:text-red-700"
                            >
                              <Trash2 className="w-4 h-4" />
                            </Button>
                          </div>
                        </TableCell>
                      </TableRow>
                    ))}
                  </TableBody>
                </Table>
                {contentBlocks.length === 0 && (
                  <div className="text-center py-8 text-gray-500">
                    Aucun contenu trouvé pour cette page. Créez votre premier bloc de contenu !
                  </div>
                )}
              </CardContent>
            </Card>
          </TabsContent>
        ))}
      </Tabs>

      {/* Content Examples */}
      <Card>
        <CardHeader>
          <CardTitle>Exemples de contenu</CardTitle>
        </CardHeader>
        <CardContent>
          <div className="grid grid-cols-1 md:grid-cols-2 gap-4 text-sm">
            <div>
              <h4 className="font-medium mb-2">Page d'accueil - Section Hero</h4>
              <ul className="space-y-1 text-gray-600">
                <li><code>title</code> - Titre principal</li>
                <li><code>subtitle</code> - Sous-titre</li>
                <li><code>description</code> - Description</li>
                <li><code>cta_text</code> - Texte du bouton</li>
                <li><code>background_image</code> - Image de fond</li>
              </ul>
            </div>
            <div>
              <h4 className="font-medium mb-2">Page Store - Section Features</h4>
              <ul className="space-y-1 text-gray-600">
                <li><code>features</code> - Liste des fonctionnalités (JSON)</li>
                <li><code>pricing_note</code> - Note sur les prix</li>
                <li><code>contact_info</code> - Informations de contact</li>
              </ul>
            </div>
          </div>
        </CardContent>
      </Card>
    </div>
  );
};

export default Content;

