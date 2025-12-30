function processData(data, folderName, fileName) {
    const essayName = data.essay_name;
    const command = data.command;
    const rubric = data.folder || data.rubric || folderName || 'unknown';

    allRubrics.add(rubric);

    let modelName;
    if (command === 'score' || command === 'reflection') {
        modelName = getModelName(data.writer);
    } else {
        modelName = getModelName(data.model);
    }

    addData(essayName, modelName, command, rubric, data, fileName);
}