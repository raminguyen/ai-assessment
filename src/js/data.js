let allData = {};
let allModels = new Set();
let allRubrics = new Set();

function addData(essayName, modelName, command, rubric, data, fileName) {
    let uniqueName;
    if (command === 'score') {
        const essayType = data.essay_type || 'unknown';
        const grader = data.grader || 'unknown';
        uniqueName = essayName + '_' + modelName + '_' + command + '_' + essayType + '_' + grader + '_' + rubric;
    } else {
        uniqueName = essayName + '_' + modelName + '_' + command + '_' + rubric;
    }

    allData[uniqueName] = {
        essayName: essayName,
        modelName: modelName,
        command: command,
        rubric: rubric,
        data: data,
        fileName: fileName
    };

    allModels.add(modelName);
    allRubrics.add(rubric);
}

function getData() {
    return allData;
}

function getModels() {
    return Array.from(allModels).sort();
}

function getRubrics() {
    return Array.from(allRubrics).sort();
}

function clearData() {
    allData = {};
    allModels.clear();
    allRubrics.clear();
}

function getTotalCount() {
    return Object.keys(allData).length;
}
