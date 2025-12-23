/**
 * PromptLoader - Loads prompts from prompt.json and maps them to essays
 * Use this to enrich essay data with prompt information
 */
class PromptLoader {
    constructor() {
        this.prompts = null;
    }

    /**
     * Load prompts from JSON file
     * @returns {Promise<object>} Promise that resolves with prompts object
     */
    async loadPrompts(filePath = '/src/ai_assessment/prompt.json') {
        try {
            const response = await fetch(filePath);
            this.prompts = await response.json();
            return this.prompts;
        } catch (error) {
            console.error('Error loading prompts:', error);
            return null;
        }
    }

    /**
     * Get prompt by key
     * @param {string} key - Prompt key (e.g., 'assignment_1_prompt')
     * @returns {string} Prompt text or empty string
     */
    getPrompt(key) {
        if (!this.prompts) return '';
        return this.prompts[key] || '';
    }

    /**
     * Map prompt to essay data
     * @param {object} essayData - Essay data object
     * @param {string} promptKey - Key to lookup in prompts
     * @returns {object} Essay data with prompt added
     */
    mapPromptToEssay(essayData, promptKey) {
        const prompt = this.getPrompt(promptKey);
        return {
            ...essayData,
            prompt: prompt
        };
    }

    /**
     * Enrich multiple essays with prompts
     * @param {array} essays - Array of essay objects
     * @param {object} keyMapping - Object mapping essay names to prompt keys
     * @returns {array} Essays with prompts added
     */
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

// Initialize global prompt loader
const promptLoader = new PromptLoader();