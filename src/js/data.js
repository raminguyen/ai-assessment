class Data {
    
    constructor() {
        this.allData = {};
        this.allModels = new Set();
        this.allRubrics = new Set();
    }

    add_data(essayName, modelName, command, rubric, data) {
        const uniqueKey = this.generate_key(essayName, modelName, command, rubric, data);
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

    generate_key(essayName, modelName, command, rubric, data) {
        if (command === 'score') {
            const essayType = data.essay_type || 'generate';
            const graderName = Parser.get_model_name(data.grader);
            return `${essayName}_${modelName}_${essayType}_score_${graderName}_${rubric}`;
        }
        return `${essayName}_${modelName}_${command}_${rubric}`;
    }

    get_data() {
        return this.allData;
    }

    get_models() {
        return Array.from(this.allModels).sort();
    }

    get_rubrics() {
        return Array.from(this.allRubrics).sort();
    }

    clear() {
        this.allData = {};
        this.allModels.clear();
        this.allRubrics.clear();
    }

    get_total_count() {
        return Object.keys(this.allData).length;
    }
}