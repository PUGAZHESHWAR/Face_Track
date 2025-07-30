// src/context/AuthContext.tsx
import React, { createContext, useContext, useEffect, useState } from 'react';
import api from '../context/api' 
import axios from 'axios';

interface User {
  id: string;
  email: string;
  [key: string]: any;
}

interface AuthContextType {
  user: User | null;
  userProfile: any;
  loading: boolean;
  signIn: (email: string, password: string) => Promise<void>;
  signUp: (name: string, email: string, password: string) => Promise<void>;
  Student_signup: (name: string, reg_no: string, password: string) => Promise<void>;
  Student_signIn: (reg_no: string, password: string) => Promise<void>
  signOut: () => Promise<void>;
  updateProfile: (data: any) => Promise<void>;
}

const AuthContext = createContext<AuthContextType | undefined>(undefined);

export const useAuth = () => {
  const context = useContext(AuthContext);
  if (!context) throw new Error('useAuth must be used within an AuthProvider');
  return context;
};

export const AuthProvider: React.FC<{ children: React.ReactNode }> = ({ children }) => {
  const [user, setUser] = useState<User | null>(null);
  const [userProfile, setUserProfile] = useState<any>(null);
  const [loading, setLoading] = useState(true);

  const fetchUserProfile = async () => {
    try {
      const res = await api.get('/profile');
      setUserProfile(res.data);
    } catch (err) {
      console.error('Failed to fetch profile:', err);
      setUserProfile(null);
    }
  };

  const signIn = async (email: string, password: string) => {
    try {
      const res = await api.post('/login', { email, password });
      const { user, token ,access_token} = res.data;
      console.log('Login successful:', access_token);
      setUser(access_token);
      localStorage.setItem('token', access_token);

      api.defaults.headers.common['Authorization'] = `Bearer ${token}`;
      await fetchUserProfile();
    } catch (err) {
      console.error('Login failed:', err);
      throw err;
    }
  };

    const Student_signIn = async (reg_no: string, password: string) => {
    try {
      const res = await api.post('/studentlogin', { reg_no, password });
      const { user, token ,access_token} = res.data;
      console.log('Login successful:', access_token);
      // setUser(access_token);
      localStorage.setItem('token', access_token);

      api.defaults.headers.common['Authorization'] = `Bearer ${token}`;
      // await fetchUserProfile();
    } catch (err) {
      console.error('Login failed:', err);
      throw err;
    }
  };


  const signUp = async (name: string, email: string, password: string) => {
    try {
      const res = await api.post('/register', {
        name,      // Not full_name
        email,
        password,
      });
      const user = res.data.user;
      setUser(user);
    } catch (err) {
      if (axios.isAxiosError(err)) {
        console.error('Signup failed:', err.response?.data || err.message);
      } else {
        console.error('Unexpected error:', err);
      }
      throw err;
    }
  };

    const Student_signup = async (name: string, reg_no: string, password: string) => {
    try {
      const res = await api.post('/studentsignup', {
        name,      // Not full_name
        reg_no,
        password,
      });
      const user = res.data.user;
      console.log('Student signup successful:', user);
      // setUser(user);
    } catch (err) {
      if (axios.isAxiosError(err)) {
        console.error('Signup failed:', err.response?.data || err.message);
      } else {
        console.error('Unexpected error:', err);
      }
      throw err;
    }
  };



  const signOut = async () => {
    try {
      await api.post('/logout'); // Or DELETE /session
    } catch (err) {
      console.warn('Logout API failed (ignored):', err);
    }
    setUser(null);
    setUserProfile(null);
    localStorage.removeItem('token');
    delete api.defaults.headers.common['Authorization'];
  };

  const updateProfile = async (data: any) => {
    try {
      await api.put('/profile', data);
      await fetchUserProfile();
    } catch (err) {
      console.error('Failed to update profile:', err);
      throw err;
    }
  };

  useEffect(() => {
    const token = localStorage.getItem('token');
    if (token) {
      api.defaults.headers.common['Authorization'] = `Bearer ${token}`;
      fetchUserProfile().then(() => setLoading(false)).catch(() => setLoading(false));
    } else {
      setLoading(false);
    }
  }, []);

  const value = {
    user,
    userProfile,
    loading,
    signIn,
    signUp,
    signOut,
    updateProfile,
    Student_signup,
    Student_signIn
  };

  return <AuthContext.Provider value={value}>{children}</AuthContext.Provider>;
};
