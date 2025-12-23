/**
 * UIRenderer - Manages all UI rendering with dynamic prompt loading
 * Works directly with Assignment_1 format (no conversion)
 */
class UIRenderer {
    /**
     * Initialize UIRenderer
     * @param {DataManager} dataManager - Reference to DataManager instance
     */
    constructor(dataManager) {
        this.dataManager = dataManager;
        this.elements = this.cacheElements();
        this.prompts = {}; // Will be loaded from file
        this.gradePrompt = ''; // Grade prompt from file
        this.loadPrompts(); // Load prompts from JSON file
    }

    /**
     * Load prompts from JSON file dynamically
     * @private
     */
    async loadPrompts() {
        try {
            // Try local path first
            let response = await fetch('src/ai_assessment/prompt.json');
            
            // If not found, try GitHub Pages path
            if (!response.ok) {
                response = await fetch('/ai-assessment/src/ai_assessment/prompt.json');
            }
            
            if (!response.ok) {
                console.warn('Could not load prompt.json, using default prompts');
                this.setDefaultPrompts();
                return;
            }
            
            const data = await response.json();
            
            // Dynamically map all assignment_X_prompt keys to Assignment_X
            this.prompts = {};
            for (const key in data) {
                if (key.startsWith('assignment_') && key.endsWith('_prompt')) {
                    const match = key.match(/assignment_(\d+)_prompt/);
                    if (match) {
                        const assignmentKey = 'Assignment_' + match[1];
                        this.prompts[assignmentKey] = data[key];
                    }
                }
            }
            
            // Load grade_prompt separately
            this.gradePrompt = data.grade_prompt || '';
            
            console.log('Prompts loaded successfully');
        } catch (error) {
            console.warn('Error loading prompts:', error);
            this.setDefaultPrompts();
        }
    }

    /**
     * Set default prompts as fallback
     * @private
     */
    setDefaultPrompts() {
        this.prompts = {
            'Assignment_1': "Let's write a 1000 word fully written college essa, plus at least 5 citations from peer-reviewed articles in the end of essay not embedded links, that answers this question: Consider the following problem: In the morning, when Professor Catlove opens a new can of cat food, his cats run into the kitchen purring and meowing and rubbing their backs against his legs. What examples, if any, of classical conditioning, operant conditioning, and social learning are at work in this brief scene? Note that both the cats and the professor might be exhibiting conditioned behavior here.",
            'Assignment_2': "Let's write a 1000 word fully written college essay, plus at least 5 citations from peer-reviewed articles, that answers this question. To what extent do the attached economic data support the hypothesis \"social service spending is inversely related to economic growth\"? Formulate a verbal argument analyzing whether the data do or do not support the hypothesis.",
            'Assignment_3': "Let's write a 1000 word fully written college essay, that includes a real estate investment market analysis in the Boston Metropolitan Area for 2024. Summarize the key findings, insights from the analysis, highlight the best real estate investment opportunities, and any significant patterns observed. Please include at least 5 citations from peer reviewed articles."
        };
        
        this.gradePrompt = "After grading the essay using the rubric, please explain how the essay was tuned to achieve a perfect score on the rubric. Add the total score at the end using this format: Total Score is [X]/[Y].";
    }

    /**
     * Cache references to all DOM elements
     * @private
     */
    cacheElements() {
    return {
        uploadBox: document.getElementById('uploadBox'),
        fileInput: document.getElementById('fileInput'),
        essayList: document.getElementById('essayList'),
        rightPanel: document.getElementById('rightPanel'),
        filters: document.getElementById('filters'),
        modelFilter: document.getElementById('modelFilter'),
        essayFilter: document.getElementById('essayFilter'),
        rubricFilter: document.getElementById('rubricFilter'),
        filterGenerate: document.getElementById('filterGenerate'),
        filterTune: document.getElementById('filterTune'),
        filterScore: document.getElementById('filterScore'),
        filterShowOriginal: document.getElementById('filterShowOriginal'),  
        githubBtn: document.getElementById('githubBtn')
    };
}

    /**
     * Display name - no conversion needed
     * @private
     */
    getDisplayName(essayName) {
        if (!essayName) return 'Unknown';
        if (typeof essayName !== 'string') return 'Unknown';
        return essayName; // Return as-is (Assignment_1, Assignment_2, etc)
    }

    /**
     * Get prompt for essay
     * @private
     */
    getPromptForEssay(essayName) {
        return this.prompts[essayName] || '';
    }

    /**
     * Get grade prompt
     * @private
     */
    getGradePrompt() {
        return this.gradePrompt;
    }

    /**
     * Setup filters by populating dropdowns and attaching listeners
     */
    setupFilters() {
        this.elements.filters.style.display = 'block';

        this.populateModelFilter();
        this.populateEssayFilter();
        this.populateRubricFilter();
        this.addResetButton();
        this.attachFilterListeners();
        
    }

    /**
     * Populate model filter dropdown
     * @private
     */
    populateModelFilter() {
        this.elements.modelFilter.innerHTML = '<option value="all">All Models</option>';
        this.dataManager.getModels().forEach(model => {
            const option = document.createElement('option');
            option.value = model;
            option.textContent = model;
            this.elements.modelFilter.appendChild(option);
        });
        this.elements.modelFilter.value = 'all';
    }

    /**
     * Populate essay filter dropdown with display names
     * @private
     */
    populateEssayFilter() {
        this.elements.essayFilter.innerHTML = '<option value="all">All Assignments</option>';
        const essayNames = new Set();
        Object.values(this.dataManager.allData).forEach(item => {
            essayNames.add(item.essayName);
        });

        Array.from(essayNames).sort().forEach(name => {
            const option = document.createElement('option');
            option.value = name;
            option.textContent = this.getDisplayName(name);
            this.elements.essayFilter.appendChild(option);
        });
        this.elements.essayFilter.value = 'Assignment_1';
    }

    /**
     * Populate rubric filter dropdown
     * @private
     */
    populateRubricFilter() {
        this.elements.rubricFilter.innerHTML = '<option value="all">All Rubrics</option>';
        this.dataManager.getRubrics().forEach(rubric => {
            const option = document.createElement('option');
            option.value = rubric;
            option.textContent = ModelParser.formatRubricName(rubric);
            this.elements.rubricFilter.appendChild(option);
        });
        this.elements.rubricFilter.value = 'critical_thinking';
    }

    /**
     * Add reset filters button
     * @private
     */
    addResetButton() {
        if (!document.getElementById('resetBtn')) {
            const resetBtn = document.createElement('button');
            resetBtn.id = 'resetBtn';
            resetBtn.className = 'copy-btn';
            resetBtn.style.cssText = 'width: 100%; margin-top: 1rem; background: rgba(255, 85, 85, 0.3);';
            resetBtn.innerHTML = '🔄 Reset Filters';
            resetBtn.onclick = () => this.resetFilters();
            this.elements.filters.appendChild(resetBtn);
        }
    }

    /**
     * Attach event listeners to filter elements
     * @private
     */
    attachFilterListeners() {
        if (!this.elements.filters.dataset.listening) {
            this.elements.essayFilter.addEventListener('change', () => this.applyFilters());
            this.elements.modelFilter.addEventListener('change', () => this.applyFilters());
            this.elements.rubricFilter.addEventListener('change', () => this.applyFilters());
            this.elements.filterGenerate.addEventListener('change', () => this.applyFilters());
            this.elements.filterTune.addEventListener('change', () => this.applyFilters());
            this.elements.filterScore.addEventListener('change', () => this.applyFilters());
            this.elements.filters.dataset.listening = 'true';
        }
    }

    /**
     * Reset all filters to default values
     */
    resetFilters() {
        this.elements.modelFilter.value = 'all';
        this.elements.essayFilter.value = 'all';
        this.elements.rubricFilter.value = 'all';
        this.elements.filterGenerate.checked = true;
        this.elements.filterTune.checked = true;
        this.elements.filterScore.checked = true;
        this.applyFilters();
    }

    /**
     * Apply current filters and redisplay essays
     */
    applyFilters() {
        this.displayEssayList();
    }

    /**
     * Display essays in left panel based on current filters
     */
    displayEssayList() {
        this.elements.essayList.innerHTML = '';

        const filters = this.getActiveFilters();
        const rubricGroups = this.groupDataByFilters(filters);

        if (Object.keys(rubricGroups).length === 0) {
            this.renderNoResults();
            return;
        }

        this.renderSummary(rubricGroups);
        this.renderRubricGroups(rubricGroups);
        this.updateRightPanelSummary(rubricGroups, filters);
    }

    /**
     * Get current filter values
     * @private
     */
    getActiveFilters() {
        return {
            essay: this.elements.essayFilter.value,
            model: this.elements.modelFilter.value,
            rubric: this.elements.rubricFilter.value,
            showGenerate: this.elements.filterGenerate.checked,
            showTune: this.elements.filterTune.checked,
            showScore: this.elements.filterScore.checked
        };
    }

    /**
     * Group data according to filters
     * @private
     */
    groupDataByFilters(filters) {
        const rubricGroups = {};

        Object.entries(this.dataManager.allData).forEach(([key, item]) => {
            if (filters.essay !== 'all' && item.essayName !== filters.essay) return;
            if (filters.model !== 'all' && item.modelName !== filters.model) return;
            if (filters.rubric !== 'all' && item.rubric !== filters.rubric) return;
            if (item.command === 'generate' && !filters.showGenerate) return;
            if (item.command === 'tune' && !filters.showTune) return;
            if (item.command === 'score' && !filters.showScore) return;

            if (!rubricGroups[item.rubric]) {
                rubricGroups[item.rubric] = {};
            }
            if (!rubricGroups[item.rubric][item.essayName]) {
                rubricGroups[item.rubric][item.essayName] = {};
            }
            if (!rubricGroups[item.rubric][item.essayName][item.modelName]) {
                rubricGroups[item.rubric][item.essayName][item.modelName] = {
                    generate: [],
                    tune: [],
                    generate_scores: [],
                    tune_scores: []
                };
            }

            if (item.command === 'generate') {
                rubricGroups[item.rubric][item.essayName][item.modelName].generate.push(item);
            } else if (item.command === 'tune') {
                rubricGroups[item.rubric][item.essayName][item.modelName].tune.push(item);
            } else if (item.command === 'score') {
                const essayType = item.data.essay_type || 'generate';
                const bucket = essayType === 'generate' ? 'generate_scores' : 'tune_scores';
                rubricGroups[item.rubric][item.essayName][item.modelName][bucket].push(item);
            }
        });

        return rubricGroups;
    }

    /**
     * Render summary statistics
     * @private
     */
    renderSummary(rubricGroups) {
        const summary = document.createElement('div');
        summary.style.cssText = `
            background: rgba(85, 255, 221, 0.1);
            border: 1px solid rgba(85, 255, 221, 0.3);
            padding: 0.75rem;
            border-radius: 6px;
            margin-bottom: 1rem;
            text-align: center;
            font-size: 0.9rem;
        `;
        summary.innerHTML = `<strong>Total:</strong> ${this.dataManager.getTotalCount()} items | <strong>Rubrics:</strong> ${this.dataManager.allRubrics.size} | <strong>Models:</strong> ${this.dataManager.allModels.size}`;
        this.elements.essayList.appendChild(summary);
    }

    /**
     * Render all rubric groups
     * @private
     */
    renderRubricGroups(rubricGroups) {
        Object.keys(rubricGroups).sort().forEach(rubricName => {
            this.renderRubricHeader(rubricName);
            this.renderEssaysInRubric(rubricGroups[rubricName], rubricName);
        });
    }

    /**
     * Render rubric header
     * @private
     */
    renderRubricHeader(rubricName) {
        const header = document.createElement('div');
        const { color, bgColor } = this.getRubricColors(rubricName);

        header.style.cssText = `
            background: ${bgColor};
            padding: 0.75rem 1rem;
            margin: 1rem 0 0.5rem 0;
            border-radius: 6px;
            font-weight: 700;
            font-size: 1rem;
            color: ${color};
            border-left: 4px solid ${color};
        `;

        header.textContent = `📋 ${ModelParser.formatRubricName(rubricName)}`;
        this.elements.essayList.appendChild(header);
    }

    /**
     * Render essays within a rubric
     * @private
     */
    renderEssaysInRubric(essayGroups, rubricName) {
        Object.keys(essayGroups).sort().forEach(essayName => {
            const essayItem = document.createElement('div');
            essayItem.className = 'essay-item';

            const header = document.createElement('div');
            header.className = 'essay-header';
            header.textContent = this.getDisplayName(essayName);
            essayItem.appendChild(header);

            const commands = document.createElement('div');
            commands.className = 'essay-commands';

            Object.keys(essayGroups[essayName]).sort().forEach(modelName => {
                this.renderModelSection(commands, modelName, essayGroups[essayName][modelName]);
            });

            essayItem.appendChild(commands);
            this.elements.essayList.appendChild(essayItem);
        });
    }

    /**
     * Render model section within an essay
     * @private
     */
    renderModelSection(container, modelName, items) {
        const modelHeader = document.createElement('div');
        modelHeader.style.cssText = `
            background: rgba(85, 255, 221, 0.15);
            padding: 0.5rem 0.75rem;
            margin: 0.5rem 0 0.25rem 0;
            border-radius: 4px;
            font-weight: 600;
            font-size: 0.85rem;
            color: var(--rami-highlight);
        `;
        modelHeader.textContent = ` ${modelName}`;
        container.appendChild(modelHeader);

        items.generate.forEach(item => {
            container.appendChild(this.createCommandElement('Generate', item.data));
        });

        items.generate_scores.forEach(item => {
            const el = this.createCommandElement('Score', item.data);
            el.style.marginLeft = '1.5rem';
            container.appendChild(el);
        });

        items.tune.forEach(item => {
            container.appendChild(this.createCommandElement('Tune', item.data));
        });

        items.tune_scores.forEach(item => {
            const el = this.createCommandElement('Score', item.data);
            el.style.marginLeft = '1.5rem';
            container.appendChild(el);
        });
    }

    /**
     * Create a command element (clickable essay item)
     * @private
     */
    createCommandElement(command, data) {
        const item = document.createElement('div');
        item.className = 'command-item';

        let label = `    ${command}`;

        if (command === 'Score') {
            const essayType = data.essay_type || 'generate';
            const graderName = ModelParser.getModelName(data.grader);
            label = `        ${essayType.charAt(0).toUpperCase() + essayType.slice(1)} Score (by ${graderName})`;

            const resultText = data.result || '';
            const endOfText = resultText.slice(-200);
            const match = endOfText.match(/(\d+\.?\d*)\s*(?:out of|\/)\s*(\d+\.?\d*)/i);
            if (match) {
                label += ` - ${match[1]}/${match[2]}`;
            }
        }

        item.textContent = label;
        item.addEventListener('click', () => this.showContentDetail(command, data));

        return item;
    }

    /**
     * Show essay content in right panel
     */
    showContentDetail(commandType, data) {
        const allItems = document.querySelectorAll('.command-item');
        allItems.forEach(item => item.classList.remove('active'));
        event.target.closest('.command-item').classList.add('active');

        // Pass grade_prompt to ContentRenderer
        const contentRenderer = new ContentRenderer(this.elements.rightPanel);
        contentRenderer.render(commandType, data, this.gradePrompt);  // ← ADD this.gradePrompt
    }

    /**
     * Render no results message
     * @private
     */
    renderNoResults() {
        this.elements.essayList.innerHTML = '<p style="text-align: center; color: rgba(255,255,255,0.5); padding: 2rem;">No essays match your filters</p>';
        this.elements.rightPanel.innerHTML = `
            <div class="welcome-message">
                <h2>🔍 No Results</h2>
                <p>No essays match your current filters. Try adjusting your search criteria.</p>
            </div>
        `;
    }

    /**
     * Update right panel with filter summary and prompts
     * @private
     */
    updateRightPanelSummary(rubricGroups, filters) {
        let html = '<h2> Filter Summary</h2>';

        html += '<div class="content-info" style="background: rgba(255, 255, 255, 0.05); border-left: 4px solid var(--rami-highlight);">';
        html += '<p><strong>Active Filters:</strong></p>';
        
        if (filters.essay !== 'all') {
            html += `<p style="margin: 0.5rem 0; padding-left: 1rem;"> Assignment: <strong>${this.getDisplayName(filters.essay)}</strong></p>`;
        }
        if (filters.model !== 'all') {
            html += `<p style="margin: 0.5rem 0; padding-left: 1rem;"> Model: <strong>${filters.model}</strong></p>`;
        }
        if (filters.rubric !== 'all') {
            html += `<p style="margin: 0.5rem 0; padding-left: 1rem;"> Rubric: <strong>${ModelParser.formatRubricName(filters.rubric)}</strong></p>`;
        }
        
        const commands = [];
        if (filters.showGenerate) commands.push('Generate');
        if (filters.showTune) commands.push('Tune');
        if (filters.showScore) commands.push('Score');
        if (commands.length > 0 && commands.length < 3) {
            html += `<p style="margin: 0.5rem 0; padding-left: 1rem;">⚙️ Commands: <strong>${commands.join(', ')}</strong></p>`;
        }
        
        html += '</div>';

        if (filters.essay !== 'all') {
            const assignmentPrompt = this.getPromptForEssay(filters.essay);
            const gradePrompt = this.getGradePrompt();
            
            if (assignmentPrompt) {
                html += '<div class="content-box prompt-box">';
                html += '<h3> ✅ Assignment Prompt</h3>';
                html += `<div class="prompt-text">${assignmentPrompt}</div>`;
                html += '</div>';
            }
            
            if (gradePrompt) {
                html += '<div class="content-box prompt-box">';
                html += '<h3> ✅ Grading Prompt</h3>';
                html += `<div class="prompt-text">${gradePrompt}</div>`;
                html += '</div>';
            }
        }

        html += '<div class="content-box"><h3> Tip</h3><p>Click on any item in the left panel to view its full content below.</p></div>';
        html += '<hr style="border: 1px solid rgba(85, 255, 221, 0.2); margin: 2rem 0;">';

        this.elements.rightPanel.innerHTML = html;
    }

    /**
     * Get rubric-specific colors
     * @private
     */
    getRubricColors(rubricName) {
        const colors = {
            critical_thinking: { color: '#ffffff', bgColor: 'rgba(3, 98, 76, 0.15)' },
            oral_communication: { color: '#2CC295', bgColor: 'rgba(44, 194, 149, 0.15)' }
        };
        return colors[rubricName] || { color: '#24ff02', bgColor: 'rgba(36, 255, 2, 0.15)' };
    }

    /**
     * Show temporary notification
     */
    showNotification(message) {
        const notif = document.createElement('div');
        notif.style.cssText = `
            position: fixed;
            top: 20px;
            right: 20px;
            background: #24ff02;
            color: #2c2c2c;
            padding: 1rem 1.5rem;
            border-radius: 8px;
            font-weight: 600;
            z-index: 1000;
        `;
        notif.textContent = message;
        document.body.appendChild(notif);

        setTimeout(() => {
            if (document.body.contains(notif)) {
                document.body.removeChild(notif);
            }
        }, 3000);
    }
}