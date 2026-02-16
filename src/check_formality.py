import os
import json
import re
import glob
import csv
import pandas as pd

def get_informal_data(text):
    if not text:
        return False, "", ""
        
    text_lower = text.lower()
    
    # TRUNCATE BEFORE REFERENCES
    ref_headers = [
        r'(?m)^#*\s*references',
        r'(?m)^#*\s*bibliography',
        r'(?m)^#*\s*works cited',
        r'(?m)^#*\s*peer-reviewed references(\s*\(cited\))?',
        r'(?m)^#*\s*citations',
    ]
    
    clean_text = text
    clean_text_lower = text_lower
    for pattern in ref_headers:
        match = re.search(pattern, text_lower)
        if match:
            clean_text = text[:match.start()]
            clean_text_lower = text_lower[:match.start()]
            break
    
    # Pronouns
    # First person: Exclude 'i' when used as roman numeral (i), initial (i.), or range (i-)
    first_person = [r'(?<!\()\bi\b(?![.\-\u2013)\)])', r'\bmyself\b', r'\bmy\b', r'\bmine\b']
    # Second person
    second_person = [r'\byou\b', r'\byour\b', r'\byours\b']
    
    # Step keywords / Enumerations
    steps = [r'\bstep 1\b', r'\bstep 2\b']

    # Remove placeholders and quoted assignment text before checking
    exclude_patterns = [
        r'\[your name\]',
        r'fine,?\s*fine,?\s*i\'ll feed you now',
        r'i like this greeting,?\s*so i keep doing it',
        r'when would you \*?not\*? need social learning to explain the scene\??\*?',
        r'i can\'t literally .?think step-by-step.? in the sense of revealing private internal reasoning,?\s*but i \*?can\*? present a clear,?\s*structured,?\s*evidence-based analysis with the logic made explicit\.?',
    ]
    for pat in exclude_patterns:
        clean_text_lower = re.sub(pat, '', clean_text_lower)
        clean_text = re.sub(pat, '', clean_text, flags=re.IGNORECASE)

    combined_pattern = '|'.join(first_person + second_person + steps)
    
    matches = list(re.finditer(combined_pattern, clean_text_lower))
    
    if not matches:
        return False, "", ""
        
    evidences = []
    found_keywords = []
    
    for match in matches:
        start_idx = match.start()
        end_idx = match.end()
        
        # Approximate sentence extraction
        sent_start = max(0, clean_text.rfind('.', 0, start_idx) + 1)
        sent_end = clean_text.find('.', end_idx)
        if sent_end == -1:
            sent_end = len(clean_text)
        else:
            sent_end += 1
            
        sentence = clean_text[sent_start:sent_end].strip().replace('\n', ' ')
        
        # Store unique sentence-keyword pairs to avoid duplicates
        # But since we want lists that align (or just unique lists), let's just collect unique sentences
        # and unique keywords found in the text.
        
        if sentence and sentence not in evidences:
            evidences.append(sentence)
        
        # Capture the actual matched word
        matched_word = match.group(0)
        if matched_word not in found_keywords:
            found_keywords.append(matched_word)
            
    return True, ", ".join(found_keywords), " | ".join(evidences)

def main():
    assignments = [1, 2, 3]
    models = ['chatgpt', 'claude', 'gemini', 'grok']
    prompts = range(1, 8)

    base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    data_dir = os.path.join(base_dir, 'data', 'critical_thinking')
    if not os.path.exists(data_dir):
        data_dir = os.path.join('data', 'critical_thinking')

    results = {} # (a, m, p) -> (is_informal, keywords, evidence)
    files = glob.glob(os.path.join(data_dir, 'a*_gen_*.json'))

    for filepath in files:
        filename = os.path.basename(filepath)
        match = re.match(r'a(\d+)_gen_([a-z]+)_p(\d+)\.json', filename)
        
        if match:
            a_num = int(match.group(1))
            m_name = match.group(2)
            p_num = int(match.group(3))
            
            try:
                with open(filepath, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    text_to_check = data.get('result', '')
                    results[(a_num, m_name, p_num)] = get_informal_data(text_to_check)
            except Exception:
                pass

    # Write combined results to CSV with evidence
    evidence_csv = 'formality_results_with_evidence.csv'
    with open(evidence_csv, 'w', newline='', encoding='utf-8') as csvfile:
        writer = csv.writer(csvfile)
        writer.writerow(['Assignment', 'Model', 'Prompt', 'Is Informal', 'Matched Keywords', 'Exact Sentence'])
        
        for a in assignments:
            for m in models:
                for p in prompts:
                    is_inf, keywords, evidence = results.get((a, m, p), (None, "", ""))
                    if is_inf is None:
                        continue
                    status = 'x' if is_inf else ' '
                    writer.writerow([f'Assignment {a}', m, f'p{p}', status, keywords, evidence])
    
    print(f"Detailed results with evidence written to {evidence_csv}")

    # Write summary table to CSV
    summary_csv = 'formality_check_results.csv'
    with open(summary_csv, 'w', newline='', encoding='utf-8') as csvfile:
        writer = csv.writer(csvfile)
        
        # Header row
        header = ['Assignment', 'Model'] + [f'p{p}' for p in prompts]
        writer.writerow(header)
        
        # Initialize counts
        counts = {p: 0 for p in prompts}
        
        for a in assignments:
            for m in models:
                row = [f'Assignment {a}', m]
                for p in prompts:
                    is_inf, _, _ = results.get((a, m, p), (False, "", ""))
                    val = 'x' if is_inf else ' '
                    row.append(val)
                    if is_inf:
                        counts[p] += 1
                writer.writerow(row)
        
        # Add total row
        total_row = ['Total Informal Essay', '']
        for p in prompts:
            total_row.append(str(counts[p]))
        writer.writerow(total_row)

    print(f"Summary results written to {summary_csv}")

    # Write Excel file with both sheets
    excel_file = 'formality_results.xlsx'

    df_evidence = pd.read_csv(evidence_csv)

    df_summary = pd.read_csv(summary_csv)

    with pd.ExcelWriter(excel_file, engine='openpyxl') as writer:

        df_evidence.to_excel(writer, sheet_name='Evidence', index=False)

        df_summary.to_excel(writer, sheet_name='Summary', index=False)
    print(f"Excel results written to {excel_file}")

if __name__ == "__main__":
    main()
