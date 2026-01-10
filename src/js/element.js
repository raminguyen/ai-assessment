let elements = {};
let prompts = {};
let rubrics = {};
let reflectionPrompt = '';
let gradePrompt = '';
let tuningPrompt = '';

function getElements() {
    return elements;
}

function findElements() {
    elements = {
        dateDisplay: document.getElementById('dateDisplay'),
        promptContent: document.getElementById('promptContent'),
        rubricSection: document.getElementById('rubricSection'),
        rubricContent: document.getElementById('rubricContent'),
        responseContent: document.getElementById('responseContent'),
        scoreBody: document.getElementById('scoreBody'),
        githubBtn: document.getElementById('githubBtn')
    };
}

async function loadPrompts() {
    const response = await fetch('src/ai_assessment/prompt.json');

    if (!response.ok) {
        prompts = {};
        gradePrompt = '';
        reflectionPrompt = '';
        return;
    }

    const data = await response.json();
    prompts = {};

    for (const key in data) {
        if (key.endsWith('_prompt')) {
            if (key.startsWith('assignment_')) {
                const match = key.match(/assignment_(\d+)_prompt/);
                if (match) {
                    prompts['Assignment_' + match[1]] = data[key];
                }
            }
            prompts[key] = data[key];
        }
    }

    gradePrompt = data.grade_prompt || '';
    reflectionPrompt = data.reflection_prompt || '';
    tuningPrompt = data.tuning_prompt || '';
}

async function loadRubrics() {
    const rubricFiles = {
        'critical_thinking': 'src/ai_assessment/rubric/rubric_critical_thinking.json',
        'oral_communication': 'src/ai_assessment/rubric/rubric_oral_communication.json'
    };

    for (const [rubricName, filePath] of Object.entries(rubricFiles)) {
        try {
            const response = await fetch(filePath);
            if (response.ok) {
                const data = await response.json();
                rubrics[rubricName] = data[rubricName] || '';
            }
        } catch (error) {}
    }
}

function getPromptForEssay(essayName, testNumber = null) {
    if (testNumber) {
        const testPromptKey = `${essayName.toLowerCase().replace('assignment_', 'a')}_test_${testNumber}_prompt`;
        if (prompts[testPromptKey]) {
            return prompts[testPromptKey];
        }
    }
    return prompts[essayName] || '';
}

function getGradePrompt() {
    return gradePrompt;
}

function getReflectionPrompt() {
    return reflectionPrompt;
}

function getTuningPrompt() {
    return tuningPrompt;
}

function getRubrics() {
    return rubrics;
}

function showNoData() {
    elements.dateDisplay.textContent = 'Date: --';
    elements.promptContent.textContent = 'No data available for this selection';
    elements.rubricSection.style.display = 'none';
    elements.responseContent.textContent = 'Please select another option or load data from GitHub';
    elements.scoreBody.innerHTML = '<p style="color: var(--rami-lightgrey); font-size: 0.85rem; text-align: center; padding: 2rem;">No scores available</p>';
}

function showNotification(message) {
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
