import json
import re
import requests
import time
from typing import Dict, Optional, List, Any
import os

def get_specific_segment_text(ref_str: str) -> Optional[Dict[str, str]]:
    """
    Gets the text for a single, specific segment from Sefaria.
    e.g., "Zevachim 35a.9" or "Zevachim 45a"
    Returns None if fetch fails OR if text is missing.
    """
    if not ref_str:
        return None

    try:
        # Convert "Zevachim 35a.9" to "Zevachim.35a.9"
        # This also works for "Zevachim 45a" -> "Zevachim.45a"
        api_ref = ref_str.replace(' ', '.', 1)
        api_url = f"https://www.sefaria.org/api/texts/{api_ref}?context=0"
        
        response = requests.get(api_url)
        response.raise_for_status()
        data = response.json()

        # If the ref was a general one (e.g., "Zevachim 45a"),
        # data["text"] will be a list. We take the first item.
        # If it was specific (e.g., "Zevachim 45a.9"), it will be a string.
        
        en_text_raw = data.get("text", "")
        he_text_raw = data.get("he", "")
        
        # Handle list (for general refs) or string (for specific refs)
        en_text = en_text_raw[0] if isinstance(en_text_raw, list) else en_text_raw
        he_text = he_text_raw[0] if isinstance(he_text_raw, list) else he_text_raw

        # Clean HTML tags from text
        en_text_cleaned = re.sub('<[^<]+?>', '', en_text).strip()
        he_text_cleaned = re.sub('<[^<]+?>', '', he_text).strip()
        
        # --- THIS IS THE NEW, STRICTER LOGIC ---
        if not en_text_cleaned or not he_text_cleaned:
            print(f"    ❌ ERROR: Ref '{ref_str}' is valid but has no text (e.g., it's a heading). Please try a different segment.")
            return None
            
        return {
            "ref": data.get("ref", ref_str), # Use the ref Sefaria returns
            "en": en_text_cleaned,
            "he": he_text_cleaned
        }
        
    except requests.exceptions.RequestException as e:
        print(f"    ❌ ERROR fetching '{ref_str}': {e}")
        return None
    except json.JSONDecodeError:
        print(f"    ❌ ERROR: Sefaria returned invalid JSON for '{ref_str}'.")
        return None

def prompt_for_valid_ref(prompt_message: str) -> Optional[Dict[str, str]]:
    """A loop that keeps asking the user for a ref until it fetches successfully."""
    while True:
        user_input = input(prompt_message).strip()
        if not user_input:
            print("    ⚠️  Skipping. No reference provided.")
            return None # User gave up
        
        print(f"    ⬇️  Fetching text for '{user_input}'...")
        # This function is now stricter and will return None for refs with no text
        text_data = get_specific_segment_text(user_input)
        
        if text_data:
            print(f"    ✅ Success! Using ref: {text_data['ref']}")
            return text_data
        else:
            print(f"    ❌ FAILED to fetch '{user_input}' or text was missing.")
            # Loop continues

def run_refiner_phases(input_file: str, output_file: str):
    """
    Runs the 3-phase interactive refiner.
    Modifies the data in-place, does not add 'spec_' keys.
    """
    try:
        with open(input_file, 'r', encoding='utf-8') as f:
            data = json.load(f)
    except FileNotFoundError:
        print(f"❌ Error: The input file '{input_file}' was not found.")
        return
    except json.JSONDecodeError:
        print(f"❌ Error: The input file '{input_file}' is not valid JSON.")
        return

    # --- PHASE 1: Check for missing daf_reference ---
    print(f"\n{'-'*80}")
    print("🚀 Starting Phase 1: Checking for missing daf_reference...")
    print(f"{'-'*80}")
    
    for idx, item in enumerate(data, 1):
        ref = item.get("daf_reference")
        if not ref or ref.strip() == "":
            print(f"\n🎞️  VIDEO {idx}/{len(data)}: {item.get('original_title')}")
            print("    THIS VIDEO HAS NO DAF_REFERENCE.")
            
            text_data = prompt_for_valid_ref("    Enter daf_reference (e.g., 'Zevachim 45a'): ")
            
            if text_data:
                # --- Overwrite existing keys ---
                item['daf_reference'] = text_data['ref']
                item['text_en'] = text_data['en']
                item['text_he'] = text_data['he']
            else:
                print(f"    ⚠️  No ref provided. '{item.get('original_title')}' will be skipped in Phase 2 & 3.")

    print("\n✅ Phase 1 Complete.")

    # --- PHASE 2: Check for missing text_en or text_he ---
    print(f"\n{'-'*80}")
    print("🚀 Starting Phase 2: Checking for missing text...")
    print(f"{'-'*80}")
    
    for idx, item in enumerate(data, 1):
        ref = item.get("daf_reference")
        en_text = item.get("text_en")
        he_text = item.get("text_he")
        
        # Only check if a ref exists but text is missing
        if ref and (not en_text or not he_text):
            print(f"\n🎞️  VIDEO {idx}/{len(data)}: {item.get('original_title')}")
            print(f"    Ref '{ref}' is missing text (or is a heading). Please correct it.")
            
            new_text_data = prompt_for_valid_ref("    Enter a corrected reference: ")
            if new_text_data:
                # --- Overwrite existing keys ---
                item['daf_reference'] = new_text_data['ref']
                item['text_en'] = new_text_data['en']
                item['text_he'] = new_text_data['he']

    print("\n✅ Phase 2 Complete. All items should now have valid text.")

    # --- PHASE 3: Manual Confirmation Loop ---
    print(f"\n{'-'*80}")
    print("🚀 Starting Phase 3: Final Confirmation...")
    print("    Press ENTER to confirm the ref, or type a new one.")
    print(f"{'-'*80}")
    
    for idx, item in enumerate(data, 1):
        print(f"\n🎞️  VIDEO {idx}/{len(data)}: {item.get('original_title')}")
        
        current_ref = item.get("daf_reference")
        
        if not current_ref:
            print("    ℹ️  Current Ref: --- NONE --- (Skipping confirmation)")
            continue
        
        print(f"    ℹ️  Current Ref: {current_ref}")
        print(f"        EN: {(item.get('text_en') or '...')[:100]}...")

        user_input = input(f"    Enter new ref (or press ENTER to keep): ").strip()
        
        if not user_input:
            # --- User pressed ENTER ---
            print(f"    ✅ Keeping: {current_ref}")
            continue # No changes needed
        
        # --- User entered a new ref, we must validate it ---
        while True:
            print(f"    ⬇️  Fetching text for '{user_input}'...")
            text_data = get_specific_segment_text(user_input)
            
            if text_data:
                # --- Overwrite existing keys ---
                print(f"    ✅ Success! Ref updated to: {text_data['ref']}")
                item['daf_reference'] = text_data['ref']
                item['text_en'] = text_data['en']
                item['text_he'] = text_data['he']
                break # Exit validation loop
            else:
                user_input = input(f"    ❌ Failed. Try new ref (or ENTER to keep original '{current_ref}'): ").strip()
                if not user_input:
                    print(f"    ✅ OK. Keeping original ref: {current_ref}")
                    break # Exit validation loop, keeping original

        time.sleep(0.1) # Small delay

    # --- SAVE FINAL FILE ---
    try:
        # We save the 'data' object itself, which has been modified in-place
        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=4, ensure_ascii=False)
        print(f"\n{'-'*80}")
        print(f"🎉 Successfully created refined file at '{output_file}'")
        print(f"Saved {len(data)} total entries.")
    except Exception as e:
        print(f"\n❌ An error occurred while writing the file: {e}")

if __name__ == "__main__":
    # The file from Script 2 (or your last processed file)
    INPUT_FILE = "refined_2025-11-22_processed_data_Dafreactions.json" 
    
    input_filename = os.path.basename(INPUT_FILE)
    output_filename = f"refined_{input_filename}"
    
    print(f"Input file:  {INPUT_FILE}")
    print(f"Output file: {output_filename}")
    
    run_refiner_phases(INPUT_FILE, output_filename)