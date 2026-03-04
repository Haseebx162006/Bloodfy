/**
 * Chatbot Integration Script
 * Handles chat interactions with the backend AI chatbot
 */

document.addEventListener('DOMContentLoaded', () => {
    // =============================================================================
    // Chat Elements
    // =============================================================================

    const messagesContainer = document.querySelector('.messages-container');
    const chatInput = document.querySelector('.chat-input');
    const sendButton = document.querySelector('.btn-send');
    const inputArea = document.querySelector('.input-area');

    if (!messagesContainer || !chatInput || !sendButton) return;

    // =============================================================================
    // Send Message Function
    // =============================================================================

    async function sendMessage() {
        const message = chatInput.value.trim();

        if (!message) return;

        // Clear input
        chatInput.value = '';

        // Add user message to UI
        addUserMessage(message);

        // Show typing indicator
        showTypingIndicator();

        // Disable input during processing
        chatInput.disabled = true;
        sendButton.disabled = true;

        try {
            // Call chatbot API
            const result = await API.chatbot.sendQuery(message);

            // Hide typing indicator
            hideTypingIndicator();

            // Add bot response to UI
            if (result.success && result.data) {
                addBotMessage(result.data.response || result.data.answer || 'I understand. How else can I help?');
            }

        } catch (error) {
            console.error('Chatbot error:', error);

            // Hide typing indicator
            hideTypingIndicator();

            // Show error message
            addBotMessage('I apologize, but I\'m having trouble processing your request right now. Please try again or contact support.');
        } finally {
            // Re-enable input
            chatInput.disabled = false;
            sendButton.disabled = false;
            chatInput.focus();
        }
    }

    // =============================================================================
    // Add User Message to UI
    // =============================================================================

    function addUserMessage(text) {
        const messageDiv = document.createElement('div');
        messageDiv.className = 'message user';
        messageDiv.textContent = text;

        messagesContainer.appendChild(messageDiv);
        scrollToBottom();
    }

    // =============================================================================
    // Add Bot Message to UI
    // =============================================================================

    function addBotMessage(text) {
        const messageDiv = document.createElement('div');
        messageDiv.className = 'message bot';
        messageDiv.innerHTML = `
            <div class="avatar"><i class="fas fa-robot"></i></div>
            ${text}
        `;

        messagesContainer.appendChild(messageDiv);
        scrollToBottom();
    }

    // =============================================================================
    // Typing Indicator
    // =============================================================================

    function showTypingIndicator() {
        // Check if indicator already exists
        if (document.querySelector('.typing-indicator')) {
            return;
        }

        const indicatorDiv = document.createElement('div');
        indicatorDiv.className = 'typing-indicator';
        indicatorDiv.innerHTML = `
            Bloodfy AI is typing
            <div class="dot"></div>
            <div class="dot"></div>
            <div class="dot"></div>
        `;

        messagesContainer.appendChild(indicatorDiv);
        scrollToBottom();
    }

    function hideTypingIndicator() {
        const indicator = document.querySelector('.typing-indicator');
        if (indicator) {
            indicator.remove();
        }
    }

    // =============================================================================
    // Scroll to Bottom
    // =============================================================================

    function scrollToBottom() {
        messagesContainer.scrollTop = messagesContainer.scrollHeight;
    }

    // =============================================================================
    // Event Listeners
    // =============================================================================

    // Send button click
    sendButton.addEventListener('click', sendMessage);

    // Enter key in input
    chatInput.addEventListener('keypress', (e) => {
        if (e.key === 'Enter' && !e.shiftKey) {
            e.preventDefault();
            sendMessage();
        }
    });

    // =============================================================================
    // Suggested Actions (Info Panel)
    // =============================================================================

    const infoCards = document.querySelectorAll('.info-card');
    infoCards.forEach(card => {
        card.addEventListener('click', () => {
            const heading = card.querySelector('h4').textContent;

            // Map headings to queries
            const queryMap = {
                'Find Donors': 'Find donors for O- blood type in Lahore',
                'Verify Donor': 'How do I verify a new donor?',
                'Check Stock': 'What is the current blood stock level?',
                'Emergency Alert': 'How do I send an emergency alert?'
            };

            const query = queryMap[heading] || heading;

            // Set query in input
            chatInput.value = query;
            chatInput.focus();
        });
    });

    // =============================================================================
    // Load Chat History (Optional)
    // =============================================================================

    async function loadChatHistory() {
        // If you want to load previous chat history from backend
        // This would require a chat history endpoint
        // For now, start with a welcome message

        // Check if there are already messages (from HTML)
        const existingMessages = messagesContainer.querySelectorAll('.message');
        if (existingMessages.length === 0) {
            addBotMessage('Hello! I am the Bloodfy AI Assistant. How can I help you with donor management or blood requests today?');
        }
    }

    // Initialize chat
    loadChatHistory();

    // Focus input on load
    chatInput.focus();
});
