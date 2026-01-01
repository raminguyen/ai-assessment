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
    } else if (item.command === 'tune') {
        prompt = buildTuningPrompt(item);
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
    const maxLength = 1000;
    const isLong = prompt.length > maxLength;

    if (!isLong) {
        elements.promptContent.textContent = prompt;
        return;
    }

    const short = prompt.substring(0, maxLength);
    const expandHtml = '... <span class="expand-text">(click to expand)</span>';

    elements.promptContent.innerHTML = promptExpanded ? prompt : (short + expandHtml);
    elements.promptContent.style.cursor = 'pointer';
    elements.promptContent.onclick = () => togglePrompt(elements, prompt, short, expandHtml);
}

function togglePrompt(elements, fullText, shortText, expandHtml) {
    promptExpanded = !promptExpanded;
    elements.promptContent.innerHTML = promptExpanded ? fullText : (shortText + expandHtml);
}

function buildReflectionPrompt(item) {
    let template = getReflectionPrompt();
    const assignmentPrompt = getPromptForEssay(item.essayName);
    const originalEssay = getOriginalEssay(item);
    const tunedEssay = getTunedEssay(item);

    template = template.replace('{ASSIGNMENT_PROMPT}', assignmentPrompt);
    template = template.replace('{ORIGINAL_ESSAY}', originalEssay);
    template = template.replace('{TUNED_ESSAY}', tunedEssay);

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
            console.log('Original file:', dataItem.fileName);
            return dataItem.data.result || dataItem.data.essay || '';
        }
    }
    return '';
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
            console.log('Tuned file:', dataItem.fileName);
            return dataItem.data.result || dataItem.data.essay || '';
        }
    }
    return '';
}

// Show or hide rubric
function displayRubricSection(elements, item) {

    if (item.command === 'tune') {
        elements.rubricSection.style.display = 'block';
    } else {
        // No, hide rubric
        elements.rubricSection.style.display = 'none';
    }
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
    totalSpan.className = 'score-total';
    totalSpan.textContent = extractTotalScore(scoreText);

    
    modelRow.appendChild(modelNameSpan);
    modelRow.appendChild(totalSpan);

    return modelRow;
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
