// Handle GitHub button click
async function handleLoadFromGitHub() {
    showNotification('Loading from GitHub...');
    const count = await loadFromGitHub();

    // After loading, re-setup buttons to handle the loaded data
    setupButtons();

    showNotification('Loaded ' + count + ' files from GitHub!');
}

// Copy text to clipboard
function copyText(text) {
    navigator.clipboard.writeText(text);
    showNotification('Copied!');
}

// Initialize app
async function initApp() {
    await initRenderer();
    document.getElementById('githubBtn').addEventListener('click', handleLoadFromGitHub);
}

// Start when ready
if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', initApp);
} else {
    initApp();
}
