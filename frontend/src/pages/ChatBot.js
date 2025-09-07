import React, { useState, useEffect, useRef } from 'react';
import { useLocation, useNavigate } from 'react-router-dom';
import api from '../services/api';

const ChatBot = () => {
  const location = useLocation();
  const navigate = useNavigate();
  const { service, userType } = location.state || {};
  
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
        messages: messages
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

  return (
    <div className="container">
      <div className="header">
        <h1>AI Support Chat</h1>
        <p>Service: {service?.replace('_', ' ').toUpperCase()} | User: {userType?.replace('_', ' ').toUpperCase()}</p>
        <button className="btn btn-secondary" onClick={handleBack} style={{ float: 'right' }}>
          Back to Dashboard
        </button>
      </div>

      <div className="chat-container" style={{ 
        height: '60vh', 
        border: '1px solid #ddd', 
        borderRadius: '8px', 
        display: 'flex', 
        flexDirection: 'column',
        backgroundColor: '#f9f9f9'
      }}>
        <div className="chat-messages" style={{ 
          flex: 1, 
          overflowY: 'auto', 
          padding: '20px',
          display: 'flex',
          flexDirection: 'column',
          gap: '15px'
        }}>
          {messages.map((message) => (
            <div key={message.id} style={{
              display: 'flex',
              justifyContent: message.sender === 'user' ? 'flex-end' : 'flex-start'
            }}>
              <div style={{
                maxWidth: '70%',
                padding: '12px 16px',
                borderRadius: '18px',
                backgroundColor: message.sender === 'user' ? '#007bff' : '#e9ecef',
                color: message.sender === 'user' ? 'white' : '#333',
                wordWrap: 'break-word',
                whiteSpace: 'pre-wrap'
              }}>
                <div>{message.text}</div>
                
                {/* Category selection buttons */}
                {message.showCategories && message.sender === 'bot' && (
                  <div style={{ marginTop: '10px' }}>
                    {categories.map((category) => (
                      <button
                        key={category.id}
                        onClick={() => handleCategorySelect(category.id, category.name)}
                        style={{
                          display: 'block',
                          width: '100%',
                          margin: '5px 0',
                          padding: '10px',
                          backgroundColor: '#007bff',
                          color: 'white',
                          border: 'none',
                          borderRadius: '8px',
                          cursor: 'pointer',
                          fontSize: '14px'
                        }}
                        onMouseOver={(e) => e.target.style.backgroundColor = '#0056b3'}
                        onMouseOut={(e) => e.target.style.backgroundColor = '#007bff'}
                      >
                        {category.name}
                      </button>
                    ))}
                  </div>
                )}
                
                {/* Sub-issue selection buttons */}
                {message.showSubIssues && message.sender === 'bot' && (
                  <div style={{ marginTop: '10px' }}>
                    {subIssues.map((subIssue) => (
                      <button
                        key={subIssue.id}
                        onClick={() => handleSubIssueSelect(subIssue.id, subIssue.name)}
                        style={{
                          display: 'block',
                          width: '100%',
                          margin: '5px 0',
                          padding: '10px',
                          backgroundColor: '#28a745',
                          color: 'white',
                          border: 'none',
                          borderRadius: '8px',
                          cursor: 'pointer',
                          fontSize: '14px'
                        }}
                        onMouseOver={(e) => e.target.style.backgroundColor = '#218838'}
                        onMouseOut={(e) => e.target.style.backgroundColor = '#28a745'}
                      >
                        {subIssue.name}
                      </button>
                    ))}
                  </div>
                )}
                
                {/* Image upload component for bot messages requesting images */}
                {message.requiresImage && message.sender === 'bot' && (
                  <div style={{ marginTop: '10px' }}>
                    <input
                      type="file"
                      accept="image/*"
                      onChange={(e) => {
                        if (e.target.files[0]) {
                          handleImageUpload(e.target.files[0], message.id);
                        }
                      }}
                      style={{
                        padding: '8px',
                        borderRadius: '4px',
                        border: '1px solid #ccc',
                        backgroundColor: 'white',
                        fontSize: '14px'
                      }}
                    />
                    <div style={{ fontSize: '12px', color: '#666', marginTop: '5px' }}>
                      {message.imageRequest || "Please upload an image to help resolve your issue"}
                    </div>
                  </div>
                )}
                
                <div style={{ 
                  fontSize: '11px', 
                  opacity: 0.7, 
                  marginTop: '5px',
                  color: message.sender === 'user' ? '#e0e0e0' : '#666'
                }}>
                  {message.timestamp.toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' })}
                </div>
              </div>
            </div>
          ))}
          
          {loading && (
            <div style={{ display: 'flex', justifyContent: 'flex-start' }}>
              <div style={{
                padding: '12px 16px',
                borderRadius: '18px',
                backgroundColor: '#e9ecef',
                color: '#333'
              }}>
                <div style={{ display: 'flex', alignItems: 'center', gap: '8px' }}>
                  <div>Thinking</div>
                  <div style={{ display: 'flex', gap: '2px' }}>
                    <div style={{ width: '6px', height: '6px', backgroundColor: '#666', borderRadius: '50%', animation: 'pulse 1.4s ease-in-out infinite' }}></div>
                    <div style={{ width: '6px', height: '6px', backgroundColor: '#666', borderRadius: '50%', animation: 'pulse 1.4s ease-in-out infinite', animationDelay: '0.2s' }}></div>
                    <div style={{ width: '6px', height: '6px', backgroundColor: '#666', borderRadius: '50%', animation: 'pulse 1.4s ease-in-out infinite', animationDelay: '0.4s' }}></div>
                  </div>
                </div>
              </div>
            </div>
          )}
          <div ref={messagesEndRef} />
        </div>

        <div className="chat-input" style={{ 
          padding: '20px', 
          borderTop: '1px solid #ddd',
          backgroundColor: 'white'
        }}>
          <div style={{ display: 'flex', gap: '10px', alignItems: 'flex-end' }}>
            <textarea
              value={currentInput}
              onChange={(e) => setCurrentInput(e.target.value)}
              onKeyPress={handleKeyPress}
              placeholder={selectedSubIssue ? "Type your message here..." : "Please select a category and issue first..."}
              rows="3"
              style={{
                flex: 1,
                padding: '12px',
                border: '1px solid #ddd',
                borderRadius: '20px',
                resize: 'none',
                fontSize: '14px',
                fontFamily: 'inherit'
              }}
              disabled={loading || !selectedSubIssue}
            />
            <button
              onClick={handleSendMessage}
              disabled={loading || !currentInput.trim() || !selectedSubIssue}
              style={{
                padding: '12px 24px',
                borderRadius: '20px',
                border: 'none',
                backgroundColor: '#007bff',
                color: 'white',
                cursor: loading || !currentInput.trim() ? 'not-allowed' : 'pointer',
                opacity: loading || !currentInput.trim() ? 0.6 : 1,
                fontSize: '14px',
                fontWeight: 'bold'
              }}
            >
              Send
            </button>
          </div>
        </div>
      </div>

      <style jsx>{`
        @keyframes pulse {
          0%, 80%, 100% { transform: scale(0); opacity: 0.5; }
          40% { transform: scale(1); opacity: 1; }
        }
      `}</style>
    </div>
  );
};

export default ChatBot;