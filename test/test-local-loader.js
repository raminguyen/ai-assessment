// Load test data files from local test/data folder
async function loadFromTestFolderLocal() {
    console.log('Loading from local test folder...');
    const folders = ['critical_thinking'];
    const basePath = 'data/';
    let totalLoaded = 0;

    for (const folder of folders) {
        const folderPath = basePath + folder + '/';
        console.log('Folder path:', folderPath);

        // List of all test files for all assignments
        const allTestFiles = [
            // Assignment 1
            'a1_test1_chatgpt.json',
            'a1_test1_gemini.json',
            'a1_test1_claude.json',
            'a1_test1_grok.json',
            'a1_test2_chatgpt.json',
            'a1_test2_gemini.json',
            'a1_test2_claude.json',
            'a1_test2_grok.json',
            // Assignment 2
            'a2_test1_chatgpt.json',
            'a2_test1_gemini.json',
            'a2_test1_claude.json',
            'a2_test1_grok.json',
            'a2_test2_chatgpt.json',
            'a2_test2_gemini.json',
            'a2_test2_claude.json',
            'a2_test2_grok.json',
            // Assignment 3
            'a3_test1_chatgpt.json',
            'a3_test1_gemini.json',
            'a3_test1_claude.json',
            'a3_test1_grok.json',
            'a3_test2_chatgpt.json',
            'a3_test2_gemini.json',
            'a3_test2_claude.json',
            'a3_test2_grok.json'
        ];

        // No filtering - load all test files
        const testFiles = allTestFiles;

        for (const fileName of testFiles) {
            try {
                const cacheBuster = '?t=' + Date.now();
                const fileResponse = await fetch(folderPath + fileName + cacheBuster);

                if (!fileResponse.ok) {
                    console.warn('Could not load file:', fileName);
                    continue;
                }

                const fileText = await fileResponse.text();
                const data = JSON.parse(fileText);
                console.log('Loaded file:', fileName, 'Has prompt:', !!data.prompt);
                processData(data, folder, fileName);
                totalLoaded++;
            } catch (error) {
                console.warn('Error loading file:', fileName, error.message);
            }
        }
    }

    return totalLoaded;
}
