import os, json, re

def save_result_as_json(result, filename="final_result.json"):
    save_path = os.path.join(os.getcwd(), filename)

    serializable = [
        r.model_dump(exclude_none=True) if hasattr(r, "model_dump") else str(r)
        for r in result
    ]

    # Save full result
    with open(save_path, "w", encoding="utf-8") as f:
        json.dump(serializable, f, ensure_ascii=False, indent=2)
    print(f"✅ Results saved to: {save_path}")

    # Extract last <result> block and save separately
    for item in reversed(serializable):
        if isinstance(item, dict) and "extracted_content" in item and "<result>" in item["extracted_content"]:
            match = re.search(r"<result>(.*?)</result>", item["extracted_content"], re.DOTALL)
            if match:
                result_text = match.group(1).strip()
                with open("final_extracted.json", "w", encoding="utf-8") as f:
                    json.dump({"result": result_text}, f, ensure_ascii=False, indent=2)
                print("✅ Saved final_extracted.json")
                break

    return save_path
