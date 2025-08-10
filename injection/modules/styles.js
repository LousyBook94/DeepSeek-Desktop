// Load Inter font from Google Fonts with all weights
const link = document.createElement('link');
link.href = 'https://fonts.googleapis.com/css2?family=Inter:wght@100..900&display=swap';
link.rel = 'stylesheet';
document.head.appendChild(link);

// Force Inter font on all elements and add custom styles
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
