let allData = {};
let allModels = new Set();
let allRubrics = new Set();

function addData(essayName, modelName, command, rubric, data, fileName) {
    let uniqueName;

    // Check for _p1, _p2 pattern first, then fall back to _test pattern
    const promptMatch = fileName.match(/_p(\d+)/);
    const testMatch = fileName.match(/_test(\d+)/);
    const testNumber = promptMatch ? promptMatch[1] : (testMatch ? testMatch[1] : '1');

    if (command === 'score') {
        const essayType = data.essay_type || 'unknown';
        const grader = data.grader || 'unknown';
        uniqueName = essayName + '_' + modelName + '_' + command + '_' + essayType + '_' + grader + '_' + rubric + '_p' + testNumber;
    } else {
        uniqueName = essayName + '_' + modelName + '_' + command + '_' + rubric + '_p' + testNumber;
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
