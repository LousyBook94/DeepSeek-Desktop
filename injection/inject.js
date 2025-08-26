// Optimized script loading with immediate execution
console.log("JS Loaded");

// Performance optimization: Use requestIdleCallback for non-critical operations
if ('requestIdleCallback' in window) {
    requestIdleCallback(() => {
        // Non-critical initialization here
    });
}

// Create a refresh button for real-time updates
function createRefreshButton() {
    // Create small trigger button element
    const triggerButton = document.createElement('div');
    triggerButton.id = 'deepseek-refresh-trigger';
    triggerButton.title = 'Refresh';
    
    // Create main refresh button element
    const refreshButton = document.createElement('button');
    refreshButton.id = 'deepseek-refresh-btn';
    refreshButton.title = 'Refresh Screen';
    
    // Create version tooltip element
    const versionTooltip = document.createElement('div');
    versionTooltip.id = 'deepseek-version-tooltip';
    versionTooltip.innerHTML = `
        <div class="tooltip-pointer"></div>
        <div class="tooltip-content">
            <p>Version <span id="version-number">0.0.0</span></p>
        </div>
    `;
    
    // Create SVG icon
    const svgIcon = document.createElementNS('http://www.w3.org/2000/svg', 'svg');
    svgIcon.setAttribute('width', '16');
    svgIcon.setAttribute('height', '16');
    svgIcon.setAttribute('viewBox', '0 0 24 24');
    svgIcon.setAttribute('fill', 'none');
    svgIcon.setAttribute('stroke', 'currentColor');
    svgIcon.setAttribute('stroke-width', '2');
    svgIcon.setAttribute('stroke-linecap', 'round');
    svgIcon.setAttribute('stroke-linejoin', 'round');
    
    const refreshPath = document.createElementNS('http://www.w3.org/2000/svg', 'path');
    refreshPath.setAttribute('d', 'M23 4v6h-6M1 20v-6h6M3.51 9a9 9 0 0 1 14.85-3.36L23 10M1 14l4.64 4.36A9 9 0 0 0 20.49 15');
    
    svgIcon.appendChild(refreshPath);
    refreshButton.appendChild(svgIcon);
    
    // Create refresh popup
    const refreshPopup = document.createElement('div');
    refreshPopup.id = 'deepseek-refresh-popup';
    refreshPopup.innerHTML = `
        <div class="refresh-icon-container">
            <div class="spinner"></div>
            <div class="refresh-icon">🔄</div>
        </div>
        <div class="popup-content">
            <h3 class="popup-title">Refreshing</h3>
            <p class="popup-text">Please wait while we update your content...</p>
            <div class="progress-bar">
                <div class="progress-fill"></div>
            </div>
        </div>
    `;
    
    // Create welcome tooltip
    const welcomeTooltip = document.createElement('div');
    welcomeTooltip.id = 'deepseek-welcome-tooltip';
    welcomeTooltip.innerHTML = `
        <div class="tooltip-pointer"></div>
        <div class="tooltip-content">
            <p>Hover here for refresh</p>
        </div>
    `;
    
    // Apply beautiful styling
    const style = document.createElement('style');
    style.textContent = `
        #deepseek-refresh-trigger {
            position: fixed;
            top: 15px;
            right: 15px;
            z-index: 10000;
            width: 12px;
            height: 12px;
            background: rgba(255, 255, 255, 0.2);
            backdrop-filter: blur(10px);
            border-radius: 50%;
            cursor: pointer;
            transition: all 0.3s ease;
            border: 1px solid rgba(255, 255, 255, 0.3);
        }
        
        #deepseek-refresh-trigger:hover {
            transform: scale(1.2);
            background: rgba(255, 255, 255, 0.3);
        }
        
        #deepseek-refresh-btn {
            position: fixed;
            top: 50px;
            right: 15px;
            z-index: 9999;
            width: 36px;
            height: 36px;
            border-radius: 8px;
            border: none;
            background: rgba(255, 255, 255, 0.1);
            backdrop-filter: blur(10px);
            color: white;
            cursor: pointer;
            box-shadow: 0 4px 15px rgba(0, 0, 0, 0.1);
            transition: all 0.3s ease;
            display: flex;
            align-items: center;
            justify-content: center;
            opacity: 0;
            transform: translateY(-10px);
            pointer-events: none;
        }
        
        #deepseek-refresh-trigger:hover + #deepseek-refresh-btn {
            opacity: 1;
            transform: translateY(0);
            pointer-events: auto;
        }
        
        #deepseek-refresh-btn:hover {
            background: rgba(255, 255, 255, 0.2);
            transform: scale(1.05);
            box-shadow: 0 6px 20px rgba(0, 0, 0, 0.15);
        }
        
        #deepseek-refresh-btn:active {
            transform: scale(0.95);
        }
        
        @keyframes rotate {
            from { transform: rotate(0deg); }
            to { transform: rotate(360deg); }
        }
        
        #deepseek-refresh-btn.refreshing {
            animation: rotate 1s linear infinite;
        }
        
        #deepseek-refresh-btn svg {
            width: 16px;
            height: 16px;
            stroke: white;
            stroke-width: 2;
        }
        
        #deepseek-refresh-popup {
            position: fixed;
            top: 50%;
            left: 50%;
            transform: translate(-50%, -50%);
            z-index: 10001;
            background: rgba(15, 23, 42, 0.95);
            backdrop-filter: blur(20px);
            padding: 30px 40px;
            border-radius: 16px;
            color: white;
            text-align: center;
            display: none;
            box-shadow: 0 20px 50px rgba(0, 0, 0, 0.4);
            border: 1px solid rgba(255, 255, 255, 0.1);
            min-width: 280px;
        }
        
        #deepseek-refresh-popup.show {
            display: block;
            animation: fadeInScale 0.4s cubic-bezier(0.175, 0.885, 0.32, 1.275);
        }
        
        .refresh-icon-container {
            position: relative;
            width: 80px;
            height: 80px;
            margin: 0 auto 20px;
        }
        
        .spinner {
            position: absolute;
            top: 50%;
            left: 50%;
            transform: translate(-50%, -50%);
            width: 50px;
            height: 50px;
            margin: 0 auto 15px;
            border: 3px solid rgba(102, 126, 234, 0.3);
            border-top-color: #667eea;
            border-radius: 50%;
            animation: spin 1s linear infinite;
        }
        
        .refresh-icon {
            position: absolute;
            top: 50%;
            left: 50%;
            transform: translate(-50%, -50%);
            font-size: 28px;
            animation: pulse 2s ease-in-out infinite;
        }
        
        .popup-content {
            display: flex;
            flex-direction: column;
            align-items: center;
        }
        
        .popup-title {
            font-size: 20px;
            font-weight: 600;
            margin: 0 0 10px 0;
            color: #667eea;
            letter-spacing: 0.5px;
        }
        
        .popup-text {
            font-size: 14px;
            font-weight: 400;
            margin: 0 0 20px 0;
            color: rgba(255, 255, 255, 0.8);
            line-height: 1.5;
        }
        
        .progress-bar {
            width: 100%;
            height: 4px;
            background: rgba(255, 255, 255, 0.1);
            border-radius: 2px;
            overflow: hidden;
        }
        
        .progress-fill {
            height: 100%;
            background: linear-gradient(90deg, #667eea, #764ba2);
            border-radius: 2px;
            width: 0%;
            animation: progress 2s ease-out forwards;
        }
        
        @keyframes progress {
            0% { width: 0%; }
            50% { width: 70%; }
            100% { width: 100%; }
        }
        
        #deepseek-welcome-tooltip {
            position: fixed;
            z-index: 9998;
            background: rgba(15, 23, 42, 0.9);
            backdrop-filter: blur(10px);
            padding: 8px 12px;
            border-radius: 8px;
            color: white;
            font-size: 13px;
            max-width: 160px;
            opacity: 0;
            transition: all 0.3s ease;
            pointer-events: none;
            border: 1px solid rgba(102, 126, 234, 0.3);
            box-shadow: 0 4px 15px rgba(0, 0, 0, 0.2);
        }
        
        #deepseek-welcome-tooltip.show {
            opacity: 1;
        }
        
        #deepseek-welcome-tooltip .tooltip-pointer {
            position: absolute;
            top: 50%;
            right: -6px;
            width: 0;
            height: 0;
            border-top: 6px solid transparent;
            border-bottom: 6px solid transparent;
            border-left: 6px solid rgba(15, 23, 42, 0.9);
            transform: translateY(-50%);
        }
        
        #deepseek-welcome-tooltip .tooltip-content {
            margin: 0;
            font-weight: 500;
        }
        
        #deepseek-version-tooltip {
            position: fixed;
            z-index: 9997;
            background: rgba(15, 23, 42, 0.9);
            backdrop-filter: blur(10px);
            padding: 12px 16px;
            border-radius: 12px;
            color: white;
            font-size: 13px;
            max-width: 200px;
            opacity: 0;
            transition: all 0.3s ease;
            pointer-events: none;
            border: 1px solid rgba(102, 126, 234, 0.3);
            box-shadow: 0 4px 15px rgba(0, 0, 0, 0.2);
        }
        
        #deepseek-version-tooltip.show {
            opacity: 1;
        }
        
        #deepseek-version-tooltip .tooltip-pointer {
            position: absolute;
            top: 50%;
            right: -6px;
            width: 0;
            height: 0;
            border-top: 6px solid transparent;
            border-bottom: 6px solid transparent;
            border-left: 6px solid rgba(15, 23, 42, 0.9);
            transform: translateY(-50%);
        }
        
        #deepseek-version-tooltip .tooltip-content {
            margin: 0;
        }
        
        .version-header {
            display: flex;
            align-items: center;
            margin-bottom: 8px;
            padding-bottom: 8px;
            border-bottom: 1px solid rgba(255, 255, 255, 0.1);
        }
        
        .version-title {
            font-size: 14px;
            font-weight: 600;
            color: #667eea;
        }
        
        .version-info {
            display: flex;
            flex-direction: column;
        }
        
        .version-number {
            font-weight: 700;
            color: #764ba2;
            font-size: 16px;
        }
        
        @keyframes spin {
            0% { transform: rotate(0deg); }
            100% { transform: rotate(360deg); }
        }
        
        @keyframes fadeInScale {
            from {
                opacity: 0;
                transform: translate(-50%, -50%) scale(0.8);
            }
            to {
                opacity: 1;
                transform: translate(-50%, -50%) scale(1);
            }
        }
        
        @keyframes pulse {
            0% { transform: translate(-50%, -50%) scale(1); }
            50% { transform: translate(-50%, -50%) scale(1.1); }
            100% { transform: translate(-50%, -50%) scale(1); }
        }
        
        body.dark-mode #deepseek-refresh-popup {
            background: rgba(255, 255, 255, 0.95);
            color: #333;
            border: 1px solid rgba(0, 0, 0, 0.1);
        }
        
        body.dark-mode #deepseek-refresh-popup .spinner {
            border-top-color: #333;
        }
        
        body.dark-mode #deepseek-refresh-popup .popup-title {
            color: #5a67d8;
        }
        
        .loading-indicator {
            position: fixed;
            top: 0;
            left: 0;
            width: 100%;
            height: 2px;
            background: rgba(102, 126, 234, 0.2);
            z-index: 10002;
        }
        
        .loading-indicator::after {
            content: "";
            position: absolute;
            top: 0;
            left: 0;
            width: 20px;
            height: 2px;
            background: linear-gradient(90deg, transparent, #667eea, transparent);
            animation: loading 2s infinite;
        }
        
        @keyframes loading {
            0% {
                left: -20px;
                top: 0;
            }
            25% {
                left: 100%;
                top: 0;
            }
            50% {
                left: 100%;
                top: calc(100% - 2px);
            }
            75% {
                left: -20px;
                top: calc(100% - 2px);
            }
            100% {
                left: -20px;
                top: 0;
            }
        }
    `;
    
    // Add styles to head
    document.head.appendChild(style);
    
    // Add elements to body
    document.body.appendChild(triggerButton);
    document.body.appendChild(refreshButton);
    document.body.appendChild(refreshPopup);
    document.body.appendChild(welcomeTooltip);
    document.body.appendChild(versionTooltip);
    
    // Create loading indicator
    const loadingIndicator = document.createElement('div');
    loadingIndicator.className = 'loading-indicator';
    document.body.appendChild(loadingIndicator);
    
    // Load version from local server
    function loadVersion() {
        fetch('http://localhost:8080/version.txt')
            .then(response => {
                if (!response.ok) {
                    throw new Error('Network response was not ok');
                }
                return response.text();
            })
            .then(version => {
                const versionNumber = version.trim();
                document.getElementById('version-number').textContent = versionNumber;
            })
            .catch(error => {
                console.error('Error loading version:', error);
                document.getElementById('version-number').textContent = '0.0.0';
            });
    }
    
    // Load version immediately
    loadVersion();
    
    // Show welcome tooltip on page load
    setTimeout(() => {
        // Position tooltip to point to the trigger button
        const triggerRect = triggerButton.getBoundingClientRect();
        welcomeTooltip.style.top = (triggerRect.top - 5) + 'px';
        welcomeTooltip.style.right = (window.innerWidth - triggerRect.right + 20) + 'px';
        
        welcomeTooltip.classList.add('show');
        
        // Hide tooltip after 5 seconds
        setTimeout(() => {
            welcomeTooltip.classList.remove('show');
        }, 5000);
    }, 2000);
    
    // Add click event listener to trigger button
    triggerButton.addEventListener('click', function() {
        showRefreshPopup();
        showLoadingIndicator();
        
        // Dispatch a custom event to notify the desktop app
        const refreshEvent = new CustomEvent('deepseekRefresh', {
            detail: { action: 'refresh' }
        });
        document.dispatchEvent(refreshEvent);
        
        // Refresh the page with current URL path
        const currentPath = window.location.pathname + window.location.search + window.location.hash;
        window.location.href = currentPath;
    });
    
    // Add click event listener to refresh button
    refreshButton.addEventListener('click', function() {
        showRefreshPopup();
        showLoadingIndicator();
        
        // Add refreshing animation
        this.classList.add('refreshing');
        
        // Dispatch a custom event to notify the desktop app
        const refreshEvent = new CustomEvent('deepseekRefresh', {
            detail: { action: 'refresh' }
        });
        document.dispatchEvent(refreshEvent);
        
        // Refresh the page with current URL path
        const currentPath = window.location.pathname + window.location.search + window.location.hash;
        window.location.href = currentPath;
    });
    
    // Function to show refresh popup
    function showRefreshPopup() {
        refreshPopup.classList.add('show');
        
        // Keep popup visible for 3 seconds to ensure user sees it
        setTimeout(() => {
            refreshPopup.classList.remove('show');
        }, 3000);
    }
    
    // Function to show loading indicator
    function showLoadingIndicator() {
        loadingIndicator.style.display = 'block';
        
        // Hide after 5 seconds or when page reloads
        setTimeout(() => {
            loadingIndicator.style.display = 'none';
        }, 5000);
    }
    
    // Auto-hide refresh button when not hovering
    let hideTimeout;
    function hideRefreshButton() {
        hideTimeout = setTimeout(() => {
            refreshButton.style.opacity = '0';
            refreshButton.style.transform = 'translateY(-10px)';
            refreshButton.style.pointerEvents = 'none';
        }, 2000);
    }
    
    function showRefreshButton() {
        clearTimeout(hideTimeout);
        refreshButton.style.opacity = '1';
        refreshButton.style.transform = 'translateY(0)';
        refreshButton.style.pointerEvents = 'auto';
    }
    
    // Add event listeners for auto-hide functionality
    triggerButton.addEventListener('mouseenter', showRefreshButton);
    refreshButton.addEventListener('mouseenter', showRefreshButton);
    triggerButton.addEventListener('mouseleave', hideRefreshButton);
    refreshButton.addEventListener('mouseleave', hideRefreshButton);
    
    // Add event listeners for version tooltip
    function showVersionTooltip() {
        const triggerRect = triggerButton.getBoundingClientRect();
        versionTooltip.style.top = (triggerRect.top - 5) + 'px';
        versionTooltip.style.right = (window.innerWidth - triggerRect.right + 60) + 'px';
        versionTooltip.classList.add('show');
    }
    
    function hideVersionTooltip() {
        versionTooltip.classList.remove('show');
    }
    
    triggerButton.addEventListener('mouseenter', showVersionTooltip);
    refreshButton.addEventListener('mouseenter', showVersionTooltip);
    triggerButton.addEventListener('mouseleave', hideVersionTooltip);
    refreshButton.addEventListener('mouseleave', hideVersionTooltip);
    
    // Initially hide the refresh button
    hideRefreshButton();
    
    return { triggerButton, refreshButton, refreshPopup };
}

// Optimized DOM ready check
function domReady(callback) {
    if (document.readyState === 'loading') {
        document.addEventListener('DOMContentLoaded', callback);
    } else {
        callback();
    }
}

// Initialize when DOM is ready
domReady(() => {
    // Create refresh button with optimized performance
    createRefreshButton();
    
    // Optimize image loading
    if ('loading' in HTMLImageElement.prototype) {
        // Native lazy loading is supported
        document.querySelectorAll('img[loading="lazy"]').forEach(img => {
            img.loading = 'lazy';
        });
    } else {
        // Fallback for browsers that don't support native lazy loading
        scriptLazyLoader();
    }
    
    // Add network performance monitoring
    if ('connection' in navigator) {
        const connection = navigator.connection || navigator.mozConnection || navigator.webkitConnection;
        
        // Adjust loading strategy based on connection type
        if (connection.effectiveType === 'slow-2g' || connection.effectiveType === '2g') {
            // Reduce resources for slow connections
            document.querySelectorAll('video, audio').forEach(media => {
                media.pause();
                media.style.display = 'none';
            });
            
            // Show loading indicator for slow connections
            const loadingIndicator = document.querySelector('.loading-indicator');
            if (loadingIndicator) {
                loadingIndicator.style.display = 'block';
                setTimeout(() => {
                    loadingIndicator.style.display = 'none';
                }, 3000);
            }
        }
    }
    
    // Add page visibility API to pause non-essential content when tab is not visible
    document.addEventListener('visibilitychange', () => {
        if (document.hidden) {
            // Pause animations or non-essential operations when tab is hidden
            document.querySelectorAll('.animate').forEach(el => {
                el.style.animationPlayState = 'paused';
            });
        } else {
            // Resume animations when tab becomes visible
            document.querySelectorAll('.animate').forEach(el => {
                el.style.animationPlayState = 'running';
            });
        }
    });
});

// Script lazy loading for better performance
function scriptLazyLoader() {
    const scripts = document.querySelectorAll('script[data-src]');
    const observer = new IntersectionObserver((entries) => {
        entries.forEach(entry => {
            if (entry.isIntersecting) {
                const script = entry.target;
                const src = script.getAttribute('data-src');
                if (src) {
                    script.src = src;
                    script.removeAttribute('data-src');
                    observer.unobserve(script);
                }
            }
        });
    });
    
    scripts.forEach(script => observer.observe(script));
}

// Load Marked.js library for markdown rendering with optimized loading
const markedScript = document.createElement('script');
markedScript.src = 'https://cdn.jsdelivr.net/npm/marked/marked.min.js';
markedScript.async = true;
markedScript.onload = () => {
    // Marked.js loaded, configure it
    configureMarked();
};
document.head.appendChild(markedScript);

// Load DOMPurify for security sanitization with optimized loading
const dompurifyScript = document.createElement('script');
dompurifyScript.src = 'https://cdn.jsdelivr.net/npm/dompurify@3.0.5/dist/purify.min.js';
dompurifyScript.async = true;
dompurifyScript.onload = () => {
    // DOMPurify loaded
    console.log('DOMPurify loaded');
};
document.head.appendChild(dompurifyScript);

// Load Inter font from Google Fonts with all weights
const interLink = document.createElement('link');
interLink.href = 'https://fonts.googleapis.com/css2?family=Inter:wght@100..900&display=swap';
interLink.rel = 'stylesheet';
interLink.onload = () => {
    // Font loaded, apply styles
    console.log('Inter font loaded');
};
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
    
    // Update dark mode class on body
    document.body.classList.toggle('dark-mode', isDark);
}

// Apply initial theme
applyTheme();

// Listen for system theme changes
if (window.matchMedia) {
    window.matchMedia('(prefers-color-scheme: dark)').addEventListener('change', applyTheme);
}

// Helper function to escape HTML entities (defensive against null/undefined)
function escapeHtml(str) {
    return String(str || '')
        .replace(/&/g, '&amp;')
        .replace(/</g, '&lt;')
        .replace(/>/g, '&gt;')
        .replace(/"/g, '&quot;')
        .replace(/'/g, '&#039;');
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
            try {
                // Handle case where code is an object from markdown parser
                let codeContent = code;
                if (code && typeof code === 'object' && !Array.isArray(code)) {
                    // If it's a code block object, use the text property
                    codeContent = code.text || '';
                }
                
                // Convert to string and trim
                const codeString = String(codeContent || '').trim();
                
                // Extract just the language name from info string (e.g., "js linenums" -> "js")
                let lang = (language || '').split(/\s+/)[0] || 'text';
                
                // If language comes in as an object, try to get it from the raw property
                if (typeof lang === 'object') {
                    const rawLang = lang.raw || '';
                    lang = rawLang.trim().split(/\s+/)[0] || 'text';
                }
                
                // Only escape if not already escaped by Marked.js to prevent double-escaping
                const safeCode = escaped ? codeString : escapeHtml(codeString);
                
                // Create a proper code block with syntax highlighting class
                return `<pre class="code-block"><code class="language-${lang}">${safeCode}</code></pre>`;
            } catch (error) {
                console.error('Error rendering code block:', error);
                const fallbackCode = (code && typeof code === 'object') ? (code.text || '') : code;
                return `<pre class="code-block"><code>${escapeHtml(String(fallbackCode || ''))}</code></pre>`;
            }
        };
        
        // Override inline code rendering
        renderer.codespan = function(code) {
            try {
                // Handle case where code is an object from markdown parser
                let codeContent = code;
                if (code && typeof code === 'object' && !Array.isArray(code)) {
                    // If it's a code span object, try to get the raw content
                    codeContent = code.raw || code.text || '';
                }
                
                // Convert to string, trim, and remove backticks
                let codeString = String(codeContent || '').trim();
                codeString = codeString.replace(/^`+|`+$/g, ''); // Remove surrounding backticks
                
                // When overriding renderer, we're responsible for escaping to prevent XSS
                return `<code class="inline-code">${escapeHtml(codeString)}</code>`;
            } catch (error) {
                console.error('Error rendering inline code:', error);
                return `<code class="inline-code">${escapeHtml(String(code || ''))}</code>`;
            }
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
                // Ensure we're working with a string
                const markdownString = typeof markdownText === 'string' 
                    ? markdownText 
                    : JSON.stringify(markdownText, null, 2);
                
                try {
                    // Parse markdown to HTML
                    const html = window.marked.parse(markdownString);
                    
                    // Sanitize the HTML to prevent XSS
                    const sanitizedHtml = sanitizeHtml(html);
                    
                    // Set the inner HTML with sanitized content
                    element.innerHTML = sanitizedHtml;
                    
                    // Fix spacing issues
                    fixSpacing(element);
                    
                    // Apply code block styling
                    styleCodeBlocks(element);
                } catch (parseError) {
                    console.error('Markdown parsing error:', parseError);
                    // Fallback to showing raw content if parsing fails
                    element.innerHTML = `<pre><code>${escapeHtml(markdownString)}</code></pre>`;
                }
            }
        } catch (error) {
            console.error('Error in renderMarkdown:', error);
            // Try to fallback to plain text if markdown parsing fails
            try {
                const plainText = element.textContent ? element.textContent.trim() : '';
                if (plainText) {
                    // Escape HTML to prevent XSS
                    const escapedText = escapeHtml(plainText);
                    element.innerHTML = `<pre><code>${escapedText}</code></pre>`;
                }
            } catch (fallbackError) {
                console.error('Fallback rendering failed:', fallbackError);
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
                const escapedText = escapeHtml(plainText);
                element.innerHTML = `<pre><code>${escapedText}</code></pre>`;
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
    // Get version from localStorage or fetch it
    function getVersion() {
        return localStorage.getItem('deepseek-version') || '0.0.0';
    }
    
    // Load version if not in localStorage
    function loadVersionIfNeeded() {
        if (!localStorage.getItem('deepseek-version')) {
            fetch('http://localhost:8080/version.txt')
                .then(response => {
                    if (!response.ok) {
                        throw new Error('Network response was not ok');
                    }
                    return response.text();
                })
                .then(version => {
                    const versionNumber = version.trim();
                    localStorage.setItem('deepseek-version', versionNumber);
                    updateFooterVersion(versionNumber);
                })
                .catch(error => {
                    console.error('Error loading version:', error);
                    updateFooterVersion('0.0.0');
                });
        } else {
            updateFooterVersion(getVersion());
        }
    }
    
    // Update footer with version
    function updateFooterVersion(version) {
        const existingFooter = document.querySelector('.deepseek-footer');
        if (existingFooter) {
            existingFooter.innerHTML = `Made by <a href='https://github.com/LousyBook94' target='_blank' style='opacity: 0.7;'>LousyBook01</a>. Powered by <a href='https://deepseek.com/' target='_blank' style='opacity: 0.7;'>DeepSeek</a>. Icons by <a href='https://icons8.com/' target='_blank' style='opacity: 0.7;'>Icons8</a> V${version}`;
        }
    }
    
    // Create footer with version
    targetElement.innerHTML = `<div class="deepseek-footer">Made by <a href='https://github.com/LousyBook94' target='_blank' style='opacity: 0.7;'>LousyBook01</a>. Powered by <a href='https://deepseek.com/' target='_blank' style='opacity: 0.7;'>DeepSeek</a>. Icons by <a href='https://icons8.com/' target='_blank' style='opacity: 0.7;'>Icons8</a> <span class="version-loading">V...</span></div>`;
    
    // Load version
    loadVersionIfNeeded();
    
    // Check for version updates periodically
    setInterval(() => {
        fetch('http://localhost:8080/version.txt')
            .then(response => {
                if (!response.ok) {
                    throw new Error('Network response was not ok');
                }
                return response.text();
            })
            .then(version => {
                const versionNumber = version.trim();
                const currentVersion = localStorage.getItem('deepseek-version');
                if (currentVersion !== versionNumber) {
                    localStorage.setItem('deepseek-version', versionNumber);
                    updateFooterVersion(versionNumber);
                }
            })
            .catch(error => {
                console.error('Error checking for version update:', error);
            });
    }, 30000); // Check every 30 seconds
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