console.log("JS Loaded");

// Load Marked.js library for markdown rendering
const markedScript = document.createElement('script');
markedScript.src = 'https://cdn.jsdelivr.net/npm/marked/marked.min.js';
markedScript.async = true;
document.head.appendChild(markedScript);

// Load DOMPurify for security sanitization
const dompurifyScript = document.createElement('script');
dompurifyScript.src = 'https://cdn.jsdelivr.net/npm/dompurify@3.0.5/dist/purify.min.js';
dompurifyScript.async = true;
document.head.appendChild(dompurifyScript);

// Load Inter font from Google Fonts with all weights
const interLink = document.createElement('link');
interLink.href = 'https://fonts.googleapis.com/css2?family=Inter:wght@100..900&display=swap';
interLink.rel = 'stylesheet';
document.head.appendChild(interLink);

// Load JetBrains Mono font from Google Fonts
const jetbrainsLink = document.createElement('link');
jetbrainsLink.href = 'https://fonts.googleapis.com/css2?family=JetBrains+Mono:wght@100..800&display=swap';
jetbrainsLink.rel = 'stylesheet';
document.head.appendChild(jetbrainsLink);

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
    
    /* Markdown content styling */
    .markdown-heading {
        margin-top: 0.5em !important;
        margin-bottom: 0.3em !important;
        line-height: 1.3 !important;
    }
    
    h1.markdown-heading { font-size: 2em; font-weight: 700; }
    h2.markdown-heading { font-size: 1.5em; font-weight: 600; }
    h3.markdown-heading { font-size: 1.25em; font-weight: 600; }
    h4.markdown-heading { font-size: 1em; font-weight: 600; }
    h5.markdown-heading { font-size: 0.875em; font-weight: 600; }
    h6.markdown-heading { font-size: 0.85em; font-weight: 600; }
    
    p {
        margin-top: 0.5em;
        margin-bottom: 0.5em;
        line-height: 1.5;
    }
    
    /* Code block styling - now handled by theme-aware styles */
    
    /* Inline code styling - now handled by theme-aware styles */
    
    /* List styling */
    ul, ol {
        margin-top: 0.5em !important;
        margin-bottom: 0.5em !important;
        padding-left: 2em !important;
    }
    
    li {
        margin: 0.25em 0;
    }
    
    /* Blockquote styling - now handled by theme-aware styles */
    
    /* Table styling - now handled by theme-aware styles */
`;
document.head.appendChild(style);

// Function to detect system theme
function getSystemTheme() {
    // Check if the user has explicitly set a preference
    if (window.matchMedia && window.matchMedia('(prefers-color-scheme: dark)').matches) {
        return 'dark';
    }
    return 'light';
}

// Function to apply theme
function applyTheme() {
    const theme = getSystemTheme();
    const isDark = theme === 'dark';
    
    // Create or update theme styles
    let themeStyle = document.getElementById('theme-styles');
    if (!themeStyle) {
        themeStyle = document.createElement('style');
        themeStyle.id = 'theme-styles';
        document.head.appendChild(themeStyle);
    }
    
    // Define theme colors
    const colors = isDark ? {
        background: '#1e1e1e',
        surface: '#252526',
        surfaceHighlight: '#2d2d30',
        text: '#d4d4d4',
        textSecondary: '#969696',
        codeBackground: '#1e1e1e',
        codeBorder: '#3e3e42',
        codeText: '#d4d4d4',
        inlineCodeBackground: '#2d2d30',
        inlineCodeBorder: '#3e3e42',
        inlineCodeText: '#d4d4d4'
    } : {
        background: '#ffffff',
        surface: '#f3f3f3',
        surfaceHighlight: '#e6e6e6',
        text: '#24292e',
        textSecondary: '#586069',
        codeBackground: '#f6f8fa',
        codeBorder: '#e1e4e8',
        codeText: '#24292e',
        inlineCodeBackground: '#f6f8fa',
        inlineCodeBorder: '#e1e4e8',
        inlineCodeText: '#24292e'
    };
    
    // Apply theme styles
    themeStyle.textContent = `
        /* Code block styling with theme support */
        .code-block {
            background-color: ${colors.codeBackground} !important;
            border: 1px solid ${colors.codeBorder} !important;
            color: ${colors.codeText} !important;
            font-family: 'JetBrains Mono', 'SFMono-Regular', Consolas, 'Liberation Mono', Menlo, monospace !important;
            font-size: 0.85em;
            line-height: 1.45;
            border-radius: 6px !important;
            padding: 16px !important;
            margin: 8px 0 !important;
            overflow-x: auto !important;
        }
        
        .code-block code {
            background-color: transparent !important;
            padding: 0 !important;
            border-radius: 0 !important;
            font-family: inherit !important;
            color: inherit !important;
        }
        
        /* Inline code styling with theme support */
        .inline-code {
            background-color: ${colors.inlineCodeBackground} !important;
            border: 1px solid ${colors.inlineCodeBorder} !important;
            color: ${colors.inlineCodeText} !important;
            font-family: 'JetBrains Mono', 'SFMono-Regular', Consolas, 'Liberation Mono', Menlo, monospace !important;
            font-size: 0.9em;
            padding: 0.2em 0.4em !important;
            border-radius: 3px !important;
        }
        
        /* Table styling with theme support */
        table {
            border-collapse: collapse;
            width: 100%;
            margin: 0.5em 0;
        }
        
        th, td {
            padding: 6px 13px;
            border: 1px solid ${isDark ? '#3e3e42' : '#dfe2e5'};
        }
        
        th {
            font-weight: 600;
            background-color: ${colors.surfaceHighlight};
        }
        
        tr:nth-child(2n) {
            background-color: ${colors.surfaceHighlight};
        }
        
        /* Blockquote styling with theme support */
        blockquote {
            color: ${colors.textSecondary};
            border-left: 0.25em solid ${colors.codeBorder};
        }
    `;
    
    // Store current theme for reference
    window.currentTheme = theme;
}

// Apply initial theme
applyTheme();

// Listen for system theme changes
if (window.matchMedia) {
    window.matchMedia('(prefers-color-scheme: dark)').addEventListener('change', applyTheme);
}

// Configure Marked.js options for better rendering
function configureMarked() {
    if (window.marked) {
        // Set options for better rendering
        window.marked.setOptions({
            breaks: true,              // Convert single line breaks to <br>
            gfm: true,                 // GitHub Flavored Markdown
            headerIds: false,          // Don't auto-generate IDs for headers
            mangle: false,             // Don't escape URLs
            sanitize: false,           // We'll use DOMPurify instead
            smartLists: true,          // Better list rendering
            smartypants: true,         // Better punctuation rendering
            xhtml: false               // Use standard HTML tags
        });
        
        // Custom renderer for better code blocks and spacing
        const renderer = new window.marked.Renderer();
        
        // Override code block rendering
        renderer.code = function(code, language, escaped) {
            const lang = language || 'text';
            
            // Ensure code is a string
            const codeString = typeof code === 'string' ? code : String(code);
            
            // Create a proper code block with syntax highlighting class
            return `<pre class="code-block"><code class="language-${lang}">${escaped ? codeString : window.marked.parseInline(codeString)}</code></pre>`;
        };
        
        // Override inline code rendering
        renderer.codespan = function(code) {
            // Ensure code is a string
            const codeString = typeof code === 'string' ? code : String(code);
            return `<code class="inline-code">${codeString}</code>`;
        };
        
        // Override heading rendering to fix spacing
        const originalHeading = renderer.heading;
        renderer.heading = function(text, level, raw) {
            const headingHtml = originalHeading.call(this, text, level, raw);
            // Add class for spacing control
            return headingHtml.replace(/<h([1-6])>/, `<h$1 class="markdown-heading">`);
        };
        
        // Set the custom renderer
        window.marked.setOptions({ renderer });
    }
}

// Function to sanitize HTML content
function sanitizeHtml(html) {
    if (window.DOMPurify) {
        return window.DOMPurify.sanitize(html, {
            ALLOWED_TAGS: [
                'h1', 'h2', 'h3', 'h4', 'h5', 'h6',
                'p', 'br', 'hr', 'pre', 'blockquote',
                'ul', 'ol', 'li', 'dl', 'dt', 'dd',
                'strong', 'em', 'b', 'i', 'u', 's', 'del',
                'code', 'pre', 'samp', 'kbd',
                'a', 'img', 'div', 'span',
                'table', 'thead', 'tbody', 'tr', 'th', 'td',
                'details', 'summary'
            ],
            ALLOWED_ATTR: ['href', 'src', 'alt', 'class', 'language', 'title'],
            ALLOW_DATA_ATTR: false,
            SAFE_FOR_JQUERY: true,
                FORBID_TAGS: ['script', 'style', 'iframe', 'object', 'embed', 'video', 'audio', 'form', 'input', 'button', 'textarea', 'select', 'option'],
                FORBID_ATTR: ['onerror', 'onclick', 'onload', 'onmouseover', 'onfocus', 'onblur', 'onchange']
        });
    }
    return html; // Fallback if DOMPurify isn't available
}

// Function to check if all dependencies are loaded
function dependenciesLoaded() {
    return window.marked && window.DOMPurify;
}

// Function to render markdown content with retry mechanism
function renderMarkdown(element, retryCount = 0) {
    if (element && dependenciesLoaded()) {
        // Configure marked if not already configured
        if (!window.marked._configured) {
            configureMarked();
            window.marked._configured = true;
        }
        
        try {
            // Get the markdown text and trim whitespace
            const markdownText = element.textContent ? element.textContent.trim() : '';
            
            // Only process if there's actual content
            if (markdownText) {
                // Parse markdown to HTML
                const html = window.marked.parse(markdownText);
                
                // Sanitize the HTML to prevent XSS
                const sanitizedHtml = sanitizeHtml(html);
                
                // Set the inner HTML with sanitized content
                element.innerHTML = sanitizedHtml;
                
                // Fix spacing issues
                fixSpacing(element);
                
                // Apply code block styling
                styleCodeBlocks(element);
            }
        } catch (error) {
            console.error('Error rendering markdown:', error);
            // Try to fallback to plain text if markdown parsing fails
            try {
                const plainText = element.textContent ? element.textContent.trim() : '';
                if (plainText) {
                    // Escape HTML to prevent XSS
                    const escapedText = plainText.replace(/&/g, '&')
                                                 .replace(/</g, '<')
                                                 .replace(/>/g, '>')
                                                 .replace(/"/g, '"')
                                                 .replace(/'/g, '&#039;');
                    element.innerHTML = `<p>${escapedText}</p>`;
                }
            } catch (fallbackError) {
                console.error('Fallback rendering also failed:', fallbackError);
            }
        }
    } else if (retryCount < 50) { // Increased retry count
        // Retry if dependencies aren't loaded yet
        setTimeout(() => renderMarkdown(element, retryCount + 1), 100);
    } else if (retryCount === 50) {
        console.warn('Markdown rendering skipped - dependencies not loaded');
        // Fallback to plain text if dependencies never load
        try {
            const plainText = element.textContent ? element.textContent.trim() : '';
            if (plainText) {
                const escapedText = plainText.replace(/&/g, '&')
                                           .replace(/</g, '<')
                                           .replace(/>/g, '>')
                                           .replace(/"/g, '"')
                                           .replace(/'/g, '&#039;');
                element.innerHTML = `<p>${escapedText}</p>`;
            }
        } catch (fallbackError) {
            console.error('Final fallback rendering failed:', fallbackError);
        }
    }
}

// Function to fix spacing issues
function fixSpacing(element) {
    // Fix heading spacing
    const headings = element.querySelectorAll('.markdown-heading, h1, h2, h3, h4, h5, h6');
    headings.forEach(heading => {
        heading.style.marginTop = '0.5em';
        heading.style.marginBottom = '0.3em';
        heading.style.lineHeight = '1.3';
    });
    
    // Fix paragraph spacing
    const paragraphs = element.querySelectorAll('p');
    paragraphs.forEach(p => {
        // Remove top margin from first paragraph
        if (p === paragraphs[0]) {
            p.style.marginTop = '0';
        }
        // Remove bottom margin from last paragraph
        if (p === paragraphs[paragraphs.length - 1]) {
            p.style.marginBottom = '0';
        }
        // Set consistent paragraph spacing
        if (p.style.marginTop !== '0') {
            p.style.marginTop = '0.5em';
        }
        if (p.style.marginBottom !== '0') {
            p.style.marginBottom = '0.5em';
        }
    });
    
    // Fix list spacing
    const lists = element.querySelectorAll('ul, ol');
    lists.forEach(list => {
        list.style.marginTop = '0.5em';
        list.style.marginBottom = '0.5em';
    });
    
    // Code block styling is now handled by theme-aware styles
    // Inline code styling is now handled by theme-aware styles
}

// Function to apply additional styling to code blocks
function styleCodeBlocks(element) {
    // Add syntax highlighting classes if available
    const codeBlocks = element.querySelectorAll('pre code');
    codeBlocks.forEach(block => {
        // Add line numbers if it's a multi-line code block
        const lines = block.textContent.split('\n').length;
        if (lines > 1) {
            block.classList.add('multiline-code');
        }
    });
}

// Function to initialize text replacement
function initTextReplacement(targetElement) {
    targetElement.innerHTML = "Made by <a href='https://github.com/LousyBook94' target='_blank' style='opacity: 0.7;'>LousyBook01</a>. Powered by <a href='https://deepseek.com/' target='_blank' style='opacity: 0.7;'>DeepSeek</a>. Icons by <a href='https://icons8.com/' target='_blank' style='opacity: 0.7;'>Icons8</a>";
}

// Track initialized text replacement elements
const initializedTextReplacements = new WeakSet();

// Track initialized markdown elements
const initializedMarkdownElements = new WeakSet();

// Observer for markdown elements
const markdownObserver = new MutationObserver((mutations) => {
    for (const mutation of mutations) {
        if (mutation.type === 'childList') {
            // Check for markdown elements
            const markdownElements = document.querySelectorAll('.fbb737a4');
            for (const element of markdownElements) {
                if (element && !initializedMarkdownElements.has(element)) {
                    renderMarkdown(element);
                    initializedMarkdownElements.add(element);
                }
            }
        }
    }
});

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

// Start observing the document body for markdown elements
markdownObserver.observe(document.body, {
    childList: true,
    subtree: true
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

// Initial check for markdown elements
const initialMarkdownElements = document.querySelectorAll('.fbb737a4');
for (const element of initialMarkdownElements) {
    if (element) {
        renderMarkdown(element);
        initializedMarkdownElements.add(element);
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