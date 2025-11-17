import React, { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { chatbotAPI } from '../services/api';
import './CreateBot.css';

const CreateBot = () => {
  const [formData, setFormData] = useState({
    name: '',
    instagram_account_id: '',
    instagram_username: '',
    access_token: '',
  });
  const [error, setError] = useState('');
  const [loading, setLoading] = useState(false);
  const navigate = useNavigate();

  const handleSubmit = async (e) => {
    e.preventDefault();
    setError('');
    setLoading(true);

    try {
      const response = await chatbotAPI.create(formData);
      navigate(`/bot/${response.data.id}`);
    } catch (err) {
      setError(err.response?.data?.detail || 'Failed to create chatbot');
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="create-bot-container">
      <div className="create-bot-card">
        <h2>Create New Chatbot</h2>
        
        {error && <div className="error-message">{error}</div>}
        
        <form onSubmit={handleSubmit}>
          <div className="form-group">
            <label>Bot Name *</label>
            <input
              type="text"
              value={formData.name}
              onChange={(e) => setFormData({ ...formData, name: e.target.value })}
              placeholder="e.g., Customer Support Bot"
              required
              disabled={loading}
            />
          </div>

          <div className="form-group">
            <label>Instagram Account ID *</label>
            <input
              type="text"
              value={formData.instagram_account_id}
              onChange={(e) => setFormData({ ...formData, instagram_account_id: e.target.value })}
              placeholder="e.g., 17841400123456789"
              required
              disabled={loading}
            />
            <small>Find this in Meta Business Suite → Instagram Settings</small>
          </div>

          <div className="form-group">
            <label>Instagram Username (Optional)</label>
            <input
              type="text"
              value={formData.instagram_username}
              onChange={(e) => setFormData({ ...formData, instagram_username: e.target.value })}
              placeholder="e.g., mybusiness"
              disabled={loading}
            />
          </div>

          <div className="form-group">
            <label>Access Token *</label>
            <textarea
              value={formData.access_token}
              onChange={(e) => setFormData({ ...formData, access_token: e.target.value })}
              placeholder="Paste your Instagram Page Access Token here"
              rows="4"
              required
              disabled={loading}
            />
            <small>Get this from Meta Developers → Your App → Access Tokens</small>
          </div>

          <div className="form-actions">
            <button
              type="button"
              onClick={() => navigate('/dashboard')}
              className="btn-secondary"
              disabled={loading}
            >
              Cancel
            </button>
            <button type="submit" className="btn-primary" disabled={loading}>
              {loading ? 'Creating...' : 'Create Chatbot'}
            </button>
          </div>
        </form>

        <div className="help-section">
          <h3>How to get your Instagram credentials:</h3>
          <ol>
            <li>Go to Meta Business Suite (business.facebook.com)</li>
            <li>Select your Instagram account</li>
            <li>Go to Settings → Instagram Account → Account ID</li>
            <li>For Access Token: developers.facebook.com → Your App → Tokens</li>
          </ol>
        </div>
      </div>
    </div>
  );
};

export default CreateBot;
