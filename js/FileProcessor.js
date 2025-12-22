/**
 * FileProcessor - Handles file reading and data processing
 * Reads JSON files from user's disk
 */
class FileProcessor {
    /**
     * Initialize FileProcessor
     * @param {DataManager} dataManager - Reference to DataManager instance
     */
    constructor(dataManager) {
        this.dataManager = dataManager;
    }

    /**
     * Process files from user's disk
     * Returns a Promise that resolves when all files are processed
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
                        reject(`Error reading ${file.name}: ${error.message}`);
                    }
                };

                reader.readAsText(file);
            });
        });
    }

    /**
     * Guess the rubric folder from filename
     * @private
     * @param {string} filename - Filename to analyze
     * @returns {string|null} Guessed folder name or null
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
     * @param {object} data - Essay data object
     * @param {string} folderName - Folder/rubric name
     */
    processData(data, folderName) {
        const essayName = data.essay_name;
        const command = data.command;

        let rubric = data.rubric || folderName || 'unknown';
        this.dataManager.allRubrics.add(rubric);

        let modelName;
        if (command === 'score') {
            modelName = ModelParser.getModelName(data.writer);
        } else {
            modelName = ModelParser.getModelName(data.model);
        }

        this.dataManager.addData(essayName, modelName, command, rubric, data);
    }
}
