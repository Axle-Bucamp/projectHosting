import React, { useState } from 'react';

const ImageGallery = ({ images = [], onImageSelect, onImageDelete, allowDelete = false }) => {
  const [selectedImage, setSelectedImage] = useState(null);
  const [viewMode, setViewMode] = useState('grid'); // 'grid' or 'list'

  const handleImageClick = (image) => {
    setSelectedImage(image);
    if (onImageSelect) {
      onImageSelect(image);
    }
  };

  const handleDelete = async (imageId, e) => {
    e.stopPropagation();
    
    if (!window.confirm('Are you sure you want to delete this image?')) {
      return;
    }

    try {
      const response = await fetch(`/api/images/${imageId}`, {
        method: 'DELETE',
      });

      if (!response.ok) {
        throw new Error('Failed to delete image');
      }

      if (onImageDelete) {
        onImageDelete(imageId);
      }
    } catch (error) {
      console.error('Delete error:', error);
      alert('Failed to delete image. Please try again.');
    }
  };

  const formatFileSize = (bytes) => {
    if (bytes === 0) return '0 Bytes';
    const k = 1024;
    const sizes = ['Bytes', 'KB', 'MB', 'GB'];
    const i = Math.floor(Math.log(bytes) / Math.log(k));
    return parseFloat((bytes / Math.pow(k, i)).toFixed(2)) + ' ' + sizes[i];
  };

  const formatDate = (dateString) => {
    return new Date(dateString).toLocaleDateString('en-US', {
      year: 'numeric',
      month: 'short',
      day: 'numeric',
      hour: '2-digit',
      minute: '2-digit'
    });
  };

  if (!images || images.length === 0) {
    return (
      <div className="text-center py-12">
        <svg
          className="w-16 h-16 text-gray-300 mx-auto mb-4"
          fill="none"
          stroke="currentColor"
          viewBox="0 0 24 24"
        >
          <path
            strokeLinecap="round"
            strokeLinejoin="round"
            strokeWidth={2}
            d="M4 16l4.586-4.586a2 2 0 012.828 0L16 16m-2-2l1.586-1.586a2 2 0 012.828 0L20 14m-6-6h.01M6 20h12a2 2 0 002-2V6a2 2 0 00-2-2H6a2 2 0 00-2 2v12a2 2 0 002 2z"
          />
        </svg>
        <p className="text-gray-500 text-lg">No images found</p>
        <p className="text-gray-400 text-sm">Upload some images to get started</p>
      </div>
    );
  }

  return (
    <div className="w-full">
      {/* View Mode Toggle */}
      <div className="flex justify-between items-center mb-4">
        <h3 className="text-lg font-semibold text-gray-800">
          Image Gallery ({images.length} images)
        </h3>
        <div className="flex space-x-2">
          <button
            onClick={() => setViewMode('grid')}
            className={`p-2 rounded ${
              viewMode === 'grid'
                ? 'bg-blue-500 text-white'
                : 'bg-gray-200 text-gray-600 hover:bg-gray-300'
            }`}
          >
            <svg className="w-4 h-4" fill="currentColor" viewBox="0 0 20 20">
              <path d="M5 3a2 2 0 00-2 2v2a2 2 0 002 2h2a2 2 0 002-2V5a2 2 0 00-2-2H5zM5 11a2 2 0 00-2 2v2a2 2 0 002 2h2a2 2 0 002-2v-2a2 2 0 00-2-2H5zM11 5a2 2 0 012-2h2a2 2 0 012 2v2a2 2 0 01-2 2h-2a2 2 0 01-2-2V5zM11 13a2 2 0 012-2h2a2 2 0 012 2v2a2 2 0 01-2 2h-2a2 2 0 01-2-2v-2z" />
            </svg>
          </button>
          <button
            onClick={() => setViewMode('list')}
            className={`p-2 rounded ${
              viewMode === 'list'
                ? 'bg-blue-500 text-white'
                : 'bg-gray-200 text-gray-600 hover:bg-gray-300'
            }`}
          >
            <svg className="w-4 h-4" fill="currentColor" viewBox="0 0 20 20">
              <path d="M3 4a1 1 0 011-1h12a1 1 0 110 2H4a1 1 0 01-1-1zM3 8a1 1 0 011-1h12a1 1 0 110 2H4a1 1 0 01-1-1zM3 12a1 1 0 011-1h12a1 1 0 110 2H4a1 1 0 01-1-1zM3 16a1 1 0 011-1h12a1 1 0 110 2H4a1 1 0 01-1-1z" />
            </svg>
          </button>
        </div>
      </div>

      {/* Grid View */}
      {viewMode === 'grid' && (
        <div className="grid grid-cols-2 md:grid-cols-3 lg:grid-cols-4 xl:grid-cols-6 gap-4">
          {images.map((image) => (
            <div
              key={image.id}
              className={`relative group cursor-pointer rounded-lg overflow-hidden shadow-md hover:shadow-lg transition-shadow ${
                selectedImage?.id === image.id ? 'ring-2 ring-blue-500' : ''
              }`}
              onClick={() => handleImageClick(image)}
            >
              <div className="aspect-square">
                <img
                  src={image.thumbnail_url || image.url}
                  alt={image.alt_text || image.filename}
                  className="w-full h-full object-cover"
                  loading="lazy"
                />
              </div>
              
              {/* Overlay */}
              <div className="absolute inset-0 bg-black bg-opacity-0 group-hover:bg-opacity-30 transition-opacity flex items-center justify-center">
                <div className="opacity-0 group-hover:opacity-100 transition-opacity">
                  <button className="bg-white text-gray-800 px-3 py-1 rounded text-sm font-medium">
                    View
                  </button>
                </div>
              </div>

              {/* Delete button */}
              {allowDelete && (
                <button
                  onClick={(e) => handleDelete(image.id, e)}
                  className="absolute top-2 right-2 bg-red-500 text-white rounded-full w-6 h-6 flex items-center justify-center text-xs opacity-0 group-hover:opacity-100 transition-opacity hover:bg-red-600"
                >
                  ×
                </button>
              )}

              {/* Image info */}
              <div className="absolute bottom-0 left-0 right-0 bg-gradient-to-t from-black to-transparent p-2">
                <p className="text-white text-xs truncate">{image.filename}</p>
              </div>
            </div>
          ))}
        </div>
      )}

      {/* List View */}
      {viewMode === 'list' && (
        <div className="space-y-2">
          {images.map((image) => (
            <div
              key={image.id}
              className={`flex items-center space-x-4 p-3 rounded-lg border cursor-pointer hover:bg-gray-50 transition-colors ${
                selectedImage?.id === image.id ? 'border-blue-500 bg-blue-50' : 'border-gray-200'
              }`}
              onClick={() => handleImageClick(image)}
            >
              <div className="flex-shrink-0">
                <img
                  src={image.thumbnail_url || image.url}
                  alt={image.alt_text || image.filename}
                  className="w-12 h-12 object-cover rounded"
                  loading="lazy"
                />
              </div>
              
              <div className="flex-1 min-w-0">
                <p className="text-sm font-medium text-gray-900 truncate">
                  {image.filename}
                </p>
                <p className="text-sm text-gray-500">
                  {formatFileSize(image.size)} • {formatDate(image.created_at)}
                </p>
                {image.alt_text && (
                  <p className="text-xs text-gray-400 truncate">{image.alt_text}</p>
                )}
              </div>

              <div className="flex items-center space-x-2">
                <button
                  onClick={(e) => {
                    e.stopPropagation();
                    navigator.clipboard.writeText(image.url);
                    alert('Image URL copied to clipboard');
                  }}
                  className="text-gray-400 hover:text-gray-600 transition-colors"
                  title="Copy URL"
                >
                  <svg className="w-4 h-4" fill="currentColor" viewBox="0 0 20 20">
                    <path d="M8 3a1 1 0 011-1h2a1 1 0 110 2H9a1 1 0 01-1-1z" />
                    <path d="M6 3a2 2 0 00-2 2v11a2 2 0 002 2h8a2 2 0 002-2V5a2 2 0 00-2-2 3 3 0 01-3 3H9a3 3 0 01-3-3z" />
                  </svg>
                </button>
                
                {allowDelete && (
                  <button
                    onClick={(e) => handleDelete(image.id, e)}
                    className="text-red-400 hover:text-red-600 transition-colors"
                    title="Delete"
                  >
                    <svg className="w-4 h-4" fill="currentColor" viewBox="0 0 20 20">
                      <path
                        fillRule="evenodd"
                        d="M9 2a1 1 0 000 2h2a1 1 0 100-2H9zM4 5a2 2 0 012-2h8a2 2 0 012 2v6a2 2 0 01-2 2H6a2 2 0 01-2-2V5zm3 4a1 1 0 102 0v3a1 1 0 11-2 0V9zm4 0a1 1 0 10-2 0v3a1 1 0 102 0V9z"
                        clipRule="evenodd"
                      />
                    </svg>
                  </button>
                )}
              </div>
            </div>
          ))}
        </div>
      )}

      {/* Image Modal */}
      {selectedImage && (
        <div
          className="fixed inset-0 bg-black bg-opacity-75 flex items-center justify-center z-50 p-4"
          onClick={() => setSelectedImage(null)}
        >
          <div className="max-w-4xl max-h-full">
            <img
              src={selectedImage.url}
              alt={selectedImage.alt_text || selectedImage.filename}
              className="max-w-full max-h-full object-contain"
            />
            <div className="bg-white p-4 mt-2 rounded">
              <h4 className="font-medium">{selectedImage.filename}</h4>
              <p className="text-sm text-gray-600">
                {formatFileSize(selectedImage.size)} • {formatDate(selectedImage.created_at)}
              </p>
              {selectedImage.alt_text && (
                <p className="text-sm text-gray-700 mt-1">{selectedImage.alt_text}</p>
              )}
            </div>
          </div>
        </div>
      )}
    </div>
  );
};

export default ImageGallery;

