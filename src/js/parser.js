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
// Parse rubric scores from text
function parseRubricScores(text) {
    const dimensions = [
        { name: 'Explanation of issues', level: '--', alt: [] },
        { name: 'Evidence', level: '--', alt: ['Evidence (selecting and using information)'] },
        { name: 'Influence of context and assumptions', level: '--', alt: [] },
        { name: 'Student\'s position', level: '--', alt: ['Student\'s position (perspective/thesis)'] },
        { name: 'Conclusions and related outcomes', level: '--', alt: ['Conclusions/outcomes'] }
    ];

    dimensions.forEach(dim => {
        const namesToTry = [dim.name].concat(dim.alt || []);

        for (const dimName of namesToTry) {

            const dimNameEscaped = dimName
                .replace(/[.*+?^${}()|[\]\\]/g, '\\$&') // Escape regex special characters
                .replace(/'/g, '[\'\u2019]'); // Handle straight and curly apostrophes

            let regex = new RegExp('^\\s*-\\s*\\*\\*' + dimNameEscaped + ':\\*\\*\\s*(\\d+)', 'im'); // Format: - **Dimension:** 3
            let match = text.match(regex);

            if (match) {
                dim.level = match[1];
                return;
            }

            regex = new RegExp('\\*\\*' + dimNameEscaped + ':\\*\\*\\s*(\\d+)', 'i'); // Format: **Dimension:** 3
            match = text.match(regex);

            if (match) {
                dim.level = match[1];
                return;
            }

            regex = new RegExp('\\|\\s*\\*\\*' + dimNameEscaped + '\\*\\*\\s*\\|\\s*\\*\\*(\\d+)\\*\\*\\s*\\|', 'i'); // Format: | **Dimension** | **3** |
            match = text.match(regex);

            if (match) {
                dim.level = match[1];
                return;
            }

            regex = new RegExp('\\|\\s*\\*\\*' + dimNameEscaped + '\\*\\*\\s*\\|\\s*(\\d+)\\s*\\|', 'i'); // Format: | **Dimension** | 3 |
            match = text.match(regex);

            if (match) {
                dim.level = match[1];
                return;
            }


            regex = new RegExp('\\|\\s*' + dimNameEscaped + '\\s*\\|\\s*(\\d+)\\s*\\|', 'i'); // Format: | Dimension | 3 |
            match = text.match(regex);

            if (match) {
                dim.level = match[1];
                return;
            }


            regex = new RegExp('\\*\\*' + dimNameEscaped + ':\\*\\*\\s*\\*\\*(\\d+)', 'i'); // Format: **Dimension:** **3
            match = text.match(regex);

            if (match) {
                dim.level = match[1];
                return;
            }

            regex = new RegExp(dimNameEscaped + ':\\s*\\*\\*(\\d+)\\*\\*', 'i'); // Format: Dimension: **3**
            match = text.match(regex);

            if (match) {
                dim.level = match[1];
                return;
            }

            regex = new RegExp(dimNameEscaped + ':\\s*\\[(\\d+)\\]', 'i'); // Format: Dimension: [3]
            match = text.match(regex);

            if (match) {
                dim.level = match[1];
                return;
            }

            regex = new RegExp(dimNameEscaped + ':\\s*(\\d+)', 'i'); // Format: Dimension: 3
            match = text.match(regex);

            if (match) {
                dim.level = match[1];
                return;
            }

            regex = new RegExp('\\*\\*' + dimNameEscaped + ':\\s*(\\d+)\\*\\*', 'i'); // Format: **Dimension: 3**
            match = text.match(regex);

            if (match) {
                dim.level = match[1];
                return;
            }

            regex = new RegExp(dimNameEscaped + '.*?:\\s*\\*\\*(\\d+)\\*\\*', 'i'); // Flexible: text before colon
            match = text.match(regex);

            if (match) {
                dim.level = match[1];
                return;
            }

            regex = new RegExp(dimNameEscaped + '.*?:\\s*(\\d+)', 'i'); // Catch-all: any colon format
            match = text.match(regex);

            if (match) {
                dim.level = match[1];
                return;
            }

            regex = new RegExp(dimNameEscaped + '.*?(Capstone 4|Milestone 3|Milestone 2|Benchmark 1)', 'i'); // Named levels: Capstone, Milestone, Benchmark 
            match = text.match(regex);

            if (match) {
                dim.level = match[1];
                return;
            }
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
