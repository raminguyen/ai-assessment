async function loadFromTestFolder(testNumber = '0') {
    console.log('--- loadFromTestFolder called ---');
    console.log('testNumber:', testNumber);
    const folders = ['critical_thinking'];
    let totalLoaded = 0;

    for (const folder of folders) {
        const apiUrl = `https://api.github.com/repos/raminguyen/ai-assessment/contents/test/test${testNumber}/data/${folder}`;
        const rawUrl = `https://raw.githubusercontent.com/raminguyen/ai-assessment/main/test/test${testNumber}/data/${folder}/`;
        console.log('apiUrl:', apiUrl);

        try {
            const response = await fetch(apiUrl);
            console.log('GitHub API response:', response);
            if (!response.ok) {
                console.error('Could not load from GitHub. Status:', response.status);
                continue;
            }

            const files = await response.json();
            console.log('Files from GitHub:', files);

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
