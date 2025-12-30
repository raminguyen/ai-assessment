async function loadFromGitHub() {
    const folders = ['critical_thinking', 'oral_communication'];
    let totalLoaded = 0;

    for (const folder of folders) {
        const apiUrl = 'https://api.github.com/repos/raminguyen/ai-assessment/contents/data/' + folder;
        const rawUrl = 'https://raw.githubusercontent.com/raminguyen/ai-assessment/main/data/' + folder + '/';

        const response = await fetch(apiUrl);
        if (!response.ok) continue;

        const files = await response.json();
        const jsonFiles = files.filter(function(file) {
            return file.name.endsWith('.json');
        });

        for (const file of jsonFiles) {
            const cacheBuster = '?t=' + Date.now();
            const fileResponse = await fetch(rawUrl + file.name + cacheBuster);
            const fileText = await fileResponse.text();
            const data = JSON.parse(fileText);

            processData(data, folder);
            totalLoaded++;
        }
    }

    return totalLoaded;
}
