class Parser {
    static parse_essay_name(filename) {
        if (!filename) return 'unknown';
        
        const parts = filename.toLowerCase().split('_');
        const prefix = parts[0];
        
        if (prefix.startsWith('a') && !isNaN(prefix.slice(1))) {
            return prefix;
        }
        
        return 'unknown';
    }
    
    static get_model_name(modelString) {
        
        if (!modelString) return 'unknown';
        const model = modelString.toLowerCase();

        if (model.includes('gpt') || model.includes('chatgpt') || model.includes('openai')) return 'ChatGPT';
        if (model.includes('claude') || model.includes('anthropic')) return 'Claude';
        if (model.includes('gemini') || model.includes('google')) return 'Gemini';
        if (model.includes('grok') || model.includes('xai') || model.includes('x.ai')) return 'Grok';

        return modelString.split('-')[0];
    }

    static format_rubric_name(rubricName) {
        return rubricName
            .split('_')
            .map(word => word.charAt(0).toUpperCase() + word.slice(1))
            .join(' ');
    }
}