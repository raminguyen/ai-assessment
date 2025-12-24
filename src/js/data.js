class Data {
    constructor() {
        this.allData = {};
        this.allModels = new Set();
        this.allRubrics = new Set();
    }

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

    generateKey(essayName, modelName, command, rubric, data) {
        if (command === 'score') {
            const essayType = data.essay_type || 'generate';
            const graderName = Parser.getModelName(data.grader);
            return `${essayName}_${modelName}_${essayType}_score_${graderName}_${rubric}`;
        }
        return `${essayName}_${modelName}_${command}_${rubric}`;
    }

    getData() {
        return this.allData;
    }

    getModels() {
        return Array.from(this.allModels).sort();
    }

    getRubrics() {
        return Array.from(this.allRubrics).sort();
    }

    clear() {
        this.allData = {};
        this.allModels.clear();
        this.allRubrics.clear();
    }

    getTotalCount() {
        return Object.keys(this.allData).length;
    }
}