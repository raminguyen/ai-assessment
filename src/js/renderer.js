let currentSelection = null;
let promptExpanded = false;

async function initRenderer() {
    findElements();
    await loadPrompts();
    await loadRubrics();
    setupButtons();
    setupFilterButtons();
}

// Make all buttons work
function setupButtons() {
    
    const allButtons = document.querySelectorAll('.action-btn');

    // Go through each button
    for (let i = 0; i < allButtons.length; i++) {
        const button = allButtons[i];

        // Make a fresh copy of button
        const newButton = button.cloneNode(true);
        button.parentNode.replaceChild(newButton, button);

        newButton.addEventListener('click', function() {
            handleButtonClick(newButton);
        });
    }
}

function handleButtonClick(button) {
    // Get info from button
    const model = button.getAttribute('data-model');
    const type = button.getAttribute('data-type');
    
    console.log('Button Clicked.');
    console.log('Model:', model);
    console.log('Type:', type);
    console.log('Current Assignment:', getCurrentAssignment());

    removeActiveFromAllButtons();
    button.classList.add('active');

    const item = findDataItem(model, type);

    // Did we find it?
    if (item) {
        currentSelection = item;
        console.log('✓ File Loaded:', item.fileName || 'unknown');
        console.log('Essay Name:', item.essayName);
        console.log('Command:', item.command);

        // Show it on screen
        displayContent(item);
    } else {
       
        console.log('✗ No data found for:', model, type);
        showNoData();
    }
}

function removeActiveFromAllButtons() {
    const allButtons = document.querySelectorAll('.action-btn');

    for (let i = 0; i < allButtons.length; i++) {
        allButtons[i].classList.remove('active');
    }
}

// Show everything on screen
function displayContent(item) {
    const elements = getElements();

    displayDate(elements, item);
    displayPrompt(elements, item);
    displayRubricSection(elements, item);
    displayResponseText(elements, item);
    displayScores(item);
}

// Show the date
function displayDate(elements, item) {
    let dateText = 'Date: ';

 
    if (item.data.timestamp) {
        dateText = dateText + item.data.timestamp;
    } else {

        const today = new Date();
        dateText = dateText + today.toLocaleDateString();
    }

    elements.dateDisplay.textContent = dateText;
}

function displayPrompt(elements, item) {
    let prompt = '';

    if (item.command === 'reflection') {
        prompt = buildReflectionPrompt(item);
        displayReflectionPrompt(elements, prompt, item);
        return;
    } else if (item.command === 'tune') {
        prompt = buildTuningPrompt(item);
        displayTuningPrompt(elements, prompt);
        return;
    } else {
        prompt = getPromptForEssay(item.essayName);
    }

    prompt = removeMarkdown(prompt);

    if (prompt) {
        displayPromptWithExpand(elements, prompt, item.command);
    } else {
        elements.promptContent.textContent = 'No prompt available';
    }
}

function displayPromptWithExpand(elements, prompt, commandType) {
    elements.promptContent.textContent = prompt;
    elements.promptContent.style.whiteSpace = 'pre-wrap';
}

function togglePrompt(elements, fullText, shortText, expandHtml) {
    promptExpanded = !promptExpanded;
    elements.promptContent.innerHTML = promptExpanded ? fullText : (shortText + expandHtml);
}

function displayReflectionPrompt(elements, prompt, item) {
    // Get essays
    const originalEssay = getOriginalEssay(item);
    const tunedEssay = getTunedEssay(item);

    // Get file names
    const originalFile = getOriginalEssayFile(item);
    const tunedFile = getTunedEssayFile(item);

    console.log('Original essay file:', originalFile);
    console.log('Tuned essay file:', tunedFile);
    console.log('Rubric link: src/ai_assessment/rubric/Critical_Thinking_VALUE_Rubric.pdf');

    // Remove markdown
    prompt = removeMarkdown(prompt);
    const cleanOriginalEssay = removeMarkdown(originalEssay);
    const cleanTunedEssay = removeMarkdown(tunedEssay);

    // Make {rubric} link to PDF
    prompt = prompt.replace('{rubric}', '<a href="src/ai_assessment/rubric/Critical_Thinking_VALUE_Rubric.pdf" target="_blank" style="color: var(--rami-highlight); text-decoration: underline;">{rubric}</a>');

    // Make {original essay} and {tuned essay} clickable
    prompt = prompt.replace('{original essay}', '<span class="expand-text" style="cursor: pointer; color: var(--rami-highlight); text-decoration: underline;" data-essay="original" data-expanded="false">{original essay}</span><div class="essay-content" data-essay-content="original" style="display: none; margin-top: 1rem; padding: 1rem; background: rgba(255,255,255,0.05); border-radius: 8px; white-space: pre-wrap;"></div>');
    prompt = prompt.replace('{tuned essay}', '<span class="expand-text" style="cursor: pointer; color: var(--rami-highlight); text-decoration: underline;" data-essay="tuned" data-expanded="false">{tuned essay}</span><div class="essay-content" data-essay-content="tuned" style="display: none; margin-top: 1rem; padding: 1rem; background: rgba(255,255,255,0.05); border-radius: 8px; white-space: pre-wrap;"></div>');

    elements.promptContent.innerHTML = prompt;

    // Put cleaned essays in hidden divs
    const originalContent = elements.promptContent.querySelector('[data-essay-content="original"]');
    const tunedContent = elements.promptContent.querySelector('[data-essay-content="tuned"]');
    if (originalContent) originalContent.textContent = cleanOriginalEssay;
    if (tunedContent) tunedContent.textContent = cleanTunedEssay;

    // Add click to expand/collapse
    const essayLinks = elements.promptContent.querySelectorAll('span[data-essay]');
    for (let i = 0; i < essayLinks.length; i++) {
        const link = essayLinks[i];
        link.addEventListener('click', function() {
            const essayType = link.getAttribute('data-essay');
            const isExpanded = link.getAttribute('data-expanded') === 'true';
            const contentDiv = elements.promptContent.querySelector('[data-essay-content="' + essayType + '"]');

            if (essayType === 'original') {
                console.log('Clicked: original essay from file:', originalFile);
            } else if (essayType === 'tuned') {
                console.log('Clicked: tuned essay from file:', tunedFile);
            }
            console.log('Expanded:', isExpanded);

            if (isExpanded) {
                contentDiv.style.display = 'none';
                link.setAttribute('data-expanded', 'false');
            } else {
                contentDiv.style.display = 'block';
                link.setAttribute('data-expanded', 'true');
            }
        });
    }
}

function displayTuningPrompt(elements, prompt) {
    console.log('Rubric link: src/ai_assessment/rubric/Critical_Thinking_VALUE_Rubric.pdf');

    // Remove markdown
    prompt = removeMarkdown(prompt);

    // Make {rubric} link to PDF
    prompt = prompt.replace('{rubric}', '<a href="src/ai_assessment/rubric/Critical_Thinking_VALUE_Rubric.pdf" target="_blank" style="color: var(--rami-highlight); text-decoration: underline;">{rubric}</a>');

    elements.promptContent.innerHTML = prompt;
}

function buildReflectionPrompt(item) {
    let template = getReflectionPrompt();
    let assignmentPrompt = getPromptForEssay(item.essayName);

    assignmentPrompt = assignmentPrompt.replace('You are an undergrad student in the first semester.\n\n', '');
    assignmentPrompt = assignmentPrompt.replace('You are an undergrad student in the first semester. ', '');

    template = template.replace('{ASSIGNMENT_PROMPT}', assignmentPrompt);

    return template;
}

function buildTuningPrompt(item) {
    let template = getTuningPrompt();
    const assignmentPrompt = getPromptForEssay(item.essayName);

    template = template.replace('{ASSIGNMENT_PROMPT}', assignmentPrompt);

    return template;
}

function getOriginalEssay(item) {
    const allData = getData();
    const allItems = Object.values(allData);

    for (let i = 0; i < allItems.length; i++) {
        const dataItem = allItems[i];

        if (dataItem.modelName === item.modelName &&
            dataItem.essayName === item.essayName &&
            dataItem.command === 'generate' &&
            dataItem.rubric === item.rubric) {
            console.log('Loading original essay from:', dataItem.fileName);
            return dataItem.data.result || dataItem.data.essay || '';
        }
    }
    console.log('Original essay not found');
    return '';
}

function getOriginalEssayFile(item) {
    const allData = getData();
    const allItems = Object.values(allData);

    for (let i = 0; i < allItems.length; i++) {
        const dataItem = allItems[i];

        if (dataItem.modelName === item.modelName &&
            dataItem.essayName === item.essayName &&
            dataItem.command === 'generate' &&
            dataItem.rubric === item.rubric) {
            return dataItem.fileName || 'unknown';
        }
    }
    return 'not found';
}

function getTunedEssay(item) {
    const allData = getData();
    const allItems = Object.values(allData);

    for (let i = 0; i < allItems.length; i++) {
        const dataItem = allItems[i];

        if (dataItem.modelName === item.modelName &&
            dataItem.essayName === item.essayName &&
            dataItem.command === 'tune' &&
            dataItem.rubric === item.rubric) {
            console.log('Loading tuned essay from:', dataItem.fileName);
            return dataItem.data.result || dataItem.data.essay || '';
        }
    }
    console.log('Tuned essay not found');
    return '';
}

function getTunedEssayFile(item) {
    const allData = getData();
    const allItems = Object.values(allData);

    for (let i = 0; i < allItems.length; i++) {
        const dataItem = allItems[i];

        if (dataItem.modelName === item.modelName &&
            dataItem.essayName === item.essayName &&
            dataItem.command === 'tune' &&
            dataItem.rubric === item.rubric) {
            return dataItem.fileName || 'unknown';
        }
    }
    return 'not found';
}

// Show or hide rubric
function displayRubricSection(elements, item) {
    // Hide rubric section since it's now in the prompt
    elements.rubricSection.style.display = 'none';
}

function displayResponseText(elements, item) {
    let responseText = '';

    if (item.data.result) {
        responseText = item.data.result;
    } else if (item.data.essay) {
        responseText = item.data.essay;
    } else {
        responseText = 'No content available';
    }

    // Clean the text
    const cleanText = removeMarkdown(responseText);

    elements.responseContent.textContent = cleanText;
}

// Show all scores
function displayScores(item) {
    const elements = getElements();

    const scores = getScoresForEssay(item);

    console.log('Scores found:', scores.length);

    for (let i = 0; i < scores.length; i++) {
        const scoreItem = scores[i];
        const fileName = scoreItem.fileName || 'unknown';
        console.log('  -', fileName);
    }

    if (scores.length === 0) {
        showNoScoresMessage(elements);
        return;
    }

    elements.scoreBody.innerHTML = '';

    // Show each score
    for (let i = 0; i < scores.length; i++) {
        const scoreItem = scores[i];
        const graderName = getModelName(scoreItem.data.grader);
        displayScoreForGrader(graderName, scoreItem);
    }
}

// Show "no scores" message
function showNoScoresMessage(elements) {
    const message = '<p style="color: var(--rami-lightgrey); font-size: 0.85rem; text-align: center; padding: 2rem;">No scores available</p>';
    elements.scoreBody.innerHTML = message;
}

// Show one grader's score
function displayScoreForGrader(graderName, scoreItem) {
    const elements = getElements();

    let scoreText = '';
    if (scoreItem.data.result) {
        scoreText = scoreItem.data.result;
    } else if (scoreItem.data.score) {
        scoreText = scoreItem.data.score;
    }

    const modelRow = createScoreHeader(graderName, scoreText);
    elements.scoreBody.appendChild(modelRow);

    const dimensions = parseRubricScores(scoreText);

    // Show each dimension
    for (let i = 0; i < dimensions.length; i++) {
        const dim = dimensions[i];
        const dimRow = createDimensionRow(dim);
        elements.scoreBody.appendChild(dimRow);
    }

    // Add space
    const spacer = document.createElement('div');
    spacer.style.height = '1.5rem';
    elements.scoreBody.appendChild(spacer);
}

// Make header with name and total
function createScoreHeader(graderName, scoreText) {
    
    const modelRow = document.createElement('div');
    modelRow.className = 'score-model-row';

    
    const modelNameSpan = document.createElement('span');
    modelNameSpan.className = 'score-model-name';
    modelNameSpan.textContent = graderName;

    
    const totalSpan = document.createElement('span');
    const totalText = extractTotalScore(scoreText);
    const totalValue = parseInt(totalText.match(/\d+/));
    const totalColorClass = getTotalScoreClass(totalValue);

    totalSpan.className = 'score-total ' + totalColorClass;
    totalSpan.textContent = totalText;

    modelRow.appendChild(modelNameSpan);
    modelRow.appendChild(totalSpan);

    return modelRow;
}

function getTotalScoreClass(score) {
    if (score >= 16) return 'capstone';
    if (score >= 12) return 'milestone-3';
    if (score >= 8) return 'milestone-2';
    return 'benchmark';
}

// Find total score in text
function extractTotalScore(scoreText) {
    const patterns = [
        /Total:\s*\*\*(\d+)\*\*\s*\/\s*(\d+)/i,  // Total: **18**/20
        /Total:?\s*\[(\d+)\]\s*\/\s*(\d+)/i,     // Total: [18]/20
        /Total:?\s*\[(\d+)\]/i,                   // Total: [18]
        /Total:?\s*(\d+)\s*\/\s*(\d+)/i,         // Total: 18/20
        /Total.*?(\d+)\s*\/\s*(\d+)/i            // Total anything 18/20
    ];

    
    for (let i = 0; i < patterns.length; i++) {
        const pattern = patterns[i];
        const match = scoreText.match(pattern);

        // Found it?
        if (match) {
            // Has two numbers?
            if (match[2]) {
                return 'Total ' + match[1] + '/' + match[2];
            } else {
                // One number, add /20
                return 'Total ' + match[1] + '/20';
            }
        }
    }

    // Not found
    return 'Total --';
}

// Make row for one dimension
function createDimensionRow(dim) {
    
    const rubricItem = document.createElement('div');
    rubricItem.className = 'score-rubric-item';

    
    const dimensionSpan = document.createElement('span');
    dimensionSpan.textContent = dim.name;

    
    const scoreClass = getScoreClass(dim.level);
    const valueSpan = document.createElement('span');
    valueSpan.className = 'score-value ' + scoreClass;
    valueSpan.textContent = dim.level;

    
    rubricItem.appendChild(dimensionSpan);
    rubricItem.appendChild(valueSpan);

    return rubricItem;
}

// Find scores for this essay
function getScoresForEssay(item) {

    const allData = getData();
    const allItems = Object.values(allData);
    const matchingScores = [];

    // Check each one
    for (let i = 0; i < allItems.length; i++) {
        const scoreItem = allItems[i];

        const isScoreCommand = scoreItem.command === 'score';
        const sameEssayName = scoreItem.essayName === item.essayName;
        const sameEssayType = scoreItem.data.essay_type === item.command;
        const writerName = getModelName(scoreItem.data.writer);
        const sameModel = writerName === item.modelName;
        const sameRubric = scoreItem.rubric === item.rubric;

        // Everything matches
        if (isScoreCommand && sameEssayName && sameEssayType && sameModel && sameRubric) {
            matchingScores.push(scoreItem);
        }
    }

    return matchingScores;
}
