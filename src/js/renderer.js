// New renderer for the three-column layout

let elements = {};
let prompts = {};
let gradePrompt = '';
let currentSelection = null;

// Start the renderer
async function initRenderer() {
    findElements();
    await loadPrompts();
    setupButtons();
}

// Find all HTML elements we need
function findElements() {
    elements = {
        dateDisplay: document.getElementById('dateDisplay'),
        promptContent: document.getElementById('promptContent'),
        responseContent: document.getElementById('responseContent'),
        scoreBody: document.getElementById('scoreBody'),
        githubBtn: document.getElementById('githubBtn')
    };
}

// Load prompts from file
async function loadPrompts() {
    const response = await fetch('src/ai_assessment/prompt.json');

    if (!response.ok) {
        console.warn('Could not load prompt.json, using defaults');
        useDefaultPrompts();
        return;
    }

    const data = await response.json();
    prompts = {};

    // Get assignment prompts
    for (const key in data) {
        if (key.startsWith('assignment_') && key.endsWith('_prompt')) {
            const match = key.match(/assignment_(\d+)_prompt/);
            if (match) {
                prompts['Assignment_' + match[1]] = data[key];
            }
        }
    }

    gradePrompt = data.grade_prompt || '';
    console.log('Prompts loaded');
}

// Default prompts if file not found
function useDefaultPrompts() {
    prompts = {
        'Assignment_1': "Let's write a 1000 word fully written college essay, plus at least 5 citations from peer-reviewed articles in the end of essay not embedded links, that answers this question: Consider the following problem: In the morning, when Professor Catlove opens a new can of cat food, his cats run into the kitchen purring and meowing and rubbing their backs against his legs. What examples, if any, of classical conditioning, operant conditioning, and social learning are at work in this brief scene? Note that both the cats and the professor might be exhibiting conditioned behavior here.",
        'Assignment_2': "Let's write a 1000 word fully written college essay, plus at least 5 citations from peer-reviewed articles, that answers this question. To what extent do the attached economic data support the hypothesis \"social service spending is inversely related to economic growth\"? Formulate a verbal argument analyzing whether the data do or do not support the hypothesis.",
        'Assignment_3': "Let's write a 1000 word fully written college essay, that includes a real estate investment market analysis in the Boston Metropolitan Area for 2024. Summarize the key findings, insights from the analysis, highlight the best real estate investment opportunities, and any significant patterns observed. Please include at least 5 citations from peer reviewed articles."
    };
    gradePrompt = "After grading the essay using the rubric, please explain how the essay was tuned to achieve a perfect score on the rubric. Add the total score at the end using this format: Total Score is [X]/[Y].";
}

// Setup button click handlers
function setupButtons() {
    const allButtons = document.querySelectorAll('.action-btn');
    allButtons.forEach(button => {
        button.addEventListener('click', function() {
            handleButtonClick(this);
        });
    });
}

// Handle button click
function handleButtonClick(button) {
    const model = button.getAttribute('data-model');
    const type = button.getAttribute('data-type');

    // Remove active class from all buttons
    document.querySelectorAll('.action-btn').forEach(btn => {
        btn.classList.remove('active');
    });

    // Add active class to clicked button
    button.classList.add('active');

    // Find the matching data
    const item = findDataItem(model, type);

    if (item) {
        currentSelection = item;
        displayContent(item);
    } else {
        showNoData();
    }
}

// Find data item matching model and type
function findDataItem(model, type) {
    // Map button model names to data model names
    const modelMap = {
        'chatgpt': 'ChatGPT',
        'gemini': 'Gemini',
        'claude': 'Claude',
        'gpt4': 'GPT-4'
    };

    // Map button type to command
    const typeMap = {
        'generation': 'generate',
        'tuning': 'tune',
        'reflection': 'reflection',
        'score': 'score'
    };

    const modelName = modelMap[model];
    const command = typeMap[type];

    // Search through all data for matching item
    const allItems = Object.values(getData());

    // For now, filter by Assignment_1 (critical thinking)
    // You can make this dynamic later
    const matches = allItems.filter(item => {
        return item.modelName === modelName &&
               item.command === command &&
               item.essayName === 'Assignment_1' &&
               item.rubric === 'critical_thinking';
    });

    return matches.length > 0 ? matches[0] : null;
}

// Display content in center and right panels
function displayContent(item) {
    // Update date
    const date = item.data.timestamp || new Date().toLocaleDateString();
    elements.dateDisplay.textContent = 'Date: ' + date;

    // Update prompt
    const prompt = getPromptForEssay(item.essayName);
    elements.promptContent.textContent = prompt || 'No prompt available';

    // Update response
    const responseText = item.data.result || item.data.essay || 'No content available';
    const cleanText = removeMarkdown(responseText);
    elements.responseContent.textContent = cleanText;

    // Update scores
    displayScores(item);
}

// Display scores in right panel
function displayScores(item) {
    elements.scoreBody.innerHTML = '';

    // Get all scores for this essay
    const scores = getScoresForEssay(item);

    if (scores.length === 0) {
        elements.scoreBody.innerHTML = '<p style="color: var(--rami-lightgrey); font-size: 0.85rem; text-align: center; padding: 2rem;">No scores available</p>';
        return;
    }

    // Group scores by grader
    scores.forEach(scoreItem => {
        const graderName = getModelName(scoreItem.data.grader);
        displayScoreForGrader(graderName, scoreItem);
    });
}

// Display score for one grader
function displayScoreForGrader(graderName, scoreItem) {
    // Model row
    const modelRow = document.createElement('div');
    modelRow.className = 'score-model-row';

    const modelNameSpan = document.createElement('span');
    modelNameSpan.className = 'score-model-name';
    modelNameSpan.textContent = graderName;

    const totalSpan = document.createElement('span');
    totalSpan.className = 'score-total';

    // Extract total score from text
    const scoreText = scoreItem.data.result || scoreItem.data.score || '';
    const totalMatch = scoreText.match(/Total.*?(\d+)\s*\/\s*(\d+)/i);
    if (totalMatch) {
        totalSpan.textContent = 'Total ' + totalMatch[1] + '/' + totalMatch[2];
    } else {
        totalSpan.textContent = 'Total --';
    }

    modelRow.appendChild(modelNameSpan);
    modelRow.appendChild(totalSpan);
    elements.scoreBody.appendChild(modelRow);

    // Parse and display rubric dimensions
    const dimensions = parseRubricScores(scoreText);
    dimensions.forEach(dim => {
        const rubricItem = document.createElement('div');
        rubricItem.className = 'score-rubric-item';

        const dimensionSpan = document.createElement('span');
        dimensionSpan.className = 'score-dimension';
        dimensionSpan.textContent = dim.name;

        const valueSpan = document.createElement('span');
        valueSpan.className = 'score-value ' + getScoreClass(dim.level);
        valueSpan.textContent = dim.level;

        rubricItem.appendChild(dimensionSpan);
        rubricItem.appendChild(valueSpan);
        elements.scoreBody.appendChild(rubricItem);
    });

    // Add spacing between graders
    const spacer = document.createElement('div');
    spacer.style.height = '1.5rem';
    elements.scoreBody.appendChild(spacer);
}

// Parse rubric scores from text
function parseRubricScores(text) {
    const dimensions = [
        { name: 'Explanation of issue', level: '--' },
        { name: 'Evidence', level: '--' },
        { name: 'Influence of context and assumptions', level: '--' },
        { name: 'Student\'s position', level: '--' },
        { name: 'Conclusions and related outcomes', level: '--' }
    ];

    // Try to extract scores from text
    // This is a simple parser - you may need to adjust based on your actual score format
    dimensions.forEach(dim => {
        const regex = new RegExp(dim.name + '.*?(Capstone 4|Milestone 3|Milestone 2|Benchmark 1)', 'i');
        const match = text.match(regex);
        if (match) {
            dim.level = match[1];
        }
    });

    return dimensions;
}

// Get CSS class for score level
function getScoreClass(level) {
    const levelLower = level.toLowerCase();
    if (levelLower.includes('capstone') || levelLower.includes('4')) return 'capstone';
    if (levelLower.includes('milestone 3') || levelLower.includes('3')) return 'milestone-3';
    if (levelLower.includes('milestone 2') || levelLower.includes('2')) return 'milestone-2';
    if (levelLower.includes('benchmark') || levelLower.includes('1')) return 'benchmark';
    return '';
}

// Get all scores for an essay
function getScoresForEssay(item) {
    const essayType = item.command; // 'generate' or 'tune'

    const scores = Object.values(getData()).filter(scoreItem => {
        const isScore = scoreItem.command === 'score';
        const sameEssay = scoreItem.essayName === item.essayName;
        const sameType = scoreItem.data.essay_type === essayType;
        const sameWriter = getModelName(scoreItem.data.writer) === item.modelName;
        const sameRubric = scoreItem.rubric === item.rubric;

        return isScore && sameEssay && sameType && sameWriter && sameRubric;
    });

    return scores;
}

// Show no data message
function showNoData() {
    elements.dateDisplay.textContent = 'Date: --';
    elements.promptContent.textContent = 'No data available for this selection';
    elements.responseContent.textContent = 'Please select another option or load data from GitHub';
    elements.scoreBody.innerHTML = '<p style="color: var(--rami-lightgrey); font-size: 0.85rem; text-align: center; padding: 2rem;">No scores available</p>';
}

// Get prompt for an essay
function getPromptForEssay(essayName) {
    return prompts[essayName] || '';
}

function getGradePrompt() {
    return gradePrompt;
}

// Remove markdown formatting from text
function removeMarkdown(text) {
    if (!text) return '';

    return text
        // Remove headers (### Header -> Header)
        .replace(/^#{1,6}\s+(.+)$/gm, '$1')
        // Remove bold (**text** or __text__ -> text)
        .replace(/(\*\*|__)(.*?)\1/g, '$2')
        // Remove italic (*text* or _text_ -> text)
        .replace(/(\*|_)(.*?)\1/g, '$2')
        // Remove inline code (`code` -> code)
        .replace(/`([^`]+)`/g, '$1')
        // Remove links ([text](url) -> text)
        .replace(/\[([^\]]+)\]\([^\)]+\)/g, '$1')
        // Remove bullet points (- item -> item)
        .replace(/^[\*\-\+]\s+/gm, '')
        // Remove numbered lists (1. item -> item)
        .replace(/^\d+\.\s+/gm, '')
        // Remove blockquotes (> quote -> quote)
        .replace(/^>\s+/gm, '')
        // Remove horizontal rules (---, ***, ___ -> empty)
        .replace(/^[\-\*\_]{3,}$/gm, '')
        // Remove code blocks (```code``` -> code)
        .replace(/```[\s\S]*?```/g, match => {
            return match.replace(/```\w*\n?/g, '').trim();
        })
        // Clean up extra whitespace
        .replace(/\n{3,}/g, '\n\n')
        .trim();
}

// Show notification popup
function showNotification(message) {
    // Create notification element
    const notif = document.createElement('div');
    notif.className = 'notification';
    notif.textContent = message;
    notif.style.cssText = `
        position: fixed;
        top: 20px;
        right: 20px;
        background: var(--rami-highlight);
        color: var(--rami-dark);
        padding: 1rem 1.5rem;
        border-radius: 8px;
        font-weight: 600;
        z-index: 1000;
        box-shadow: 0 4px 12px rgba(34, 204, 157, 0.5);
        animation: slideIn 0.3s ease;
    `;

    document.body.appendChild(notif);

    setTimeout(() => {
        if (document.body.contains(notif)) {
            document.body.removeChild(notif);
        }
    }, 3000);
}
