import React, { useState, useEffect } from 'react';
import ImageUpload from '../components/ImageUpload';
import ImageGallery from '../components/ImageGallery';

const ImageManager = () => {
  const [images, setImages] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [selectedImage, setSelectedImage] = useState(null);
  const [showUpload, setShowUpload] = useState(false);

  useEffect(() => {
    fetchImages();
  }, []);

  const fetchImages = async () => {
    try {
      setLoading(true);
      const response = await fetch('/api/images');
      
      if (!response.ok) {
        throw new Error('Failed to fetch images');
      }
      
      const data = await response.json();
      setImages(data.images || []);
    } catch (err) {
      setError(err.message);
      console.error('Error fetching images:', err);
    } finally {
      setLoading(false);
    }
  };

  const handleImageUpload = async (imageUrl, filename) => {
    if (imageUrl) {
      // Refresh the image list
      await fetchImages();
      setShowUpload(false);
    }
  };

  const handleImageDelete = async (imageId) => {
    try {
      // Remove from local state immediately for better UX
      setImages(prev => prev.filter(img => img.id !== imageId));
      
      // If the deleted image was selected, clear selection
      if (selectedImage?.id === imageId) {
        setSelectedImage(null);
      }
    } catch (err) {
      console.error('Error handling image deletion:', err);
      // Refresh the list to ensure consistency
      await fetchImages();
    }
  };

  const handleImageSelect = (image) => {
    setSelectedImage(image);
  };

  const copyImageUrl = (url) => {
    navigator.clipboard.writeText(url).then(() => {
      alert('Image URL copied to clipboard!');
    }).catch(err => {
      console.error('Failed to copy URL:', err);
      alert('Failed to copy URL to clipboard');
    });
  };

  const downloadImage = (image) => {
    const link = document.createElement('a');
    link.href = image.url;
    link.download = image.filename;
    document.body.appendChild(link);
    link.click();
    document.body.removeChild(link);
  };

  if (loading) {
    return (
      <div className="flex items-center justify-center min-h-64">
        <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-600"></div>
      </div>
    );
  }

  if (error) {
    return (
      <div className="bg-red-50 border border-red-200 rounded-lg p-6 text-center">
        <svg className="w-12 h-12 text-red-400 mx-auto mb-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
          <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 8v4m0 4h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z" />
        </svg>
        <h3 className="text-lg font-medium text-red-800 mb-2">Error Loading Images</h3>
        <p className="text-red-600 mb-4">{error}</p>
        <button
          onClick={fetchImages}
          className="bg-red-600 text-white px-4 py-2 rounded hover:bg-red-700 transition-colors"
        >
          Try Again
        </button>
      </div>
    );
  }

  return (
    <div className="max-w-7xl mx-auto p-6">
      <div className="flex justify-between items-center mb-6">
        <div>
          <h1 className="text-3xl font-bold text-gray-900">Image Manager</h1>
          <p className="text-gray-600 mt-1">Upload, organize, and manage your images</p>
        </div>
        <button
          onClick={() => setShowUpload(!showUpload)}
          className="bg-blue-600 text-white px-4 py-2 rounded-lg hover:bg-blue-700 transition-colors flex items-center space-x-2"
        >
          <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 4v16m8-8H4" />
          </svg>
          <span>{showUpload ? 'Cancel' : 'Upload Image'}</span>
        </button>
      </div>

      {/* Upload Section */}
      {showUpload && (
        <div className="bg-white rounded-lg shadow-md p-6 mb-6">
          <h2 className="text-xl font-semibold text-gray-800 mb-4">Upload New Image</h2>
          <ImageUpload
            onImageUpload={handleImageUpload}
            placeholder="Upload a new image"
          />
        </div>
      )}

      {/* Selected Image Details */}
      {selectedImage && (
        <div className="bg-white rounded-lg shadow-md p-6 mb-6">
          <div className="flex items-start space-x-6">
            <div className="flex-shrink-0">
              <img
                src={selectedImage.thumbnail_url || selectedImage.url}
                alt={selectedImage.alt_text || selectedImage.filename}
                className="w-32 h-32 object-cover rounded-lg"
              />
            </div>
            <div className="flex-1">
              <h3 className="text-xl font-semibold text-gray-800 mb-2">
                {selectedImage.filename}
              </h3>
              <div className="grid grid-cols-2 gap-4 text-sm">
                <div>
                  <span className="font-medium text-gray-600">Size:</span>
                  <span className="ml-2 text-gray-800">
                    {(selectedImage.size / 1024 / 1024).toFixed(2)} MB
                  </span>
                </div>
                <div>
                  <span className="font-medium text-gray-600">Dimensions:</span>
                  <span className="ml-2 text-gray-800">
                    {selectedImage.width} × {selectedImage.height}
                  </span>
                </div>
                <div>
                  <span className="font-medium text-gray-600">Type:</span>
                  <span className="ml-2 text-gray-800">{selectedImage.mime_type}</span>
                </div>
                <div>
                  <span className="font-medium text-gray-600">Uploaded:</span>
                  <span className="ml-2 text-gray-800">
                    {new Date(selectedImage.created_at).toLocaleDateString()}
                  </span>
                </div>
              </div>
              {selectedImage.alt_text && (
                <div className="mt-3">
                  <span className="font-medium text-gray-600">Alt Text:</span>
                  <p className="text-gray-800 mt-1">{selectedImage.alt_text}</p>
                </div>
              )}
            </div>
            <div className="flex flex-col space-y-2">
              <button
                onClick={() => copyImageUrl(selectedImage.url)}
                className="bg-blue-600 text-white px-4 py-2 rounded hover:bg-blue-700 transition-colors text-sm"
              >
                Copy URL
              </button>
              <button
                onClick={() => downloadImage(selectedImage)}
                className="bg-green-600 text-white px-4 py-2 rounded hover:bg-green-700 transition-colors text-sm"
              >
                Download
              </button>
              <button
                onClick={() => setSelectedImage(null)}
                className="bg-gray-600 text-white px-4 py-2 rounded hover:bg-gray-700 transition-colors text-sm"
              >
                Close
              </button>
            </div>
          </div>
        </div>
      )}

      {/* Image Gallery */}
      <div className="bg-white rounded-lg shadow-md p-6">
        <ImageGallery
          images={images}
          onImageSelect={handleImageSelect}
          onImageDelete={handleImageDelete}
          allowDelete={true}
        />
      </div>

      {/* Statistics */}
      {images.length > 0 && (
        <div className="bg-white rounded-lg shadow-md p-6 mt-6">
          <h3 className="text-lg font-semibold text-gray-800 mb-4">Statistics</h3>
          <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
            <div className="text-center">
              <div className="text-2xl font-bold text-blue-600">{images.length}</div>
              <div className="text-sm text-gray-600">Total Images</div>
            </div>
            <div className="text-center">
              <div className="text-2xl font-bold text-green-600">
                {(images.reduce((sum, img) => sum + img.size, 0) / 1024 / 1024).toFixed(1)}MB
              </div>
              <div className="text-sm text-gray-600">Total Size</div>
            </div>
            <div className="text-center">
              <div className="text-2xl font-bold text-purple-600">
                {Math.round(images.reduce((sum, img) => sum + img.size, 0) / images.length / 1024)}KB
              </div>
              <div className="text-sm text-gray-600">Average Size</div>
            </div>
            <div className="text-center">
              <div className="text-2xl font-bold text-orange-600">
                {new Set(images.map(img => img.mime_type)).size}
              </div>
              <div className="text-sm text-gray-600">File Types</div>
            </div>
          </div>
        </div>
      )}
    </div>
  );
};

export default ImageManager;

