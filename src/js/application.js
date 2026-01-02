async function handleLoadFromGitHub() {
    showNotification('Loading from GitHub.');
    const count = await loadFromGitHub();
    setupButtons();
    showNotification('Loaded ' + count + ' files from GitHub!');

    // Auto-select default
    autoSelectDefault();
}

function autoSelectDefault() {
    // Find ChatGPT Generation button
    const defaultButton = document.querySelector('[data-model="chatgpt"][data-type="generation"]');
    if (defaultButton) {
        defaultButton.click();
    }
}

function copyText(text) {
    navigator.clipboard.writeText(text);
    showNotification('Copied!');
}

async function initApp() {
    await initRenderer();
    document.getElementById('githubBtn').addEventListener('click', handleLoadFromGitHub);
}

if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', initApp);
} else {
    initApp();
}
