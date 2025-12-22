/**
 * UIRenderer - Manages all UI rendering and user interactions
 * Handles filters, essay list display, and event listeners
 */
class UIRenderer {
    /**
     * Initialize UIRenderer
     * @param {DataManager} dataManager - Reference to DataManager instance
     */
    constructor(dataManager) {
        this.dataManager = dataManager;
        this.elements = this.cacheElements();
    }

    /**
     * Cache references to all DOM elements
     * @private
     * @returns {object} Object containing cached DOM elements
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
            githubBtn: document.getElementById('githubBtn')
        };
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
        this.elements.modelFilter.value = 'ChatGPT';
    }

    /**
     * Populate essay filter dropdown
     * @private
     */
    populateEssayFilter() {
        this.elements.essayFilter.innerHTML = '<option value="all">All Essays</option>';
        const essayNames = new Set();
        Object.values(this.dataManager.allData).forEach(item => {
            essayNames.add(item.essayName);
        });

        Array.from(essayNames).sort().forEach(name => {
            const option = document.createElement('option');
            option.value = name;
            option.textContent = name;
            this.elements.essayFilter.appendChild(option);
        });
        this.elements.essayFilter.value = 'Essay_1';
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
        this.updateRightPanelSummary(rubricGroups);
    }

    /**
     * Get current filter values
     * @private
     * @returns {object} Current filter values
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
     * @param {object} filters - Filter criteria
     * @returns {object} Grouped data structure
     */
    groupDataByFilters(filters) {
        const rubricGroups = {};

        Object.entries(this.dataManager.allData).forEach(([key, item]) => {
            // Apply filters
            if (filters.essay !== 'all' && item.essayName !== filters.essay) return;
            if (filters.model !== 'all' && item.modelName !== filters.model) return;
            if (filters.rubric !== 'all' && item.rubric !== filters.rubric) return;
            if (item.command === 'generate' && !filters.showGenerate) return;
            if (item.command === 'tune' && !filters.showTune) return;
            if (item.command === 'score' && !filters.showScore) return;

            // Group by rubric -> essay -> model
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

            // Place in appropriate bucket
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
            header.textContent = essayName;
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

        const contentRenderer = new ContentRenderer(this.elements.rightPanel);
        contentRenderer.render(commandType, data);
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
     * Update right panel with summary
     * @private
     */
    updateRightPanelSummary(rubricGroups) {
        let html = '<h2>Filter Results Summary</h2>';

        html += '<div class="content-info">';
        html += `<p><strong>Total Items:</strong> ${this.dataManager.getTotalCount()}</p>`;
        html += `<p><strong>Rubrics:</strong> ${this.dataManager.allRubrics.size}</p>`;
        html += `<p><strong>Models:</strong> ${this.dataManager.allModels.size}</p>`;
        html += '</div>';

        html += '<div class="content-box"><h3>By Rubric</h3>';
        Object.entries(rubricGroups).forEach(([rubricName, essayGroups]) => {
            const essayCount = Object.keys(essayGroups).length;
            let totalItems = 0;
            Object.values(essayGroups).forEach(models => {
                Object.values(models).forEach(buckets => {
                    totalItems += buckets.generate.length + buckets.tune.length + buckets.generate_scores.length + buckets.tune_scores.length;
                });
            });
            const formatted = ModelParser.formatRubricName(rubricName);
            html += `<p><strong>${formatted}:</strong> ${essayCount} essays, ${totalItems} items</p>`;
        });
        html += '</div>';

        html += '<div class="content-box"><h3>💡 Tip</h3><p>Click on any item in the left panel to view its full content below.</p></div>';
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
