// Look for essay names "a1, a2"
function parseEssayName(filename) {
    if (!filename) return 'unknown';

    // Get first part: "a1_essay" → "a1"
    const firstPart = filename.toLowerCase().split('_')[0];

    // If starts with 'a' and has number, return it
    if (firstPart.startsWith('a')) {
        return firstPart;
    }

    return 'unknown';
}

// Figure out which AI model
function getModelName(modelString) {
    if (!modelString) return 'unknown';

    const model = modelString.toLowerCase();

    // Check for human graders first
    if (model.includes('human')) {
        // Extract human number if present (e.g., "Human Grader 1" -> "Human 1")
        const match = modelString.match(/human.*?(\d+)/i);
        if (match) {
            return 'Human ' + match[1];
        }
        return 'Human';
    }

    // Check in order: more specific patterns first
    if (model.startsWith('gpt-') || model.startsWith('gpt') || model.includes('chatgpt')) return 'ChatGPT';
    if (model.includes('claude')) return 'Claude';
    if (model.includes('gemini')) return 'Gemini';
    if (model.includes('grok')) return 'Grok';

    return modelString;
}

// Format name: "critical_thinking" → "Critical Thinking"
function formatRubricName(rubricName) {
    return rubricName
        .split('_')
        .map(word => word.charAt(0).toUpperCase() + word.slice(1))
        .join(' ');
}