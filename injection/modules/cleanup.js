// --- UI Cleanup ---

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
