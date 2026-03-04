// Load data files from GitHub - Prompt 12 only (_p12 files)
// Uses Git Trees API to avoid the 1000-file Contents API limit
async function loadFromGitHub() {
    const folder = 'critical_thinking';
    const suffix = '_p12.json';
    let totalLoaded = 0;

    const treeUrl = 'https://api.github.com/repos/raminguyen/ai-assessment/git/trees/main?recursive=1';
    const rawBase = 'https://raw.githubusercontent.com/raminguyen/ai-assessment/main/';

    const response = await fetch(treeUrl);
    if (!response.ok) return totalLoaded;

    const treeData = await response.json();

    const jsonFiles = treeData.tree.filter(function(item) {
        return item.type === 'blob' &&
               item.path.startsWith('data/' + folder + '/') &&
               item.path.endsWith(suffix);
    });

    for (const file of jsonFiles) {
        const fileName = file.path.split('/').pop();
        const cacheBuster = '?t=' + Date.now();
        const fileResponse = await fetch(rawBase + file.path + cacheBuster);
        const fileText = await fileResponse.text();

        try {
            const data = JSON.parse(fileText);
            processData(data, folder, fileName);
            totalLoaded++;
        } catch (error) {
            console.error('JSON parse error in file:', fileName);
            console.error('Error:', error.message);
            throw error;
        }
    }

    return totalLoaded;
}
