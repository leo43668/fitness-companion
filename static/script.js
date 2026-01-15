
document.addEventListener('DOMContentLoaded', () => {
    const userInput = document.getElementById('user-input');
    const sendBtn = document.getElementById('send-btn');
    const micBtn = document.getElementById('mic-btn');
    const chatContainer = document.getElementById('chat-container');
    const emotionDisplay = document.getElementById('emotion-display');
    const emotionLabel = document.getElementById('emotion-label');

    // --- Voice Recognition Logic ---
    const SpeechRecognition = window.SpeechRecognition || window.webkitSpeechRecognition;
    let recognition;

    if (SpeechRecognition) {
        recognition = new SpeechRecognition();
        recognition.continuous = false;
        recognition.lang = 'en-US';

        recognition.onstart = () => {
            micBtn.classList.add('listening');
            userInput.placeholder = "Listening...";
        };

        recognition.onend = () => {
            micBtn.classList.remove('listening');
            userInput.placeholder = "Type your message here...";
        };

        recognition.onresult = (event) => {
            const transcript = event.results[0][0].transcript;
            userInput.value = transcript;
            setTimeout(sendMessage, 500); // Auto send after brief pause
        };

        micBtn.addEventListener('click', () => {
            recognition.start();
        });
    } else {
        micBtn.style.display = 'none';
    }

    // --- TTS Logic ---
    function speak(text) {
        if ('speechSynthesis' in window) {
            const utterance = new SpeechSynthesisUtterance(text);
            utterance.rate = 1;         // Normal speed
            utterance.pitch = 1.1;      // Slightly higher pitch for friendliness

            // Try to select a female voice if available
            const voices = window.speechSynthesis.getVoices();
            const femaleVoice = voices.find(v => v.name.includes('Female') || v.name.includes('Zira') || v.name.includes('Samantha'));
            if (femaleVoice) utterance.voice = femaleVoice;

            window.speechSynthesis.speak(utterance);
        }
    }

    function appendMessage(text, isUser, recommendation = null) {
        const msgDiv = document.createElement('div');
        msgDiv.className = `message ${isUser ? 'user-message' : 'bot-message'}`;

        let contentHtml = `<div class="message-content">${text}</div>`;

        // Append Recommendation Card if exists
        if (recommendation) {
            if (recommendation.type === 'video') {
                contentHtml += `
                    <div class="recommendation-card">
                        <div class="rec-title">Recommended: ${recommendation.title}</div>
                        <div class="video-container">
                            <iframe src="${recommendation.url}" frameborder="0" allow="accelerometer; autoplay; clipboard-write; encrypted-media; gyroscope; picture-in-picture" allowfullscreen></iframe>
                        </div>
                    </div>
                `;
            } else if (recommendation.type === 'action') {
                contentHtml += `
                    <div class="recommendation-card action-card">
                        <div class="rec-title">Try this: ${recommendation.title}</div>
                        <div class="rec-action">${recommendation.action}</div>
                    </div>
                `;
            }
        }

        msgDiv.innerHTML = contentHtml;
        msgDiv.innerHTML = contentHtml;
        chatContainer.appendChild(msgDiv);
        scrollToBottom();
    }

    function scrollToBottom() {
        // Force scroll to bottom
        setTimeout(() => {
            chatContainer.scrollTop = chatContainer.scrollHeight;
        }, 50);
    }

    async function sendMessage() {
        const text = userInput.value.trim();
        if (!text) return;

        userInput.value = '';
        appendMessage(text, true);

        try {
            const response = await fetch('/chat', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ message: text })
            });

            if (!response.ok) throw new Error('Network error');

            const data = await response.json();


            appendMessage(data.response, false, data.recommendation);

            // Update emotion display
            if (data.emotion) {
                updateEmotionDisplay(data.emotion);
            }

            // Speak response
            speak(data.response);

        } catch (error) {
            console.error('Error:', error);
            appendMessage("Sorry, I'm having trouble connecting right now.", false);
        }
    }

    function updateEmotionDisplay(emotion) {
        if (!emotionDisplay) return;

        emotionDisplay.style.display = 'flex';
        const label = document.getElementById('emotion-label');
        const icon = document.getElementById('emotion-icon');

        // Map emotion to Emoji
        const emojiMap = {
            'positive': '😊',
            'neutral': '😌',
            'fatigue': '😫',
            'anxiety': '😰',
            'frustration': '😤'
        };

        // Reset classes
        emotionDisplay.className = 'emotion-pill';
        emotionDisplay.classList.add(emotion); // Add color class

        if (label) label.textContent = emotion.charAt(0).toUpperCase() + emotion.slice(1);
        if (icon) icon.textContent = emojiMap[emotion] || '😐';
    }

    sendBtn.addEventListener('click', sendMessage);

    userInput.addEventListener('keypress', (e) => {
        if (e.key === 'Enter') sendMessage();
    });
});

