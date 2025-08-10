// --- Dynamic Greeting ---

// Function to get appropriate greeting based on time
function getGreeting() {
    const now = new Date();
    const hour = now.getHours();

    if (hour >= 5 && hour < 12) {
        return "Good Morning!";
    } else if (hour >= 12 && hour < 18) {
        return "Good Afternoon!";
    } else {
        return "Good Evening!";
    }
}

// Function to initialize greeting animation
function initGreetingAnimation(greetingElement) {
    // Create container for dynamic text
    let currentHtml = greetingElement.innerHTML;
    const initialTextPlaceholder = "Hi, I'm DeepSeek."; // The original text to replace
    const dynamicContainer = `
        <span class="dynamic-container">
            <span id="static-greeting"></span>
            <span id="dynamic-text"></span>
            <span class="typing-cursor"></span>
        </span>
    `;

    let updatedHtml;
    if (currentHtml.includes(initialTextPlaceholder)) {
        updatedHtml = currentHtml.replace(initialTextPlaceholder, dynamicContainer);
    } else {
        updatedHtml = `${currentHtml} ${dynamicContainer}`;
    }

    greetingElement.innerHTML = updatedHtml;
    const staticGreetingElement = document.getElementById('static-greeting');
    const dynamicTextElement = document.getElementById('dynamic-text');

    // Set initial greeting
    staticGreetingElement.textContent = getGreeting();

    // Random phrases to append
    const randomPhrases = [
        "What can I do for you?", "Look who's here!", "Ready to create something amazing?",
        "Glad to see you!", "Let's make some magic!", "How may I assist you?",
        "Hope you're having a great day!", "What's on your mind?", "Ready for new adventures?",
        "Always a pleasure!", "Let's dive in!", "Your wish is my command!",
        "Feeling creative today?", "Let's get to work!", "Welcome back!",
        "What's cooking?", "Ready for anything!", "What's the plan?",
        "Ready to assist!", "Let's make it happen!", "Always here to help!",
        "Ready to roll!", "What's next on our list?", "Hope you're doing well!",
        "Let's build something awesome!"
    ];

    let phraseIndex = 0;
    let charIndex = 0;
    let isDeleting = false;
    let typingSpeed = 100; // ms per character
    const pauseBetween = 2000; // ms between actions

    function typeAnimation() {
        const currentPhrase = randomPhrases[phraseIndex];

        if (!isDeleting) {
            // Typing mode
            if (charIndex < currentPhrase.length) {
                dynamicTextElement.textContent = currentPhrase.substring(0, charIndex + 1);
                charIndex++;
                setTimeout(typeAnimation, typingSpeed);
            } else {
                isDeleting = true;
                setTimeout(typeAnimation, pauseBetween);
            }
        } else {
            // Deleting mode
            if (charIndex > 0) {
                dynamicTextElement.textContent = currentPhrase.substring(0, charIndex - 1);
                charIndex--;
                setTimeout(typeAnimation, typingSpeed / 2);
            } else {
                isDeleting = false;
                phraseIndex = (phraseIndex + 1) % randomPhrases.length;
                setTimeout(typeAnimation, typingSpeed);
            }
        }
    }

    // Start the typing animation
    typeAnimation();

    // Check for greeting changes every minute
    setInterval(() => {
        const newGreeting = getGreeting();
        if (staticGreetingElement.textContent !== newGreeting) {
            staticGreetingElement.style.transition = 'opacity 0.5s ease';
            staticGreetingElement.style.opacity = 0;

            setTimeout(() => {
                staticGreetingElement.textContent = newGreeting;
                staticGreetingElement.style.opacity = 1;
            }, 500);
        }
    }, 60000);
}

// Track initialized greeting elements
const initializedGreetings = new WeakSet();

// Observer for greeting element
const greetingObserver = new MutationObserver((mutations) => {
    for (const mutation of mutations) {
        if (mutation.type === 'childList') {
            const greetingElement = document.querySelector('._6c7e7df');
            if (greetingElement && !initializedGreetings.has(greetingElement)) {
                initGreetingAnimation(greetingElement);
                initializedGreetings.add(greetingElement);
            }
        }
    }
});

// Start observing the document body for greeting element
greetingObserver.observe(document.body, {
    childList: true,
    subtree: true
});

// Initial check for greeting element
const initialGreetingElement = document.querySelector('._6c7e7df');
if (initialGreetingElement) {
    initGreetingAnimation(initialGreetingElement);
    initializedGreetings.add(initialGreetingElement);
}
