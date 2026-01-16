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
    // Adjust path for subdirectories
    const basePath = window.location.pathname.includes('/test/') ? '../' : '';
    const response = await fetch(basePath + 'src/ai_assessment/prompt.json');

    if (!response.ok) {
        prompts = {};
        gradePrompt = '';
        reflectionPrompt = '';
        return;
    }

    const data = await response.json();

    for (const key in data) {
        // Handle new format: assignment_1_p1, assignment_1_p2
        if (key.startsWith('assignment_') && key.includes('_p')) {
            const match = key.match(/assignment_(\d+)_p(\d+)/);
            if (match) {
                // Store as Assignment_1_p1, Assignment_1_p2
                prompts['Assignment_' + match[1] + '_p' + match[2]] = data[key];
            }
            prompts[key] = data[key];
        }
        // Handle old format: assignment_X_prompt
        else if (key.includes('_prompt')) {
            if (key.startsWith('assignment_')) {
                const match = key.match(/assignment_(\d+)_prompt/);
                if (match) {
                    prompts['Assignment_' + match[1]] = data[key];
                }
            }
            prompts[key] = data[key];
        }
        // Handle tuning_p1, tuning_p2
        else if (key.startsWith('tuning_p')) {
            prompts[key] = data[key];
        }
    }

    gradePrompt = data.grade_prompt || '';
    reflectionPrompt = data.reflection_prompt || '';
    tuningPrompt = data.tuning_prompt || data.tuning_p1 || '';
}

async function loadRubrics() {
    // Adjust path for subdirectories
    const basePath = window.location.pathname.includes('/test/') ? '../' : '';
    const rubricFiles = {
        'critical_thinking': 'src/ai_assessment/rubric/rubric_critical_thinking.json',
        'oral_communication': 'src/ai_assessment/rubric/rubric_oral_communication.json'
    };

    for (const [rubricName, filePath] of Object.entries(rubricFiles)) {
        try {
            const response = await fetch(basePath + filePath);
            if (response.ok) {
                const data = await response.json();
                rubrics[rubricName] = data[rubricName] || '';
            }
        } catch (error) {}
    }
}

function getPromptForEssay(essayName, promptNumber = null) {
    console.log('getPromptForEssay called with:', essayName, promptNumber);
    console.log('Available prompts:', Object.keys(prompts));

    // Try new format first: Assignment_1_p1, Assignment_1_p2
    if (promptNumber) {
        const newFormatKey = essayName + '_p' + promptNumber;
        console.log('Looking for key:', newFormatKey);
        if (prompts[newFormatKey]) {
            console.log('Found prompt for:', newFormatKey);
            return prompts[newFormatKey];
        }

        // Try test format: a1_test_1_prompt
        const testPromptKey = essayName.toLowerCase().replace('assignment_', 'a') + '_test_' + promptNumber + '_prompt';
        console.log('Looking for test key:', testPromptKey);
        if (prompts[testPromptKey]) {
            console.log('Found prompt for:', testPromptKey);
            return prompts[testPromptKey];
        }
    }
    console.log('Falling back to:', essayName);
    return prompts[essayName] || '';
}

function getGradePrompt() {
    return gradePrompt;
}

function getReflectionPrompt() {
    return reflectionPrompt;
}

function getTuningPrompt(promptNumber = null) {
    console.log('getTuningPrompt called with:', promptNumber);
    console.log('Looking for tuning_p' + promptNumber, 'in prompts');

    // Try new format: tuning_p1, tuning_p2
    if (promptNumber !== null && prompts['tuning_p' + promptNumber]) {
        console.log('Found tuning_p' + promptNumber);
        return prompts['tuning_p' + promptNumber];
    }
    // Try old format: tuning_prompt_X
    if (promptNumber !== null && prompts['tuning_prompt_' + promptNumber]) {
        console.log('Found tuning_prompt_' + promptNumber);
        return prompts['tuning_prompt_' + promptNumber];
    }
    console.log('Using default tuningPrompt');
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
