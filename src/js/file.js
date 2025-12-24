class File {
    constructor(dataManager) {
        this.dataManager = dataManager;
        this.prompts = {};
        this.loadPrompts();
    }

    async loadPrompts() {
        const response = await fetch('src/ai_assessment/prompt.json');
        if (!response.ok) {
            console.warn('Could not load prompts');
            return;
        }
        this.prompts = await response.json();
        console.log('Prompts loaded successfully');
    }

    getPrompt(key) {
        return this.prompts[key] || '';
    }

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
                    const data = JSON.parse(e.target.result);
                    const folderGuess = this.guessFolderFromFilename(file.name);
                    this.processData(data, folderGuess);
                    filesRead++;
                    if (filesRead === jsonFiles.length) {
                        resolve(filesRead);
                    }
                };
                reader.readAsText(file);
            });
        });
    }

    async processFolder() {
        const handle = await window.showDirectoryPicker();
        const files = [];
        
        await this.collectJsonFiles(handle, files);
        
        if (files.length === 0) {
            throw new Error('No JSON files found in folder!');
        }
        
        let filesRead = 0;
        return new Promise((resolve, reject) => {
            files.forEach(({file, path}) => {
                const reader = new FileReader();
                reader.onload = (e) => {
                    const data = JSON.parse(e.target.result);
                    const folderGuess = this.guessFolderFromFilename(file.name);
                    this.processData(data, folderGuess);
                    filesRead++;
                    if (filesRead === files.length) {
                        resolve(filesRead);
                    }
                };
                reader.readAsText(file);
            });
        });
    }

    async collectJsonFiles(handle, files, path = '') {
        for await (const entry of handle.values()) {
            const currentPath = path ? path + '/' + entry.name : entry.name;
            
            if (entry.kind === 'file' && entry.name.endsWith('.json')) {
                const file = await entry.getFile();
                files.push({file, path: currentPath});
            } else if (entry.kind === 'directory') {
                await this.collectJsonFiles(entry, files, currentPath);
            }
        }
    }

    guessFolderFromFilename(filename) {
        if (filename.includes('critical')) {
            return 'critical_thinking';
        } else if (filename.includes('oral')) {
            return 'oral_communication';
        }
        return null;
    }

    processData(data, folderName) {
        const essayName = data.essay_name;
        const command = data.command;
        let rubric = data.folder || data.rubric || folderName || 'unknown';
        this.dataManager.allRubrics.add(rubric);

        if (!data.prompt) {
            const promptKey = this.getPromptKeyForEssay(essayName);
            if (promptKey) {
                const prompt = this.getPrompt(promptKey);
                if (prompt) {
                    data.prompt = prompt;
                }
            }
        }

        let modelName;
        if (command === 'score') {
            modelName = Parser.getModelName(data.writer);
        } else {
            modelName = Parser.getModelName(data.model);
        }

        this.dataManager.addData(essayName, modelName, command, rubric, data);
    }

    getPromptKeyForEssay(essayName) {
        const mapping = {
            'Psychology_Essay_1': 'assignment_1_prompt',
            'Economics_Essay_1': 'assignment_2_prompt',
            'RealEstate_Boston_Analysis': 'assignment_3_prompt',
            'Test_Essay': 'test_prompt'
        };
        
        if (mapping[essayName]) {
            return mapping[essayName];
        }
        
        const match = essayName.match(/(\d+)/);
        if (match) {
            return 'assignment_' + match[1] + '_prompt';
        }
        
        return null;
    }
}