class DataManager {
    constructor() {
        this.allData = {};
        this.allModels = new Set();
        this.allRubrics = new Set();
    }

    addData(essayName, modelName, command, rubric, data) {
        const uniqueKey = this.generateKey(essayName, modelName, command, rubric, data);
        this.allData[uniqueKey] = {
            essayName,
            modelName,
            command,
            rubric,
            data
        };
        this.allModels.add(modelName);
        this.allRubrics.add(rubric);
    }

    generateKey(essayName, modelName, command, rubric, data) {
        if (command === 'score') {
            const essayType = data.essay_type || 'generate';
            const graderName = ModelParser.getModelName(data.grader);
            return `${essayName}_${modelName}_${essayType}_score_${graderName}_${rubric}`;
        }
        return `${essayName}_${modelName}_${command}_${rubric}`;
    }

    getData() {
        return this.allData;
    }

    getModels() {
        return Array.from(this.allModels).sort();
    }

    getRubrics() {
        return Array.from(this.allRubrics).sort();
    }

    clear() {
        this.allData = {};
        this.allModels.clear();
        this.allRubrics.clear();
    }

    getTotalCount() {
        return Object.keys(this.allData).length;
    }
}

/**
 * ModelParser - Utility for model name extraction and formatting
 */

class ModelParser {
    static getModelName(modelString) {
        if (!modelString) return 'unknown';

        const model = modelString.toLowerCase();

        if (model.includes('gpt') || model.includes('chatgpt') || model.includes('openai')) {
            return 'ChatGPT';
        }
        if (model.includes('claude') || model.includes('anthropic')) {
            return 'Claude';
        }
        if (model.includes('gemini') || model.includes('google')) {
            return 'Gemini';
        }
        if (model.includes('grok') || model.includes('xai') || model.includes('x.ai')) {
            return 'Grok';
        }

        return modelString.split('-')[0];
    }

    static formatRubricName(rubricName) {
        return rubricName
            .split('_')
            .map(word => word.charAt(0).toUpperCase() + word.slice(1))
            .join(' ');
    }
}

/**
 * FileProcessor - Handles file reading and data processing
 */

class FileProcessor {
    constructor(dataManager) {
        this.dataManager = dataManager;
    }

    processLocalFiles(files) {
        return new Promise((resolve, reject) => {
            const jsonFiles = Array.from(files).filter(f => f.name.endsWith('.json'));

            if (jsonFiles.length === 0) {
                reject('No JSON files found!');
                return;
            }

            let filesRead = 0;

            jsonFiles.forEach(file => {
                const reader = new FileReader();

                reader.onload = (e) => {
                    try {
                        const data = JSON.parse(e.target.result);
                        const folderGuess = this.guessFolderFromFilename(file.name);
                        this.processData(data, folderGuess);

                        filesRead++;
                        if (filesRead === jsonFiles.length) {
                            resolve(filesRead);
                        }
                    } catch (error) {
                        reject(`Error reading ${file.name}: ${error.message}`);
                    }
                };

                reader.readAsText(file);
            });
        });
    }

    guessFolderFromFilename(filename) {
        if (filename.includes('critical')) {
            return 'critical_thinking';
        } else if (filename.includes('oral')) {
            return 'oral_communication';
        }
        return null;
    }

    processData(data, folderName) {
        const essayName = data.essay_name;
        const command = data.command;

        let rubric = data.rubric || folderName || 'unknown';
        this.dataManager.allRubrics.add(rubric);

        let modelName;
        if (command === 'score') {
            modelName = ModelParser.getModelName(data.writer);
        } else {
            modelName = ModelParser.getModelName(data.model);
        }

        this.dataManager.addData(essayName, modelName, command, rubric, data);
    }
}

/**
 * GitHubLoader - Handles GitHub data loading
 */

class GitHubLoader {
    constructor(dataManager) {
        this.dataManager = dataManager;
        this.folders = ['critical_thinking', 'oral_communication'];
    }

    async loadFromGitHub() {
        let totalLoaded = 0;

        for (const folder of this.folders) {
            const apiUrl = `https://api.github.com/repos/raminguyen/ai-assessment/contents/data/${folder}`;
            const rawUrl = `https://raw.githubusercontent.com/raminguyen/ai-assessment/main/data/${folder}/`;

            try {
                const response = await fetch(apiUrl);
                const files = await response.json();
                const jsonFiles = files.filter(file => file.name.endsWith('.json'));

                for (const file of jsonFiles) {
                    try {
                        const fileResponse = await fetch(rawUrl + file.name);
                        const fileText = await fileResponse.text();
                        const data = JSON.parse(fileText);
                        
                        const processor = new FileProcessor(this.dataManager);
                        processor.processData(data, folder);
                        totalLoaded++;
                    } catch (error) {
                        console.error(`Error loading ${file.name}:`, error);
                    }
                }
            } catch (error) {
                console.error(`Error loading from folder ${folder}:`, error);
            }
        }

        return totalLoaded;
    }
}

/**
 * UIRenderer - Handles all UI rendering
 */

class UIRenderer {
    constructor(dataManager) {
        this.dataManager = dataManager;
        this.elements = this.cacheElements();
    }

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

    setupFilters() {
        this.elements.filters.style.display = 'block';

        this.populateModelFilter();
        this.populateEssayFilter();
        this.populateRubricFilter();
        this.addResetButton();
        this.attachFilterListeners();
    }

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

    resetFilters() {
        this.elements.modelFilter.value = 'all';
        this.elements.essayFilter.value = 'all';
        this.elements.rubricFilter.value = 'all';
        this.elements.filterGenerate.checked = true;
        this.elements.filterTune.checked = true;
        this.elements.filterScore.checked = true;
        this.applyFilters();
    }

    applyFilters() {
        this.displayEssayList();
    }

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

    renderRubricGroups(rubricGroups) {
        Object.keys(rubricGroups).sort().forEach(rubricName => {
            this.renderRubricHeader(rubricName);
            this.renderEssaysInRubric(rubricGroups[rubricName], rubricName);
        });
    }

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

    showContentDetail(commandType, data) {
        const allItems = document.querySelectorAll('.command-item');
        allItems.forEach(item => item.classList.remove('active'));
        event.target.closest('.command-item').classList.add('active');

        const contentRenderer = new ContentRenderer(this.elements.rightPanel);
        contentRenderer.render(commandType, data);
    }

    renderNoResults() {
        this.elements.essayList.innerHTML = '<p style="text-align: center; color: rgba(255,255,255,0.5); padding: 2rem;">No essays match your filters</p>';
        this.elements.rightPanel.innerHTML = `
            <div class="welcome-message">
                <h2>🔍 No Results</h2>
                <p>No essays match your current filters. Try adjusting your search criteria.</p>
            </div>
        `;
    }

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

    getRubricColors(rubricName) {
        const colors = {
            critical_thinking: { color: '#ffffff', bgColor: 'rgba(3, 98, 76, 0.15)' },
            oral_communication: { color: '#2CC295', bgColor: 'rgba(44, 194, 149, 0.15)' }
        };
        return colors[rubricName] || { color: '#24ff02', bgColor: 'rgba(36, 255, 2, 0.15)' };
    }

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

/**
 * ContentRenderer - Handles content display in right panel
 */

class ContentRenderer {
    constructor(rightPanel) {
        this.rightPanel = rightPanel;
    }

    render(commandType, data) {
        const html = this.buildHTML(commandType, data);
        this.rightPanel.innerHTML = html;

        const contentStart = this.rightPanel.querySelector('h2:last-of-type');
        if (contentStart) {
            contentStart.scrollIntoView({ behavior: 'smooth', block: 'start' });
        }
    }

    buildHTML(commandType, data) {
        let html = `<h2>${data.essay_name}</h2>`;

        html += this.buildInfoBox(commandType, data);
        html += this.buildContentBox(commandType, data);
        html += this.buildCopyButton(commandType);

        return html;
    }

    buildInfoBox(commandType, data) {
        let html = '<div class="content-info">';
        html += `<p><strong>Command:</strong> ${commandType}</p>`;

        if (data.rubric) {
            html += `<p><strong>Rubric:</strong> ${ModelParser.formatRubricName(data.rubric)}</p>`;
        }

        if (commandType === 'Score') {
            html += `<p><strong>Essay Type:</strong> ${data.essay_type || 'generate'}</p>`;
            html += `<p><strong>Writer Model:</strong> ${data.writer}</p>`;
            html += `<p><strong>Grader Model:</strong> ${data.grader}</p>`;
        } else {
            html += `<p><strong>Model:</strong> ${data.model}</p>`;
        }

        html += `<p><strong>Time:</strong> ${data.timestamp}</p>`;
        html += `<p><strong>Processing Time:</strong> ${data.time_minutes} minutes</p>`;
        html += '</div>';

        return html;
    }

    buildContentBox(commandType, data) {
        let html = '';

        if (commandType === 'Generate' || commandType === 'Tune') {
            html += '<div class="content-box">';
            html += '<h3>Essay Text</h3>';
            html += `<div class="essay-text" id="essayText">${this.formatText(data.result)}</div>`;
            html += '</div>';
        } else if (commandType === 'Score') {
            html += '<div class="content-box">';
            html += '<h3>Evaluation</h3>';
            html += `<div class="essay-text" id="evaluationText">${this.formatText(data.result)}</div>`;
            html += '</div>';

            if (data.scored_essay_text) {
                html += '<div class="content-box">';
                html += '<h3>Original Essay (Being Scored)</h3>';
                html += `<div class="essay-text" id="originalEssay">${this.formatText(data.scored_essay_text)}</div>`;
                html += '</div>';
            }
        }

        return html;
    }

    buildCopyButton(commandType) {
        if (commandType === 'Generate' || commandType === 'Tune') {
            return '<button class="copy-btn" onclick="app.copyEssayText()">📋 Copy Essay</button>';
        } else if (commandType === 'Score') {
            return '<button class="copy-btn" onclick="app.copyEvaluationText()">📋 Copy Evaluation</button>';
        }
        return '';
    }

    formatText(text) {
        return text
            .replace(/^#{1,6}\s+/gm, '')
            .replace(/\*\*(.+?)\*\*/g, '$1')
            .replace(/__(.+?)__/g, '$1')
            .replace(/\*(.+?)\*/g, '$1')
            .replace(/_(.+?)_/g, '$1')
            .replace(/^---+$/gm, '')
            .replace(/^[\*\-]\s+/gm, '')
            .replace(/\n/g, '<br>');
    }
}

/**
 * Application - Main app controller
 */
class Application {
    constructor() {
        this.dataManager = new DataManager();
        this.fileProcessor = new FileProcessor(this.dataManager);
        this.gitHubLoader = new GitHubLoader(this.dataManager);
        this.uiRenderer = new UIRenderer(this.dataManager);
        this.init();
    }

    init() {
        this.setupEventListeners();
    }

    setupEventListeners() {
        this.uiRenderer.elements.uploadBox.addEventListener('click', () => {
            this.uiRenderer.elements.fileInput.click();
        });

        this.uiRenderer.elements.fileInput.addEventListener('change', (e) => {
            this.handleLocalFileUpload(e.target.files);
        });

        this.uiRenderer.elements.uploadBox.addEventListener('dragover', (e) => {
            e.preventDefault();
            this.uiRenderer.elements.uploadBox.classList.add('drag-over');
        });

        this.uiRenderer.elements.uploadBox.addEventListener('dragleave', () => {
            this.uiRenderer.elements.uploadBox.classList.remove('drag-over');
        });

        this.uiRenderer.elements.uploadBox.addEventListener('drop', (e) => {
            e.preventDefault();
            this.uiRenderer.elements.uploadBox.classList.remove('drag-over');
            this.handleLocalFileUpload(e.dataTransfer.files);
        });

        this.uiRenderer.elements.githubBtn.addEventListener('click', () => {
            this.handleGitHubLoad();
        });
    }

    async handleLocalFileUpload(files) {
        try {
            const count = await this.fileProcessor.processLocalFiles(files);
            this.uiRenderer.setupFilters();
            this.uiRenderer.displayEssayList();
            this.uiRenderer.showNotification(`✓ ${count} files added!`);
        } catch (error) {
            alert(error);
        }
    }

    async handleGitHubLoad() {
        try {
            this.uiRenderer.showNotification('Loading files from GitHub...');
            const count = await this.gitHubLoader.loadFromGitHub();
            this.uiRenderer.setupFilters();
            this.uiRenderer.displayEssayList();
            this.uiRenderer.showNotification(`✓ Loaded ${count} files from GitHub!`);
        } catch (error) {
            alert(`Failed to load from GitHub: ${error.message}`);
        }
    }

    copyEssayText() {
        const text = document.getElementById('essayText').innerText;
        this.copyToClipboard(text);
    }

    copyEvaluationText() {
        const text = document.getElementById('evaluationText').innerText;
        this.copyToClipboard(text);
    }

    copyToClipboard(text) {
        navigator.clipboard.writeText(text).then(() => {
            alert('✓ Copied to clipboard!');
        }).catch(() => {
            alert('Failed to copy');
        });
    }
}

// ============================================
// Initialize App
// ============================================

const app = new Application();