// SIMPLE VERSION - Show essay on screen
function renderContent(rightPanel, commandType, data, gradePrompt = '') {
    // Step 1: Create the HTML
    let html = '';

    // Add title
    html += '<h2>' + data.essay_name + '</h2>';

    // Add info section
    html += '<div class="content-info">';
    html += '<p><strong>Command:</strong> ' + commandType + '</p>';
    html += '<p><strong>Model:</strong> ' + (data.model || data.writer) + '</p>';
    html += '<p><strong>Time:</strong> ' + data.timestamp + '</p>';
    html += '</div>';

    // Add essay or evaluation
    if (data.prompt) {
        html += '<div class="content-box prompt-box">';
        html += '<h3>Prompt</h3>';
        html += '<div class="prompt-text">' + data.prompt + '</div>';
        html += '</div>';
    }

    html += '<div class="content-box">';
    html += '<h3>' + (commandType === 'Score' ? 'Evaluation' : 'Essay Text') + '</h3>';
    html += '<div class="essay-text">' + data.result + '</div>';
    html += '</div>';

    // Add copy button
    html += '<button class="copy-btn" onclick="copyEssayText()">Copy</button>';

    // Step 2: Put HTML on the page
    rightPanel.innerHTML = html;

    // Step 3: Scroll to top
    rightPanel.scrollIntoView({ behavior: 'smooth' });
}

// Copy the essay text
function copyEssayText() {
    const text = document.querySelector('.essay-text').textContent;
    navigator.clipboard.writeText(text);
    alert('Copied!');
}

// Remove markdown formatting from text
function removeMarkdown(text) {
    if (!text) return '';

    return text
        // Remove headers (### Header -> Header)
        .replace(/^#{1,6}\s+(.+)$/gm, '$1')
        // Remove bold (**text** or __text__ -> text)
        .replace(/(\*\*|__)(.*?)\1/g, '$2')
        // Remove italic (*text* or _text_ -> text)
        .replace(/(\*|_)(.*?)\1/g, '$2')
        // Remove inline code (`code` -> code)
        .replace(/`([^`]+)`/g, '$1')
        // Remove links ([text](url) -> text)
        .replace(/\[([^\]]+)\]\([^\)]+\)/g, '$1')
        // Remove bullet points (- item -> item)
        .replace(/^[\*\-\+]\s+/gm, '')
        // Remove numbered lists (1. item -> item)
        .replace(/^\d+\.\s+/gm, '')
        // Remove blockquotes (> quote -> quote)
        .replace(/^>\s+/gm, '')
        // Remove horizontal rules (---, ***, ___ -> empty)
        .replace(/^[\-\*\_]{3,}$/gm, '')
        // Remove code blocks (```code``` -> code)
        .replace(/```[\s\S]*?```/g, match => {
            return match.replace(/```\w*\n?/g, '').trim();
        })
        // Clean up extra whitespace
        .replace(/\n{3,}/g, '\n\n')
        .trim();
}
