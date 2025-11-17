import React, { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import { useAuth } from '../context/AuthContext';
import { chatbotAPI } from '../services/api';
import './Dashboard.css';

const Dashboard = () => {
  const [chatbots, setChatbots] = useState([]);
  const [loading, setLoading] = useState(true);
  const [showCreateModal, setShowCreateModal] = useState(false);
  const [error, setError] = useState('');
  const { user, logout } = useAuth();
  const navigate = useNavigate();

  useEffect(() => {
    fetchChatbots();
  }, []);

  const fetchChatbots = async () => {
    try {
      const response = await chatbotAPI.getAll();
      setChatbots(response.data);
    } catch (err) {
      setError('Failed to load chatbots');
    } finally {
      setLoading(false);
    }
  };

  const handleDelete = async (id) => {
    if (!window.confirm('Are you sure you want to delete this chatbot?')) return;

    try {
      await chatbotAPI.delete(id);
      setChatbots(chatbots.filter((bot) => bot.id !== id));
    } catch (err) {
      alert('Failed to delete chatbot');
    }
  };

  const toggleBotStatus = async (bot) => {
    try {
      await chatbotAPI.update(bot.id, { is_active: !bot.is_active });
      fetchChatbots();
    } catch (err) {
      alert('Failed to update bot status');
    }
  };

  if (loading) {
    return <div className="loading">Loading...</div>;
  }

  return (
    <div className="dashboard">
      <header className="dashboard-header">
        <h1>Instagram Chatbot Platform</h1>
        <div className="header-actions">
          <span>Welcome, {user?.username}</span>
          <button onClick={logout} className="btn-secondary">Logout</button>
        </div>
      </header>

      <div className="dashboard-content">
        <div className="content-header">
          <h2>Your Chatbots</h2>
          <button onClick={() => navigate('/create-bot')} className="btn-primary">
            + Create New Chatbot
          </button>
        </div>

        {error && <div className="error-message">{error}</div>}

        {chatbots.length === 0 ? (
          <div className="empty-state">
            <p>No chatbots yet. Create your first one!</p>
          </div>
        ) : (
          <div className="chatbots-grid">
            {chatbots.map((bot) => (
              <div key={bot.id} className="chatbot-card">
                <div className="card-header">
                  <h3>{bot.name}</h3>
                  <span className={`status ${bot.is_active ? 'active' : 'inactive'}`}>
                    {bot.is_active ? '● Active' : '○ Inactive'}
                  </span>
                </div>

                <div className="card-body">
                  <p><strong>Instagram:</strong> @{bot.instagram_username || 'N/A'}</p>
                  <p><strong>Account ID:</strong> {bot.instagram_account_id}</p>
                  <p><strong>Created:</strong> {new Date(bot.created_at).toLocaleDateString()}</p>
                </div>

                <div className="card-actions">
                  <button
                    onClick={() => navigate(`/bot/${bot.id}`)}
                    className="btn-primary"
                  >
                    Edit Keywords
                  </button>
                  <button
                    onClick={() => toggleBotStatus(bot)}
                    className="btn-secondary"
                  >
                    {bot.is_active ? 'Deactivate' : 'Activate'}
                  </button>
                  <button
                    onClick={() => handleDelete(bot.id)}
                    className="btn-danger"
                  >
                    Delete
                  </button>
                </div>
              </div>
            ))}
          </div>
        )}
      </div>
    </div>
  );
};

export default Dashboard;
