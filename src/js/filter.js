let currentAssignment = 'a1';

function getCurrentAssignment() {
    return currentAssignment;
}

function setCurrentAssignment(assignment) {
    currentAssignment = assignment;
}

function setupFilterButtons() {
    const filterButtons = document.querySelectorAll('.filter-btn');
    filterButtons.forEach(button => {
        button.addEventListener('click', function() {
            handleFilterClick(this);
        });
    });
}

function handleFilterClick(button) {
    const assignment = button.getAttribute('data-assignment');

    document.querySelectorAll('.filter-btn').forEach(btn => {
        btn.classList.remove('active');
    });

    button.classList.add('active');
    currentAssignment = assignment;
    console.log('Filter:', assignment);

    document.querySelectorAll('.action-btn').forEach(btn => {
        btn.classList.remove('active');
    });

    showNoData();
}

function findDataItem(model, type) {
    const modelMap = {
        'chatgpt': 'ChatGPT',
        'gemini': 'Gemini',
        'claude': 'Claude',
        'grok': 'Grok'
    };

    const typeMap = {
        'generation': 'generate',
        'tuning': 'tune',
        'reflection': 'reflection',
        'score': 'score'
    };

    const modelName = modelMap[model];
    const command = typeMap[type];

    const assignmentMap = {
        'a1': 'Assignment_1',
        'a2': 'Assignment_2',
        'a3': 'Assignment_3'
    };

    const essayName = assignmentMap[currentAssignment] || 'Assignment_1';

    const allItems = Object.values(getData());

    const matches = allItems.filter(item => {
        return item.modelName === modelName &&
               item.command === command &&
               item.essayName === essayName &&
               item.rubric === 'critical_thinking';
    });

    return matches.length > 0 ? matches[0] : null;
}
