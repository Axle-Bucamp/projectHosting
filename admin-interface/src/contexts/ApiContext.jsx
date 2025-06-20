import React, { createContext, useContext } from 'react';
import { useAuth } from './AuthContext';

const ApiContext = createContext();

export const useApi = () => {
  const context = useContext(ApiContext);
  if (!context) {
    throw new Error('useApi must be used within an ApiProvider');
  }
  return context;
};

export const ApiProvider = ({ children }) => {
  const { token } = useAuth();

  const apiCall = async (endpoint, options = {}) => {
    const url = endpoint.startsWith('http') ? endpoint : `/api${endpoint}`;
    
    const config = {
      headers: {
        'Content-Type': 'application/json',
        ...(token && { 'Authorization': `Bearer ${token}` }),
        ...options.headers
      },
      ...options
    };

    try {
      const response = await fetch(url, config);
      const data = await response.json();
      
      if (!response.ok) {
        throw new Error(data.error || `HTTP error! status: ${response.status}`);
      }
      
      return data;
    } catch (error) {
      console.error('API call failed:', error);
      throw error;
    }
  };

  // Dashboard API
  const getDashboard = () => apiCall('/admin/dashboard');

  // Projects API
  const getProjects = () => apiCall('/projects');
  const createProject = (data) => apiCall('/projects', {
    method: 'POST',
    body: JSON.stringify(data)
  });
  const updateProject = (id, data) => apiCall(`/projects/${id}`, {
    method: 'PUT',
    body: JSON.stringify(data)
  });
  const deleteProject = (id) => apiCall(`/projects/${id}`, {
    method: 'DELETE'
  });

  // Store API
  const getStoreItems = () => apiCall('/store');
  const createStoreItem = (data) => apiCall('/store', {
    method: 'POST',
    body: JSON.stringify(data)
  });
  const updateStoreItem = (id, data) => apiCall(`/store/${id}`, {
    method: 'PUT',
    body: JSON.stringify(data)
  });
  const deleteStoreItem = (id) => apiCall(`/store/${id}`, {
    method: 'DELETE'
  });

  // Contacts API
  const getContacts = (params = {}) => {
    const query = new URLSearchParams(params).toString();
    return apiCall(`/contact${query ? `?${query}` : ''}`);
  };
  const updateContactStatus = (id, status) => apiCall(`/contact/${id}/status`, {
    method: 'PUT',
    body: JSON.stringify({ status })
  });

  // Content API
  const getContent = (page) => apiCall(`/content/${page}`);
  const createContentBlock = (data) => apiCall('/content', {
    method: 'POST',
    body: JSON.stringify(data)
  });
  const updateContentBlock = (id, data) => apiCall(`/content/${id}`, {
    method: 'PUT',
    body: JSON.stringify(data)
  });
  const deleteContentBlock = (id) => apiCall(`/content/${id}`, {
    method: 'DELETE'
  });

  // System API
  const getSystemInfo = () => apiCall('/admin/system/info');
  const createBackup = () => apiCall('/admin/backup', {
    method: 'POST'
  });

  const value = {
    apiCall,
    getDashboard,
    getProjects,
    createProject,
    updateProject,
    deleteProject,
    getStoreItems,
    createStoreItem,
    updateStoreItem,
    deleteStoreItem,
    getContacts,
    updateContactStatus,
    getContent,
    createContentBlock,
    updateContentBlock,
    deleteContentBlock,
    getSystemInfo,
    createBackup
  };

  return (
    <ApiContext.Provider value={value}>
      {children}
    </ApiContext.Provider>
  );
};

