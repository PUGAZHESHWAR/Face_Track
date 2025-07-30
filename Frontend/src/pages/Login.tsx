import React, { useState } from 'react';
import { GraduationCap, Eye, EyeOff, User2, Shield } from 'lucide-react';
import toast from 'react-hot-toast';
import { Navigate } from 'react-router-dom';
import { useAuth } from '../context/AuthContext';
type UserType = 'student' | 'admin';

const Login: React.FC = () => {
  const [userType, setUserType] = useState<UserType>('student');
  const [isSignUp, setIsSignUp] = useState(false);
  const [showPassword, setShowPassword] = useState(false);
  const [loading, setLoading] = useState(false);
  const { user, signIn, signUp, Student_signup } = useAuth(); // <- useAuth() is a hook

  // 💡 All other hooks declared before return

  // Student form state
  const [studentData, setStudentData] = useState({
    regNo: '',
    password: '',
    fullName: ''
  });

  // Admin form state
  const [adminData, setAdminData] = useState({
    email: '',
    password: '',
    fullName: ''
  });

    if (user) {
    console.log('User already logged in:', user);
    return <Navigate to="/dashboard" replace />;
  }

  const handleUserTypeChange = (type: UserType) => {
    setUserType(type);
    setIsSignUp(false);
    setStudentData({ regNo: '', password: '', fullName: '' });
    setAdminData({ email: '', password: '', fullName: '' });
  };

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setLoading(true);

    try {
      // Here you would integrate with your authentication API
      if (userType === 'student') {
        if (isSignUp) {
          console.log('Student Sign Up:', studentData);
          await Student_signup(studentData.fullName, studentData.regNo, studentData.password);
          toast.success('Account created successfully!');
        } else {
          console.log('Student Login:', { regNo: studentData.regNo, password: studentData.password });
          // await signIn(email, password);
          toast.success('Signed in successfully!');
        }
      } else {
        if (isSignUp) {
          console.log('Admin Sign Up:', adminData);
        await signUp(adminData.fullName, adminData.email, adminData.password);
        toast.success('Account created successfully!');
        } else {
          console.log('Admin Login:', { email: adminData.email, password: adminData.password });
          await signIn(adminData.email, adminData.password);
          toast.success('Signed in successfully!');
        }
      }
    } catch (error: any) {
      console.error('Authentication Error:', error);
      toast.error(error?.response?.data?.detail || error.message || 'An error occurred');
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="min-h-screen bg-gradient-to-br from-blue-50 to-indigo-100 flex items-center justify-center py-12 px-4">
      <div className="max-w-md w-full bg-white p-8 rounded-2xl shadow-lg space-y-6">
        <div className="flex justify-center">
          <div className="h-16 w-16 bg-blue-600 rounded-full flex items-center justify-center">
            <GraduationCap className="h-8 w-8 text-white" />
          </div>
        </div>

        {/* Role Toggle */}
        <div className="flex bg-gray-100 p-1 rounded-lg">
          <button
            onClick={() => handleUserTypeChange('student')}
            className={`flex-1 flex items-center justify-center gap-2 px-4 py-2 rounded-lg text-sm font-medium transition-all ${
              userType === 'student' 
                ? 'bg-blue-600 text-white shadow-sm' 
                : 'text-gray-600 hover:text-gray-800'
            }`}
          >
            <User2 className="h-4 w-4" />
            Student
          </button>
          <button
            onClick={() => handleUserTypeChange('admin')}
            className={`flex-1 flex items-center justify-center gap-2 px-4 py-2 rounded-lg text-sm font-medium transition-all ${
              userType === 'admin' 
                ? 'bg-blue-600 text-white shadow-sm' 
                : 'text-gray-600 hover:text-gray-800'
            }`}
          >
            <Shield className="h-4 w-4" />
            Admin
          </button>
        </div>

        <div className="text-center">
          <h2 className="text-2xl font-bold text-gray-900 mb-1">
            {isSignUp ? 'Create Account' : 'Welcome Back'}
          </h2>
          <p className="text-sm text-gray-500">
            {userType === 'student' ? 'Student Portal Access' : 'Admin Portal Access'}
          </p>
        </div>

        <form onSubmit={handleSubmit} className="space-y-4">
          {isSignUp && (
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1">Full Name</label>
              <input
                type="text"
                required
                value={userType === 'student' ? studentData.fullName : adminData.fullName}
                onChange={(e) => {
                  if (userType === 'student') {
                    setStudentData(prev => ({ ...prev, fullName: e.target.value }));
                  } else {
                    setAdminData(prev => ({ ...prev, fullName: e.target.value }));
                  }
                }}
                placeholder="Enter your full name"
                className="w-full px-3 py-2 border border-gray-300 rounded-lg text-sm focus:ring-2 focus:ring-blue-500 focus:border-blue-500 outline-none transition-all"
              />
            </div>
          )}

          {userType === 'student' ? (
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1">
                Registration Number
              </label>
              <input
                type="text"
                required
                value={studentData.regNo}
                onChange={(e) => setStudentData(prev => ({ ...prev, regNo: e.target.value }))}
                placeholder="Enter your registration number"
                className="w-full px-3 py-2 border border-gray-300 rounded-lg text-sm focus:ring-2 focus:ring-blue-500 focus:border-blue-500 outline-none transition-all"
              />
            </div>
          ) : (
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1">Email</label>
              <input
                type="email"
                required
                value={adminData.email}
                onChange={(e) => setAdminData(prev => ({ ...prev, email: e.target.value }))}
                placeholder="Enter your email"
                className="w-full px-3 py-2 border border-gray-300 rounded-lg text-sm focus:ring-2 focus:ring-blue-500 focus:border-blue-500 outline-none transition-all"
              />
            </div>
          )}

          <div>
            <label className="block text-sm font-medium text-gray-700 mb-1">Password</label>
            <div className="relative">
              <input
                type={showPassword ? 'text' : 'password'}
                required
                value={userType === 'student' ? studentData.password : adminData.password}
                onChange={(e) => {
                  if (userType === 'student') {
                    setStudentData(prev => ({ ...prev, password: e.target.value }));
                  } else {
                    setAdminData(prev => ({ ...prev, password: e.target.value }));
                  }
                }}
                placeholder="Enter your password"
                className="w-full px-3 py-2 pr-10 border border-gray-300 rounded-lg text-sm focus:ring-2 focus:ring-blue-500 focus:border-blue-500 outline-none transition-all"
              />
              <button
                type="button"
                onClick={() => setShowPassword(!showPassword)}
                className="absolute inset-y-0 right-0 flex items-center px-3 text-gray-400 hover:text-gray-600"
              >
                {showPassword ? <EyeOff className="h-4 w-4" /> : <Eye className="h-4 w-4" />}
              </button>
            </div>
          </div>

          <button
            type="submit"
            disabled={loading}
            className="w-full flex justify-center items-center py-2.5 px-4 bg-blue-600 hover:bg-blue-700 text-white text-sm font-medium rounded-lg transition-colors disabled:opacity-50 disabled:cursor-not-allowed"
          >
            {loading ? (
              <div className="animate-spin h-4 w-4 border-2 border-white border-t-transparent rounded-full" />
            ) : isSignUp ? (
              'Create Account'
            ) : (
              'Sign In'
            )}
          </button>

          <div className="text-center">
            <button
              type="button"
              onClick={() => setIsSignUp(!isSignUp)}
              className="text-sm text-blue-600 hover:text-blue-700 font-medium"
            >
              {isSignUp ? 'Already have an account? Sign In' : "Don't have an account? Sign up"}
            </button>
          </div>
        </form>
      </div>
    </div>
  );
};

export default Login;