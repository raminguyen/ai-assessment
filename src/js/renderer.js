let currentSelection = null;

// Initialize the renderer by loading prompts, rubrics, and setting up UI elements
async function initRenderer() {
    findElements();
    await loadPrompts();
    await loadRubrics();
    setupButtons();
    setupFilterButtons();
}

// Setup action button click handlers
function setupButtons() {
    const allButtons = document.querySelectorAll('.action-btn');
    allButtons.forEach(button => {
        const newButton = button.cloneNode(true);
        button.parentNode.replaceChild(newButton, button);
        newButton.addEventListener('click', () => handleButtonClick(newButton));
    });
}

// Handle button click to load and display selected essay data
function handleButtonClick(button) {
    const model = button.getAttribute('data-model');
    const type = button.getAttribute('data-type');

    document.querySelectorAll('.action-btn').forEach(btn => btn.classList.remove('active'));
    button.classList.add('active');

    const item = findDataItem(model, type);

    if (item) {
        currentSelection = item;
        console.log('Loaded:', item.fileName || 'unknown');
        displayContent(item);
    } else {
        console.log('No data:', model, type);
        showNoData();
    }
}

// Display essay content including prompt, response text, and rubric section
function displayContent(item) {
    const elements = getElements();

    elements.dateDisplay.textContent = 'Date: ' + (item.data.timestamp || new Date().toLocaleDateString());
    elements.promptContent.textContent = getPromptForEssay(item.essayName) || 'No prompt available';
    elements.rubricSection.style.display = item.command === 'tune' ? 'block' : 'none';

    const responseText = item.data.result || item.data.essay || 'No content available';
    elements.responseContent.textContent = removeMarkdown(responseText);

    displayScores(item);
}

// Display all scores for the selected essay
function displayScores(item) {
    const elements = getElements();
    const scores = getScoresForEssay(item);

    console.log('Scores found:', scores.length);
    scores.forEach(scoreItem => console.log('  -', scoreItem.fileName || 'unknown'));

    if (scores.length === 0) {
        elements.scoreBody.innerHTML = '<p style="color: var(--rami-lightgrey); font-size: 0.85rem; text-align: center; padding: 2rem;">No scores available</p>';
        return;
    }

    elements.scoreBody.innerHTML = '';
    scores.forEach(scoreItem => {
        const graderName = getModelName(scoreItem.data.grader);
        displayScoreForGrader(graderName, scoreItem);
    });
}

// Display individual grader's score with rubric dimensions
function displayScoreForGrader(graderName, scoreItem) {
    const elements = getElements();
    const scoreText = scoreItem.data.result || scoreItem.data.score || '';

    const modelRow = createScoreHeader(graderName, scoreText);
    elements.scoreBody.appendChild(modelRow);

    const dimensions = parseRubricScores(scoreText);
    dimensions.forEach(dim => {
        elements.scoreBody.appendChild(createDimensionRow(dim));
    });

    const spacer = document.createElement('div');
    spacer.style.height = '1.5rem';
    elements.scoreBody.appendChild(spacer);
}

// Create score header row with grader name and total score
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

// Extract total score from score text using multiple regex patterns
function extractTotalScore(scoreText) {
    const patterns = [
        /Total:\s*\*\*(\d+)\*\*\s*\/\s*(\d+)/i,
        /Total:?\s*\[(\d+)\]\s*\/\s*(\d+)/i,
        /Total:?\s*\[(\d+)\]/i,
        /Total:?\s*(\d+)\s*\/\s*(\d+)/i,
        /Total.*?(\d+)\s*\/\s*(\d+)/i
    ];

    for (const pattern of patterns) {
        const match = scoreText.match(pattern);
        if (match) {
            // Handle both [20]/20 and [20] formats
            if (match[2]) {
                return 'Total ' + match[1] + '/' + match[2];
            } else {
                return 'Total ' + match[1] + '/20';
            }
        }
    }

    return 'Total --';
}

// Create dimension score row element
function createDimensionRow(dim) {
    const rubricItem = document.createElement('div');
    rubricItem.className = 'score-rubric-item';

    const dimensionSpan = document.createElement('span');
    dimensionSpan.textContent = dim.name;

    const valueSpan = document.createElement('span');
    valueSpan.className = 'score-value ' + getScoreClass(dim.level);
    valueSpan.textContent = dim.level;

    rubricItem.appendChild(dimensionSpan);
    rubricItem.appendChild(valueSpan);

    return rubricItem;
}

// Get all scores matching the current essay's criteria
function getScoresForEssay(item) {
    return Object.values(getData()).filter(scoreItem => {
        return scoreItem.command === 'score' &&
               scoreItem.essayName === item.essayName &&
               scoreItem.data.essay_type === item.command &&
               getModelName(scoreItem.data.writer) === item.modelName &&
               scoreItem.rubric === item.rubric;
    });
}
