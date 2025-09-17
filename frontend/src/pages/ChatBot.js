import React, { useState, useEffect, useRef } from 'react';
import { useLocation, useNavigate } from 'react-router-dom';
import api from '../services/api';
import '../Mobile.css';
import '../EnhancedAnimations.css';
import AnimatedBackground from '../components/AnimatedBackground';
import LoadingSpinner from '../components/LoadingSpinner';
import TypingIndicator from '../components/TypingIndicator';

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

  // Function to parse and format LLM output with proper styling
  const formatLLMResponse = (text) => {
    if (!text) return text;

    // Convert markdown-style formatting to HTML
    let formatted = text
      // Handle URLs first to preserve them
      .replace(/(https?:\/\/[^\s]+)/g, '<a href="$1" target="_blank" rel="noopener noreferrer" style="color: #007bff; text-decoration: underline; font-weight: bold;">$1</a>')
      // Bold text: **text** -> <strong>text</strong>
      .replace(/\*\*(.*?)\*\*/g, '<strong>$1</strong>')
      // Handle emoji headers and sections
      .replace(/^(🚨|💰|✈️|🚗|🆘|📞|📝|📋|☐|✅)\s*\*\*(.*?)\*\*/gm, '<div class="section-header">$1 <strong>$2</strong></div>')
      // Handle bullet points
      .replace(/^- (.*$)/gm, '<div class="bullet-point">• $1</div>')
      // Handle numbered lists
      .replace(/^\d+\.\s+(.*$)/gm, '<div class="numbered-point">$&</div>')
      // Handle checkbox items
      .replace(/^☐\s+(.*$)/gm, '<div class="checkbox-item">☐ $1</div>')
      // Handle checkmarks
      .replace(/^✅\s+(.*$)/gm, '<div class="checkmark-item">✅ $1</div>')
      // Convert line breaks to proper spacing
      .replace(/\n\n/g, '<div class="paragraph-break"></div>')
      .replace(/\n/g, '<br/>');

    return formatted;
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

    // Special handling for missing items - call dedicated endpoint
    if (subIssueId === 'handle_missing_items') {
      setLoading(true);
      try {
        const response = await api.post('/missing-items', {
          message: `I need to report missing items from my order`,
          username: username,
          order_id: orderId
        });

        const botMessage = {
          id: Date.now() + 1,
          text: response.data.response || 'I apologize, but I encountered an error. Please try again.',
          sender: 'bot',
          timestamp: new Date()
        };

        setMessages(prev => [...prev, botMessage]);
        setShowSubIssueSelection(false);
        setLoading(false);
        return;

      } catch (error) {
        console.error('Error getting missing items interface:', error);
        setLoading(false);
      }
    }

    // Default behavior for other issues
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

  // Function to check if message contains missing items selection interface
  const isMissingItemsSelection = (text) => {
    return (text.includes('Which items are missing from your order?') ||
           text.includes('Missing Items Selection') ||
           (text.includes('1.') && text.includes('2.') && text.includes('missing'))) &&
           !text.includes('Harassment Report') &&
           !text.includes('Select Harassment Type') &&
           !text.includes('Select Issue Type') &&
           !text.includes('Airport Booking') &&
           !text.includes('Cancellation/Refund');
  };

  // Function to check if message contains grab_cabs dropdown selection
  const isGrabCabsDropdownSelection = (text) => {
    return text.includes('📋 Select Harassment Type:') ||
           text.includes('📋 Select Issue Type:') ||
           text.includes('📋 Select Airport Issue Type:') ||
           text.includes('📋 Select Policy Issue Type:') ||
           text.includes('🚨 **Driver Harassment Report**') ||
           text.includes('🚗 **App/Booking Issues Report**') ||
           text.includes('✈️ **Airport Booking Problems**') ||
           text.includes('💰 **Cancellation/Refund Policy Issues**');
  };

  // Function to parse grab_cabs dropdown options
  const parseGrabCabsDropdownOptions = (text) => {
    const lines = text.split('\n');
    const options = [];

    for (const line of lines) {
      if (line.trim().startsWith('☐ ')) {
        const option = line.trim().substring(2).trim();
        if (option) {
          options.push(option);
        }
      }
    }

    return options;
  };

  // Function to parse items from missing items selection message
  const parseMissingItemsOptions = (text) => {
    const lines = text.split('\n');
    const items = [];

    for (const line of lines) {
      const match = line.match(/☐\s*(\d+)\.\s*(.+)$/) || line.match(/^(\d+)\.\s*(.+)$/);
      if (match) {
        const [, number, itemName] = match;
        items.push({
          number: parseInt(number),
          name: itemName.trim(),
          selected: false
        });
      }
    }

    return items;
  };

  // Function to handle item selection
  const handleItemSelection = (items, selectedItems) => {
    if (selectedItems.length === 0) {
      handleSendMessageDirect("All items are present");
    } else {
      const itemNumbers = selectedItems.map(item => item.number);
      const itemNames = selectedItems.map(item => item.name);

      if (itemNumbers.length === 1) {
        handleSendMessageDirect(`Item ${itemNumbers[0]} is missing: ${itemNames[0]}`);
      } else {
        handleSendMessageDirect(`Items ${itemNumbers.join(', ')} are missing: ${itemNames.join(', ')}`);
      }
    }
  };

  // Function to send message directly (without user input)
  const handleSendMessageDirect = async (messageText) => {
    if (loading) return;

    const userMessage = {
      id: Date.now(),
      text: messageText,
      sender: 'user',
      timestamp: new Date()
    };

    setMessages(prev => [...prev, userMessage]);
    setLoading(true);

    try {
      const response = await api.post('/chat', {
        message: messageText,
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

  // Component for rendering missing items selection interface
  const MissingItemsSelector = ({ message }) => {
    const [selectedItems, setSelectedItems] = useState([]);
    const [items, setItems] = useState([]);
    const [orderInfo, setOrderInfo] = useState({});

    useEffect(() => {
      if (isMissingItemsSelection(message.text)) {
        const parsedItems = parseMissingItemsOptions(message.text);
        setItems(parsedItems);

        // Extract order info from the text
        const orderMatch = message.text.match(/Your Order:\*\* ([^\s]+) from (.+)/);
        if (orderMatch) {
          setOrderInfo({
            orderId: orderMatch[1],
            restaurant: orderMatch[2].split('\n')[0].trim()
          });
        }
      }
    }, [message.text]);

    const toggleItemSelection = (itemIndex) => {
      const item = items[itemIndex];
      const isSelected = selectedItems.some(selected => selected.number === item.number);

      if (isSelected) {
        setSelectedItems(prev => prev.filter(selected => selected.number !== item.number));
      } else {
        setSelectedItems(prev => [...prev, item]);
      }
    };

    const submitSelection = () => {
      handleItemSelection(items, selectedItems);
    };

    if (!isMissingItemsSelection(message.text) || items.length === 0) {
      return null;
    }

    return (
      <div style={{ marginTop: '12px' }}>
        {orderInfo.orderId && (
          <div style={{
            fontSize: '13px',
            marginBottom: '12px',
            padding: '8px',
            backgroundColor: '#f8f9fa',
            borderRadius: '6px',
            color: '#666'
          }}>
            📋 <strong>Order {orderInfo.orderId}</strong> from {orderInfo.restaurant}
          </div>
        )}

        <div style={{
          fontSize: '14px',
          fontWeight: 'bold',
          marginBottom: '8px',
          color: '#2196f3'
        }}>
          📝 Select Missing Items:
        </div>

        {items.map((item, index) => {
          const isSelected = selectedItems.some(selected => selected.number === item.number);
          return (
            <div
              key={item.number}
              onClick={() => toggleItemSelection(index)}
              style={{
                display: 'flex',
                alignItems: 'center',
                padding: '8px 12px',
                margin: '4px 0',
                backgroundColor: isSelected ? '#e3f2fd' : '#f8f9fa',
                border: `2px solid ${isSelected ? '#2196f3' : '#dee2e6'}`,
                borderRadius: '6px',
                cursor: 'pointer',
                transition: 'all 0.2s ease'
              }}
            >
              <div style={{
                marginRight: '8px',
                fontSize: '18px',
                color: isSelected ? '#2196f3' : '#666'
              }}>
                {isSelected ? '✅' : '☐'}
              </div>
              <div style={{
                flex: 1,
                fontSize: '14px',
                color: isSelected ? '#2196f3' : '#333'
              }}>
                {item.number}. {item.name}
              </div>
            </div>
          );
        })}

        <div style={{
          display: 'flex',
          gap: '8px',
          marginTop: '12px',
          flexWrap: 'wrap'
        }}>
          <button
            onClick={submitSelection}
            style={{
              background: selectedItems.length > 0 ? '#dc3545' : '#28a745',
              color: 'white',
              border: 'none',
              padding: '8px 16px',
              borderRadius: '4px',
              fontSize: '12px',
              cursor: 'pointer',
              fontWeight: 'bold'
            }}
          >
            {selectedItems.length > 0
              ? `🚨 Report ${selectedItems.length} Missing Item${selectedItems.length > 1 ? 's' : ''}`
              : '✅ All Items Present'
            }
          </button>

          {selectedItems.length > 0 && (
            <button
              onClick={() => setSelectedItems([])}
              style={{
                background: '#6c757d',
                color: 'white',
                border: 'none',
                padding: '8px 16px',
                borderRadius: '4px',
                fontSize: '12px',
                cursor: 'pointer'
              }}
            >
              Clear Selection
            </button>
          )}
        </div>

        {selectedItems.length > 0 && (
          <div style={{
            marginTop: '8px',
            padding: '8px',
            backgroundColor: '#fff3cd',
            border: '1px solid #ffeaa7',
            borderRadius: '4px',
            fontSize: '12px'
          }}>
            <strong>Selected:</strong> {selectedItems.map(item => item.name).join(', ')}
          </div>
        )}
      </div>
    );
  };

  // Grab Cabs Dropdown Selector Component
  const GrabCabsDropdownSelector = ({ message }) => {
    const [selectedOption, setSelectedOption] = useState('');
    const [options, setOptions] = useState([]);

    useEffect(() => {
      if (isGrabCabsDropdownSelection(message.text)) {
        const parsedOptions = parseGrabCabsDropdownOptions(message.text);
        setOptions(parsedOptions);
      }
    }, [message.text]);

    const submitSelection = (option) => {
      setSelectedOption(option);

      // Send the selected option directly (this will add user message and call backend)
      handleSendMessageDirect(option);
    };

    if (!isGrabCabsDropdownSelection(message.text) || options.length === 0) {
      return null;
    }

    // Extract title from message
    let title = 'Select an Option';
    if (message.text.includes('Harassment Report')) {
      title = '🚨 Select Harassment Type';
    } else if (message.text.includes('App/Booking Issues')) {
      title = '🚗 Select Issue Type';
    } else if (message.text.includes('Airport Booking')) {
      title = '✈️ Select Airport Issue Type';
    } else if (message.text.includes('Cancellation/Refund')) {
      title = '💰 Select Policy Issue Type';
    }

    return (
      <div style={{ marginTop: '12px' }}>
        <div style={{
          fontSize: '16px',
          fontWeight: '600',
          marginBottom: '16px',
          color: '#1e40af',
          textAlign: 'center',
          padding: '8px 12px',
          backgroundColor: '#eff6ff',
          borderRadius: '8px',
          border: '1px solid #dbeafe'
        }}>
          {title}
        </div>

        <div style={{
          display: 'flex',
          flexDirection: 'column',
          gap: '10px',
          width: '100%'
        }}>
          {options.map((option, index) => (
            <button
              key={index}
              onClick={() => submitSelection(option)}
              style={{
                background: '#ffffff',
                border: '2px solid #e0e7ff',
                borderRadius: '12px',
                padding: '14px 18px',
                textAlign: 'left',
                fontSize: '15px',
                color: '#1e293b',
                cursor: 'pointer',
                transition: 'all 0.3s ease',
                width: '100%',
                boxShadow: '0 2px 4px rgba(0,0,0,0.05)',
                fontWeight: '500',
                lineHeight: '1.4',
                minHeight: '52px',
                display: 'flex',
                alignItems: 'center',
                justifyContent: 'flex-start',
                WebkitTapHighlightColor: 'transparent',
                userSelect: 'none'
              }}
              onMouseEnter={(e) => {
                e.target.style.borderColor = '#3b82f6';
                e.target.style.backgroundColor = '#f0f9ff';
                e.target.style.boxShadow = '0 4px 12px rgba(59, 130, 246, 0.15)';
                e.target.style.transform = 'translateY(-1px)';
              }}
              onMouseLeave={(e) => {
                e.target.style.borderColor = '#e0e7ff';
                e.target.style.backgroundColor = '#ffffff';
                e.target.style.boxShadow = '0 2px 4px rgba(0,0,0,0.05)';
                e.target.style.transform = 'translateY(0px)';
              }}
              onTouchStart={(e) => {
                e.target.style.borderColor = '#3b82f6';
                e.target.style.backgroundColor = '#f0f9ff';
                e.target.style.transform = 'scale(0.98)';
              }}
              onTouchEnd={(e) => {
                setTimeout(() => {
                  e.target.style.borderColor = '#e0e7ff';
                  e.target.style.backgroundColor = '#ffffff';
                  e.target.style.transform = 'scale(1)';
                }, 150);
              }}
            >
              <div style={{
                display: 'flex',
                alignItems: 'center',
                gap: '12px',
                width: '100%'
              }}>
                <span style={{
                  color: '#3b82f6',
                  fontSize: '18px',
                  minWidth: '18px',
                  fontWeight: 'bold'
                }}>☐</span>
                <span style={{
                  flex: 1,
                  color: '#1e293b',
                  fontSize: '15px',
                  fontWeight: '500'
                }}>{option}</span>
              </div>
            </button>
          ))}
        </div>
      </div>
    );
  };

  return (
    <div className="App">
      <AnimatedBackground />
      <div className="mobile-container">
        <div className="mobile-header">
          <button className="mobile-header-icon-btn" onClick={handleBack}>
            ←
          </button>
          <div className="mobile-header-content">
            <h1 className="animated-title">{getServiceEmoji(service)} AI Support Chat</h1>
            <p>{service?.replace('_', ' ').replace(/\b\w/g, l => l.toUpperCase())} • {getUserTypeEmoji(userType)} {userType?.replace('_', ' ').replace(/\b\w/g, l => l.toUpperCase())}</p>
          </div>
        </div>

        <div className="mobile-chat-container">
          <div className="mobile-chat-messages">
            {messages.map((message) => (
              <div key={message.id} className={`mobile-message ${message.sender}`}>
                <div className={`mobile-message-bubble ${message.sender}`}>
                  {/* Only show text if it's NOT a missing items or grab_cabs dropdown selection interface */}
                  {!isMissingItemsSelection(message.text) && !isGrabCabsDropdownSelection(message.text) && (
                    <div
                      dangerouslySetInnerHTML={{ __html: formatLLMResponse(message.text) }}
                      style={{
                        lineHeight: '1.6',
                        whiteSpace: 'pre-wrap'
                      }}
                    />
                  )}

                  {/* Show custom header for missing items selection */}
                  {isMissingItemsSelection(message.text) && (
                    <div style={{
                      fontSize: '16px',
                      fontWeight: 'bold',
                      marginBottom: '12px',
                      color: '#2196f3'
                    }}>
                      🔍 Select Missing Items from Your Order
                    </div>
                  )}
                  
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

                  {/* Missing Items Interactive Selection */}
                  {message.sender === 'bot' && isMissingItemsSelection(message.text) && (
                    <MissingItemsSelector message={message} />
                  )}

                  {/* Grab Cabs Dropdown Interactive Selection */}
                  {message.sender === 'bot' && isGrabCabsDropdownSelection(message.text) && (
                    <GrabCabsDropdownSelector message={message} />
                  )}

                  <div className="mobile-message-time">
                    {message.timestamp.toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' })}
                  </div>
                </div>
              </div>
            ))}
            
            {loading && (
              <TypingIndicator />
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

// Add styles for LLM response formatting
const styles = `
  .section-header {
    font-size: 16px;
    font-weight: bold;
    margin: 12px 0 8px 0;
    color: #2c3e50;
    display: flex;
    align-items: center;
    gap: 8px;
  }

  .bullet-point {
    margin: 2px 0 2px 16px;
    line-height: 1.3;
  }

  .numbered-point {
    margin: 2px 0 2px 16px;
    line-height: 1.3;
  }

  .checkbox-item {
    margin: 6px 0;
    padding: 8px 12px;
    background-color: #f8f9fa;
    border: 1px solid #dee2e6;
    border-radius: 6px;
    font-weight: 500;
  }

  .checkmark-item {
    margin: 2px 0;
    color: #28a745;
    font-weight: 500;
    display: flex;
    align-items: center;
    gap: 6px;
  }

  .paragraph-break {
    height: 6px;
  }
`;

// Inject styles
if (typeof document !== 'undefined') {
  const styleSheet = document.createElement("style");
  styleSheet.innerText = styles;
  document.head.appendChild(styleSheet);
}

export default ChatBot;