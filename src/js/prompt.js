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
        if (!this.prompts) return '';
        return this.prompts[key] || '';
    }

    mapPromptToEssay(essayData, promptKey) {
        const prompt = this.getPrompt(promptKey);
        return {
            ...essayData,
            prompt: prompt
        };
    }

    enrichEssays(essays, keyMapping) {
        return essays.map(essay => {
            const promptKey = keyMapping[essay.essay_name];
            if (promptKey) {
                return this.mapPromptToEssay(essay, promptKey);
            }
            return essay;
        });
    }
}

const promptLoader = new Prompt();