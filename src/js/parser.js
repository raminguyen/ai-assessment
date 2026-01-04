function parseEssayName(filename) {
    if (!filename) return 'unknown';
    const firstPart = filename.toLowerCase().split('_')[0];
    if (firstPart.startsWith('a')) {
        return firstPart;
    }
    if (firstPart.startsWith('h')) {
        return firstPart;
    }
    return 'unknown';
}

function getModelName(modelString) {
    if (!modelString) return 'unknown';
    const model = modelString.toLowerCase();

    if (model.includes('human')) {
        const match = modelString.match(/human.*?(\d+)/i);
        if (match) {
            return 'Human ' + match[1];
        }
        return 'Human';
    }

    if (model.startsWith('gpt-') || model.startsWith('gpt') || model.includes('chatgpt')) return 'ChatGPT';
    if (model.includes('claude')) return 'Claude';
    if (model.includes('gemini')) return 'Gemini';
    if (model.includes('grok')) return 'Grok';

    return modelString;
}

function formatRubricName(rubricName) {
    return rubricName
        .split('_')
        .map(word => word.charAt(0).toUpperCase() + word.slice(1))
        .join(' ');
}
// Parse rubric scores from text and extract dimension levels
function parseRubricScores(text) {
    const dimensions = [
        { name: 'Explanation of issues', level: '--' },
        { name: 'Evidence', level: '--' },
        { name: 'Influence of context and assumptions', level: '--' },
        { name: 'Student\'s position', level: '--' },
        { name: 'Conclusions and related outcomes', level: '--' }
    ];

    dimensions.forEach(dim => {
        // Table with bold
        let regex = new RegExp('\\|\\s*\\*\\*' + dim.name + '\\*\\*\\s*\\|\\s*(\\d+)\\s*\\|', 'i');
        let match = text.match(regex);

        if (match) {
            dim.level = match[1];
            return;
        }

        // Table without bold
        regex = new RegExp('\\|\\s*' + dim.name + '\\s*\\|\\s*(\\d+)\\s*\\|', 'i');
        match = text.match(regex);

        if (match) {
            dim.level = match[1];
            return;
        }

        // Colon with bold
        regex = new RegExp(dim.name + ':\\s*\\*\\*(\\d+)\\*\\*', 'i');
        match = text.match(regex);

        if (match) {
            dim.level = match[1];
            return;
        }

        // Colon with brackets
        regex = new RegExp(dim.name + ':\\s*\\[(\\d+)\\]', 'i');
        match = text.match(regex);

        if (match) {
            dim.level = match[1];
            return;
        }

        // Simple colon format
        regex = new RegExp(dim.name + ':\\s*(\\d+)', 'i');
        match = text.match(regex);

        if (match) {
            dim.level = match[1];
            return;
        }

        // Flexible with bold
        const dimNameEscaped = dim.name.replace(/[.*+?^${}()|[\]\\]/g, '\\$&');
        regex = new RegExp(dimNameEscaped + '.*?:\\s*\\*\\*(\\d+)\\*\\*', 'i');
        match = text.match(regex);

        if (match) {
            dim.level = match[1];
            return;
        }

        // Flexible without bold
        regex = new RegExp(dimNameEscaped + '.*?:\\s*(\\d+)', 'i');
        match = text.match(regex);

        if (match) {
            dim.level = match[1];
            return;
        }

        // Named levels
        regex = new RegExp(dim.name + '.*?(Capstone 4|Milestone 3|Milestone 2|Benchmark 1)', 'i');
        match = text.match(regex);

        if (match) {
            dim.level = match[1];
        }
    });

    return dimensions;
}

function getScoreClass(level) {
    const levelStr = String(level).toLowerCase();

    if (levelStr === '4' || levelStr.includes('capstone')) return 'capstone';
    if (levelStr === '3' || levelStr.includes('milestone 3')) return 'milestone-3';
    if (levelStr === '2' || levelStr.includes('milestone 2')) return 'milestone-2';
    if (levelStr === '1' || levelStr.includes('benchmark')) return 'benchmark';

    return '';
}

function removeMarkdown(text) {
    
    if (!text) return '';

    return text

        .replace(/^#{1,6}\s+(.+)$/gm, '$1')         // Remove headers (#, ##, ###)

        .replace(/(\*\*|__)(.*?)\1/g, '$2')         // Remove bold (**text** or __text__)

        .replace(/(\*|_)(.*?)\1/g, '$2')            // Remove italic (*text* or _text_)

        .replace(/`([^`]+)`/g, '$1')                // Remove inline code (`text`)

        .replace(/\[([^\]]+)\]\([^\)]+\)/g, '$1')   // Remove links [text](url)

        .replace(/^[\*\-\+]\s+/gm, '')              // Remove bullet points (*, -, +)

        .replace(/^\d+\.\s+/gm, '')                 // Remove numbered lists (1., 2., etc)

        .replace(/^>\s+/gm, '')                     // Remove blockquotes (>)

        .replace(/^[\-\*\_]{3,}$/gm, '')            // Remove horizontal rules (---, ***, ___)

        .replace(/```[\s\S]*?```/g, match => {      // Remove code blocks (```code```)

            return match.replace(/```\w*\n?/g, '').trim();
            
        })
        .replace(/\n{3,}/g, '\n\n')                 // Replace 3+ newlines with 2
        .trim();
}
