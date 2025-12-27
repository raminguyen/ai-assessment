// Process one essay and add it to storage
function processData(data, folderName) {
    // Get basic info from essay data
    const essayName = data.essay_name;
    const command = data.command;
    const rubric = data.folder || data.rubric || folderName || 'unknown';

    // Add rubric to our list
    allRubrics.add(rubric);

    // Figure out which AI model wrote this
    let modelName;
    if (command === 'score') {
        modelName = getModelName(data.writer);
    } else {
        modelName = getModelName(data.model);
    }

    // Store the essay in our data box
    addData(essayName, modelName, command, rubric, data);
}