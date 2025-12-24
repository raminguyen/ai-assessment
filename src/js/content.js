class Content {
    constructor(rightPanel) {
        this.rightPanel = rightPanel;
    }

    render(commandType, data, gradePrompt = '') {
        const html = this.buildHTML(commandType, data, gradePrompt);
        this.rightPanel.innerHTML = html;

        const contentStart = this.rightPanel.querySelector('h2:last-of-type');
        if (contentStart) {
            contentStart.scrollIntoView({ behavior: 'smooth', block: 'start' });
        }
    }

    buildHTML(commandType, data, gradePrompt = '') {
        let html = `<h2>${data.essay_name}</h2>`;
        html += this.buildInfoBox(commandType, data);
        html += this.buildContentBox(commandType, data, gradePrompt);
        html += this.buildCopyButton(commandType);
        return html;
    }

    buildContentBox(commandType, data, gradePrompt = '') {
        let html = '';

        if (commandType === 'Generate') {
            if (data.prompt) {
                html += '<div class="content-box prompt-box">';
                html += '<h3>📝 Prompt</h3>';
                html += `<div class="prompt-text">${this.formatText(data.prompt)}</div>`;
                html += '</div>';
            }
            
            html += '<div class="content-box">';
            html += '<h3>Essay Text</h3>';
            html += `<div class="essay-text" id="essayText">${this.formatText(data.result)}</div>`;
            html += '</div>';

        } else if (commandType === 'Tune') {
            if (data.prompt) {
                html += '<div class="content-box prompt-box">';
                html += '<h3>Prompt</h3>';
                html += `<div class="prompt-text">${this.formatText(data.prompt)}</div>`;
                html += '</div>';
            }

            if (data.rubric) {
                html += '<div class="content-box prompt-box">';
                html += '<h3>✅ Rubric Type</h3>';
                html += `<div class="prompt-text">${ModelParser.formatRubricName(data.rubric)}${this.buildRubricLink(data.rubric)}</div>`;
                html += '</div>';
            }
            
            html += '<div class="content-box">';
            html += '<h3>Essay Text</h3>';
            html += `<div class="essay-text" id="essayText">${this.formatText(data.result)}</div>`;
            html += '</div>';

        } else if (commandType === 'Score') {
            if (data.prompt) {
                html += '<div class="content-box prompt-box">';
                html += '<h3>📝 Assignment Prompt</h3>';
                html += `<div class="prompt-text">${this.formatText(data.prompt)}</div>`;
                html += '</div>';
            }

            if (data.rubric) {
                html += '<div class="content-box prompt-box">';
                html += '<h3>✅ Rubric Type</h3>';
                html += `<div class="prompt-text">${ModelParser.formatRubricName(data.rubric)}${this.buildRubricLink(data.rubric)}</div>`;
                html += '</div>';
            }

            if (gradePrompt) {
                html += '<div class="content-box prompt-box">';
                html += '<h3>✅ Grading Rubric</h3>';
                html += `<div class="prompt-text">${this.formatText(gradePrompt)}</div>`;
                html += '</div>';
            }

            html += '<div class="content-box">';
            html += '<h3>Evaluation</h3>';
            html += `<div class="essay-text" id="evaluationText">${this.formatText(data.result)}</div>`;
            html += '</div>';
        }

        return html;
    }

    buildRubricLink(rubric) {
        const rubricLinks = {
            'critical_thinking': 'https://chsu.edu/wp-content/uploads/CriticalThinking.pdf',
            'oral_communication': 'https://assessment.unc.edu/wp-content/uploads/sites/1284/2022/08/AACU_OC_ValueRubric.pdf'
        };

        const url = rubricLinks[rubric] || 'https://www.aacu.org/value/rubrics';
        
        return ' <a href="' + url + '" target="_blank" style="color: #55ffdd; text-decoration: underline; cursor: pointer;">view full version here</a>';
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