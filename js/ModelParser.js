/**
 * ModelParser - Utility class for parsing and formatting text
 * All methods are static - use directly without instantiation
 */
class ModelParser {
    /**
     * Parse model string and return standardized model name
     * @param {string} modelString - Model string to parse
     * @returns {string} Standardized model name
     */
    static getModelName(modelString) {
        if (!modelString) return 'unknown';

        const model = modelString.toLowerCase();

        // ChatGPT variations
        if (model.includes('gpt') || model.includes('chatgpt') || model.includes('openai')) {
            return 'ChatGPT';
        }

        // Claude variations
        if (model.includes('claude') || model.includes('anthropic')) {
            return 'Claude';
        }

        // Gemini variations
        if (model.includes('gemini') || model.includes('google')) {
            return 'Gemini';
        }

        // Grok variations
        if (model.includes('grok') || model.includes('xai') || model.includes('x.ai')) {
            return 'Grok';
        }

        // Fallback: take text before first dash
        return modelString.split('-')[0];
    }

    /**
     * Format rubric name from snake_case to Title Case
     * @param {string} rubricName - Rubric name in snake_case
     * @returns {string} Formatted rubric name
     */
    static formatRubricName(rubricName) {
        return rubricName
            .split('_')
            .map(word => word.charAt(0).toUpperCase() + word.slice(1))
            .join(' ');
    }
}
