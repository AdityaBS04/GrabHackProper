import React, { useState, useEffect, useRef } from 'react';
import { useLocation, useNavigate } from 'react-router-dom';
import api from '../services/api';
import '../Mobile.css';

const ChatBot = () => {
  const location = useLocation();
  const navigate = useNavigate();
  const { service, userType, orderId } = location.state || {};
  
  // Get username from localStorage
  const user = JSON.parse(localStorage.getItem('user') || '{}');
  const username = user.username || 'anonymous';
  
  const [messages, setMessages] = useState([]);
  const [currentInput, setCurrentInput] = useState('');
  const [loading, setLoading] = useState(false);
  const [conversationId] = useState(Date.now().toString());
  const [categories, setCategories] = useState([]);
  const [selectedCategory, setSelectedCategory] = useState('');
  const [subIssues, setSubIssues] = useState([]);
  const [selectedSubIssue, setSelectedSubIssue] = useState('');
  const [showCategorySelection, setShowCategorySelection] = useState(true);
  const [showSubIssueSelection, setShowSubIssueSelection] = useState(false);
  const messagesEndRef = useRef(null);

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: "smooth" });
  };

  useEffect(() => {
    scrollToBottom();
  }, [messages]);

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
      
      // Initialize conversation with category selection
      const serviceName = service.replace('_', ' ').split(' ').map(word => 
        word.charAt(0).toUpperCase() + word.slice(1).toLowerCase()
      ).join(' ');
      
      const welcomeMessage = {
        id: Date.now(),
        text: `Hello! I'm your ${serviceName} support agent. Please select the category that best describes your issue:`,
        sender: 'bot',
        timestamp: new Date(),
        showCategories: true
      };
      setMessages([welcomeMessage]);
    } catch (error) {
      console.error('Error fetching categories:', error);
      const errorMessage = {
        id: Date.now(),
        text: 'Sorry, I had trouble loading the issue categories. Please try refreshing the page.',
        sender: 'bot',
        timestamp: new Date()
      };
      setMessages([errorMessage]);
    }
  };

  const handleCategorySelect = async (categoryId, categoryName) => {
    setSelectedCategory(categoryId);
    
    // Add user selection message
    const userMessage = {
      id: Date.now(),
      text: `I selected: ${categoryName}`,
      sender: 'user',
      timestamp: new Date()
    };
    setMessages(prev => [...prev, userMessage]);
    
    setLoading(true);
    try {
      const response = await api.get(`/subissues/${service}/${userType}/${categoryId}`);
      setSubIssues(response.data.subissues || []);
      
      const botMessage = {
        id: Date.now() + 1,
        text: 'Great! Now please select the specific issue you\'re experiencing:',
        sender: 'bot',
        timestamp: new Date(),
        showSubIssues: true
      };
      
      setMessages(prev => [...prev, botMessage]);
      setShowCategorySelection(false);
      setShowSubIssueSelection(true);
    } catch (error) {
      console.error('Error fetching sub-issues:', error);
      const errorMessage = {
        id: Date.now() + 1,
        text: 'Sorry, I had trouble loading the specific issues. Please try again.',
        sender: 'bot',
        timestamp: new Date()
      };
      setMessages(prev => [...prev, errorMessage]);
    }
    setLoading(false);
  };

  const handleSubIssueSelect = async (subIssueId, subIssueName) => {
    setSelectedSubIssue(subIssueId);
    
    // Add user selection message
    const userMessage = {
      id: Date.now(),
      text: `I selected: ${subIssueName}`,
      sender: 'user',
      timestamp: new Date()
    };
    setMessages(prev => [...prev, userMessage]);
    
    // Now start AI conversation
    const botMessage = {
      id: Date.now() + 1,
      text: 'Thank you for selecting your issue. Please describe what happened in detail, and I\'ll help you resolve it.',
      sender: 'bot',
      timestamp: new Date()
    };
    
    setMessages(prev => [...prev, botMessage]);
    setShowSubIssueSelection(false);
  };

  const handleSendMessage = async () => {
    if (!currentInput.trim() || loading || !selectedSubIssue) return;

    const userMessage = {
      id: Date.now(),
      text: currentInput.trim(),
      sender: 'user',
      timestamp: new Date()
    };

    setMessages(prev => [...prev, userMessage]);
    setCurrentInput('');
    setLoading(true);

    try {
      const response = await api.post('/chat', {
        message: currentInput.trim(),
        service,
        user_type: userType,
        username: username,
        conversation_id: conversationId,
        category: selectedCategory,
        sub_issue: selectedSubIssue,
        messages: messages,
        order_id: orderId
      });

      const botMessage = {
        id: Date.now() + 1,
        text: response.data.response || 'I apologize, but I encountered an error processing your request. Please try again.',
        sender: 'bot',
        timestamp: new Date(),
        requiresImage: response.data.requires_image || false,
        imageRequest: response.data.image_request || null
      };

      setMessages(prev => [...prev, botMessage]);
    } catch (error) {
      console.error('Error sending message:', error);
      const errorMessage = {
        id: Date.now() + 1,
        text: 'Sorry, I encountered an error. Please try again or contact support if the issue persists.',
        sender: 'bot',
        timestamp: new Date()
      };
      setMessages(prev => [...prev, errorMessage]);
    }
    setLoading(false);
  };

  const handleImageUpload = async (file, messageId) => {
    try {
      const reader = new FileReader();
      reader.onloadend = async () => {
        const base64String = reader.result.split(',')[1];
        setLoading(true);

        try {
          const response = await api.post('/chat/image', {
            image_data: base64String,
            service,
            user_type: userType,
            username: username,
            conversation_id: conversationId,
            message_id: messageId
          });

          const botMessage = {
            id: Date.now(),
            text: response.data.response || 'Thank you for the image. Let me analyze it and provide a solution.',
            sender: 'bot',
            timestamp: new Date()
          };

          setMessages(prev => [...prev, botMessage]);
        } catch (error) {
          console.error('Error uploading image:', error);
          const errorMessage = {
            id: Date.now(),
            text: 'Sorry, I had trouble processing your image. Please try uploading it again.',
            sender: 'bot',
            timestamp: new Date()
          };
          setMessages(prev => [...prev, errorMessage]);
        }
        setLoading(false);
      };
      reader.readAsDataURL(file);
    } catch (error) {
      console.error('Error reading file:', error);
    }
  };

  const handleKeyPress = (e) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault();
      handleSendMessage();
    }
  };

  const handleBack = () => {
    navigate('/dashboard');
  };

  const getServiceEmoji = (service) => {
    const serviceMap = {
      'grab_food': '🍕',
      'grab_cabs': '🚗', 
      'grab_mart': '🛒',
      'grab_express': '📦'
    };
    return serviceMap[service] || '🤖';
  };

  const getUserTypeEmoji = (userType) => {
    const userMap = {
      'customer': '👤',
      'delivery_agent': '🏍️',
      'restaurant': '🍳',
      'driver': '🚗',
      'darkstore': '🏪'
    };
    return userMap[userType] || '👤';
  };

  return (
    <div className="App">
      <div className="mobile-container">
        <div className="mobile-header">
          <button className="mobile-header-icon-btn" onClick={handleBack}>
            ←
          </button>
          <div className="mobile-header-content">
            <h1>{getServiceEmoji(service)} AI Support Chat</h1>
            <p>{service?.replace('_', ' ').replace(/\b\w/g, l => l.toUpperCase())} • {getUserTypeEmoji(userType)} {userType?.replace('_', ' ').replace(/\b\w/g, l => l.toUpperCase())}</p>
          </div>
        </div>

        <div className="mobile-chat-container">
          <div className="mobile-chat-messages">
            {messages.map((message) => (
              <div key={message.id} className={`mobile-message ${message.sender}`}>
                <div className={`mobile-message-bubble ${message.sender}`}>
                  <div>
                    {message.text.split(/(https?:\/\/[^\s]+)/g).map((part, index) => {
                      if (part.match(/https?:\/\/[^\s]+/)) {
                        return (
                          <a 
                            key={index} 
                            href={part} 
                            target="_blank" 
                            rel="noopener noreferrer" 
                            style={{ 
                              color: '#007bff', 
                              textDecoration: 'underline',
                              fontWeight: 'bold'
                            }}
                          >
                            {part}
                          </a>
                        );
                      }
                      return part;
                    })}
                  </div>
                  
                  {/* Category selection buttons */}
                  {message.showCategories && message.sender === 'bot' && (
                    <div style={{ marginTop: '12px' }}>
                      {categories.map((category) => (
                        <button
                          key={category.id}
                          onClick={() => handleCategorySelect(category.id, category.name)}
                          className="mobile-category-btn"
                        >
                          {category.name}
                        </button>
                      ))}
                    </div>
                  )}
                  
                  {/* Sub-issue selection buttons */}
                  {message.showSubIssues && message.sender === 'bot' && (
                    <div style={{ marginTop: '12px' }}>
                      {subIssues.map((subIssue) => (
                        <button
                          key={subIssue.id}
                          onClick={() => handleSubIssueSelect(subIssue.id, subIssue.name)}
                          className="mobile-subissue-btn"
                        >
                          {subIssue.name}
                        </button>
                      ))}
                    </div>
                  )}
                  
                  {/* Image upload component for bot messages requesting images */}
                  {message.requiresImage && message.sender === 'bot' && (
                    <div className="mobile-image-upload">
                      <input
                        type="file"
                        accept="image/*"
                        onChange={(e) => {
                          if (e.target.files[0]) {
                            handleImageUpload(e.target.files[0], message.id);
                          }
                        }}
                      />
                      <div className="mobile-image-help">
                        📷 {message.imageRequest || "Upload an image to help resolve your issue"}
                      </div>
                    </div>
                  )}
                  
                  <div className="mobile-message-time">
                    {message.timestamp.toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' })}
                  </div>
                </div>
              </div>
            ))}
            
            {loading && (
              <div className="mobile-message bot">
                <div className="mobile-message-bubble bot">
                  <div style={{ display: 'flex', alignItems: 'center', gap: '8px' }}>
                    <div>🤖 Thinking</div>
                    <div className="mobile-spinner" style={{ width: '16px', height: '16px' }}></div>
                  </div>
                </div>
              </div>
            )}
            <div ref={messagesEndRef} />
          </div>

          <div className="mobile-chat-input">
            <textarea
              value={currentInput}
              onChange={(e) => setCurrentInput(e.target.value)}
              onKeyPress={handleKeyPress}
              placeholder={selectedSubIssue ? "Type your message..." : "Select a category first..."}
              className="mobile-chat-textarea"
              rows="2"
              disabled={loading || !selectedSubIssue}
            />
            <button
              onClick={handleSendMessage}
              disabled={loading || !currentInput.trim() || !selectedSubIssue}
              className="mobile-chat-send"
            >
              {loading ? '⏳' : '➤'}
            </button>
          </div>
        </div>
      </div>
    </div>
  );
};

export default ChatBot;