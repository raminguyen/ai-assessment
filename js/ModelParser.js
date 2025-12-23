/**
 * ModelParser - Utility class for parsing and formatting text
 * All methods are static - use directly without instantiation
 */
class ModelParser {
    /**
     * Extracts "a1", "a2", etc. from filenames like "a1_gen_chatgpt.json"
     */
    static parseEssayName(filename) {
        if (!filename) return 'unknown';
        
        // Split by underscore and take the first part (e.g., "a1")
        const parts = filename.toLowerCase().split('_');
        const prefix = parts[0];
        
        // Ensure it starts with 'a' followed by a number
        if (prefix.startsWith('a') && !isNaN(prefix.slice(1))) {
            return prefix;
        }
        
        return 'unknown';
    }
    
    /**
     * Parse model string and return standardized model name
     */
    static getModelName(modelString) {
        if (!modelString) return 'unknown';
        const model = modelString.toLowerCase();

        if (model.includes('gpt') || model.includes('chatgpt') || model.includes('openai')) return 'ChatGPT';
        if (model.includes('claude') || model.includes('anthropic')) return 'Claude';
        if (model.includes('gemini') || model.includes('google')) return 'Gemini';
        if (model.includes('grok') || model.includes('xai') || model.includes('x.ai')) return 'Grok';

        return modelString.split('-')[0];
    }

    /**
     * Format rubric name from snake_case to Title Case
     */
    static formatRubricName(rubricName) {
        return rubricName
            .split('_')
            .map(word => word.charAt(0).toUpperCase() + word.slice(1))
            .join(' ');
    }
}