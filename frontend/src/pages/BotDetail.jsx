import React, { useState, useEffect } from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import { chatbotAPI, keywordAPI } from '../services/api';
import './BotDetail.css';

const BotDetail = () => {
  const { id } = useParams();
  const navigate = useNavigate();
  const [bot, setBot] = useState(null);
  const [keywords, setKeywords] = useState([]);
  const [loading, setLoading] = useState(true);
  const [showAddModal, setShowAddModal] = useState(false);
  const [editingKeyword, setEditingKeyword] = useState(null);
  const [formData, setFormData] = useState({ trigger: '', response: '' });

  useEffect(() => {
    fetchBotData();
  }, [id]);

  const fetchBotData = async () => {
    try {
      const [botResponse, keywordsResponse] = await Promise.all([
        chatbotAPI.getById(id),
        keywordAPI.getByBotId(id),
      ]);
      setBot(botResponse.data);
      setKeywords(keywordsResponse.data);
    } catch (err) {
      alert('Failed to load bot data');
      navigate('/dashboard');
    } finally {
      setLoading(false);
    }
  };

  const handleAddKeyword = async (e) => {
    e.preventDefault();
    try {
      await keywordAPI.create({ ...formData, chatbot_id: parseInt(id) });
      setFormData({ trigger: '', response: '' });
      setShowAddModal(false);
      fetchBotData();
    } catch (err) {
      alert('Failed to add keyword');
    }
  };

  const handleUpdateKeyword = async (e) => {
    e.preventDefault();
    try {
      await keywordAPI.update(editingKeyword.id, formData);
      setEditingKeyword(null);
      setFormData({ trigger: '', response: '' });
      fetchBotData();
    } catch (err) {
      alert('Failed to update keyword');
    }
  };

  const handleDeleteKeyword = async (keywordId) => {
    if (!window.confirm('Delete this keyword?')) return;
    try {
      await keywordAPI.delete(keywordId);
      fetchBotData();
    } catch (err) {
      alert('Failed to delete keyword');
    }
  };

  const openEditModal = (keyword) => {
    setEditingKeyword(keyword);
    setFormData({ trigger: keyword.trigger, response: keyword.response });
  };

  if (loading) {
    return <div className="loading">Loading...</div>;
  }

  return (
    <div className="bot-detail">
      <header className="bot-detail-header">
        <button onClick={() => navigate('/dashboard')} className="btn-back">
          ← Back to Dashboard
        </button>
        <h1>{bot?.name}</h1>
      </header>

      <div className="bot-info">
        <p><strong>Instagram:</strong> @{bot?.instagram_username || 'N/A'}</p>
        <p><strong>Status:</strong> {bot?.is_active ? '✅ Active' : '❌ Inactive'}</p>
      </div>

      <div className="keywords-section">
        <div className="section-header">
          <h2>Keywords & Responses</h2>
          <button onClick={() => setShowAddModal(true)} className="btn-primary">
            + Add Keyword
          </button>
        </div>

        {keywords.length === 0 ? (
          <div className="empty-state">
            <p>No keywords yet. Add your first one!</p>
          </div>
        ) : (
          <div className="keywords-list">
            {keywords.map((keyword) => (
              <div key={keyword.id} className="keyword-card">
                <div className="keyword-content">
                  <div className="keyword-trigger">
                    <strong>Trigger:</strong> {keyword.trigger}
                  </div>
                  <div className="keyword-response">
                    <strong>Response:</strong> {keyword.response}
                  </div>
                </div>
                <div className="keyword-actions">
                  <button onClick={() => openEditModal(keyword)} className="btn-edit">
                    Edit
                  </button>
                  <button onClick={() => handleDeleteKeyword(keyword.id)} className="btn-delete">
                    Delete
                  </button>
                </div>
              </div>
            ))}
          </div>
        )}
      </div>

      {/* Add Keyword Modal */}
      {showAddModal && (
        <div className="modal-overlay" onClick={() => setShowAddModal(false)}>
          <div className="modal" onClick={(e) => e.stopPropagation()}>
            <h3>Add New Keyword</h3>
            <form onSubmit={handleAddKeyword}>
              <div className="form-group">
                <label>Trigger Word/Phrase</label>
                <input
                  type="text"
                  value={formData.trigger}
                  onChange={(e) => setFormData({ ...formData, trigger: e.target.value })}
                  placeholder="e.g., cena, hello, pomoć"
                  required
                />
              </div>
              <div className="form-group">
                <label>Bot Response</label>
                <textarea
                  value={formData.response}
                  onChange={(e) => setFormData({ ...formData, response: e.target.value })}
                  placeholder="Enter the automated response..."
                  rows="4"
                  required
                />
              </div>
              <div className="modal-actions">
                <button type="button" onClick={() => setShowAddModal(false)} className="btn-secondary">
                  Cancel
                </button>
                <button type="submit" className="btn-primary">Add</button>
              </div>
            </form>
          </div>
        </div>
      )}

      {/* Edit Keyword Modal */}
      {editingKeyword && (
        <div className="modal-overlay" onClick={() => setEditingKeyword(null)}>
          <div className="modal" onClick={(e) => e.stopPropagation()}>
            <h3>Edit Keyword</h3>
            <form onSubmit={handleUpdateKeyword}>
              <div className="form-group">
                <label>Trigger Word/Phrase</label>
                <input
                  type="text"
                  value={formData.trigger}
                  onChange={(e) => setFormData({ ...formData, trigger: e.target.value })}
                  required
                />
              </div>
              <div className="form-group">
                <label>Bot Response</label>
                <textarea
                  value={formData.response}
                  onChange={(e) => setFormData({ ...formData, response: e.target.value })}
                  rows="4"
                  required
                />
              </div>
              <div className="modal-actions">
                <button type="button" onClick={() => setEditingKeyword(null)} className="btn-secondary">
                  Cancel
                </button>
                <button type="submit" className="btn-primary">Update</button>
              </div>
            </form>
          </div>
        </div>
      )}
    </div>
  );
};

export default BotDetail;
