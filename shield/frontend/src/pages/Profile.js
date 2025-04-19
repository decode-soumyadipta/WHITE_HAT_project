import React, { useState, useEffect, useContext } from 'react';
import axios from 'axios';
import AuthContext from '../utils/AuthContext';

const Profile = () => {
  const { user, updateUser } = useContext(AuthContext);
  const [formData, setFormData] = useState({
    username: '',
    email: '',
    current_password: '',
    new_password: '',
    confirm_password: ''
  });
  const [isEditing, setIsEditing] = useState(false);
  const [error, setError] = useState('');
  const [success, setSuccess] = useState('');
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    if (user) {
      setFormData({
        username: user.username || '',
        email: user.email || '',
        current_password: '',
        new_password: '',
        confirm_password: ''
      });
      setLoading(false);
    }
  }, [user]);

  const handleInputChange = (e) => {
    setFormData({
      ...formData,
      [e.target.name]: e.target.value
    });
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    setError('');
    setSuccess('');

    // Validate password confirmation
    if (formData.new_password && formData.new_password !== formData.confirm_password) {
      setError('New passwords do not match');
      return;
    }

    try {
      const token = localStorage.getItem('token');
      const payload = {
        username: formData.username,
        email: formData.email
      };

      // Only include password fields if the user is trying to change their password
      if (formData.current_password && formData.new_password) {
        payload.current_password = formData.current_password;
        payload.new_password = formData.new_password;
      }

      const response = await axios.put(
        `${process.env.REACT_APP_API_URL || 'http://localhost:5000'}/api/users/profile`,
        payload,
        {
          headers: {
            Authorization: `Bearer ${token}`
          }
        }
      );

      updateUser(response.data);
      setSuccess('Profile updated successfully');
      setIsEditing(false);
      
      // Clear password fields
      setFormData({
        ...formData,
        current_password: '',
        new_password: '',
        confirm_password: ''
      });
    } catch (err) {
      setError(err.response?.data?.message || 'Failed to update profile');
    }
  };

  if (loading) {
    return <div className="flex justify-center items-center h-64">Loading...</div>;
  }

  return (
    <div className="container mx-auto px-4">
      <h1 className="text-2xl font-bold mb-6">Your Profile</h1>
      
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
      
      <div className="bg-white shadow-md rounded-lg overflow-hidden">
        <div className="p-6">
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
                <p className="text-gray-800 font-medium">{user?.username}</p>
              </div>
              
              <div className="mb-4">
                <p className="text-gray-600 text-sm">Email</p>
                <p className="text-gray-800 font-medium">{user?.email}</p>
              </div>
              
              <div className="mb-4">
                <p className="text-gray-600 text-sm">Role</p>
                <p className="text-gray-800 font-medium">{user?.role || 'User'}</p>
              </div>
              
              {user?.created_at && (
                <div className="mb-4">
                  <p className="text-gray-600 text-sm">Account Created</p>
                  <p className="text-gray-800 font-medium">{new Date(user.created_at).toLocaleDateString()}</p>
                </div>
              )}
            </div>
          ) : (
            <div>
              <div className="flex justify-between items-center mb-6">
                <h2 className="text-xl font-semibold">Edit Profile</h2>
                <button
                  onClick={() => setIsEditing(false)}
                  className="bg-gray-300 hover:bg-gray-400 text-gray-800 font-bold py-2 px-4 rounded"
                >
                  Cancel
                </button>
              </div>
              
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
                
                <h3 className="text-lg font-semibold mt-8 mb-4">Change Password (optional)</h3>
                
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
                
                <div className="flex justify-end">
                  <button
                    type="submit"
                    className="bg-blue-500 hover:bg-blue-700 text-white font-bold py-2 px-4 rounded focus:outline-none focus:shadow-outline"
                  >
                    Save Changes
                  </button>
                </div>
              </form>
            </div>
          )}
        </div>
      </div>
      
      <div className="bg-white shadow-md rounded-lg p-6 mt-6">
        <h2 className="text-xl font-semibold mb-4">Account Security</h2>
        
        <div className="mb-4">
          <h3 className="text-md font-medium mb-2">Two-Factor Authentication</h3>
          <p className="text-gray-600 mb-2">Enhance your account security by enabling two-factor authentication.</p>
          <button className="bg-green-500 hover:bg-green-700 text-white font-bold py-2 px-4 rounded">
            Enable 2FA
          </button>
        </div>
        
        <div>
          <h3 className="text-md font-medium mb-2">API Keys</h3>
          <p className="text-gray-600 mb-2">Manage your API keys for programmatic access to SHIELD.</p>
          <button className="bg-blue-500 hover:bg-blue-700 text-white font-bold py-2 px-4 rounded">
            Manage API Keys
          </button>
        </div>
      </div>
    </div>
  );
};

export default Profile; 