import React, { useState, useEffect } from 'react';
import { useLocation, useNavigate } from 'react-router-dom';
import api from '../services/api';

const ComplaintForm = () => {
  const location = useLocation();
  const navigate = useNavigate();
  const { service, userType } = location.state || {};
  
  const [categories, setCategories] = useState([]);
  const [selectedCategory, setSelectedCategory] = useState('');
  const [subIssues, setSubIssues] = useState([]);
  const [selectedSubIssue, setSelectedSubIssue] = useState('');
  const [description, setDescription] = useState('');
  const [loading, setLoading] = useState(false);
  const [response, setResponse] = useState('');
  const [selectedImage, setSelectedImage] = useState(null);
  const [imagePreview, setImagePreview] = useState('');

  useEffect(() => {
    if (!service || !userType) {
      navigate('/dashboard');
      return;
    }
    fetchCategories();
  }, [service, userType, navigate]);

  const fetchCategories = async () => {
    try {
      const response = await api.get(`/categories/${service}/${userType}`);
      setCategories(response.data.categories || []);
    } catch (error) {
      console.error('Error fetching categories:', error);
    }
  };

  const handleCategoryChange = async (categoryId) => {
    setSelectedCategory(categoryId);
    setSelectedSubIssue('');
    
    try {
      const response = await api.get(`/subissues/${service}/${userType}/${categoryId}`);
      setSubIssues(response.data.subissues || []);
    } catch (error) {
      console.error('Error fetching sub-issues:', error);
    }
  };

  const handleImageChange = (e) => {
    const file = e.target.files[0];
    if (file) {
      setSelectedImage(file);
      const reader = new FileReader();
      reader.onloadend = () => {
        setImagePreview(reader.result);
      };
      reader.readAsDataURL(file);
    }
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    if (!selectedCategory || !selectedSubIssue || !description.trim()) {
      alert('Please fill in all fields');
      return;
    }

    setLoading(true);
    try {
      let imageData = null;
      if (selectedImage) {
        const reader = new FileReader();
        imageData = await new Promise((resolve) => {
          reader.onloadend = () => {
            const base64String = reader.result.split(',')[1]; // Remove data:image/jpeg;base64, prefix
            resolve(base64String);
          };
          reader.readAsDataURL(selectedImage);
        });
      }

      const response = await api.post('/complaint', {
        service,
        user_type: userType,
        category: selectedCategory,
        sub_issue: selectedSubIssue,
        description: description.trim(),
        image_data: imageData
      });

      setResponse(response.data.solution || 'Your complaint has been submitted and is being processed.');
    } catch (error) {
      setResponse('Error processing your complaint. Please try again.');
    }
    setLoading(false);
  };

  const handleBack = () => {
    navigate('/dashboard');
  };

  return (
    <div className="container">
      <div className="header">
        <h1>Submit Complaint</h1>
        <p>Service: {service?.replace('_', ' ').toUpperCase()} | User: {userType?.replace('_', ' ').toUpperCase()}</p>
        <button className="btn btn-secondary" onClick={handleBack} style={{ float: 'right' }}>
          Back to Dashboard
        </button>
      </div>

      <div className="card">
        <form onSubmit={handleSubmit}>
          <div className="form-group">
            <label className="form-label">Select Issue Category</label>
            <select 
              className="form-input"
              value={selectedCategory}
              onChange={(e) => handleCategoryChange(e.target.value)}
              required
            >
              <option value="">-- Select Category --</option>
              {categories.map(category => (
                <option key={category.id} value={category.id}>
                  {category.name}
                </option>
              ))}
            </select>
          </div>

          {subIssues.length > 0 && (
            <div className="form-group">
              <label className="form-label">Select Specific Issue</label>
              <select 
                className="form-input"
                value={selectedSubIssue}
                onChange={(e) => setSelectedSubIssue(e.target.value)}
                required
              >
                <option value="">-- Select Specific Issue --</option>
                {subIssues.map(subIssue => (
                  <option key={subIssue.id} value={subIssue.id}>
                    {subIssue.name}
                  </option>
                ))}
              </select>
            </div>
          )}

          <div className="form-group">
            <label className="form-label">Upload Image (if applicable)</label>
            <input
              type="file"
              className="form-input"
              accept="image/*"
              onChange={handleImageChange}
            />
            {imagePreview && (
              <div style={{ marginTop: '10px' }}>
                <img 
                  src={imagePreview} 
                  alt="Preview" 
                  style={{ maxWidth: '300px', maxHeight: '200px', borderRadius: '8px' }}
                />
              </div>
            )}
            <small style={{ color: '#666', fontSize: '14px' }}>
              Some issues may require image evidence for better resolution
            </small>
          </div>

          <div className="form-group">
            <label className="form-label">Describe Your Issue</label>
            <textarea
              className="form-input"
              rows="6"
              value={description}
              onChange={(e) => setDescription(e.target.value)}
              placeholder="Please provide detailed information about your issue..."
              required
            />
          </div>

          <button 
            type="submit" 
            className="btn btn-primary" 
            disabled={loading}
            style={{ width: '100%' }}
          >
            {loading ? 'Processing...' : 'Submit Complaint'}
          </button>
        </form>

        {response && (
          <div className={`${response.includes('Error') ? 'error-message' : 'success-message'}`} style={{ marginTop: '20px' }}>
            <h4>AI Agent Response:</h4>
            <div style={{ whiteSpace: 'pre-line', lineHeight: '1.6' }}>{response}</div>
          </div>
        )}
      </div>
    </div>
  );
};

export default ComplaintForm;