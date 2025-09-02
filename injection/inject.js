// Simplified injection script for version display and refresh button

// Function to create refresh button
function createRefreshButton() {
    try {
        // Create small trigger button element
        const triggerButton = document.createElement('div');
        triggerButton.id = 'deepseek-refresh-trigger';
        triggerButton.title = 'Refresh';
        
        // Create main refresh button element
        const refreshButton = document.createElement('button');
        refreshButton.id = 'deepseek-refresh-btn';
        refreshButton.title = 'Refresh Screen';
        
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
        `;
        
        // Add styles to head
        document.head.appendChild(style);
        
        // Add elements to body
        document.body.appendChild(triggerButton);
        document.body.appendChild(refreshButton);
        
        // Add click event listener to trigger button
        triggerButton.addEventListener('click', function() {
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
        
        // Initially hide the refresh button
        hideRefreshButton();
        
    } catch (error) {
        console.error('Error creating refresh button:', error);
    }
}

// Function to create footer
function createFooter() {
    try {
        // Hide the element with class "._0fcaa63._7941d9f"
        const conflictingElements = document.querySelectorAll('._0fcaa63._7941d9f');
        conflictingElements.forEach(element => {
            element.style.display = 'none';
        });
        
        // Create footer element if it doesn't exist
        let footer = document.querySelector('.deepseek-footer');
        if (!footer) {
            footer = document.createElement('div');
            footer.className = 'deepseek-footer';
            footer.innerHTML = '' +
                'Made by <a href=\'https://github.com/LousyBook94\' target=\'_blank\' style=\'opacity: 0.7;\'>LousyBook01</a>. ' +
                'Powered by <a href=\'https://deepseek.com/\' target=\'_blank\' style=\'opacity: 0.7;\'>DeepSeek</a>. ' +
                'Icons by <a href=\'https://icons8.com/\' target=\'_blank\' style=\'opacity: 0.7;\'>Icons8</a>. ' +
                '<span class="version-loading">v...</span>';
            footer.style.position = 'fixed';
            footer.style.bottom = '10px';
            footer.style.right = '10px';
            footer.style.left = 'auto';
            footer.style.width = 'auto';
            // Убираем фон и эффекты размытия
            footer.style.backgroundColor = 'transparent';
            footer.style.backdropFilter = 'none';
            footer.style.padding = '6px 12px';
            footer.style.textAlign = 'right';
            footer.style.fontSize = '11px';
            footer.style.color = 'rgba(255, 255, 255, 0.6)';
            footer.style.zIndex = '9998';
            // Убираем рамку и тень
            footer.style.borderTop = 'none';
            footer.style.boxShadow = 'none';
            // Добавляем немного прозрачности для лучшей интеграции
            footer.style.opacity = '0.7';
            // Добавляем скругление углов для лучшего вида
            footer.style.borderRadius = '4px';
            
            document.body.appendChild(footer);
        }
        
        // Update version in footer
        updateFooterVersion('0.0.0'); // This will be replaced by Python code
    } catch (error) {
        console.error('Error creating footer:', error);
    }
}

// Function to update footer version
function updateFooterVersion(version) {
    try {
        const footer = document.querySelector('.deepseek-footer');
        if (footer) {
            // Create a safe document fragment with links
            const fragment = document.createDocumentFragment();
            
            // Made by link
            const madeByLink = document.createElement('a');
            madeByLink.href = 'https://github.com/LousyBook94';
            madeByLink.target = '_blank';
            madeByLink.textContent = 'LousyBook01';
            madeByLink.style.color = 'rgba(102, 126, 234, 0.8)';
            madeByLink.style.textDecoration = 'none';
            madeByLink.style.opacity = '1';
            madeByLink.style.transition = 'color 0.2s ease';
            // Добавляем hover эффект
            madeByLink.addEventListener('mouseenter', function() {
                this.style.color = 'rgba(102, 126, 234, 1)';
            });
            madeByLink.addEventListener('mouseleave', function() {
                this.style.color = 'rgba(102, 126, 234, 0.8)';
            });
            fragment.appendChild(document.createTextNode('Made by '));
            fragment.appendChild(madeByLink);
            fragment.appendChild(document.createTextNode(' • '));
            
            // Powered by link
            const poweredByLink = document.createElement('a');
            poweredByLink.href = 'https://deepseek.com/';
            poweredByLink.target = '_blank';
            poweredByLink.textContent = 'DeepSeek';
            poweredByLink.style.color = 'rgba(102, 126, 234, 0.8)';
            poweredByLink.style.textDecoration = 'none';
            poweredByLink.style.opacity = '1';
            poweredByLink.style.transition = 'color 0.2s ease';
            // Добавляем hover эффект
            poweredByLink.addEventListener('mouseenter', function() {
                this.style.color = 'rgba(102, 126, 234, 1)';
            });
            poweredByLink.addEventListener('mouseleave', function() {
                this.style.color = 'rgba(102, 126, 234, 0.8)';
            });
            fragment.appendChild(document.createTextNode('Powered by '));
            fragment.appendChild(poweredByLink);
            fragment.appendChild(document.createTextNode(' • '));
            
            // Icons by link
            const iconsByLink = document.createElement('a');
            iconsByLink.href = 'https://icons8.com/';
            iconsByLink.target = '_blank';
            iconsByLink.textContent = 'Icons8';
            iconsByLink.style.color = 'rgba(102, 126, 234, 0.8)';
            iconsByLink.style.textDecoration = 'none';
            iconsByLink.style.opacity = '1';
            iconsByLink.style.transition = 'color 0.2s ease';
            // Добавляем hover эффект
            iconsByLink.addEventListener('mouseenter', function() {
                this.style.color = 'rgba(102, 126, 234, 1)';
            });
            iconsByLink.addEventListener('mouseleave', function() {
                this.style.color = 'rgba(102, 126, 234, 0.8)';
            });
            fragment.appendChild(document.createTextNode('Icons by '));
            fragment.appendChild(iconsByLink);
            fragment.appendChild(document.createTextNode(' • '));
            fragment.appendChild(document.createTextNode('v' + version)); // This will be replaced by Python code
            
            // Clear existing content and add the new fragment
            footer.innerHTML = '';
            footer.appendChild(fragment);
        }
        
        // Also hide the element with class "._0fcaa63._7941d9f" if it appears later
        const conflictingElements = document.querySelectorAll('._0fcaa63._7941d9f');
        conflictingElements.forEach(element => {
            element.style.display = 'none';
        });
    } catch (error) {
        console.error('Error updating footer version:', error);
    }
}

// Function to set version in localStorage
function setVersion(version) {
    try {
        localStorage.setItem('deepseek-version', version); // This will be replaced by Python code
    } catch (e) {
        console.log('Could not set localStorage version');
    }
}

// Run immediately to create elements
createRefreshButton();
createFooter();

// Also run when DOM is ready
if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', function() {
        // This will be replaced by Python code
        updateFooterVersion('0.0.0');
        setVersion('0.0.0');
    });
} else {
    // This will be replaced by Python code
    updateFooterVersion('0.0.0');
    setVersion('0.0.0');
}

// Run once after a short delay to catch dynamic content
setTimeout(function() {
    // This will be replaced by Python code
    updateFooterVersion('0.0.0');
    setVersion('0.0.0');
    
    // Also hide the element with class "._0fcaa63._7941d9f" if it appears later
    const conflictingElements = document.querySelectorAll('._0fcaa63._7941d9f');
    conflictingElements.forEach(element => {
        element.style.display = 'none';
    });
}, 1000);