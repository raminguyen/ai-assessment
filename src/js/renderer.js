class Renderer {
    constructor(dataManager) {
        this.dataManager = dataManager;
        this.elements = this.cache_elements();
        this.prompts = {};
        this.gradePrompt = '';
        this.load_prompts();
    }

    async load_prompts() {

    const response = await fetch('src/ai_assessment/prompt.json');

    if (!response.ok) {
        console.warn('Could not load prompt.json, using default prompts');
        this.set_default_prompts();
        return;
    }
    
    const data = await response.json();
    
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
    
    this.gradePrompt = data.grade_prompt || '';
    
    console.log('Prompts loaded successfully');
}

    set_default_prompts() {
        this.prompts = {
            'Assignment_1': "Let's write a 1000 word fully written college essa, plus at least 5 citations from peer-reviewed articles in the end of essay not embedded links, that answers this question: Consider the following problem: In the morning, when Professor Catlove opens a new can of cat food, his cats run into the kitchen purring and meowing and rubbing their backs against his legs. What examples, if any, of classical conditioning, operant conditioning, and social learning are at work in this brief scene? Note that both the cats and the professor might be exhibiting conditioned behavior here.",
            'Assignment_2': "Let's write a 1000 word fully written college essay, plus at least 5 citations from peer-reviewed articles, that answers this question. To what extent do the attached economic data support the hypothesis \"social service spending is inversely related to economic growth\"? Formulate a verbal argument analyzing whether the data do or do not support the hypothesis.",
            'Assignment_3': "Let's write a 1000 word fully written college essay, that includes a real estate investment market analysis in the Boston Metropolitan Area for 2024. Summarize the key findings, insights from the analysis, highlight the best real estate investment opportunities, and any significant patterns observed. Please include at least 5 citations from peer reviewed articles."
        };
        
        this.gradePrompt = "After grading the essay using the rubric, please explain how the essay was tuned to achieve a perfect score on the rubric. Add the total score at the end using this format: Total Score is [X]/[Y].";
    }

    cache_elements() {
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

    get_display_name(essayName) {
        if (!essayName) return 'Unknown';
        if (typeof essayName !== 'string') return 'Unknown';
        return essayName;
    }

    get_prompt_for_essay(essayName) {
        return this.prompts[essayName] || '';
    }

    get_grade_prompt() {
        return this.gradePrompt;
    }

    setup_filters() {
        this.elements.filters.style.display = 'block';
        this.populate_model_filter();
        this.populate_essay_filter();
        this.populate_rubric_filter();
        this.add_reset_button();
        this.attach_filter_listeners();
    }

    populate_model_filter() {
        this.elements.modelFilter.innerHTML = '<option value="all">All Models</option>';
        this.dataManager.get_models().forEach(model => {
            const option = document.createElement('option');
            option.value = model;
            option.textContent = model;
            this.elements.modelFilter.appendChild(option);
        });
        this.elements.modelFilter.value = 'all';
    }

    populate_essay_filter() {
        this.elements.essayFilter.innerHTML = '<option value="all">All Assignments</option>';
        const essayNames = new Set();
        Object.values(this.dataManager.allData).forEach(item => {
            essayNames.add(item.essayName);
        });

        Array.from(essayNames).sort().forEach(name => {
            const option = document.createElement('option');
            option.value = name;
            option.textContent = this.get_display_name(name);
            this.elements.essayFilter.appendChild(option);
        });
        this.elements.essayFilter.value = 'Assignment_1';
    }

    populate_rubric_filter() {
        this.elements.rubricFilter.innerHTML = '<option value="all">All Rubrics</option>';
        this.dataManager.get_rubrics().forEach(rubric => {
            const option = document.createElement('option');
            option.value = rubric;
            option.textContent = Parser.format_rubric_name(rubric);
            this.elements.rubricFilter.appendChild(option);
        });
        this.elements.rubricFilter.value = 'critical_thinking';
    }

    add_reset_button() {
        if (!document.getElementById('resetBtn')) {
            const resetBtn = document.createElement('button');
            resetBtn.id = 'resetBtn';
            resetBtn.className = 'copy-btn';
            resetBtn.style.cssText = 'width: 100%; margin-top: 1rem; background: rgba(255, 85, 85, 0.3);';
            resetBtn.innerHTML = '🔄 Reset Filters';
            resetBtn.onclick = () => this.reset_filters();
            this.elements.filters.appendChild(resetBtn);
        }
    }

    attach_filter_listeners() {
        if (!this.elements.filters.dataset.listening) {
            this.elements.essayFilter.addEventListener('change', () => this.apply_filters());
            this.elements.modelFilter.addEventListener('change', () => this.apply_filters());
            this.elements.rubricFilter.addEventListener('change', () => this.apply_filters());
            this.elements.filterGenerate.addEventListener('change', () => this.apply_filters());
            this.elements.filterTune.addEventListener('change', () => this.apply_filters());
            this.elements.filterScore.addEventListener('change', () => this.apply_filters());
            this.elements.filters.dataset.listening = 'true';
        }
    }

    reset_filters() {
        this.elements.modelFilter.value = 'all';
        this.elements.essayFilter.value = 'all';
        this.elements.rubricFilter.value = 'all';
        this.elements.filterGenerate.checked = true;
        this.elements.filterTune.checked = true;
        this.elements.filterScore.checked = true;
        this.apply_filters();
    }

    apply_filters() {
        this.display_essay_list();
    }

    display_essay_list() {
        this.elements.essayList.innerHTML = '';

        const filters = this.get_active_filters();
        const rubricGroups = this.group_data_by_filters(filters);

        if (Object.keys(rubricGroups).length === 0) {
            this.render_no_results();
            return;
        }

        this.render_summary(rubricGroups);
        this.render_rubric_groups(rubricGroups);
        this.update_right_panel_summary(rubricGroups, filters);
    }

    get_active_filters() {
        return {
            essay: this.elements.essayFilter.value,
            model: this.elements.modelFilter.value,
            rubric: this.elements.rubricFilter.value,
            showGenerate: this.elements.filterGenerate.checked,
            showTune: this.elements.filterTune.checked,
            showScore: this.elements.filterScore.checked
        };
    }

    group_data_by_filters(filters) {
        const rubricGroups = {};

        Object.entries(this.dataManager.allData).forEach(([key, item]) => {
            if (filters.essay !== 'all' && item.essayName !== filters.essay) return;
            if (filters.rubric !== 'all' && item.rubric !== filters.rubric) return;
            if (item.command === 'generate' && !filters.showGenerate) return;
            if (item.command === 'tune' && !filters.showTune) return;
            if (item.command === 'score' && !filters.showScore) return;

            let writerModel = item.modelName;
            if (item.command === 'score') {
                writerModel = Parser.get_model_name(item.data.writer);
            }
            
            if (filters.model !== 'all' && writerModel !== filters.model) return;

            if (!rubricGroups[item.rubric]) rubricGroups[item.rubric] = {};
            if (!rubricGroups[item.rubric][item.essayName]) rubricGroups[item.rubric][item.essayName] = {};
            if (!rubricGroups[item.rubric][item.essayName][writerModel]) {
                rubricGroups[item.rubric][item.essayName][writerModel] = {
                    generate: [],
                    tune: [],
                    generate_scores: [],
                    tune_scores: []
                };
            }

            if (item.command === 'generate') {
                rubricGroups[item.rubric][item.essayName][writerModel].generate.push(item);
            } else if (item.command === 'tune') {
                rubricGroups[item.rubric][item.essayName][writerModel].tune.push(item);
            } else if (item.command === 'score') {
                const essayType = item.data.essay_type || 'generate';
                const bucket = essayType === 'generate' ? 'generate_scores' : 'tune_scores';
                rubricGroups[item.rubric][item.essayName][writerModel][bucket].push(item);
            }
        });

        return rubricGroups;
    }

    render_summary(rubricGroups) {
        const template = document.getElementById('summaryTemplate');
        const summary = template.content.cloneNode(true);

        summary.querySelector('.total-count').textContent = this.dataManager.get_total_count();
        summary.querySelector('.rubrics-count').textContent = this.dataManager.allRubrics.size;
        summary.querySelector('.models-count').textContent = this.dataManager.allModels.size;

        this.elements.essayList.appendChild(summary);
    }

    render_rubric_groups(rubricGroups) {
        Object.keys(rubricGroups).sort().forEach(rubricName => {
            this.render_rubric_header(rubricName);
            this.render_essays_in_rubric(rubricGroups[rubricName], rubricName);
        });
    }

    render_rubric_header(rubricName) {
        const header = document.createElement('div');
        header.className = 'rubric-header';
        const { color, bgColor } = this.get_rubric_colors(rubricName);

        header.style.background = bgColor;
        header.style.color = color;
        header.style.borderLeftColor = color;
        header.textContent = `📋 ${Parser.format_rubric_name(rubricName)}`;

        this.elements.essayList.appendChild(header);
    }

    render_essays_in_rubric(essayGroups, rubricName) {
        Object.keys(essayGroups).sort().forEach(essayName => {
            const essayItem = document.createElement('div');
            essayItem.className = 'essay-item';

            const header = document.createElement('div');
            header.className = 'essay-header';
            header.textContent = this.get_display_name(essayName);
            essayItem.appendChild(header);

            const commands = document.createElement('div');
            commands.className = 'essay-commands';

            Object.keys(essayGroups[essayName]).sort().forEach(modelName => {
                this.render_model_section(commands, modelName, essayGroups[essayName][modelName]);
            });

            essayItem.appendChild(commands);
            this.elements.essayList.appendChild(essayItem);
        });
    }

    render_model_section(container, modelName, items) {
        const modelHeader = document.createElement('div');
        modelHeader.className = 'model-header';
        modelHeader.textContent = ` ${modelName}`;
        container.appendChild(modelHeader);

        items.generate.forEach(item => {
            container.appendChild(this.create_command_element('Generate', item.data));
        });

        items.generate_scores.forEach(item => {
            const el = this.create_command_element('Score', item.data);
            el.style.marginLeft = '1.5rem';
            container.appendChild(el);
        });

        items.tune.forEach(item => {
            container.appendChild(this.create_command_element('Tune', item.data));
        });

        items.tune_scores.forEach(item => {
            const el = this.create_command_element('Score', item.data);
            el.style.marginLeft = '1.5rem';
            container.appendChild(el);
        });
    }
    create_command_element(command, data) {
        const item = document.createElement('div');
        item.className = 'command-item';

        let label = `    ${command}`;

        if (command === 'Score') {
            const essayType = data.essay_type || 'generate';
            const graderName = Parser.get_model_name(data.grader);
            const essayTypeCapitalized = essayType.charAt(0).toUpperCase() + essayType.slice(1);
            label = `        ${essayTypeCapitalized} Essay (by ${graderName})`;
        }

        item.textContent = label;
        item.addEventListener('click', (event) => this.show_content_detail(event, command, data));

        return item;
    }

    show_content_detail(event, commandType, data) {
        const allItems = document.querySelectorAll('.command-item');
        allItems.forEach(item => item.classList.remove('active'));
        event.target.closest('.command-item').classList.add('active');

        const contentRenderer = new Content(this.elements.rightPanel);
        contentRenderer.render(commandType, data, this.gradePrompt);
    }

    render_no_results() {
        const listTemplate = document.getElementById('noResultsTemplate');
        const panelTemplate = document.getElementById('noResultsPanelTemplate');

        this.elements.essayList.innerHTML = '';
        this.elements.essayList.appendChild(listTemplate.content.cloneNode(true));

        this.elements.rightPanel.innerHTML = '';
        this.elements.rightPanel.appendChild(panelTemplate.content.cloneNode(true));
    }

    update_right_panel_summary(rubricGroups, filters) {
        this.elements.rightPanel.innerHTML = '';

        const title = document.createElement('h2');
        title.textContent = ' Filter Summary';
        this.elements.rightPanel.appendChild(title);

        const filterInfo = this.create_filter_info(filters);
        this.elements.rightPanel.appendChild(filterInfo);

        if (filters.essay !== 'all') {
            this.add_prompt_boxes(filters.essay);
        }

        this.add_tip_box();
        this.add_separator();
    }

    create_filter_info(filters) {
        const filterDiv = document.createElement('div');
        filterDiv.className = 'content-info';
        filterDiv.style.background = 'rgba(255, 255, 255, 0.05)';
        filterDiv.style.borderLeft = '4px solid var(--rami-highlight)';

        const title = document.createElement('p');
        const strong = document.createElement('strong');
        strong.textContent = 'Active Filters:';
        title.appendChild(strong);
        filterDiv.appendChild(title);

        if (filters.essay !== 'all') {
            filterDiv.appendChild(this.create_filter_item(' Assignment:', this.get_display_name(filters.essay)));
        }
        if (filters.model !== 'all') {
            filterDiv.appendChild(this.create_filter_item(' Model:', filters.model));
        }
        if (filters.rubric !== 'all') {
            filterDiv.appendChild(this.create_filter_item(' Rubric:', Parser.format_rubric_name(filters.rubric)));
        }

        const commands = [];
        if (filters.showGenerate) commands.push('Generate');
        if (filters.showTune) commands.push('Tune');
        if (filters.showScore) commands.push('Score');
        if (commands.length > 0 && commands.length < 3) {
            filterDiv.appendChild(this.create_filter_item('⚙️ Commands:', commands.join(', ')));
        }

        return filterDiv;
    }

    create_filter_item(label, value) {
        const p = document.createElement('p');
        p.style.margin = '0.5rem 0';
        p.style.paddingLeft = '1rem';
        p.textContent = label + ' ';

        const strong = document.createElement('strong');
        strong.textContent = value;
        p.appendChild(strong);

        return p;
    }

    add_prompt_boxes(essayName) {
        const assignmentPrompt = this.get_prompt_for_essay(essayName);
        const gradePrompt = this.get_grade_prompt();

        if (assignmentPrompt) {
            const box = this.create_prompt_box(' Assignment Prompt', assignmentPrompt);
            this.elements.rightPanel.appendChild(box);
        }

        if (gradePrompt) {
            const box = this.create_prompt_box(' ✅ Grading Prompt', gradePrompt);
            this.elements.rightPanel.appendChild(box);
        }
    }

    create_prompt_box(title, content) {
        const box = document.createElement('div');
        box.className = 'content-box prompt-box';

        const h3 = document.createElement('h3');
        h3.textContent = title;
        box.appendChild(h3);

        const promptText = document.createElement('div');
        promptText.className = 'prompt-text';
        promptText.textContent = content;
        box.appendChild(promptText);

        return box;
    }

    add_tip_box() {
        const tipBox = document.createElement('div');
        tipBox.className = 'content-box';

        const h3 = document.createElement('h3');
        h3.textContent = ' Tip';
        tipBox.appendChild(h3);

        const p = document.createElement('p');
        p.textContent = 'Click on any item in the left panel to view its full content below.';
        tipBox.appendChild(p);

        this.elements.rightPanel.appendChild(tipBox);
    }

    add_separator() {
        const hr = document.createElement('hr');
        hr.style.border = '1px solid rgba(85, 255, 221, 0.2)';
        hr.style.margin = '2rem 0';
        this.elements.rightPanel.appendChild(hr);
    }

    get_rubric_colors(rubricName) {
        const colors = {
            critical_thinking: { color: '#ffffff', bgColor: 'rgba(3, 98, 76, 0.15)' },
            oral_communication: { color: '#2CC295', bgColor: 'rgba(44, 194, 149, 0.15)' }
        };
        return colors[rubricName] || { color: '#24ff02', bgColor: 'rgba(36, 255, 2, 0.15)' };
    }

    show_notification(message) {
        const template = document.getElementById('notificationTemplate');
        const notif = template.content.cloneNode(true).querySelector('.notification');

        notif.textContent = message;
        document.body.appendChild(notif);

        setTimeout(() => {
            if (document.body.contains(notif)) {
                document.body.removeChild(notif);
            }
        }, 3000);
    }
}