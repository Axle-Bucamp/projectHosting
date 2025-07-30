import React, { useState, useEffect } from 'react';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Badge } from '@/components/ui/badge';
import { Button } from '@/components/ui/button';
import { Star, Euro, ExternalLink, Package } from 'lucide-react';

const StoreGrid = () => {
  const [items, setItems] = useState([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    fetchStoreItems();
  }, []);

  const fetchStoreItems = async () => {
    try {
      const response = await fetch('/api/store');
      const data = await response.json();

      if (data.success) {
        const fixedItems = (data.items || []).map(item => ({
          ...item,
          features: typeof item.features === 'string'
            ? JSON.parse(item.features)
            : item.features
        }));

        setItems(fixedItems);
      }
    } catch (error) {
      console.error('Failed to fetch store items:', error);
    } finally {
      setLoading(false);
    }
  };

  const getCategoryColor = (category) => {
    const colors = {
      service: 'bg-blue-100 text-blue-800',
      product: 'bg-green-100 text-green-800',
      template: 'bg-purple-100 text-purple-800',
      consultation: 'bg-orange-100 text-orange-800'
    };
    return colors[category] || colors.service;
  };

  const renderStars = (rating) => {
    return (
      <div className="flex items-center">
        {[...Array(5)].map((_, i) => (
          <Star
            key={i}
            className={`w-4 h-4 ${
              i < Math.floor(rating)
                ? 'text-yellow-400 fill-current'
                : 'text-gray-300'
            }`}
          />
        ))}
        <span className="ml-1 text-sm text-gray-600">({rating})</span>
      </div>
    );
  };

  if (loading) {
    return (
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
        {[...Array(6)].map((_, i) => (
          <Card key={i} className="animate-pulse">
            <CardContent className="p-6">
              <div className="h-32 bg-gray-200 rounded mb-4"></div>
              <div className="h-4 bg-gray-200 rounded w-3/4 mb-2"></div>
              <div className="h-3 bg-gray-200 rounded w-1/2 mb-4"></div>
              <div className="h-8 bg-gray-200 rounded w-1/3"></div>
            </CardContent>
          </Card>
        ))}
      </div>
    );
  }

  return (
    <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
      {items.map((item) => (
        <Card key={item.id} className="hover:shadow-lg transition-shadow relative">
          {item.popular && (
            <div className="absolute top-4 right-4 z-10">
              <Badge className="bg-yellow-500 text-white">
                <Star className="w-3 h-3 mr-1" />
                Populaire
              </Badge>
            </div>
          )}
          
          <CardHeader className="pb-3">
            {item.image_url && (
              <img
                src={item.image_url}
                alt={item.name}
                className="w-full h-32 object-cover rounded-lg mb-4"
              />
            )}
            <div className="flex items-start justify-between">
              <div className="flex-1">
                <CardTitle className="text-lg">{item.name}</CardTitle>
                <Badge className={`mt-1 ${getCategoryColor(item.category)}`}>
                  {item.category}
                </Badge>
              </div>
            </div>
          </CardHeader>
          
          <CardContent>
            <p className="text-gray-600 text-sm mb-4 line-clamp-3">
              {item.description}
            </p>

            {item.features && item.features.length > 0 && (
              <ul className="text-sm text-gray-600 mb-4 space-y-1">
                {item.features.slice(0, 3).map((feature, index) => (
                  <li key={index} className="flex items-center">
                    <div className="w-1.5 h-1.5 bg-blue-500 rounded-full mr-2"></div>
                    {feature}
                  </li>
                ))}
                {item.features.length > 3 && (
                  <li className="text-xs text-gray-500">
                    +{item.features.length - 3} autres fonctionnalités
                  </li>
                )}
              </ul>
            )}

            <div className="flex items-center justify-between mb-4">
              <div className="flex items-center">
                <Euro className="w-4 h-4 mr-1 text-green-600" />
                <span className="text-xl font-bold text-green-600">
                  {item.price}
                </span>
                <span className="text-sm text-gray-500 ml-1">
                  {item.currency}
                  {item.duration && ` / ${item.duration}`}
                </span>
              </div>
            </div>

            {item.rating > 0 && (
              <div className="flex items-center justify-between mb-4">
                {renderStars(item.rating)}
                <span className="text-sm text-gray-500">
                  {item.reviews_count} avis
                </span>
              </div>
            )}

            <Button
              className="w-full"
              asChild={!!item.external_url}
            >
              {item.external_url ? (
                <a
                  href={item.external_url}
                  target="_blank"
                  rel="noopener noreferrer"
                  className="flex items-center justify-center"
                >
                  <ExternalLink className="w-4 h-4 mr-2" />
                  Voir l'offre
                </a>
              ) : (
                <span className="flex items-center justify-center">
                  <Package className="w-4 h-4 mr-2" />
                  Commander
                </span>
              )}
            </Button>
          </CardContent>
        </Card>
      ))}

      {items.length === 0 && !loading && (
        <div className="col-span-full text-center py-12">
          <div className="text-gray-500">
            <Package className="w-12 h-12 mx-auto mb-4 opacity-50" />
            <h3 className="text-lg font-medium mb-2">Aucun produit disponible</h3>
            <p>Notre catalogue sera bientôt disponible.</p>
          </div>
        </div>
      )}
    </div>
  );
};

export default StoreGrid;

