async function handleLoadFromGitHub() {
    showNotification('Loading from GitHub...');
    const count = await loadFromGitHub();
    setupButtons();
    showNotification('Loaded ' + count + ' files from GitHub!');
}

async function handleLoadFromLocal() {
    showNotification('Loading local files...');
    const count = await loadFromLocal();
    setupButtons();
    showNotification('Loaded ' + count + ' local files!');
}

function copyText(text) {
    navigator.clipboard.writeText(text);
    showNotification('Copied!');
}

async function initApp() {
    await initRenderer();
    document.getElementById('githubBtn').addEventListener('click', handleLoadFromGitHub);
    document.getElementById('localBtn').addEventListener('click', handleLoadFromLocal);
}

if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', initApp);
} else {
    initApp();
}
