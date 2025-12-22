/**
 * DataManager - Handles all data operations
 * Stores essays, models, and rubrics in memory
 */
class DataManager {
    constructor() {
        this.allData = {};
        this.allModels = new Set();
        this.allRubrics = new Set();
    }

    /**
     * Add an essay to the data store
     * @param {string} essayName - Name of the essay
     * @param {string} modelName - Name of the model
     * @param {string} command - Command type (generate/tune/score)
     * @param {string} rubric - Rubric type
     * @param {object} data - The essay data object
     */
    addData(essayName, modelName, command, rubric, data) {
        const uniqueKey = this.generateKey(essayName, modelName, command, rubric, data);
        this.allData[uniqueKey] = {
            essayName,
            modelName,
            command,
            rubric,
            data
        };
        this.allModels.add(modelName);
        this.allRubrics.add(rubric);
    }

    /**
     * Generate a unique key for storing the essay
     * @private
     */
    generateKey(essayName, modelName, command, rubric, data) {
        if (command === 'score') {
            const essayType = data.essay_type || 'generate';
            const graderName = ModelParser.getModelName(data.grader);
            return `${essayName}_${modelName}_${essayType}_score_${graderName}_${rubric}`;
        }
        return `${essayName}_${modelName}_${command}_${rubric}`;
    }

    /**
     * Get all stored data
     * @returns {object} All essays
     */
    getData() {
        return this.allData;
    }

    /**
     * Get sorted list of all models
     * @returns {array} Sorted model names
     */
    getModels() {
        return Array.from(this.allModels).sort();
    }

    /**
     * Get sorted list of all rubrics
     * @returns {array} Sorted rubric names
     */
    getRubrics() {
        return Array.from(this.allRubrics).sort();
    }

    /**
     * Clear all data from storage
     */
    clear() {
        this.allData = {};
        this.allModels.clear();
        this.allRubrics.clear();
    }

    /**
     * Get total count of essays
     * @returns {number} Total number of essays
     */
    getTotalCount() {
        return Object.keys(this.allData).length;
    }
}
