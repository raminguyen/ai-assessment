// Storage boxes for all essays
let allData = {};
let allModels = new Set();
let allRubrics = new Set();

// Add an essay to storage
function addData(essayName, modelName, command, rubric, data) {
    // Make a unique name for this essay
    // For scores, include essay_type and grader to avoid collisions
    let uniqueName;
    if (command === 'score') {
        const essayType = data.essay_type || 'unknown';
        const grader = data.grader || 'unknown';
        uniqueName = essayName + '_' + modelName + '_' + command + '_' + essayType + '_' + grader + '_' + rubric;
    } else {
        uniqueName = essayName + '_' + modelName + '_' + command + '_' + rubric;
    }

    // Store the essay
    allData[uniqueName] = {
        essayName: essayName,
        modelName: modelName,
        command: command,
        rubric: rubric,
        data: data
    };

    // Remember this model and rubric
    allModels.add(modelName);
    allRubrics.add(rubric);
}

// Get all essays
function getData() {
    return allData;
}

// Get list of all AI models (sorted A-Z)
function getModels() {
    return Array.from(allModels).sort();
}

// Get list of all rubric types (sorted A-Z)
function getRubrics() {
    return Array.from(allRubrics).sort();
}

// Empty all storage boxes
function clearData() {
    allData = {};
    allModels.clear();
    allRubrics.clear();
}

// Count how many essays we have
function getTotalCount() {
    return Object.keys(allData).length;
}
