let allData = {};
let allModels = new Set();
let allRubrics = new Set();

function addData(essayName, modelName, command, rubric, data, fileName) {
    let uniqueName;
    const testMatch = fileName.match(/_test(\\d+)/);
    const testNumber = testMatch ? testMatch[1] : '1'; // Default to '1' if not found

    if (command === 'score') {
        const essayType = data.essay_type || 'unknown';
        const grader = data.grader || 'unknown';
        uniqueName = essayName + '_' + modelName + '_' + command + '_' + essayType + '_' + grader + '_' + rubric + '_test' + testNumber;
    } else {
        uniqueName = essayName + '_' + modelName + '_' + command + '_' + rubric + '_test' + testNumber;
    }

    allData[uniqueName] = {
        essayName: essayName,
        modelName: modelName,
        command: command,
        rubric: rubric,
        data: data,
        fileName: fileName,
        testNumber: testNumber
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
