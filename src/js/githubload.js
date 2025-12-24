class LoadGitHub {
    constructor(dataManager) {
        this.dataManager = dataManager;
        this.folders = ['critical_thinking', 'oral_communication'];
    }

    async loadFromGitHub() {
        let totalLoaded = 0;
        for (const folder of this.folders) {
            const apiUrl = `https://api.github.com/repos/raminguyen/ai-assessment/contents/data/${folder}`;
            const rawUrl = `https://raw.githubusercontent.com/raminguyen/ai-assessment/main/data/${folder}/`;
            
            const response = await fetch(apiUrl);
            
            if (!response.ok) {
                console.warn(`Skipping ${folder}: ${response.status}`);
                continue;
            }
            
            const files = await response.json();
            
            if (!Array.isArray(files)) {
                console.warn(`Skipping ${folder}: unexpected response format`);
                continue;
            }
            
            const jsonFiles = files.filter(file => file.name.endsWith('.json'));
            
            for (const file of jsonFiles) {
                const fileResponse = await fetch(rawUrl + file.name);
                const fileText = await fileResponse.text();
                const data = JSON.parse(fileText);
                
                const processor = new File(this.dataManager);
                processor.processData(data, folder);
                totalLoaded++;
            }
        }
        return totalLoaded;
    }
}