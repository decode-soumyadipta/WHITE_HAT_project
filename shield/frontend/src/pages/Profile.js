import React, { useState } from 'react';
import { FaUserLock, FaGithub, FaShieldAlt, FaCheckCircle, FaExclamationTriangle } from 'react-icons/fa';

const Profile = () => {
  const [formData, setFormData] = useState({
    username: 'SecurityManager',
    email: 'security@example.com',
    current_password: '',
    new_password: '',
    confirm_password: ''
  });
  
  const [isEditing, setIsEditing] = useState(false);
  const [success, setSuccess] = useState('');
  const [error, setError] = useState('');
  
  // Mock user data
  const mockUserData = {
    username: 'SecurityManager',
    email: 'security@example.com',
    role: 'Security Manager',
    created_at: '2023-01-15T00:00:00Z',
    github_connected: true,
    organization: 'SHIELD Security'
  };

  const handleInputChange = (e) => {
    setFormData({
      ...formData,
      [e.target.name]: e.target.value
    });
  };

  const handleSubmit = (e) => {
    e.preventDefault();
    setError('');
    
    // Validate password confirmation
    if (formData.new_password && formData.new_password !== formData.confirm_password) {
      setError('New passwords do not match');
      return;
    }
    
    // Simulate successful update
    setSuccess('Profile updated successfully');
    setIsEditing(false);
    
    // Clear password fields
    setFormData({
      ...formData,
      current_password: '',
      new_password: '',
      confirm_password: ''
    });
  };

  return (
    <div className="container mx-auto px-4 py-6">
      <div className="flex flex-col lg:flex-row gap-6">
        <div className="w-full lg:w-1/3">
          {/* Profile Card */}
          <div className="bg-white rounded-lg shadow-md overflow-hidden mb-6">
            <div className="bg-blue-600 text-white px-6 py-4">
              <h1 className="text-2xl font-bold flex items-center">
                <FaUserLock className="mr-2" /> Security Manager Profile
              </h1>
            </div>
            
            <div className="p-6">
              {error && (
                <div className="bg-red-100 border border-red-400 text-red-700 px-4 py-3 rounded relative mb-4" role="alert">
                  <span className="block sm:inline">{error}</span>
                </div>
              )}
              
              {success && (
                <div className="bg-green-100 border border-green-400 text-green-700 px-4 py-3 rounded relative mb-4" role="alert">
                  <span className="block sm:inline">{success}</span>
                </div>
              )}
              
              {!isEditing ? (
                <div>
                  <div className="flex justify-between items-center mb-6">
                    <h2 className="text-xl font-semibold">Account Information</h2>
                    <button
                      onClick={() => setIsEditing(true)}
                      className="bg-blue-500 hover:bg-blue-700 text-white font-bold py-2 px-4 rounded"
                    >
                      Edit Profile
                    </button>
                  </div>
                  
                  <div className="mb-4">
                    <p className="text-gray-600 text-sm">Username</p>
                    <p className="text-gray-800 font-medium">{mockUserData.username}</p>
                  </div>
                  
                  <div className="mb-4">
                    <p className="text-gray-600 text-sm">Email</p>
                    <p className="text-gray-800 font-medium">{mockUserData.email}</p>
                  </div>
                  
                  <div className="mb-4">
                    <p className="text-gray-600 text-sm">Role</p>
                    <p className="text-gray-800 font-medium">{mockUserData.role}</p>
                  </div>
                  
                  <div className="mb-4">
                    <p className="text-gray-600 text-sm">Account Created</p>
                    <p className="text-gray-800 font-medium">{new Date(mockUserData.created_at).toLocaleDateString()}</p>
                  </div>
                  
                  <div className="mb-4">
                    <p className="text-gray-600 text-sm">Organization</p>
                    <p className="text-gray-800 font-medium">{mockUserData.organization}</p>
                  </div>
                </div>
              ) : (
                <form onSubmit={handleSubmit}>
                  <div className="mb-4">
                    <label className="block text-gray-700 text-sm font-bold mb-2" htmlFor="username">
                      Username
                    </label>
                    <input
                      className="shadow appearance-none border rounded w-full py-2 px-3 text-gray-700 leading-tight focus:outline-none focus:shadow-outline"
                      id="username"
                      type="text"
                      name="username"
                      value={formData.username}
                      onChange={handleInputChange}
                      required
                    />
                  </div>
                  
                  <div className="mb-4">
                    <label className="block text-gray-700 text-sm font-bold mb-2" htmlFor="email">
                      Email
                    </label>
                    <input
                      className="shadow appearance-none border rounded w-full py-2 px-3 text-gray-700 leading-tight focus:outline-none focus:shadow-outline"
                      id="email"
                      type="email"
                      name="email"
                      value={formData.email}
                      onChange={handleInputChange}
                      required
                    />
                  </div>
                  
                  <div className="mb-4">
                    <label className="block text-gray-700 text-sm font-bold mb-2" htmlFor="current_password">
                      Current Password
                    </label>
                    <input
                      className="shadow appearance-none border rounded w-full py-2 px-3 text-gray-700 leading-tight focus:outline-none focus:shadow-outline"
                      id="current_password"
                      type="password"
                      name="current_password"
                      value={formData.current_password}
                      onChange={handleInputChange}
                    />
                  </div>
                  
                  <div className="mb-4">
                    <label className="block text-gray-700 text-sm font-bold mb-2" htmlFor="new_password">
                      New Password
                    </label>
                    <input
                      className="shadow appearance-none border rounded w-full py-2 px-3 text-gray-700 leading-tight focus:outline-none focus:shadow-outline"
                      id="new_password"
                      type="password"
                      name="new_password"
                      value={formData.new_password}
                      onChange={handleInputChange}
                    />
                  </div>
                  
                  <div className="mb-6">
                    <label className="block text-gray-700 text-sm font-bold mb-2" htmlFor="confirm_password">
                      Confirm New Password
                    </label>
                    <input
                      className="shadow appearance-none border rounded w-full py-2 px-3 text-gray-700 leading-tight focus:outline-none focus:shadow-outline"
                      id="confirm_password"
                      type="password"
                      name="confirm_password"
                      value={formData.confirm_password}
                      onChange={handleInputChange}
                    />
                  </div>
                  
                  <div className="flex items-center justify-between">
                    <button
                      className="bg-blue-500 hover:bg-blue-700 text-white font-bold py-2 px-4 rounded focus:outline-none focus:shadow-outline"
                      type="submit"
                    >
                      Save Changes
                    </button>
                    <button
                      className="bg-gray-500 hover:bg-gray-700 text-white font-bold py-2 px-4 rounded focus:outline-none focus:shadow-outline"
                      type="button"
                      onClick={() => setIsEditing(false)}
                    >
                      Cancel
                    </button>
                  </div>
                </form>
              )}
            </div>
          </div>
        </div>
        
        <div className="w-full lg:w-2/3">
          {/* GitHub Integration Card */}
          <div className="bg-white rounded-lg shadow-md overflow-hidden mb-6">
            <div className="bg-gray-800 text-white px-6 py-4 flex justify-between items-center">
              <h2 className="text-xl font-bold flex items-center">
                <FaGithub className="mr-2" /> GitHub Integration
              </h2>
              <span className="bg-green-500 text-white px-2 py-1 rounded text-sm flex items-center">
                <FaCheckCircle className="mr-1" /> Connected
              </span>
            </div>
            
            <div className="p-6">
              <p className="mb-4">Your GitHub account is connected. You can manage repositories for security scanning below.</p>
              
              <div className="mb-6">
                <h3 className="text-lg font-semibold mb-2">Connected Repositories</h3>
                <div className="border rounded-lg">
                  <div className="p-4 border-b bg-gray-50 flex justify-between items-center">
                    <div>
                      <h4 className="font-semibold">shield-platform</h4>
                      <p className="text-sm text-gray-600">Last scan: 2 days ago</p>
                    </div>
                    <span className="bg-red-100 text-red-800 px-2 py-1 rounded-full text-xs flex items-center">
                      <FaExclamationTriangle className="mr-1" /> 3 Critical
                    </span>
                  </div>
                  
                  <div className="p-4 border-b flex justify-between items-center">
                    <div>
                      <h4 className="font-semibold">auth-service</h4>
                      <p className="text-sm text-gray-600">Last scan: 1 week ago</p>
                    </div>
                    <span className="bg-green-100 text-green-800 px-2 py-1 rounded-full text-xs flex items-center">
                      <FaCheckCircle className="mr-1" /> 0 Issues
                    </span>
                  </div>
                  
                  <div className="p-4 flex justify-between items-center">
                    <div>
                      <h4 className="font-semibold">api-gateway</h4>
                      <p className="text-sm text-gray-600">Last scan: 3 days ago</p>
                    </div>
                    <span className="bg-yellow-100 text-yellow-800 px-2 py-1 rounded-full text-xs flex items-center">
                      <FaExclamationTriangle className="mr-1" /> 2 Medium
                    </span>
                  </div>
                </div>
              </div>
              
              <div className="flex justify-between">
                <button className="bg-blue-500 hover:bg-blue-700 text-white font-bold py-2 px-4 rounded">
                  Manage Repositories
                </button>
                <button className="bg-gray-300 hover:bg-gray-400 text-gray-800 font-bold py-2 px-4 rounded">
                  Disconnect GitHub
                </button>
              </div>
            </div>
          </div>
          
          {/* Security Stats Card */}
          <div className="bg-white rounded-lg shadow-md overflow-hidden">
            <div className="bg-blue-600 text-white px-6 py-4">
              <h2 className="text-xl font-bold flex items-center">
                <FaShieldAlt className="mr-2" /> Security Performance
              </h2>
            </div>
            
            <div className="p-6">
              <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4 mb-6">
                <div className="bg-gray-50 rounded-lg p-4 text-center">
                  <p className="text-gray-600 text-sm mb-1">Vulnerabilities Fixed</p>
                  <p className="text-3xl font-bold text-blue-600">47</p>
                </div>
                
                <div className="bg-gray-50 rounded-lg p-4 text-center">
                  <p className="text-gray-600 text-sm mb-1">Current Risk Score</p>
                  <p className="text-3xl font-bold text-green-600">72%</p>
                </div>
                
                <div className="bg-gray-50 rounded-lg p-4 text-center">
                  <p className="text-gray-600 text-sm mb-1">Pending Alerts</p>
                  <p className="text-3xl font-bold text-red-600">5</p>
                </div>
              </div>
              
              <p className="text-sm text-gray-600 mb-2">Recent Activity</p>
              <div className="border-l-2 border-blue-500 pl-4 space-y-4">
                <div>
                  <p className="text-sm">Fixed XSS vulnerability in login component</p>
                  <p className="text-xs text-gray-500">2 days ago</p>
                </div>
                <div>
                  <p className="text-sm">Updated dependencies with security patches</p>
                  <p className="text-xs text-gray-500">1 week ago</p>
                </div>
                <div>
                  <p className="text-sm">Completed security training</p>
                  <p className="text-xs text-gray-500">2 weeks ago</p>
                </div>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
};

export default Profile; 