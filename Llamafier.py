import json
import requests
import datetime
import os
import time
import sys

def get_canonical_refs(ref_string):
  
    if not ref_string:
        return None

   
    if ":" not in ref_string:
        ref_to_check = f"{ref_string}:1"
    else:
        ref_to_check = ref_string

    api_ref = ref_to_check.replace(" ", "_")

    try:
        url = f"https://www.sefaria.org/api/texts/{api_ref}?context=0"
        response = requests.get(url)
        
        if response.status_code != 200:
            print(f"    ⚠️  API Error {response.status_code} for '{ref_to_check}'")
            return None

        data = response.json()


        if "error" in data:
            print(f"    ⚠️  Sefaria Error for '{ref_to_check}': {data['error']}")
            return None
            
        return {
            "ref_en": data.get("ref"),   # Canonical English (e.g., "Zevachim 45a:9")
            "ref_he": data.get("heRef")  # Canonical Hebrew (e.g., "זבחים מה א:ט")
        }

    except Exception as e:
        print(f"    ❌ Connection error checking '{ref_string}': {e}")
        return None

def run_llamafier(input_file):
    print(f"🚀 Starting Llamafier on {input_file}...")
    
    try:
        with open(input_file, 'r', encoding='utf-8') as f:
            data = json.load(f)
    except FileNotFoundError:
        print("❌ Input file not found.")
        return
    except json.JSONDecodeError:
        print("❌ Invalid JSON in input file.")
        return

    updated_count = 0
    
    # Iterate through the data
    for idx, item in enumerate(data, 1):
        original_ref = item.get("daf_reference", "")
        original_he = item.get("daf_reference_he", "")
        
        print(f"[{idx}/{len(data)}] Processing: {original_ref}...")

        # Validate and Normalize
        canonical_data = get_canonical_refs(original_ref)

        if canonical_data:
            new_en = canonical_data['ref_en']
            new_he = canonical_data['ref_he']

            # Check if changes are needed
            if new_en != original_ref or new_he != original_he:
                print(f"    🔄 Updating: '{original_ref}' -> '{new_en}'")
                print(f"    🔄 Hebrew:   '{original_he}' -> '{new_he}'")
                
                item['daf_reference'] = new_en
                item['daf_reference_he'] = new_he
                updated_count += 1
            else:
                print("    ✅ Already correct.")
        else:
            print(f"    ❌ Could not validate '{original_ref}'. Keeping original.")

        # Be polite to the API
        time.sleep(0.1)

    # Generate Output Filename
    today = datetime.date.today().isoformat() # YYYY-MM-DD
    output_filename = f"{today}_dafreaction_llamafied.json"

    try:
        with open(output_filename, 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=4, ensure_ascii=False)
        
        print(f"\n{'-'*60}")
        print(f"✨ Llamafication Complete!")
        print(f"📄 Output saved to: {output_filename}")
        print(f"✏️  Updated {updated_count} entries.")
        print(f"{'-'*60}")
        
    except Exception as e:
        print(f"❌ Error saving file: {e}")

if __name__ == "__main__":
    DEFAULT_INPUT = "refined_refined_2025-11-22_processed_data_Dafreactions.json"
    
    if len(sys.argv) > 1:
        file_to_process = sys.argv[1]
    else:
        file_to_process = DEFAULT_INPUT
        
    run_llamafier(file_to_process)