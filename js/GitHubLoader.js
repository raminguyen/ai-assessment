/**
 * GitHubLoader - Handles fetching essay data from GitHub
 * Loads files from specific GitHub repository folders
 */
class GitHubLoader {
    /**
     * Initialize GitHubLoader
     * @param {DataManager} dataManager - Reference to DataManager instance
     */
    constructor(dataManager) {
        this.dataManager = dataManager;
        this.folders = ['critical_thinking', 'oral_communication'];
    }

    /**
     * Load essays from GitHub repository
     * @returns {Promise<number>} Promise that resolves with count of files loaded
     */
    async loadFromGitHub() {
        let totalLoaded = 0;
        for (const folder of this.folders) {
            const apiUrl = `https://api.github.com/repos/raminguyen/ai-assessment/contents/data/${folder}`;
            const rawUrl = `https://raw.githubusercontent.com/raminguyen/ai-assessment/main/data/${folder}/`;
            try {
                const response = await fetch(apiUrl);
                const files = await response.json();
                const jsonFiles = files.filter(file => file.name.endsWith('.json'));
                for (const file of jsonFiles) {
                    try {
                        const fileResponse = await fetch(rawUrl + file.name);
                        const fileText = await fileResponse.text();
                        const data = JSON.parse(fileText);
                        
                        const processor = new FileProcessor(this.dataManager);
                        processor.processData(data, folder);
                        totalLoaded++;
                    } catch (error) {
                        console.error(`Error loading ${file.name}:`, error);
                    }
                }
            } catch (error) {
                console.error(`Error loading from folder ${folder}:`, error);
            }
        }
        return totalLoaded;
    }
}