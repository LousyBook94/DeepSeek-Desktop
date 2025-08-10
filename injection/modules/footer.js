// --- Custom Footer ---

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
