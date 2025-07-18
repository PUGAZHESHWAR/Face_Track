import React, { useState, useEffect } from 'react';
import { Plus, Search, Edit, Trash2, Download } from 'lucide-react';
import { useOrganization } from '../context/OrganizationContext';
import api from '../context/api';
import toast from 'react-hot-toast';
import * as XLSX from 'xlsx';
import Webcam from 'react-webcam';


const Students: React.FC = () => {
  const webcamRef = React.useRef<Webcam>(null);
  const [isProcessing, setIsProcessing] = useState(false);
  const [showWebcam, setShowWebcam] = useState(false);
  const { currentOrganization } = useOrganization();
  const [students, setStudents] = useState<any[]>([]);
  const [departments, setDepartments] = useState<any[]>([]);
  const [classes, setClasses] = useState<any[]>([]);
  const [loading, setLoading] = useState(true);
  const [showModal, setShowModal] = useState(false);
  const [editingStudent, setEditingStudent] = useState<any>(null);
  const [searchTerm, setSearchTerm] = useState('');
  const [filterDepartment, setFilterDepartment] = useState('');
  
  const [formData, setFormData] = useState({
    roll_number: '',
    full_name: '',
    email: '',
    phone: '',
    department_id: '',
    class_id: '',
    semester: '',
    course: '',
    address: '',
    date_of_birth: '',
    gender: '',
  });
  const [faceFile, setFaceFile] = useState<File | null>(null);
  const [faceUploadLoading, setFaceUploadLoading] = useState(false);

  // Add at top
  type FaceImageState = {
    file: File | null;
    status: 'idle' | 'verified' | 'unverified' | 'uploading' | 'error';
    message: string;
  };
  const [faceImages, setFaceImages] = useState<FaceImageState[]>([
    { file: null, status: 'idle', message: '' },
    { file: null, status: 'idle', message: '' },
    { file: null, status: 'idle', message: '' },
    { file: null, status: 'idle', message: '' },
  ]);


  const handleCaptureImage = async (index: number) => {
    if (!webcamRef.current) return;

    const imageSrc = webcamRef.current.getScreenshot();
    if (!imageSrc) return;

    const res = await fetch(imageSrc);
    const blob = await res.blob();
    const file = new File([blob], `face_${index + 1}.jpg`, { type: 'image/jpeg' });

    updateFaceImage(index, { file, status: 'idle', message: 'Image captured' });
  };

  const handleVerifyFace = async (index: number) => {
    const face = faceImages[index];
    if (!face.file || !formData.roll_number) {
      updateFaceImage(index, { ...face, status: 'error', message: 'Missing image or roll number' });
      return;
    }

    const formDataObj = new FormData();
    formDataObj.append('face', face.file);
    formDataObj.append('identifier', formData.roll_number);
    formDataObj.append('id_type', 'student');

    try {
      const response = await fetch('http://localhost:8000/api/verify-face', {
        method: 'POST',
        body: formDataObj,
      });

      const result = await response.json();

      if (response.ok && result.encoded === true) {
        updateFaceImage(index, { ...face, status: 'verified', message: 'Verified ✅' });
      } else {
        updateFaceImage(index, { ...face, status: 'unverified', message: 'Verification failed ❌' });
      }
    } catch (error) {
      updateFaceImage(index, { ...face, status: 'error', message: 'Error verifying image ❌' });
    }
  };

  const handleUploadFace = async (index: number) => {
    const face = faceImages[index];
    if (!face.file || face.status !== 'verified' || !formData.roll_number) {
      updateFaceImage(index, { ...face, message: 'Cannot upload: Not verified' });
      return;
    }

    const formDataObj = new FormData();
    formDataObj.append('face', face.file);
    formDataObj.append('identifier', formData.roll_number);
    formDataObj.append('id_type', 'student');

    try {
      updateFaceImage(index, { ...face, status: 'uploading', message: 'Uploading...' });

      const response = await fetch('http://localhost:8000/api/upload-face', {
        method: 'POST',
        body: formDataObj,
      });

      if (!response.ok) throw new Error('Upload failed');

      updateFaceImage(index, { ...face, message: 'Uploaded ✅', status: 'verified' });
    } catch {
      updateFaceImage(index, { ...face, message: 'Upload failed ❌', status: 'error' });
    }
  };

  const updateFaceImage = (index: number, newState: FaceImageState) => {
    setFaceImages(prev => {
      const updated = [...prev];
      updated[index] = newState;
      return updated;
    });
  };


  useEffect(() => {
    if (currentOrganization) {
      fetchData();
    }
  }, [currentOrganization]);

    const fetchData = async () => {
    if (!currentOrganization) return;

    try {
        setLoading(true);
        const [studentsRes, departmentsRes, classesRes] = await Promise.all([
        api.get(`/api/students/${currentOrganization.id}`),
        api.get(`/api/departments/${currentOrganization.id}`),
        api.get(`/api/classes/${currentOrganization.id}`),
        ]);

        const departmentsMap = Object.fromEntries(
        departmentsRes.data.map((dept: any) => [dept.id, dept.name])
        );

        const classesMap = Object.fromEntries(
        classesRes.data.map((cls: any) => [cls.id, cls.name])
        );

        const enrichedStudents = studentsRes.data.map((student: any) => ({
        ...student,
        department_name: departmentsMap[student.department_id] || 'N/A',
        class_name: classesMap[student.class_id] || 'N/A',
        }));

        setStudents(enrichedStudents);
        setDepartments(departmentsRes.data);
        setClasses(classesRes.data);
    } catch (error) {
        console.error('Error fetching data:', error);
        toast.error('Failed to fetch data');
    } finally {
        setLoading(false);
    }
    };



  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!currentOrganization) return;
    setFaceUploadLoading(true);
    
    try {
      // First validate roll number
      if (!formData.roll_number.trim()) {
        throw new Error('Roll number is required before uploading face image');
      }
  
      // Upload face image if presen
      // if (faceFile) {
      //   const formDataObj = new FormData();
      //   formDataObj.append('face', faceFile);
      //   formDataObj.append('identifier', formData.roll_number); 
      //   formDataObj.append('id_type', 'student'); 
      //   console.log('Submitting with roll number:', formData.roll_number); // Debug log
  
      //   const uploadResponse = await fetch('http://51.21.171.26:8000/api/upload-face', {
      //     method: 'POST',
      //     body: formDataObj,
      //   });
        
      //   if (!uploadResponse.ok) {
      //     const errorData = await uploadResponse.json();
      //     console.error('Upload error:', errorData); // Debug log
      //     throw new Error(errorData.error || 'Face image upload failed');
      //   }
      // }

      // if (faceFile) {
      //   const formDataObj = new FormData();
      //   formDataObj.append('face', faceFile);
      //   formDataObj.append('identifier', formData.roll_number); // 🎯 Student Roll No
      //   formDataObj.append('id_type', 'student');

      //   const uploadResponse = await fetch('http://51.21.171.26:8000/api/upload-face', {
      //     method: 'POST',
      //     body: formDataObj,
      //   });

      //   if (!uploadResponse.ok) {
      //     const errorData = await uploadResponse.json();
      //     throw new Error(errorData.error || 'Face image upload failed');
      //   }
      // }

      if (faceFile) {
        const formDataObj = new FormData();
        formDataObj.append('face', faceFile);
        formDataObj.append('identifier', formData.roll_number); // for students
        formDataObj.append('id_type', 'student');

        const uploadResponse = await fetch('http://localhost:8000/api/upload-face', {
          method: 'POST',
          body: formDataObj,
        });

        if (!uploadResponse.ok) {
          const errorData = await uploadResponse.json();
          throw new Error(errorData.error || 'Face image upload failed');
        }
      }

  
      // Then save student data
      const studentData = {
        ...formData,
        organization_id: currentOrganization.id,
      };
  
    if (editingStudent) {
    await api.put(`/api/students/${editingStudent.id}`, studentData);
    toast.success('Student updated successfully');
    } else {
    await api.post('/api/students/', studentData);
    toast.success('Student created successfully');
    }

  
      setShowModal(false);
      setEditingStudent(null);
      resetForm();
      setFaceFile(null);
      fetchData();
    } catch (error: any) {
      toast.error(error.message || 'Failed to save student');
    } finally {
      setFaceUploadLoading(false);
    }
  };
  const handleEdit = (student: any) => {
    setEditingStudent(student);
    setFormData({
      roll_number: student.roll_number || '',
      full_name: student.full_name || '',
      email: student.email || '',
      phone: student.phone || '',
      department_id: student.department_id || '',
      class_id: student.class_id || '',
      semester: student.semester || '',
      course: student.course || '',
      address: student.address || '',
      date_of_birth: student.date_of_birth || '',
      gender: student.gender || '',
    });
    setShowModal(true);
  };

  const handleDelete = async (id: string) => {
    await api.delete(`/api/students/${id}`);
    toast.success('Student deleted successfully');
    fetchStudents();
  };
  const fetchStudents = async () => {
  if (!currentOrganization) return;

  try {
    const res = await api.get(`/api/students/${currentOrganization.id}`);
    setStudents(res.data);
  } catch (error) {
    toast.error('Failed to fetch students');
    console.error(error);
  }
};



  const resetForm = () => {
    setFormData({
      roll_number: '',
      full_name: '',
      email: '',
      phone: '',
      department_id: '',
      class_id: '',
      semester: '',
      course: '',
      address: '',
      date_of_birth: '',
      gender: '',
    });
  };

  const openCreateModal = () => {
    setEditingStudent(null);
    resetForm();
    setShowModal(true);
  };

  const exportToExcel = () => {
    const exportData = students.map(student => ({
      'Roll Number': student.roll_number,
      'Full Name': student.full_name,
      'Email': student.email,
      'Phone': student.phone,
      'Department': student.departments?.name,
      'Class': student.classes?.name,
      'Semester': student.semester,
      'Course': student.course,
      'Gender': student.gender,
      'Date of Birth': student.date_of_birth,
    }));

    const ws = XLSX.utils.json_to_sheet(exportData);
    const wb = XLSX.utils.book_new();
    XLSX.utils.book_append_sheet(wb, ws, 'Students');
    XLSX.writeFile(wb, `students_${currentOrganization?.name || 'export'}.xlsx`);
  };

  const filteredStudents = students.filter(student => {
    const matchesSearch = student.full_name?.toLowerCase().includes(searchTerm.toLowerCase()) ||
                         student.roll_number?.toLowerCase().includes(searchTerm.toLowerCase()) ||
                         student.email?.toLowerCase().includes(searchTerm.toLowerCase());
    const matchesDepartment = !filterDepartment || student.department_id === filterDepartment;
    return matchesSearch && matchesDepartment;
  });

  if (loading) {
    return (
      <div className="flex items-center justify-center h-64">
        <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-600"></div>
      </div>
    );
  }

  return (
    <div className="space-y-6">
      <div className="flex items-center justify-between">
        <h1 className="text-2xl font-bold text-gray-900">Students</h1>
        <div className="flex space-x-3">
          <button
            onClick={exportToExcel}
            className="flex items-center px-4 py-2 bg-green-600 text-white rounded-lg hover:bg-green-700 transition-colors"
          >
            <Download className="w-4 h-4 mr-2" />
            Export
          </button>
          <button
            onClick={openCreateModal}
            className="flex items-center px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 transition-colors"
          >
            <Plus className="w-4 h-4 mr-2" />
            Add Student
          </button>
        </div>
      </div>

      {/* Filters */}
      <div className="bg-white rounded-lg shadow-sm p-4 border border-gray-200">
        <div className="flex flex-col md:flex-row gap-4">
          <div className="flex-1">
            <div className="relative">
              <Search className="absolute left-3 top-1/2 transform -translate-y-1/2 text-gray-400 w-4 h-4" />
              <input
                type="text"
                placeholder="Search students..."
                value={searchTerm}
                onChange={(e) => setSearchTerm(e.target.value)}
                className="pl-10 pr-4 py-2 w-full border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
              />
            </div>
          </div>
          <div className="w-full md:w-48">
            <select
              value={filterDepartment}
              onChange={(e) => setFilterDepartment(e.target.value)}
              className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
            >
              <option value="">All Departments</option>
              {departments.map((dept) => (
                <option key={dept.id} value={dept.id}>
                  {dept.name}
                </option>
              ))}
            </select>
          </div>
        </div>
      </div>

      {/* Students Table */}
      <div className="bg-white rounded-lg shadow-sm border border-gray-200 overflow-hidden">
        <div className="overflow-x-auto">
          <table className="min-w-full divide-y divide-gray-200">
            <thead className="bg-gray-50">
              <tr>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                  Student
                </th>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                  Roll Number
                </th>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                  Department
                </th>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                  Class
                </th>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                  Contact
                </th>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                  Actions
                </th>
              </tr>
            </thead>
            <tbody className="bg-white divide-y divide-gray-200">
              {filteredStudents.map((student) => (
                <tr key={student.id} className="hover:bg-gray-50">
                  <td className="px-6 py-4 whitespace-nowrap">
                    <div className="flex items-center">
                      <div className="w-10 h-10 bg-blue-100 rounded-full flex items-center justify-center">
                        <span className="text-blue-600 font-medium">
                          {student.full_name?.charAt(0) || 'S'}
                        </span>
                      </div>
                      <div className="ml-4">
                        <div className="text-sm font-medium text-gray-900">
                          {student.full_name}
                        </div>
                        <div className="text-sm text-gray-500">{student.email}</div>
                      </div>
                    </div>
                  </td>
                  <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-900">
                    {student.roll_number}
                  </td>
                  <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-900">
                    {student.department_name || 'N/A'}
                  </td>
                  <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-900">
                    {student.class_name || 'N/A'}
                  </td>
                  <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-900">
                    {student.phone}
                  </td>
                  <td className="px-6 py-4 whitespace-nowrap text-sm font-medium">
                    <div className="flex space-x-2">
                      <button
                        onClick={() => handleEdit(student)}
                        className="text-blue-600 hover:text-blue-900"
                      >
                        <Edit className="w-4 h-4" />
                      </button>
                      <button
                        onClick={() => handleDelete(student.id)}
                        className="text-red-600 hover:text-red-900"
                      >
                        <Trash2 className="w-4 h-4" />
                      </button>
                    </div>
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      </div>

      {/* Modal */}
      {showModal && (
        <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50 p-4">
          <div className="bg-white rounded-lg p-6 w-full max-w-2xl max-h-[90vh] overflow-y-auto">
            <h2 className="text-xl font-semibold text-gray-900 mb-4">
              {editingStudent ? 'Edit Student' : 'Add New Student'}
            </h2>
            <form onSubmit={handleSubmit} className="space-y-4">
              <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-1">
                    Roll Number *
                  </label>
                  <input
                    type="text"
                    required
                    value={formData.roll_number}
                    onChange={(e) => setFormData({ ...formData, roll_number: e.target.value })}
                    className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                  />
                </div>
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-1">
                    Full Name *
                  </label>
                  <input
                    type="text"
                    required
                    value={formData.full_name}
                    onChange={(e) => setFormData({ ...formData, full_name: e.target.value })}
                    className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                  />
                </div>
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-1">
                    Email *
                  </label>
                  <input
                    type="email"
                    required
                    value={formData.email}
                    onChange={(e) => setFormData({ ...formData, email: e.target.value })}
                    className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                  />
                </div>
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-1">
                    Phone
                  </label>
                  <input
                    type="tel"
                    value={formData.phone}
                    onChange={(e) => setFormData({ ...formData, phone: e.target.value })}
                    className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                  />
                </div>
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-1">
                    Department
                  </label>
                  <select
                    value={formData.department_id}
                    onChange={(e) => setFormData({ ...formData, department_id: e.target.value })}
                    className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                  >
                    <option value="">Select Department</option>
                    {departments.map((dept) => (
                      <option key={dept.id} value={dept.id}>
                        {dept.name}
                      </option>
                    ))}
                  </select>
                </div>
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-1">
                    Class
                  </label>
                  <select
                    value={formData.class_id}
                    onChange={(e) => setFormData({ ...formData, class_id: e.target.value })}
                    className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                  >
                    <option value="">Select Class</option>
                    {classes.map((cls) => (
                      <option key={cls.id} value={cls.id}>
                        {cls.name}
                      </option>
                    ))}
                  </select>
                </div>
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-1">
                    Course
                  </label>
                  <input
                    type="text"
                    value={formData.course}
                    onChange={(e) => setFormData({ ...formData, course: e.target.value })}
                    className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                  />
                </div>
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-1">
                    Semester
                  </label>
                  <input
                    type="text"
                    value={formData.semester}
                    onChange={(e) => setFormData({ ...formData, semester: e.target.value })}
                    className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                  />
                </div>
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-1">
                    Gender
                  </label>
                  <select
                    value={formData.gender}
                    onChange={(e) => setFormData({ ...formData, gender: e.target.value })}
                    className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                  >
                    <option value="">Select Gender</option>
                    <option value="male">Male</option>
                    <option value="female">Female</option>
                    <option value="other">Other</option>
                  </select>
                </div>
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-1">
                    Date of Birth
                  </label>
                  <input
                    type="date"
                    value={formData.date_of_birth}
                    onChange={(e) => setFormData({ ...formData, date_of_birth: e.target.value })}
                    className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                  />
                </div>
              </div>

                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-1">
                    Face Image Check
                  </label>
                  <input
                    type="file"
                    accept="image/*"
                    onChange={e => setFaceFile(e.target.files?.[0] || null)}
                    className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                  />

                    {/* 👇 Show the file name if faceFile is present */}
                    {faceFile && (
                      <p className="mt-1 text-sm text-green-600">
                        Selected File: <strong>{faceFile.name}</strong>
                      </p>
                    )}
                  {/* Webcam Button */}
                  <button
                    type="button"
                    onClick={() => setShowWebcam((prev) => !prev)}
                    className="mt-2 px-3 py-1 bg-gray-200 rounded hover:bg-gray-300 text-sm"
                  >
                    {showWebcam ? 'Close Webcam' : 'Capture with Webcam'}
                  </button>

                {/* Webcam Viewer */}
                {showWebcam && (
                  <div className="mb-4">
                    <Webcam
                      audio={false}
                      ref={webcamRef}
                      screenshotFormat="image/jpeg"
                      width={220}
                      videoConstraints={{ facingMode: 'user' }}
                    />
                  </div>
                )}

                <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                  {faceImages.map((face, index) => (
                    <div key={index} className="border p-3 rounded shadow-sm bg-gray-50">
                      <h4 className="font-medium mb-2">Face Image {index + 1}</h4>

                      <input
                        type="file"
                        accept="image/*"
                        onChange={(e) => {
                          const file = e.target.files?.[0] || null;
                          updateFaceImage(index, {
                            file,
                            status: 'idle',
                            message: file ? 'Image selected' : '',
                          });
                        }}
                        className="mb-2"
                      />

                      <div className="flex gap-2 mb-2">
                        <button
                          type="button"
                          className="px-3 py-1 bg-gray-200 rounded hover:bg-gray-300 text-sm"
                          onClick={() => handleCaptureImage(index)}
                        >
                          Capture
                        </button>
                        <button
                          type="button"
                          className="px-3 py-1 bg-yellow-500 text-white rounded hover:bg-yellow-600 text-sm"
                          onClick={() => handleVerifyFace(index)}
                        >
                          Verify
                        </button>
                        <button
                          type="button"
                          className="px-3 py-1 bg-blue-600 text-white rounded hover:bg-blue-700 text-sm"
                          onClick={() => handleUploadFace(index)}
                        >
                          Upload
                        </button>
                      </div>

                      <div className="text-sm">
                        {face.message && (
                          <span
                            className={
                              face.status === 'verified'
                                ? 'text-green-600'
                                : face.status === 'unverified' || face.status === 'error'
                                ? 'text-red-600'
                                : 'text-gray-600'
                            }
                          >
                            {face.message}
                          </span>
                        )}
                      </div>
                    </div>
                  ))}
                </div>



                  {faceUploadLoading && <span className="text-xs text-blue-600">Uploading...</span>}
                </div>
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">
                  Address
                </label>
                <textarea
                  value={formData.address}
                  onChange={(e) => setFormData({ ...formData, address: e.target.value })}
                  className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                  rows={3}
                />
              </div>
              <div className="flex justify-end space-x-3 pt-4">
                <button
                  type="button"
                  onClick={() => setShowModal(false)}
                  className="px-4 py-2 text-gray-600 border border-gray-300 rounded-lg hover:bg-gray-50 transition-colors"
                >
                  Cancel
                </button>
                <button
                  type="submit"
                  className="px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 transition-colors"
                >
                  {editingStudent ? 'Update' : 'Create'}
                </button>
              </div>
            </form>
          </div>
        </div>
      )}
    </div>
  );
};

export default Students;