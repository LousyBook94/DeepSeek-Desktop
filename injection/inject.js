console.log("JS Loaded");

// Load Inter font from Google Fonts with all weights
const link = document.createElement('link');
link.href = 'https://fonts.googleapis.com/css2?family=Inter:wght@100..900&display=swap';
link.rel = 'stylesheet';
document.head.appendChild(link);

// Force Inter font on all elements
const style = document.createElement('style');
style.textContent = `
    * { font-family: 'Inter', sans-serif !important; }
    
    /* Sphere cursor styling */
    .typing-cursor {
        display: inline-block;
        width: 0.9em; /* 1.5x text size */
        height: 0.9em;
        background-color: currentColor;
        border-radius: 50%;
        margin-left: 0.1em;
        vertical-align: middle;
        animation: blink 1s infinite;
    }
    
    @keyframes blink {
        0%, 100% { opacity: 1; }
        50% { opacity: 0.5; }
    }
    
    /* Container for dynamic text */
    .dynamic-container {
        display: inline-block;
        position: relative;
    }
`;
document.head.appendChild(style);

// Function to initialize text replacement
function initTextReplacement(targetElement) {
    targetElement.innerHTML = "Made by <a href='https://github.com/LousyBook94' target='_blank' style='opacity: 0.7;'>LousyBook01</a>. Powered by <a href='https://deepseek.com/' target='_blank' style='opacity: 0.7;'>DeepSeek</a>. Icons by <a href='https://icons8.com/' target='_blank' style='opacity: 0.7;'>Icons8</a>";
}

// Track initialized text replacement elements
const initializedTextReplacements = new WeakSet();

// Observer for text replacement elements
const textReplacementObserver = new MutationObserver((mutations) => {
    for (const mutation of mutations) {
        if (mutation.type === 'childList') {
            // Check for both element types
            const targetElements = [
                ...document.querySelectorAll('._0fcaa63._7941d9f'),
                ...document.querySelectorAll('._0fcaa63')
            ];
            
            for (const targetElement of targetElements) {
                if (targetElement && !initializedTextReplacements.has(targetElement)) {
                    initTextReplacement(targetElement);
                    initializedTextReplacements.add(targetElement);
                }
            }
        }
    }
});

// Start observing the document body for text replacement elements
textReplacementObserver.observe(document.body, {
    childList: true,
    subtree: true
});

// Initial check for text replacement elements
const initialTargetElements = [
    ...document.querySelectorAll('._0fcaa63._7941d9f'),
    ...document.querySelectorAll('._0fcaa63')
];

for (const targetElement of initialTargetElements) {
    if (targetElement) {
        initTextReplacement(targetElement);
        initializedTextReplacements.add(targetElement);
    }
}

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
    const cursorElement = document.querySelector('.typing-cursor');

    // Set initial greeting
    staticGreetingElement.textContent = getGreeting();
    
    // Random phrases to append
    const randomPhrases = [
        "What can I do for you?",
        "Look who's here!",
        "Ready to create something amazing?",
        "Glad to see you!",
        "Let's make some magic!",
        "How may I assist you?",
        "Hope you're having a great day!",
        "What's on your mind?",
        "Ready for new adventures?",
        "Always a pleasure!",
        "Let's dive in!",
        "Your wish is my command!",
        "Feeling creative today?",
        "Let's get to work!",
        "Welcome back!",
        "What's cooking?",
        "Ready for anything!",
        "What's the plan?",
        "Ready to assist!",
        "Let's make it happen!",
        "Always here to help!",
        "Ready to roll!",
        "What's next on our list?",
        "Hope you're doing well!",
        "Let's build something awesome!"
    ];

    let phraseIndex = 0;
    let charIndex = 0;
    let isDeleting = false;
    let typingSpeed = 100; // milliseconds per character
    const pauseBetween = 2000; // milliseconds between actions

    function typeAnimation() {
        const currentPhrase = randomPhrases[phraseIndex];
        
        if (!isDeleting) {
            // Typing mode
            if (charIndex < currentPhrase.length) {
                dynamicTextElement.textContent = currentPhrase.substring(0, charIndex + 1);
                charIndex++;
                setTimeout(typeAnimation, typingSpeed);
            } else {
                // Finished typing, pause then start deleting
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
                // Finished deleting, move to next phrase
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
            // Add fade out effect
            staticGreetingElement.style.transition = 'opacity 0.5s ease';
            staticGreetingElement.style.opacity = 0;
            
            setTimeout(() => {
                // Update greeting and fade in
                staticGreetingElement.textContent = newGreeting;
                staticGreetingElement.style.opacity = 1;
            }, 500);
        }
    }, 60000); // Check every minute
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

// List of classes to remove
const classesToRemove = ['_41b9122', 'a1e75851'];

function removeElementsWithClasses() {
    classesToRemove.forEach(className => {
        document.querySelectorAll(`.${className}`).forEach(element => {
            console.log(`Removing element with class: ${className}`);
            element.remove();
        });
    });
}

// Initial removal in case elements are already present
removeElementsWithClasses();

// Set up a MutationObserver to watch for new elements
const observer = new MutationObserver((mutationsList) => {
    for (const mutation of mutationsList) {
        if (mutation.type === 'childList' && mutation.addedNodes.length > 0) {
            removeElementsWithClasses(); // Check for and remove new elements
        }
    }
});

// Start observing the document body for changes
observer.observe(document.body, { childList: true, subtree: true });

// --- Markdown Rendering ---

// 1. Load marked.js library from a CDN
const script = document.createElement('script');
script.src = 'https://cdn.jsdelivr.net/npm/marked/marked.min.js';
document.head.appendChild(script);

script.onload = () => {
    console.log('marked.js loaded');

    // 2. Function to render Markdown in an element
    function renderMarkdown(element) {
        const rawText = element.innerText;
        // Basic check to see if it might be markdown
        if (rawText.includes('*') || rawText.includes('_') || rawText.includes('`')) {
            const formattedHtml = marked.parse(rawText);
            element.innerHTML = formattedHtml;
        }
    }

    // 3. Use a MutationObserver to detect new messages
    const chatObserver = new MutationObserver((mutations) => {
        for (const mutation of mutations) {
            if (mutation.type === 'childList') {
                mutation.addedNodes.forEach(node => {
                    // Check if the added node is an element and contains user messages
                    if (node.nodeType === 1) {
                        const userMessages = node.querySelectorAll('.fbb737a4');
                        userMessages.forEach(renderMarkdown);
                    }
                });
            }
        }
    });

    // 4. Start observing the chat container
    // A bit of a broad approach, but should be effective.
    chatObserver.observe(document.body, {
        childList: true,
        subtree: true
    });

    // 5. Initial check for any messages that are already on the page
    document.querySelectorAll('.fbb737a4').forEach(renderMarkdown);
};
