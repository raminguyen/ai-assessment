/**
 * FileProcessor - Enhanced with prompt loading and folder support
 * Reads JSON files and enriches them with prompts from prompt.json
 * Supports both file upload and folder picker (Chrome/Firefox)
 */
class FileProcessor {
    /**
     * Initialize FileProcessor
     * @param {DataManager} dataManager - Reference to DataManager instance
     */
    constructor(dataManager) {
        this.dataManager = dataManager;
        this.promptLoader = new PromptLoader();
        this.initPrompts();
    }

    /**
     * Initialize prompt loader
     * @private
     */
    async initPrompts() {
        await this.promptLoader.loadPrompts('/src/ai_assessment/prompt.json');
    }

    /**
     * Process files from user's disk
     * @param {FileList} files - Files to process
     * @returns {Promise<number>} Promise that resolves with count of files processed
     */
    processLocalFiles(files) {
        return new Promise((resolve, reject) => {
            const jsonFiles = Array.from(files).filter(f => f.name.endsWith('.json'));
            if (jsonFiles.length === 0) {
                reject('No JSON files found!');
                return;
            }
            let filesRead = 0;
            jsonFiles.forEach(file => {
                const reader = new FileReader();
                reader.onload = (e) => {
                    try {
                        const data = JSON.parse(e.target.result);
                        const folderGuess = this.guessFolderFromFilename(file.name);
                        this.processData(data, folderGuess);
                        filesRead++;
                        if (filesRead === jsonFiles.length) {
                            resolve(filesRead);
                        }
                    } catch (error) {
                        reject('Error reading ' + file.name + ': ' + error.message);
                    }
                };
                reader.readAsText(file);
            });
        });
    }

    /**
     * Process folder using File System Access API (Chrome/Firefox)
     * @returns {Promise<number>} Promise that resolves with count of files processed
     */
    async processFolder() {
        try {
            const handle = await window.showDirectoryPicker();
            const files = [];
            
            // Recursively collect JSON files from folder
            await this.collectJsonFiles(handle, files);
            
            if (files.length === 0) {
                throw new Error('No JSON files found in folder!');
            }
            
            // Process all files
            let filesRead = 0;
            return new Promise((resolve, reject) => {
                files.forEach(({file, path}) => {
                    const reader = new FileReader();
                    reader.onload = (e) => {
                        try {
                            const data = JSON.parse(e.target.result);
                            const folderGuess = this.guessFolderFromFilename(file.name);
                            this.processData(data, folderGuess);
                            filesRead++;
                            if (filesRead === files.length) {
                                resolve(filesRead);
                            }
                        } catch (error) {
                            reject('Error reading ' + file.name + ': ' + error.message);
                        }
                    };
                    reader.readAsText(file);
                });
            });
        } catch (error) {
            if (error.name === 'AbortError') {
                throw new Error('Folder selection cancelled');
            }
            throw error;
        }
    }

    /**
     * Recursively collect JSON files from folder
     * @private
     */
    async collectJsonFiles(handle, files, path = '') {
        for await (const entry of handle.values()) {
            const currentPath = path ? path + '/' + entry.name : entry.name;
            
            if (entry.kind === 'file' && entry.name.endsWith('.json')) {
                const file = await entry.getFile();
                files.push({file, path: currentPath});
            } else if (entry.kind === 'directory') {
                // Recursively process subdirectories
                await this.collectJsonFiles(entry, files, currentPath);
            }
        }
    }

    /**
     * Guess the rubric folder from filename
     * @private
     */
    guessFolderFromFilename(filename) {
        if (filename.includes('critical')) {
            return 'critical_thinking';
        } else if (filename.includes('oral')) {
            return 'oral_communication';
        }
        return null;
    }

    /**
     * Process essay data and add to DataManager
     * Enriches with prompt if available
     * @private
     */
    processData(data, folderName) {
        const essayName = data.essay_name;
        const command = data.command;
        // Use folder field from JSON first, then rubric field, then folder parameter
        let rubric = data.folder || data.rubric || folderName || 'unknown';
        this.dataManager.allRubrics.add(rubric);

        // Try to add prompt if not already present
        if (!data.prompt) {
            const promptKey = this.getPromptKeyForEssay(essayName);
            if (promptKey) {
                const prompt = this.promptLoader.getPrompt(promptKey);
                if (prompt) {
                    data.prompt = prompt;
                }
            }
        }

        let modelName;
        if (command === 'score') {
            modelName = ModelParser.getModelName(data.grader || data.model);
        } else {
            modelName = ModelParser.getModelName(data.model);
        }

        this.dataManager.addData(essayName, modelName, command, rubric, data);
    }

    /**
     * Map essay name to prompt key
     * @private
     */
    getPromptKeyForEssay(essayName) {
        // Try static mapping first
        const mapping = {
            'Psychology_Essay_1': 'assignment_1_prompt',
            'Economics_Essay_1': 'assignment_2_prompt',
            'RealEstate_Boston_Analysis': 'assignment_3_prompt',
            'Test_Essay': 'test_prompt'
        };
        
        if (mapping[essayName]) {
            return mapping[essayName];
        }
        
        // If not in mapping, extract number dynamically (Assignment_1 -> assignment_1_prompt)
        const match = essayName.match(/(\d+)/);
        if (match) {
            return 'assignment_' + match[1] + '_prompt';
        }
        
        return null;
    }
}