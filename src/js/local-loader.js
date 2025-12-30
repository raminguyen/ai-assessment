async function loadFromLocal() {
    const folder = 'critical_thinking';
    const localBasePath = 'data/' + folder + '/';
    let totalLoaded = 0;

    const filesToTry = [
        'a1_gen_chatgpt.json',
        'a1_gen_chatgpt_score_claude.json',
        'a1_gen_chatgpt_score_gemini.json',
        'a1_gen_chatgpt_score_grok.json',
        'a1_gen_gemini.json',
        'a1_gen_gemini_score_chatgpt.json',
        'a1_gen_gemini_score_claude.json',
        'a1_gen_gemini_score_grok.json',
        'a1_reflection_chatgpt.json',
        'a1_reflection_gemini.json',
        'a1_tune_chatgpt.json',
        'a1_tune_chatgpt_score_claude.json',
        'a1_tune_chatgpt_score_gemini.json',
        'a1_tune_chatgpt_score_grok.json',
        'a1_tune_gemini.json',
        'a1_tune_gemini_score_chatgpt.json',
        'a1_tune_gemini_score_claude.json',
        'a1_tune_gemini_score_grok.json',
        'a2_gen_chatgpt.json',
        'a2_gen_chatgpt_score_claude.json',
        'a2_gen_chatgpt_score_gemini.json',
        'a2_gen_chatgpt_score_grok.json',
        'a2_reflection_chatgpt.json',
        'a2_tune_chatgpt.json',
        'a2_tune_chatgpt_score_claude.json',
        'a2_tune_chatgpt_score_gemini.json',
        'a2_tune_chatgpt_score_grok.json',
        'a3_gen_chatgpt.json',
        'a3_gen_chatgpt_score_claude.json',
        'a3_gen_chatgpt_score_gemini.json',
        'a3_gen_chatgpt_score_grok.json',
        'a3_reflection_chatgpt.json',
        'a3_tune_chatgpt.json',
        'a3_tune_chatgpt_score_claude.json',
        'a3_tune_chatgpt_score_gemini.json',
        'a3_tune_chatgpt_score_grok.json'
    ];

    for (const fileName of filesToTry) {
        try {
            const fileResponse = await fetch(localBasePath + fileName);

            if (fileResponse.ok) {
                const fileText = await fileResponse.text();
                const data = JSON.parse(fileText);

                processData(data, folder, fileName);
                totalLoaded++;
            }
        } catch (error) {}
    }

    return totalLoaded;
}
