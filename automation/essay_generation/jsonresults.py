import os, json, re

def save_result_as_json(result, filename="final_result.json", provider=None, essay_number=None):
    """
    Save agent result into a folder named after the provider (chatgpt, gemini, claude, copilot).
    """

    if essay_number:
        base_dir = os.path.join(os.getcwd(), f"tuned_essay_{essay_number}")
    else:
        base_dir = os.path.join(os.getcwd(), "default_tuned_essay")

    provider_folder = provider if provider else "default"

    save_dir = os.path.join(base_dir, provider_folder)

    os.makedirs(save_dir, exist_ok=True)

    # Full path for JSON file
    save_path = os.path.join(save_dir, filename)

    # Convert model outputs into serializable JSON
    serializable = [
        r.model_dump(exclude_none=True) if hasattr(r, "model_dump") else str(r)
        for r in result
    ]

    # 4️⃣ Save the full result
    with open(save_path, "w", encoding="utf-8") as f:
        json.dump(serializable, f, ensure_ascii=False, indent=2)
    print(f"✅ Results saved to: {save_path}")

    # 5️⃣ Extract last <result> block and save as final_extracted.json
    for item in reversed(serializable):
        if isinstance(item, dict) and "extracted_content" in item and "<result>" in item["extracted_content"]:
            match = re.search(r"<result>(.*?)</result>", item["extracted_content"], re.DOTALL)
            
            if match:
                result_text = match.group(1).strip()
                extracted_path = os.path.join(save_dir, "final_extracted.json")
                with open(extracted_path, "w", encoding="utf-8") as f:
                    json.dump({"result": result_text}, f, ensure_ascii=False, indent=2)
                print(f"✅ Extracted result saved to: {extracted_path}")

                break
            
    for item in reversed(serializable):  # Iterate in reverse order
        if isinstance(item, dict) and "long_term_memory" in item:
            # Modify regex to capture a link with a number
            match = re.search(r"(https?://\S*\d\S*)", item["long_term_memory"])

            if match:
                link = match.group(1)
                
                # Path to save the extracted link
                link_path = os.path.join(save_dir, "extracted_link.json")

                # Save the extracted link in the desired format
                with open(link_path, "w", encoding="utf-8") as f:
                    json.dump({"extracted_link": link}, f, ensure_ascii=False, indent=2)

                print(f"✅ Link extracted and saved to: {link_path}")
                break

    #6:Extract link from this
    return save_path

