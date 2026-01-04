async function handleLoadFromGitHub() {
    showNotification('Loading from GitHub.');
    const count = await loadFromGitHub();
    setupButtons();
    showNotification('Loaded ' + count + ' files from GitHub!');

    // Auto-select default
    autoSelectDefault();
}

async function handleLoadFromLocal() {
    showNotification('Loading from local files.');
    const count = await loadFromLocal();
    setupButtons();
    showNotification('Loaded ' + count + ' files from local directory!');

    // Auto-select default
    autoSelectDefault();
}

function autoSelectDefault() {
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
    document.getElementById('localBtn').addEventListener('click', handleLoadFromLocal);

    await handleLoadFromLocal();
}

if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', initApp);
} else {
    initApp();
}
