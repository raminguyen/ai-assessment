async function loadFromLocal() {
    const folders = ['critical_thinking'];
    const basePath = 'data/';
    let totalLoaded = 0;

    for (const folder of folders) {
        const folderPath = basePath + folder + '/';

        try {
            const response = await fetch(folderPath);
            const html = await response.text();

            const parser = new DOMParser();
            const doc = parser.parseFromString(html, 'text/html');
            const links = doc.querySelectorAll('a');

            const jsonFiles = [];
            links.forEach(function(link) {
                const href = link.getAttribute('href');
                if (href && href.endsWith('.json')) {
                    jsonFiles.push(href);
                }
            });

            // Fallback list
            if (jsonFiles.length === 0) {
                const knownFiles = [
                    'a1_gen_chatgpt.json',
                    'a1_gen_chatgpt_score_claude.json',
                    'a1_gen_chatgpt_score_gemini.json',
                    'a1_gen_chatgpt_score_grok.json',
                    'a1_reflection_chatgpt.json',
                    'a1_tune_chatgpt.json',
                    'a1_tune_chatgpt_score_claude.json',
                    'a1_tune_chatgpt_score_gemini.json',
                    'a1_tune_chatgpt_score_grok.json'
                ];

                for (const fileName of knownFiles) {
                    jsonFiles.push(fileName);
                }
            }

            for (const fileName of jsonFiles) {
                try {
                    const cacheBuster = '?t=' + Date.now();
                    const fileResponse = await fetch(folderPath + fileName + cacheBuster);

                    if (!fileResponse.ok) {
                        console.warn('Could not load file:', fileName);
                        continue;
                    }

                    const fileText = await fileResponse.text();
                    const data = JSON.parse(fileText);
                    processData(data, folder, fileName);
                    totalLoaded++;
                } catch (error) {
                    console.error('Error loading file:', fileName);
                    console.error('Error:', error.message);
                }
            }
        } catch (error) {
            console.error('Error accessing folder:', folder);
            console.error('Error:', error.message);
        }
    }

    return totalLoaded;
}
