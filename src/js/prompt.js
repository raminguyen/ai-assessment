class Prompt {
    constructor() {
        this.prompts = null;
    }

    async loadPrompts(filePath = '/src/ai_assessment/prompt.json') {
        const response = await fetch(filePath);

        if (!response.ok) {
            console.warn('Could not load prompts from ' + filePath);
            return null;
        }

        this.prompts = await response.json();
        console.log('Prompts loaded successfully from ' + filePath);
        return this.prompts;
    }

    getPrompt(key) {
        if (!this.prompts) {
            return '';
        }

        if (this.prompts[key]) {
            return this.prompts[key];
        }

        return '';
    }

    mapPromptToEssay(essayData, promptKey) {
        const prompt = this.getPrompt(promptKey);

        const result = {
            essayName: essayData.essayName,
            model: essayData.model,
            command: essayData.command,
            result: essayData.result,
            prompt: prompt
        };

        return result;
    }

    enrichEssays(essays, keyMapping) {
        const enrichedEssays = [];

        for (let i = 0; i < essays.length; i++) {
            
            const essay = essays[i];
            const essayName = essay.essay_name;
            const promptKey = keyMapping[essayName];

            if (promptKey) {
                const enrichedEssay = this.mapPromptToEssay(essay, promptKey);
                enrichedEssays.push(enrichedEssay);
            } else {
                enrichedEssays.push(essay);
            }
        }

        return enrichedEssays;
    }
}

const promptLoader = new Prompt();
