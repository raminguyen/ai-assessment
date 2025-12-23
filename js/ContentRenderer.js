/**
 * ContentRenderer - Renders essay content in the right panel
 * Handles building and formatting of content HTML
 */
class ContentRenderer {
    /**
     * Initialize ContentRenderer
     * @param {HTMLElement} rightPanel - Reference to right panel element
     */
    constructor(rightPanel) {
        this.rightPanel = rightPanel;
    }

    /**
     * Render content in right panel
     * @param {string} commandType - Type of command (Generate/Tune/Score)
     * @param {object} data - Essay data object
     * @param {string} gradePrompt - Grade prompt from UIRenderer
     */
    render(commandType, data, gradePrompt = '') {
        const html = this.buildHTML(commandType, data, gradePrompt);
        this.rightPanel.innerHTML = html;

        // Smooth scroll to top
        const contentStart = this.rightPanel.querySelector('h2:last-of-type');
        if (contentStart) {
            contentStart.scrollIntoView({ behavior: 'smooth', block: 'start' });
        }
    }
        /**
     * Build complete HTML for content
     * @private
     * @returns {string} HTML string
     */
    buildHTML(commandType, data, gradePrompt = '') {
        let html = `<h2>${data.essay_name}</h2>`;

        html += this.buildInfoBox(commandType, data);
        html += this.buildContentBox(commandType, data, gradePrompt);
        html += this.buildCopyButton(commandType);

        return html;
    }

     /**
     * Build content box with essay or score
     * @private
     */
    buildContentBox(commandType, data, gradePrompt = '') {
        let html = '';

        if (commandType === 'Generate') {
            // Generate: Show ONLY prompt
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
            // Tune: Show ONLY prompt and rubric
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
            // Score: Show assignment prompt and rubric (grading prompt)
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

    /**
     * Build rubric link button
     * @private
     */
    buildRubricLink(rubric) {
        const rubricLinks = {
            'critical_thinking': 'https://chsu.edu/wp-content/uploads/CriticalThinking.pdf',
            'oral_communication': 'https://assessment.unc.edu/wp-content/uploads/sites/1284/2022/08/AACU_OC_ValueRubric.pdf'
        };

        const url = rubricLinks[rubric] || 'https://www.aacu.org/value/rubrics';
        const rubricName = ModelParser.formatRubricName(rubric);
        
        return ' <a href="' + url + '" target="_blank" style="color: #55ffdd; text-decoration: underline; cursor: pointer;">' +
            'view full version here' +
            '</a>';
    }
    /**
     * Build info box with metadata
     * @private
     */
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

   
    
        /**
     * Build copy button
     * @private
     */
    buildCopyButton(commandType) {
        if (commandType === 'Generate' || commandType === 'Tune') {
            return '<button class="copy-btn" onclick="app.copyEssayText()">📋 Copy Essay</button>';
        } else if (commandType === 'Score') {
            return '<button class="copy-btn" onclick="app.copyEvaluationText()">📋 Copy Evaluation</button>';
        }
        return '';
    }

    /**
     * Format text by removing markdown
     * @private
     * @param {string} text - Text to format
     * @returns {string} Formatted text with HTML
     */
    formatText(text) {
        return text
            .replace(/^#{1,6}\s+/gm, '')           // Remove markdown headers
            .replace(/\*\*(.+?)\*\*/g, '$1')       // Remove bold (**text**)
            .replace(/__(.+?)__/g, '$1')           // Remove bold (__text__)
            .replace(/\*(.+?)\*/g, '$1')           // Remove italic (*text*)
            .replace(/_(.+?)_/g, '$1')             // Remove italic (_text_)
            .replace(/^---+$/gm, '')               // Remove horizontal rules
            .replace(/^[\*\-]\s+/gm, '')           // Remove bullet points
            .replace(/\n/g, '<br>');               // Convert newlines to <br>
    }
}