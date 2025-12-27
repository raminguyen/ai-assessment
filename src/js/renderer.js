// SIMPLE VERSION - Show essays on screen

// Keep track of HTML elements
let elements = {};
let prompts = {};
let gradePrompt = '';

// Start the renderer
async function initRenderer() {
    findElements();
    await loadPrompts();
}

// Find all HTML elements we need
function findElements() {
    elements = {
        essayList: document.getElementById('essayList'),
        rightPanel: document.getElementById('rightPanel'),
        filters: document.getElementById('filters'),
        modelFilter: document.getElementById('modelFilter'),
        essayFilter: document.getElementById('essayFilter'),
        rubricFilter: document.getElementById('rubricFilter'),
        filterGenerate: document.getElementById('filterGenerate'),
        filterTune: document.getElementById('filterTune'),
        filterScore: document.getElementById('filterScore')
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
        'Assignment_1': "Let's write a 1000 word fully written college essa, plus at least 5 citations from peer-reviewed articles in the end of essay not embedded links, that answers this question: Consider the following problem: In the morning, when Professor Catlove opens a new can of cat food, his cats run into the kitchen purring and meowing and rubbing their backs against his legs. What examples, if any, of classical conditioning, operant conditioning, and social learning are at work in this brief scene? Note that both the cats and the professor might be exhibiting conditioned behavior here.",
        'Assignment_2': "Let's write a 1000 word fully written college essay, plus at least 5 citations from peer-reviewed articles, that answers this question. To what extent do the attached economic data support the hypothesis \"social service spending is inversely related to economic growth\"? Formulate a verbal argument analyzing whether the data do or do not support the hypothesis.",
        'Assignment_3': "Let's write a 1000 word fully written college essay, that includes a real estate investment market analysis in the Boston Metropolitan Area for 2024. Summarize the key findings, insights from the analysis, highlight the best real estate investment opportunities, and any significant patterns observed. Please include at least 5 citations from peer reviewed articles."
    };
    gradePrompt = "After grading the essay using the rubric, please explain how the essay was tuned to achieve a perfect score on the rubric. Add the total score at the end using this format: Total Score is [X]/[Y].";
}

// Get prompt for an essay
function getPromptForEssay(essayName) {
    return prompts[essayName] || '';
}

function getGradePrompt() {
    return gradePrompt;
}

// Setup all filters
function setupFilters() {
    elements.filters.style.display = 'block';
    fillModelDropdown();
    fillEssayDropdown();
    fillRubricDropdown();
    addResetButton();
    attachFilterListeners();
}

// Fill model dropdown
function fillModelDropdown() {
    elements.modelFilter.innerHTML = '<option value="all">All Models</option>';
    getModels().forEach(model => {
        const option = document.createElement('option');
        option.value = model;
        option.textContent = model;
        elements.modelFilter.appendChild(option);
    });
}

// Fill essay dropdown
function fillEssayDropdown() {
    elements.essayFilter.innerHTML = '<option value="all">All Assignments</option>';
    const names = new Set();
    Object.values(getData()).forEach(item => names.add(item.essayName));

    Array.from(names).sort().forEach(name => {
        const option = document.createElement('option');
        option.value = name;
        option.textContent = name;
        elements.essayFilter.appendChild(option);
    });
    elements.essayFilter.value = 'Assignment_1';
}

// Fill rubric dropdown
function fillRubricDropdown() {
    elements.rubricFilter.innerHTML = '<option value="all">All Rubrics</option>';
    getRubrics().forEach(rubric => {
        const option = document.createElement('option');
        option.value = rubric;
        option.textContent = formatRubricName(rubric);
        elements.rubricFilter.appendChild(option);
    });
    elements.rubricFilter.value = 'critical_thinking';
}

// Add reset button
function addResetButton() {
    if (!document.getElementById('resetBtn')) {
        const btn = document.createElement('button');
        btn.id = 'resetBtn';
        btn.className = 'copy-btn';
        btn.style.cssText = 'width: 100%; margin-top: 1rem; background: rgba(255, 85, 85, 0.3);';
        btn.innerHTML = '🔄 Reset Filters';
        btn.onclick = resetFilters;
        elements.filters.appendChild(btn);
    }
}

// Listen for filter changes
function attachFilterListeners() {
    if (elements.filters.dataset.listening) return;

    elements.essayFilter.addEventListener('change', displayEssayList);
    elements.modelFilter.addEventListener('change', displayEssayList);
    elements.rubricFilter.addEventListener('change', displayEssayList);
    elements.filterGenerate.addEventListener('change', displayEssayList);
    elements.filterTune.addEventListener('change', displayEssayList);
    elements.filterScore.addEventListener('change', displayEssayList);
    elements.filters.dataset.listening = 'true';
}

// Reset all filters
function resetFilters() {
    elements.modelFilter.value = 'all';
    elements.essayFilter.value = 'all';
    elements.rubricFilter.value = 'all';
    elements.filterGenerate.checked = true;
    elements.filterTune.checked = true;
    elements.filterScore.checked = true;
    displayEssayList();
}

// Show the essay list - NEW SIMPLE VERSION
function displayEssayList() {
    elements.essayList.innerHTML = '';

    // Get all data grouped by rubric
    const rubricGroups = groupByRubric();

    if (Object.keys(rubricGroups).length === 0) {
        showNoResults();
        return;
    }

    // Show each rubric and its experiments
    Object.keys(rubricGroups).sort().forEach(rubricName => {
        showRubricSection(rubricName, rubricGroups[rubricName]);
    });
}

// Group all data by rubric first
function groupByRubric() {
    const rubricGroups = {};

    Object.values(getData()).forEach(item => {
        if (item.command === 'generate' || item.command === 'tune') {
            const rubric = item.rubric;
            if (!rubricGroups[rubric]) {
                rubricGroups[rubric] = new Set();
            }
            rubricGroups[rubric].add(item.essayName);
        }
    });

    // Convert sets to arrays
    Object.keys(rubricGroups).forEach(rubric => {
        rubricGroups[rubric] = Array.from(rubricGroups[rubric]).sort();
    });

    return rubricGroups;
}

// Show a rubric section with all its experiments
function showRubricSection(rubricName, experimentNames) {
    // Create rubric container
    const rubricDiv = document.createElement('div');
    rubricDiv.className = 'rubric-section';
    rubricDiv.style.marginBottom = '2rem';

    // Add rubric header
    const rubricHeader = document.createElement('div');
    rubricHeader.className = 'rubric-section-header';
    rubricHeader.textContent = `📋 ${formatRubricName(rubricName)}`;
    rubricDiv.appendChild(rubricHeader);

    // Show each experiment in this rubric
    experimentNames.forEach(experimentName => {
        showExperiment(experimentName, rubricName, rubricDiv);
    });

    elements.essayList.appendChild(rubricDiv);
}

// Get list of unique experiments (Assignment_1, Assignment_2, etc.)
function getExperiments() {
    const experiments = new Set();
    Object.values(getData()).forEach(item => {
        experiments.add(item.essayName);
    });
    return Array.from(experiments).sort();
}

// Show one experiment section
function showExperiment(experimentName, rubricFilter, parentContainer) {
    // Create experiment container
    const experimentDiv = document.createElement('div');
    experimentDiv.className = 'experiment-section';

    // Get all essays for this experiment and rubric
    const essays = getEssaysForExperiment(experimentName, rubricFilter);

    // Add experiment header
    const header = document.createElement('div');
    header.className = 'experiment-header';
    header.textContent = `${experimentName} (${essays.length} essays)`;
    experimentDiv.appendChild(header);

    // Group by model and type (generate/tune)
    const grouped = groupByModelAndType(essays);

    // Show each model's essays
    Object.keys(grouped).sort().forEach(modelName => {
        const modelData = grouped[modelName];

        // Show GENERATED essays
        if (modelData.generate.length > 0) {
            modelData.generate.forEach(item => {
                const essayBtn = createEssayButton('GENERATED', modelName, item);
                experimentDiv.appendChild(essayBtn);
            });
        }

        // Show TUNED essays
        if (modelData.tune.length > 0) {
            modelData.tune.forEach(item => {
                const essayBtn = createEssayButton('TUNED', modelName, item);
                experimentDiv.appendChild(essayBtn);
            });
        }
    });

    parentContainer.appendChild(experimentDiv);
}

// Get all essays for an experiment
function getEssaysForExperiment(experimentName, rubricFilter) {
    return Object.values(getData()).filter(item =>
        item.essayName === experimentName &&
        (item.command === 'generate' || item.command === 'tune') &&
        (!rubricFilter || item.rubric === rubricFilter)
    );
}

// Group essays by model and type
function groupByModelAndType(essays) {
    const grouped = {};

    essays.forEach(item => {
        const model = item.modelName;

        if (!grouped[model]) {
            grouped[model] = {
                generate: [],
                tune: []
            };
        }

        if (item.command === 'generate') {
            grouped[model].generate.push(item);
        } else if (item.command === 'tune') {
            grouped[model].tune.push(item);
        }
    });

    return grouped;
}

// Create a button for an essay
function createEssayButton(type, modelName, item) {
    const btn = document.createElement('div');
    btn.className = 'essay-button';

    // Create badge for model
    const badge = document.createElement('span');
    badge.className = 'model-badge';
    badge.textContent = modelName;

    // Create label for type
    const label = document.createElement('span');
    label.className = 'essay-type-label';
    label.textContent = type;

    btn.appendChild(badge);
    btn.appendChild(label);

    // Click handler
    btn.onclick = () => showEssayDetails(item, btn);

    return btn;
}

// Show essay details in right panel
function showEssayDetails(item, buttonElement) {
    // Remove active class from all buttons
    document.querySelectorAll('.essay-button').forEach(btn =>
        btn.classList.remove('active')
    );

    // Add active class to clicked button
    if (buttonElement) {
        buttonElement.classList.add('active');
    }

    // Get scores for this essay
    const scores = getScoresForEssay(item);

    // Render in right panel
    renderEssayDetails(item, scores);
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

// Render essay details in right panel
function renderEssayDetails(item, scores) {
    const panel = elements.rightPanel;
    panel.innerHTML = '';

    // Add header
    const header = document.createElement('h2');
    header.textContent = `${item.essayName} - ${item.command.toUpperCase()}`;
    panel.appendChild(header);

    // Add model info
    const info = document.createElement('div');
    info.className = 'content-info';
    info.innerHTML = `
        <p><strong>Model:</strong> ${item.modelName}</p>
        <p><strong>Rubric:</strong> ${formatRubricName(item.rubric)}</p>
        <p><strong>Time:</strong> ${item.data.timestamp || 'N/A'}</p>
    `;
    panel.appendChild(info);

    // Add prompt
    const prompt = getPromptForEssay(item.essayName);
    if (prompt) {
        const promptBox = document.createElement('div');
        promptBox.className = 'content-box prompt-box';
        promptBox.innerHTML = `
            <h3>📝 Prompt</h3>
            <div class="prompt-text">${prompt}</div>
        `;
        panel.appendChild(promptBox);
    }

    // Add response with toggle functionality
    const responseBox = document.createElement('div');
    responseBox.className = 'content-box';

    const responseHeader = document.createElement('h3');
    responseHeader.textContent = '📄 Response';
    responseHeader.style.cursor = 'pointer';
    responseHeader.style.userSelect = 'none';

    const responseContent = document.createElement('div');
    responseContent.className = 'response-content';
    responseContent.style.display = 'none'; // Start collapsed

    const responseText = item.data.result || item.data.essay || 'No content';
    const cleanResponseText = removeMarkdown(responseText);
    responseContent.innerHTML = `
        <div class="essay-text">${cleanResponseText}</div>
        <button class="copy-btn" onclick="copyText(\`${cleanResponseText.replace(/`/g, '\\`').replace(/\$/g, '\\$')}\`)">📋 Copy</button>
    `;

    // Toggle on header click
    responseHeader.onclick = () => {
        if (responseContent.style.display === 'none') {
            responseContent.style.display = 'block';
            responseHeader.textContent = '📄 Response ▼';
        } else {
            responseContent.style.display = 'none';
            responseHeader.textContent = '📄 Response';
        }
    };

    responseBox.appendChild(responseHeader);
    responseBox.appendChild(responseContent);
    panel.appendChild(responseBox);

    // Add scores section with tabs
    if (scores.length > 0) {
        const scoresBox = document.createElement('div');
        scoresBox.className = 'content-box scores-section';
        scoresBox.innerHTML = '<h3>📊 Scores</h3>';

        // Create tabs container
        const tabsContainer = document.createElement('div');
        tabsContainer.className = 'score-tabs';

        // Create content container
        const contentContainer = document.createElement('div');
        contentContainer.className = 'score-tab-content';
        contentContainer.innerHTML = '<div class="score-placeholder"><p style="color: var(--rami-lightgreen); font-style: italic;">Click a tab to view score</p></div>';

        // Separate AI and Human scores
        const aiScores = [];
        const humanScores = [];

        scores.forEach(scoreItem => {
            const graderModel = getModelName(scoreItem.data.grader);
            if (graderModel.startsWith('Human')) {
                humanScores.push(scoreItem);
            } else {
                aiScores.push(scoreItem);
            }
        });

        // Add AI model tabs
        aiScores.forEach(scoreItem => {
            const graderModel = getModelName(scoreItem.data.grader);
            const tab = document.createElement('button');
            tab.className = 'score-tab';
            tab.textContent = graderModel;
            tab.onclick = () => switchScoreTab(tab, scoreItem, contentContainer);
            tabsContainer.appendChild(tab);
        });

        // Add Human tabs dynamically
        humanScores.forEach(scoreItem => {
            const graderModel = getModelName(scoreItem.data.grader);
            const tab = document.createElement('button');
            tab.className = 'score-tab human-tab';
            tab.textContent = graderModel;
            tab.onclick = () => switchScoreTab(tab, scoreItem, contentContainer);
            tabsContainer.appendChild(tab);
        });

        scoresBox.appendChild(tabsContainer);
        scoresBox.appendChild(contentContainer);

        panel.appendChild(scoresBox);
    }

    panel.scrollTop = 0;
}

// Switch between score tabs
function switchScoreTab(tabButton, scoreItem, contentContainer) {
    // Check if this tab is already active
    const isActive = tabButton.classList.contains('active');

    // Remove active class from all tabs
    const allTabs = tabButton.parentElement.querySelectorAll('.score-tab');
    allTabs.forEach(tab => tab.classList.remove('active'));

    if (isActive) {
        // If clicking the same tab, close it (show placeholder)
        contentContainer.innerHTML = '<div class="score-placeholder"><p style="color: var(--rami-lightgreen); font-style: italic;">Click a tab to view score</p></div>';
    } else {
        // Add active class to clicked tab and show content
        tabButton.classList.add('active');
        showScoreContent(scoreItem, contentContainer);
    }
}

// Show score content in the container
function showScoreContent(scoreItem, contentContainer) {
    contentContainer.innerHTML = '';

    if (!scoreItem) {
        // Show placeholder
        contentContainer.innerHTML = `
            <div class="score-placeholder">
                <p style="color: var(--rami-lightgreen); font-style: italic;">No score data available</p>
            </div>
        `;
        return;
    }

    // Create score content display
    const scoreContent = document.createElement('div');
    scoreContent.className = 'score-details';

    const graderModel = getModelName(scoreItem.data.grader);
    const fullGraderName = scoreItem.data.grader || graderModel;
    const scoreText = scoreItem.data.result || scoreItem.data.score || 'No score available';
    const cleanScoreText = removeMarkdown(scoreText);

    scoreContent.innerHTML = `
        <div class="score-meta">
            <p><strong>Graded by:</strong> ${fullGraderName}</p>
            <p><strong>Essay Type:</strong> ${scoreItem.data.essay_type || 'generate'}</p>
            <p><strong>Time:</strong> ${scoreItem.data.timestamp || 'N/A'}</p>
        </div>
        <div class="score-text">${cleanScoreText}</div>
        <button class="copy-btn" onclick="copyText(\`${cleanScoreText.replace(/`/g, '\\`').replace(/\$/g, '\\$')}\`)">📋 Copy Score</button>
    `;

    contentContainer.appendChild(scoreContent);
}

// Check if item matches filters
function itemMatchesFilters(item, model, filters) {
    if (filters.essay !== 'all' && item.essayName !== filters.essay) return false;
    if (filters.rubric !== 'all' && item.rubric !== filters.rubric) return false;
    if (filters.model !== 'all' && model !== filters.model) return false;
    if (item.command === 'generate' && !filters.showGenerate) return false;
    if (item.command === 'tune' && !filters.showTune) return false;
    if (item.command === 'score' && !filters.showScore) return false;
    return true;
}

// Get model for item
function getModelForItem(item) {
    if (item.command === 'score') {
        return getModelName(item.data.writer);
    }
    return item.modelName;
}

// Make empty buckets
function makeEmptyBuckets() {
    return {
        generate: [],
        tune: [],
        generate_scores: [],
        tune_scores: []
    };
}

// Add item to correct bucket
function addItemToBucket(buckets, item) {
    if (item.command === 'generate') {
        buckets.generate.push(item);
    } else if (item.command === 'tune') {
        buckets.tune.push(item);
    } else if (item.command === 'score') {
        const type = item.data.essay_type || 'generate';
        if (type === 'generate') {
            buckets.generate_scores.push(item);
        } else {
            buckets.tune_scores.push(item);
        }
    }
}

// Group essays by rubric/essay/model
function groupEssays(filters) {
    const groups = {};

    // Look at each item
    Object.values(getData()).forEach(item => {
        const model = getModelForItem(item);

        // Skip if doesn't match filters
        if (!itemMatchesFilters(item, model, filters)) return;

        // Get the names we need
        const rubricName = item.rubric;
        const essayName = item.essayName;
        const modelName = model;

        // Create rubric if not exist
        if (!groups[rubricName]) {
            groups[rubricName] = {};
        }

        // Create essay if not exist
        if (!groups[rubricName][essayName]) {
            groups[rubricName][essayName] = {};
        }

        // Create model bucket if not exist
        if (!groups[rubricName][essayName][modelName]) {
            groups[rubricName][essayName][modelName] = makeEmptyBuckets();
        }

        // Get the bucket
        const bucket = groups[rubricName][essayName][modelName];

        // Put item in bucket
        addItemToBucket(bucket, item);
    });

    return groups;
}

// Show summary at top
function showSummary() {
    const template = document.getElementById('summaryTemplate');
    const summary = template.content.cloneNode(true);
    summary.querySelector('.total-count').textContent = getTotalCount();
    summary.querySelector('.rubrics-count').textContent = allRubrics.size;
    summary.querySelector('.models-count').textContent = allModels.size;
    elements.essayList.appendChild(summary);
}

// Show all groups
function showGroups(groups) {
    Object.keys(groups).sort().forEach(rubric => {
        showRubricHeader(rubric);
        showEssaysInRubric(groups[rubric]);
    });
}

// Show rubric header
function showRubricHeader(rubric) {
    const header = document.createElement('div');
    header.className = 'rubric-header';
    const colors = getRubricColors(rubric);
    header.style.background = colors.bgColor;
    header.style.color = colors.color;
    header.style.borderLeftColor = colors.color;
    header.textContent = `📋 ${formatRubricName(rubric)}`;
    elements.essayList.appendChild(header);
}

// Show essays in rubric
function showEssaysInRubric(essays) {
    Object.keys(essays).sort().forEach(essayName => {
        const item = document.createElement('div');
        item.className = 'essay-item';

        const header = document.createElement('div');
        header.className = 'essay-header';
        header.textContent = essayName;
        item.appendChild(header);

        const commands = document.createElement('div');
        commands.className = 'essay-commands';

        Object.keys(essays[essayName]).sort().forEach(model => {
            showModelCommands(commands, model, essays[essayName][model]);
        });

        item.appendChild(commands);
        elements.essayList.appendChild(item);
    });
}

// Show commands for a model
function showModelCommands(container, model, items) {
    const header = document.createElement('div');
    header.className = 'model-header';
    header.textContent = ` ${model}`;
    container.appendChild(header);

    items.generate.forEach(item => {
        container.appendChild(makeCommandButton('Generate', item.data));
    });

    items.generate_scores.forEach(item => {
        const btn = makeCommandButton('Score', item.data);
        btn.style.marginLeft = '1.5rem';
        container.appendChild(btn);
    });

    items.tune.forEach(item => {
        container.appendChild(makeCommandButton('Tune', item.data));
    });

    items.tune_scores.forEach(item => {
        const btn = makeCommandButton('Score', item.data);
        btn.style.marginLeft = '1.5rem';
        container.appendChild(btn);
    });
}

// Make a clickable command button
function makeCommandButton(command, data) {
    const btn = document.createElement('div');
    btn.className = 'command-item';

    let label = `    ${command}`;
    if (command === 'Score') {
        const type = data.essay_type || 'generate';
        const grader = getModelName(data.grader);
        label = `        ${type.charAt(0).toUpperCase() + type.slice(1)} Essay (by ${grader})`;
    }

    btn.textContent = label;
    btn.onclick = (e) => showContent(e, command, data);
    return btn;
}

// Show content when clicked
function showContent(event, command, data) {
    document.querySelectorAll('.command-item').forEach(item => item.classList.remove('active'));
    event.target.classList.add('active');
    renderContent(elements.rightPanel, command, data, gradePrompt);
}

// Show no results message
function showNoResults() {
    const listTemplate = document.getElementById('noResultsTemplate');
    const panelTemplate = document.getElementById('noResultsPanelTemplate');
    elements.essayList.appendChild(listTemplate.content.cloneNode(true));
    elements.rightPanel.appendChild(panelTemplate.content.cloneNode(true));
}

// Show right panel summary
function showRightPanel(filters) {
    elements.rightPanel.innerHTML = '';

    // Add summary template
    const summaryTemplate = document.getElementById('rightPanelSummaryTemplate');
    const summary = summaryTemplate.content.cloneNode(true);

    // Get the filter list container
    const filtersList = summary.querySelector('.active-filters-list');

    // Add active filters
    if (filters.essay !== 'all') {
        filtersList.appendChild(createFilterItem('📝 Assignment', filters.essay));
    }
    if (filters.model !== 'all') {
        filtersList.appendChild(createFilterItem('🤖 Model', filters.model));
    }
    if (filters.rubric !== 'all') {
        filtersList.appendChild(createFilterItem('📋 Rubric', formatRubricName(filters.rubric)));
    }

    elements.rightPanel.appendChild(summary);

    // Show prompts if essay selected
    if (filters.essay !== 'all') {
        const prompt = getPromptForEssay(filters.essay);
        if (prompt) {
            elements.rightPanel.appendChild(createPromptBox('📝 Assignment Prompt', prompt));
        }

        const grade = getGradePrompt();
        if (grade) {
            elements.rightPanel.appendChild(createPromptBox('✅ Grading Prompt', grade));
        }
    }

    // Add tip box
    const tipTemplate = document.getElementById('tipBoxTemplate');
    elements.rightPanel.appendChild(tipTemplate.content.cloneNode(true));
}

// Create a filter item from template
function createFilterItem(label, value) {
    const template = document.getElementById('filterItemTemplate');
    const item = template.content.cloneNode(true);
    item.querySelector('.filter-label').textContent = label;
    item.querySelector('.filter-value').textContent = value;
    return item;
}

// Create a prompt box from template
function createPromptBox(title, text) {
    const template = document.getElementById('promptBoxTemplate');
    const box = template.content.cloneNode(true);
    box.querySelector('.prompt-title').textContent = title;
    box.querySelector('.prompt-text').textContent = text;
    return box;
}

// Get colors for rubric
function getRubricColors(rubric) {
    const colors = {
        critical_thinking: { color: '#ffffff', bgColor: 'rgba(3, 98, 76, 0.15)' },
        oral_communication: { color: '#2CC295', bgColor: 'rgba(44, 194, 149, 0.15)' }
    };
    return colors[rubric] || { color: '#24ff02', bgColor: 'rgba(36, 255, 2, 0.15)' };
}

// Show notification popup
function showNotification(message) {
    const template = document.getElementById('notificationTemplate');
    const notif = template.content.cloneNode(true).querySelector('.notification');
    notif.textContent = message;
    document.body.appendChild(notif);
    setTimeout(() => {
        if (document.body.contains(notif)) document.body.removeChild(notif);
    }, 3000);
}
