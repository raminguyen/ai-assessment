async function handleLoadFromGitHub() {
    showNotification('Loading from GitHub.');
    const count = await loadFromGitHub();
    setupButtons();
    showNotification('Loaded ' + count + ' files from GitHub!');
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
