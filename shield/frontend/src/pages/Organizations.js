import React, { useState, useEffect } from 'react';
import { Link } from 'react-router-dom';
import axios from 'axios';

const Organizations = () => {
  const [organizations, setOrganizations] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState('');
  const [formData, setFormData] = useState({
    name: '',
    industry: '',
    description: ''
  });
  const [showForm, setShowForm] = useState(false);

  const fetchOrganizations = async () => {
    try {
      const token = localStorage.getItem('token');
      const response = await axios.get(
        `${process.env.REACT_APP_API_URL || 'http://localhost:5000'}/api/organizations`,
        {
          headers: {
            Authorization: `Bearer ${token}`
          }
        }
      );
      setOrganizations(response.data);
      setLoading(false);
    } catch (err) {
      setError('Failed to fetch organizations');
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchOrganizations();
  }, []);

  const handleInputChange = (e) => {
    setFormData({
      ...formData,
      [e.target.name]: e.target.value
    });
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    try {
      const token = localStorage.getItem('token');
      await axios.post(
        `${process.env.REACT_APP_API_URL || 'http://localhost:5000'}/api/organizations`,
        formData,
        {
          headers: {
            Authorization: `Bearer ${token}`
          }
        }
      );
      setFormData({ name: '', industry: '', description: '' });
      setShowForm(false);
      fetchOrganizations();
    } catch (err) {
      setError('Failed to create organization');
    }
  };

  if (loading) {
    return <div className="flex justify-center items-center h-64">Loading...</div>;
  }

  return (
    <div className="container mx-auto px-4">
      <div className="flex justify-between items-center mb-6">
        <h1 className="text-2xl font-bold">Organizations</h1>
        <button
          onClick={() => setShowForm(!showForm)}
          className="bg-blue-500 hover:bg-blue-700 text-white font-bold py-2 px-4 rounded"
        >
          {showForm ? 'Cancel' : 'Add Organization'}
        </button>
      </div>

      {error && (
        <div className="bg-red-100 border border-red-400 text-red-700 px-4 py-3 rounded relative mb-4" role="alert">
          <span className="block sm:inline">{error}</span>
        </div>
      )}

      {showForm && (
        <div className="bg-white shadow-md rounded px-8 pt-6 pb-8 mb-4">
          <h2 className="text-xl font-semibold mb-4">Add New Organization</h2>
          <form onSubmit={handleSubmit}>
            <div className="mb-4">
              <label className="block text-gray-700 text-sm font-bold mb-2" htmlFor="name">
                Name
              </label>
              <input
                className="shadow appearance-none border rounded w-full py-2 px-3 text-gray-700 leading-tight focus:outline-none focus:shadow-outline"
                id="name"
                type="text"
                placeholder="Organization Name"
                name="name"
                value={formData.name}
                onChange={handleInputChange}
                required
              />
            </div>
            <div className="mb-4">
              <label className="block text-gray-700 text-sm font-bold mb-2" htmlFor="industry">
                Industry
              </label>
              <input
                className="shadow appearance-none border rounded w-full py-2 px-3 text-gray-700 leading-tight focus:outline-none focus:shadow-outline"
                id="industry"
                type="text"
                placeholder="Industry"
                name="industry"
                value={formData.industry}
                onChange={handleInputChange}
                required
              />
            </div>
            <div className="mb-6">
              <label className="block text-gray-700 text-sm font-bold mb-2" htmlFor="description">
                Description
              </label>
              <textarea
                className="shadow appearance-none border rounded w-full py-2 px-3 text-gray-700 leading-tight focus:outline-none focus:shadow-outline"
                id="description"
                placeholder="Description"
                name="description"
                value={formData.description}
                onChange={handleInputChange}
                rows="3"
              ></textarea>
            </div>
            <div className="flex items-center justify-end">
              <button
                className="bg-blue-500 hover:bg-blue-700 text-white font-bold py-2 px-4 rounded focus:outline-none focus:shadow-outline"
                type="submit"
              >
                Save
              </button>
            </div>
          </form>
        </div>
      )}

      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
        {organizations.length > 0 ? (
          organizations.map((org) => (
            <Link key={org.id} to={`/organizations/${org.id}`}>
              <div className="bg-white hover:bg-gray-50 rounded-lg shadow-md p-6 transition duration-300">
                <h2 className="text-xl font-semibold text-gray-800">{org.name}</h2>
                <p className="text-sm text-gray-600 mt-1">{org.industry}</p>
                <p className="text-gray-700 mt-3 line-clamp-3">{org.description}</p>
                <div className="mt-4 flex justify-between items-center">
                  <span className="text-sm text-gray-500">
                    {org.vulnerabilities_count || 0} vulnerabilities
                  </span>
                  <span className="text-blue-500 hover:text-blue-700">View details →</span>
                </div>
              </div>
            </Link>
          ))
        ) : (
          <div className="col-span-full text-center py-10">
            <p className="text-gray-600">No organizations found. Add your first organization to get started.</p>
          </div>
        )}
      </div>
    </div>
  );
};

export default Organizations; 