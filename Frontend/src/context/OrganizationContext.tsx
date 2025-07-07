import React, { createContext, useContext, useEffect, useState } from 'react';
import api from '../context/api'; // Axios instance
import { useAuth } from './AuthContext';

interface Organization {
  id: string;
  name: string;
  logo?: string;
  address?: string;
  contact?: string;
  created_at: string;
}

interface OrganizationContextType {
  organizations: Organization[];
  currentOrganization: Organization | null;
  loading: boolean;
  setCurrentOrganization: (org: Organization | null) => void;
  fetchOrganizations: () => Promise<void>;
  createOrganization: (data: Partial<Organization>) => Promise<void>;
  updateOrganization: (id: string, data: Partial<Organization>) => Promise<void>;
  deleteOrganization: (id: string) => Promise<void>;
}

const OrganizationContext = createContext<OrganizationContextType | undefined>(undefined);

export const useOrganization = () => {
  const context = useContext(OrganizationContext);
  if (!context) {
    throw new Error('useOrganization must be used within an OrganizationProvider');
  }
  return context;
};

export const OrganizationProvider: React.FC<{ children: React.ReactNode }> = ({ children }) => {
  const [organizations, setOrganizations] = useState<Organization[]>([]);
  const [currentOrganization, setCurrentOrganization] = useState<Organization | null>(null);
  const [loading, setLoading] = useState(true);
  const { user } = useAuth();

  useEffect(() => {
    if (user) {
      fetchOrganizations();
    }
  }, [user]);

  const fetchOrganizations = async () => {
    try {
      setLoading(true);
      const res = await api.get<Organization[]>('/organizations');
      const data = res.data;

      setOrganizations(data);

      if (data.length > 0 && !currentOrganization) {
        setCurrentOrganization(data[0]);
      }
    } catch (error) {
      console.error('Error fetching organizations:', error);
    } finally {
      setLoading(false);
    }
  };

  const createOrganization = async (data: Partial<Organization>) => {
    try {
      await api.post('/organizations', data);
      await fetchOrganizations();
    } catch (error) {
      console.error('Error creating organization:', error);
      throw error;
    }
  };

  const updateOrganization = async (id: string, data: Partial<Organization>) => {
    try {
      await api.put(`/organizations/${id}`, data);
      await fetchOrganizations();
    } catch (error) {
      console.error('Error updating organization:', error);
      throw error;
    }
  };

  const deleteOrganization = async (id: string) => {
    try {
      await api.delete(`/organizations/${id}`);
      await fetchOrganizations();
    } catch (error) {
      console.error('Error deleting organization:', error);
      throw error;
    }
  };

  const value = {
    organizations,
    currentOrganization,
    loading,
    setCurrentOrganization,
    fetchOrganizations,
    createOrganization,
    updateOrganization,
    deleteOrganization,
  };

  return (
    <OrganizationContext.Provider value={value}>
      {children}
    </OrganizationContext.Provider>
  );
};
