// Load test data files from test/data folder
async function loadFromTestFolder() {
    const folders = ['critical_thinking'];
    let totalLoaded = 0;

    for (const folder of folders) {
        const apiUrl = 'https://api.github.com/repos/raminguyen/ai-assessment/contents/test/data/' + folder;
        const rawUrl = 'https://raw.githubusercontent.com/raminguyen/ai-assessment/main/test/data/' + folder + '/';

        try {
            const response = await fetch(apiUrl);
            if (!response.ok) {
                console.log('Could not load from GitHub, trying local...');
                continue;
            }

            const files = await response.json();

            // Load all test JSON files (a1, a2, a3)
            const jsonFiles = files.filter(function(file) {
                return file.name.endsWith('.json');
            });

            for (const file of jsonFiles) {
                const cacheBuster = '?t=' + Date.now();
                const fileResponse = await fetch(rawUrl + file.name + cacheBuster);
                const fileText = await fileResponse.text();

                try {
                    const data = JSON.parse(fileText);
                    processData(data, folder, file.name);
                    totalLoaded++;
                } catch (error) {
                    console.error('JSON parse error in file:', file.name);
                    console.error('Error:', error.message);
                }
            }
        } catch (error) {
            console.error('Error loading from GitHub:', error);
        }
    }

    return totalLoaded;
}
