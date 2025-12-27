// Download essays from GitHub
async function loadFromGitHub() {
    const folders = ['critical_thinking', 'oral_communication'];
    let totalLoaded = 0;

    // Download from each folder
    for (const folder of folders) {
        const apiUrl = 'https://api.github.com/repos/raminguyen/ai-assessment/contents/data/' + folder;
        const rawUrl = 'https://raw.githubusercontent.com/raminguyen/ai-assessment/main/data/' + folder + '/';

        // Get list of files in this folder
        const response = await fetch(apiUrl);
        if (!response.ok) continue;

        const files = await response.json();
        const jsonFiles = files.filter(function(file) {
            return file.name.endsWith('.json');
        });

        // Download each JSON file
        for (const file of jsonFiles) {
            // Add cache-busting parameter to ensure fresh data
            const cacheBuster = '?t=' + Date.now();
            const fileResponse = await fetch(rawUrl + file.name + cacheBuster);
            const fileText = await fileResponse.text();
            const data = JSON.parse(fileText);

            // Process and store this essay
            processData(data, folder);
            totalLoaded++;
        }
    }

    return totalLoaded;
}
