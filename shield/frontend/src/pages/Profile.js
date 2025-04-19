import React, { useState, useEffect, useContext, useCallback } from 'react';
import axios from 'axios';
import AuthContext from '../utils/AuthContext';
import { FaGithub, FaShieldAlt, FaUserLock, FaCodeBranch, FaBuilding, FaExclamationTriangle, FaCheck, FaLock } from 'react-icons/fa';

const Profile = () => {
  const { 
    user, 
    updateUser, 
    token,
    connectToGithub, 
    disconnectFromGithub,
    fetchGithubRepositories,
    githubRepos,
    githubLoading 
  } = useContext(AuthContext);

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
  const [selectedRepos, setSelectedRepos] = useState([]);
  const [organizationSettings, setOrganizationSettings] = useState({
    name: '',
    industry: '',
    size: '',
    tech_stack: []
  });
  const [securitySettings, setSecuritySettings] = useState({
    scanFrequency: 'weekly',
    notificationEmail: '',
    criticalThreshold: 'high',
    autoRemediation: false
  });

  const loadGithubRepositories = useCallback(async () => {
    if (user?.github_connected) {
      await fetchGithubRepositories();
    }
  }, [user?.github_connected, fetchGithubRepositories]);

  useEffect(() => {
    if (user) {
      setFormData({
        username: user.username || '',
        email: user.email || '',
        current_password: '',
        new_password: '',
        confirm_password: ''
      });
      
      if (user.github_connected) {
        loadGithubRepositories();
      }
      
      setLoading(false);
    }
  }, [user, loadGithubRepositories]);

  const handleInputChange = (e) => {
    setFormData({
      ...formData,
      [e.target.name]: e.target.value
    });
  };

  const handleOrgSettingsChange = (e) => {
    const { name, value } = e.target;
    setOrganizationSettings({
      ...organizationSettings,
      [name]: value
    });
  };

  const handleSecuritySettingsChange = (e) => {
    const { name, value, type, checked } = e.target;
    setSecuritySettings({
      ...securitySettings,
      [name]: type === 'checkbox' ? checked : value
    });
  };

  const handleRepoSelect = (repo) => {
    if (selectedRepos.some(r => r.id === repo.id)) {
      setSelectedRepos(selectedRepos.filter(r => r.id !== repo.id));
    } else {
      setSelectedRepos([...selectedRepos, repo]);
    }
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

  const handleConnectGithub = async () => {
    try {
      await connectToGithub();
    } catch (err) {
      setError('Failed to connect to GitHub');
    }
  };

  const handleDisconnectGithub = async () => {
    try {
      const success = await disconnectFromGithub();
      if (success) {
        setSelectedRepos([]);
        setSuccess('GitHub account disconnected successfully');
      }
    } catch (err) {
      setError('Failed to disconnect from GitHub');
    }
  };

  const handleSaveRepos = async () => {
    setError('');
    setSuccess('');
    
    try {
      // This would send the selected repos to the backend for scanning
      await axios.post(
        `${process.env.REACT_APP_API_URL || 'http://localhost:5000'}/api/github/repositories/scan`,
        { repositories: selectedRepos.map(repo => repo.full_name) },
        {
          headers: {
            Authorization: `Bearer ${token}`
          }
        }
      );
      
      setSuccess('Repositories saved for scanning');
    } catch (err) {
      setError('Failed to save repositories');
    }
  };

  if (loading) {
    return <div className="flex justify-center items-center h-64">Loading...</div>;
  }

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
                    <p className="text-gray-800 font-medium">{user?.username}</p>
                  </div>
                  
                  <div className="mb-4">
                    <p className="text-gray-600 text-sm">Email</p>
                    <p className="text-gray-800 font-medium">{user?.email}</p>
                  </div>
                  
                  <div className="mb-4">
                    <p className="text-gray-600 text-sm">Role</p>
                    <p className="text-gray-800 font-medium">{user?.role || 'Security Manager'}</p>
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
          
          {/* Security Settings */}
          <div className="bg-white rounded-lg shadow-md overflow-hidden mb-6">
            <div className="bg-gray-800 text-white px-6 py-4">
              <h2 className="text-xl font-bold flex items-center">
                <FaShieldAlt className="mr-2" /> Security Settings
              </h2>
            </div>
            <div className="p-6">
              <div className="mb-4">
                <label className="block text-gray-700 text-sm font-bold mb-2">
                  Scan Frequency
                </label>
                <select
                  name="scanFrequency"
                  value={securitySettings.scanFrequency}
                  onChange={handleSecuritySettingsChange}
                  className="shadow border rounded w-full py-2 px-3 text-gray-700 leading-tight focus:outline-none focus:shadow-outline"
                >
                  <option value="daily">Daily</option>
                  <option value="weekly">Weekly</option>
                  <option value="monthly">Monthly</option>
                </select>
              </div>
              
              <div className="mb-4">
                <label className="block text-gray-700 text-sm font-bold mb-2">
                  Notification Email
                </label>
                <input
                  type="email"
                  name="notificationEmail"
                  value={securitySettings.notificationEmail}
                  onChange={handleSecuritySettingsChange}
                  placeholder={user?.email}
                  className="shadow appearance-none border rounded w-full py-2 px-3 text-gray-700 leading-tight focus:outline-none focus:shadow-outline"
                />
                <p className="text-gray-600 text-xs mt-1">Leave empty to use your primary email</p>
              </div>
              
              <div className="mb-4">
                <label className="block text-gray-700 text-sm font-bold mb-2">
                  Critical Alert Threshold
                </label>
                <select
                  name="criticalThreshold"
                  value={securitySettings.criticalThreshold}
                  onChange={handleSecuritySettingsChange}
                  className="shadow border rounded w-full py-2 px-3 text-gray-700 leading-tight focus:outline-none focus:shadow-outline"
                >
                  <option value="low">Low (All Issues)</option>
                  <option value="medium">Medium</option>
                  <option value="high">High</option>
                  <option value="critical">Critical Only</option>
                </select>
              </div>
              
              <div className="mb-4 flex items-center">
                <input
                  type="checkbox"
                  id="autoRemediation"
                  name="autoRemediation"
                  checked={securitySettings.autoRemediation}
                  onChange={handleSecuritySettingsChange}
                  className="mr-2"
                />
                <label htmlFor="autoRemediation" className="text-gray-700 font-bold">
                  Enable Auto-Remediation Suggestions
                </label>
              </div>
              
              <div className="mt-6">
                <button className="bg-blue-500 hover:bg-blue-700 text-white font-bold py-2 px-4 rounded focus:outline-none focus:shadow-outline">
                  Save Security Settings
                </button>
              </div>
            </div>
          </div>
        </div>
        
        <div className="w-full lg:w-2/3">
          {/* GitHub Integration */}
          <div className="bg-white rounded-lg shadow-md overflow-hidden mb-6">
            <div className="bg-gray-900 text-white px-6 py-4">
              <h2 className="text-xl font-bold flex items-center">
                <FaGithub className="mr-2" /> GitHub Integration
              </h2>
            </div>
            <div className="p-6">
              {user?.github_connected ? (
                <div>
                  <div className="flex items-center justify-between mb-6">
                    <div className="flex items-center">
                      <div className="bg-green-100 text-green-800 flex items-center px-3 py-1 rounded-full mr-4">
                        <FaCheck className="mr-1" /> Connected
                      </div>
                      <span className="font-semibold">{user.github_username}</span>
                      {user.github_avatar_url && (
                        <img 
                          src={user.github_avatar_url} 
                          alt="GitHub Avatar" 
                          className="h-8 w-8 rounded-full ml-2" 
                        />
                      )}
                    </div>
                    <button
                      onClick={handleDisconnectGithub}
                      className="bg-red-500 hover:bg-red-700 text-white py-2 px-4 rounded"
                    >
                      Disconnect GitHub
                    </button>
                  </div>
                  
                  {/* Repository Selection */}
                  <div className="mt-4">
                    <h3 className="text-lg font-semibold mb-4 flex items-center">
                      <FaCodeBranch className="mr-2" /> Select Repositories to Scan
                    </h3>
                    
                    {githubLoading ? (
                      <div className="text-center py-4">Loading repositories...</div>
                    ) : (
                      <div>
                        {githubRepos.length > 0 ? (
                          <div>
                            <div className="mb-4">
                              <input
                                type="text"
                                placeholder="Filter repositories..."
                                className="shadow appearance-none border rounded w-full py-2 px-3 text-gray-700 leading-tight focus:outline-none focus:shadow-outline"
                              />
                            </div>
                            
                            <div className="max-h-80 overflow-y-auto border border-gray-200 rounded">
                              {githubRepos.map(repo => (
                                <div 
                                  key={repo.id} 
                                  className={`border-b border-gray-200 last:border-b-0 p-3 ${
                                    selectedRepos.some(r => r.id === repo.id) ? 'bg-blue-50' : ''
                                  }`}
                                >
                                  <div className="flex items-center">
                                    <input
                                      type="checkbox"
                                      id={`repo-${repo.id}`}
                                      checked={selectedRepos.some(r => r.id === repo.id)}
                                      onChange={() => handleRepoSelect(repo)}
                                      className="mr-3"
                                    />
                                    <div>
                                      <label 
                                        htmlFor={`repo-${repo.id}`}
                                        className="font-medium text-gray-800 block hover:text-blue-600 cursor-pointer"
                                      >
                                        {repo.name}
                                      </label>
                                      <div className="flex items-center text-sm text-gray-600 mt-1">
                                        {repo.private ? (
                                          <span className="flex items-center mr-4">
                                            <FaLock className="mr-1 text-xs" /> Private
                                          </span>
                                        ) : (
                                          <span className="mr-4">Public</span>
                                        )}
                                        {repo.language && (
                                          <span className="mr-4">{repo.language}</span>
                                        )}
                                        <span>Updated: {new Date(repo.updated_at).toLocaleDateString()}</span>
                                      </div>
                                    </div>
                                  </div>
                                </div>
                              ))}
                            </div>
                            
                            <div className="mt-4 flex justify-between items-center">
                              <div className="text-sm text-gray-600">
                                {selectedRepos.length} of {githubRepos.length} repositories selected
                              </div>
                              <button
                                onClick={handleSaveRepos}
                                disabled={selectedRepos.length === 0}
                                className={`${
                                  selectedRepos.length === 0
                                    ? 'bg-gray-300 cursor-not-allowed'
                                    : 'bg-blue-500 hover:bg-blue-700'
                                } text-white font-bold py-2 px-4 rounded`}
                              >
                                Save and Start Scanning
                              </button>
                            </div>
                          </div>
                        ) : (
                          <div className="text-center py-6 bg-gray-50 rounded border border-gray-200">
                            <FaExclamationTriangle className="text-yellow-500 text-4xl mx-auto mb-2" />
                            <h3 className="text-lg font-semibold mb-1">No repositories found</h3>
                            <p className="text-gray-600">Your GitHub account doesn't have any accessible repositories</p>
                          </div>
                        )}
                      </div>
                    )}
                  </div>
                </div>
              ) : (
                <div className="text-center py-8">
                  <FaGithub className="text-5xl mx-auto mb-4 text-gray-700" />
                  <h3 className="text-xl font-semibold mb-2">Connect Your GitHub Account</h3>
                  <p className="text-gray-600 mb-6 max-w-md mx-auto">
                    Connect your GitHub account to scan your repositories for security vulnerabilities and get customized recommendations.
                  </p>
                  <button
                    onClick={handleConnectGithub}
                    className="bg-gray-800 hover:bg-gray-900 text-white font-bold py-3 px-6 rounded-lg flex items-center mx-auto"
                  >
                    <FaGithub className="mr-2" /> Connect with GitHub
                  </button>
                </div>
              )}
            </div>
          </div>
          
          {/* Organization Settings */}
          <div className="bg-white rounded-lg shadow-md overflow-hidden">
            <div className="bg-blue-700 text-white px-6 py-4">
              <h2 className="text-xl font-bold flex items-center">
                <FaBuilding className="mr-2" /> Organization Settings
              </h2>
            </div>
            <div className="p-6">
              <div className="mb-4">
                <label className="block text-gray-700 text-sm font-bold mb-2">
                  Organization Name
                </label>
                <input
                  type="text"
                  name="name"
                  value={organizationSettings.name}
                  onChange={handleOrgSettingsChange}
                  placeholder="Enter your organization name"
                  className="shadow appearance-none border rounded w-full py-2 px-3 text-gray-700 leading-tight focus:outline-none focus:shadow-outline"
                />
              </div>
              
              <div className="mb-4">
                <label className="block text-gray-700 text-sm font-bold mb-2">
                  Industry
                </label>
                <select
                  name="industry"
                  value={organizationSettings.industry}
                  onChange={handleOrgSettingsChange}
                  className="shadow border rounded w-full py-2 px-3 text-gray-700 leading-tight focus:outline-none focus:shadow-outline"
                >
                  <option value="">Select Industry</option>
                  <option value="finance">Finance</option>
                  <option value="healthcare">Healthcare</option>
                  <option value="technology">Technology</option>
                  <option value="retail">Retail</option>
                  <option value="manufacturing">Manufacturing</option>
                  <option value="education">Education</option>
                  <option value="government">Government</option>
                  <option value="other">Other</option>
                </select>
              </div>
              
              <div className="mb-4">
                <label className="block text-gray-700 text-sm font-bold mb-2">
                  Organization Size
                </label>
                <select
                  name="size"
                  value={organizationSettings.size}
                  onChange={handleOrgSettingsChange}
                  className="shadow border rounded w-full py-2 px-3 text-gray-700 leading-tight focus:outline-none focus:shadow-outline"
                >
                  <option value="">Select Size</option>
                  <option value="1-10">1-10 employees</option>
                  <option value="11-50">11-50 employees</option>
                  <option value="51-200">51-200 employees</option>
                  <option value="201-500">201-500 employees</option>
                  <option value="501-1000">501-1000 employees</option>
                  <option value="1001+">1001+ employees</option>
                </select>
              </div>
              
              <div className="mb-6">
                <label className="block text-gray-700 text-sm font-bold mb-2">
                  Technology Stack (Choose all that apply)
                </label>
                <div className="grid grid-cols-2 gap-2">
                  {[
                    'JavaScript', 'Python', 'Java', 'C#', 'PHP', 'Ruby', 'Go',
                    'React', 'Angular', 'Vue.js', 'Node.js', 'Django', 'Rails',
                    'AWS', 'Azure', 'GCP', 'Docker', 'Kubernetes', 'MongoDB', 'MySQL'
                  ].map(tech => (
                    <div key={tech} className="flex items-center">
                      <input
                        type="checkbox"
                        id={`tech-${tech}`}
                        className="mr-2"
                      />
                      <label htmlFor={`tech-${tech}`}>{tech}</label>
                    </div>
                  ))}
                </div>
              </div>
              
              <div className="flex justify-end">
                <button className="bg-blue-500 hover:bg-blue-700 text-white font-bold py-2 px-4 rounded focus:outline-none focus:shadow-outline">
                  Save Organization Settings
                </button>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
};

export default Profile; 