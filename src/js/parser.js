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
                .replace(/'/g, '[\'\u2019]') // Handle straight and curly apostrophes
                .replace(/\b(and|&)\b/gi, '(?:and|&)') // Handle "and" vs "&" interchangeably

            let regex = new RegExp('^\\s*-\\s*\\*\\*' + dimNameEscaped + ':\\*\\*\\s*(\\d+(?:\\.\\d+)?)', 'im'); // Format: - **Dimension:** 3 or 3.5
            let match = text.match(regex);

            if (match) {
                dim.level = match[1];
                return;
            }

            regex = new RegExp('###\\s*\\d+\\.\\s*' + dimNameEscaped + ':[^\\n]*?\\*\\*(\\d+(?:\\.\\d+)?)', 'i'); // Format: ### 1. Dimension: **3.5/4
            match = text.match(regex);

            if (match) {
                dim.level = match[1];
                return;
            }

            regex = new RegExp(dimNameEscaped + '[^\\n]*?\\n[\\s\\S]{0,500}?\\*\\*Score:\\s*(\\d+(?:\\.\\d+)?)\\s*\\([^)]+\\)\\*\\*', 'i'); // Format: **Score: 4 (Capstone)**
            match = text.match(regex);

            if (match) {
                dim.level = match[1];
                return;
            }

            regex = new RegExp(dimNameEscaped + '[^\\n]*?\\n[\\s\\S]{0,500}?\\*\\*Score:\\*\\*\\s*(\\d+(?:\\.\\d+)?)', 'i'); // Format: **Score:** 3.5
            match = text.match(regex);

            if (match) {
                dim.level = match[1];
                return;
            }

            regex = new RegExp('\\*\\*' + dimNameEscaped + ':\\*\\*\\s*(\\d+(?:\\.\\d+)?)/\\d+', 'i'); // Format: **Dimension:** 3.5/4
            match = text.match(regex);

            if (match) {
                dim.level = match[1];
                return;
            }

            regex = new RegExp('\\*\\*' + dimNameEscaped + ':\\*\\*\\s*(\\d+(?:\\.\\d+)?)', 'i'); // Format: **Dimension:** 3 or 3.5
            match = text.match(regex);

            if (match) {
                dim.level = match[1];
                return;
            }

            regex = new RegExp('\\|\\s*\\*\\*' + dimNameEscaped + '\\*\\*\\s*\\|\\s*(\\d+(?:\\.\\d+)?)\\s*\\([^)]+\\)\\s*\\|', 'i'); // Format: | **Dimension** | 4 (Capstone) |
            match = text.match(regex);

            if (match) {
                dim.level = match[1];
                return;
            }

            regex = new RegExp('\\|\\s*\\*\\*' + dimNameEscaped + '\\*\\*\\s*\\|\\s*\\*\\*(\\d+(?:\\.\\d+)?)\\*\\*\\s*\\|', 'i'); // Format: | **Dimension** | **3** | or **3.5** |
            match = text.match(regex);

            if (match) {
                dim.level = match[1];
                return;
            }

            regex = new RegExp('\\|\\s*\\*\\*' + dimNameEscaped + '\\*\\*\\s*\\|\\s*(\\d+(?:\\.\\d+)?)\\s*\\|', 'i'); // Format: | **Dimension** | 3 | or 3.5 |
            match = text.match(regex);

            if (match) {
                dim.level = match[1];
                return;
            }


            regex = new RegExp('\\|\\s*' + dimNameEscaped + '\\s*\\|\\s*(\\d+(?:\\.\\d+)?)\\s*\\|', 'i'); // Format: | Dimension | 3 | or 3.5 |
            match = text.match(regex);

            if (match) {
                dim.level = match[1];
                return;
            }


            regex = new RegExp('\\*\\*' + dimNameEscaped + ':\\*\\*\\s*\\*\\*(\\d+(?:\\.\\d+)?)', 'i'); // Format: **Dimension:** **3 or **3.5
            match = text.match(regex);

            if (match) {
                dim.level = match[1];
                return;
            }

            regex = new RegExp(dimNameEscaped + ':\\s*\\*\\*(\\d+(?:\\.\\d+)?)\\*\\*', 'i'); // Format: Dimension: **3** or **3.5**
            match = text.match(regex);

            if (match) {
                dim.level = match[1];
                return;
            }

            regex = new RegExp(dimNameEscaped + ':\\s*\\[(\\d+(?:\\.\\d+)?)\\]', 'i'); // Format: Dimension: [3] or [3.5]
            match = text.match(regex);

            if (match) {
                dim.level = match[1];
                return;
            }

            regex = new RegExp(dimNameEscaped + ':\\s*(\\d+(?:\\.\\d+)?)', 'i'); // Format: Dimension: 3 or 3.5
            match = text.match(regex);

            if (match) {
                dim.level = match[1];
                return;
            }

            regex = new RegExp('\\*\\*' + dimNameEscaped + ':\\s*(\\d+(?:\\.\\d+)?)\\*\\*', 'i'); // Format: **Dimension: 3** or **Dimension: 3.5**
            match = text.match(regex);

            if (match) {
                dim.level = match[1];
                return;
            }

            regex = new RegExp(dimNameEscaped + '.*?:\\s*\\*\\*(\\d+(?:\\.\\d+)?)\\*\\*', 'i'); // Flexible: any text then bold score
            match = text.match(regex);

            if (match) {
                dim.level = match[1];
                return;
            }

            regex = new RegExp(dimNameEscaped + '.*?:\\s*(\\d+(?:\\.\\d+)?)', 'i'); // Catch-all: any colon with decimal
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

            // | Dimension | 3 |
            regex = new RegExp('\\|\\s*' + dimNameEscaped + '\\s*\\|\\s*(\\d+(?:\\.\\d+)?)\\s*\\|', 'i'); // Dimension | 3 |
            match = text.match(regex);

            if (match) {
                dim.level = match[1];
                return;
            }

            regex = new RegExp('###\\s*\\d+[).]?\\s*' + dimNameEscaped + '\\s*[\\u2014\\u2013\\-]\\s*\\*\\*(\\d+(?:\\.\\d+)?)\\b', 'i'); // 1) Explanation of issues — **3 (Milestone)**
            match = text.match(regex);

            if (match) {
                dim.level = match[1];
                return;
            }
            
            regex = new RegExp('\\*\\*' + dimNameEscaped + ':\\*\\*\\s*\\*\\*(\\d+(?:\\.\\d+)?)', 'i'); // **Dimension:** **3**
            match = text.match(regex);

            if (match) {
                dim.level = match[1];
                return;
            }

            regex = new RegExp('\\|\\s*\\*\\*' + dimNameEscaped + '\\*\\*\\s*\\|\\s*(\\d+(?:\\.\\d+)?)\\s*\\|', 'i'); // Bold Table Rows: | **Explanation of Issues** | 4 | Capstone |
            match = text.match(regex);

            if (match) {
                dim.level = match[1];
                return;
            }

            regex = new RegExp('\\|\\s*\\*\\*' + dimNameEscaped + '\\*\\*\\s*\\|\\s*\\*\\*(\\d+(?:\\.\\d+)?)(?:\\s*\\([^)]+\\))?\\*\\*\\s*\\|', 'i'); // Bold Table Rows with Bold Scores: | **Explanation of issues** | **4 (Capstone)** |
            match = text.match(regex);

            if (match) {
                dim.level = match[1];
                return;
            }

            regex = new RegExp('\\|\\s*\\*\\*' + dimNameEscaped + '\\*\\*\\s*\\|\\s*\\*\\*(\\d+(?:\\.\\d+)?)(?:\\s*\\([^)]+\\))?\\*\\*\\s*\\|', 'i'); // Bold Table Rows with Score and Label: | **Explanation of issues** | **3 (Milestone)** |
            match = text.match(regex);
            if (match) {
                dim.level = match[1];
                return;
            }

            regex = new RegExp('\\|\\s*\\*\\*' + dimNameEscaped + '\\*\\*\\s*\\|\\s*\\*\\*(\\d+(?:\\.\\d+)?)(?:\\s*\\([^)]+\\))?\\*\\*\\s*\\|', 'i'); // | **Influence of context & assumptions** | **2 (Milestone)** |
            match = text.match(regex);

            if (match) {
                dim.level = match[1];
                return;
            }

            regex = new RegExp('\\|?\\s*\\*?\\*?' + dimNameEscaped + '(?:\\s*\\([^)]+\\))?\\*?\\*?\\s*\\|?\\s*[\\u2014\\u2013\\-:]?\\s*\\|?\\s*\\*\\*(\\d+(?:\\.\\d+)?)(?:\\s*\\([^)]+\\))?\\*\\*', 'i'); // "Student's position" even if it has "(perspective...)" after it
            match = text.match(regex);

            if (match) {
                dim.level = match[1];
                return;
        }

            regex = new RegExp('\\*?\\s*\\*\\*' + dimNameEscaped + '(?:\\s*\\([^)]+\\))?:?\\*\\*\\s*[:\\-]?\\s*\\*\\*(\\d+(?:\\.\\d+)?)\\*\\*', 'i'); // * **Student's position (perspective, thesis/hypothesis):** **4**
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
    const numericLevel = parseFloat(level);

    // Handle decimal scores by rounding down to integer
    if (!isNaN(numericLevel)) {
        const intLevel = Math.floor(numericLevel);
        if (intLevel === 4) return 'capstone';
        if (intLevel === 3) return 'milestone-3';
        if (intLevel === 2) return 'milestone-2';
        if (intLevel === 1) return 'benchmark';
    }

    // Handle named levels
    if (levelStr.includes('capstone')) return 'capstone';
    if (levelStr.includes('milestone 3')) return 'milestone-3';
    if (levelStr.includes('milestone 2')) return 'milestone-2';
    if (levelStr.includes('benchmark')) return 'benchmark';

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
