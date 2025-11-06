import json
import re
import requests
from typing import Dict, Optional
# from datetime import datetime # Removed, not used

# -------------------------------
# 🔠 Tractate and Reference Helpers
# -------------------------------

def get_tractate_names_map() -> Dict[str, str]:
    """Returns a dictionary mapping English tractate names to their Hebrew equivalents."""
    return {
        "Berakhot": "ברכות", "Brachot": "ברכות", "Peah": "פאה", "Demai": "דמאי", "Kilayim": "כלאים",
        "Sheviit": "שביעית", "Terumot": "תרומות", "Maasrot": "מעשרות", "Maaser Sheni": "מעשר שני",
        "Challah": "חלה", "Orlah": "ערלה", "Bikkurim": "ביכורים", "Shabbat": "שבת",
        "Eruvin": "עירובין", "Pesachim": "פסחים", "Shekalim": "שקלים", "Yoma": "יומא",
        "Sukkah": "סוכה", "Beitzah": "ביצה", "Rosh Hashanah": "ראש השנה", "Taanit": "תענית",
        "Ta'anit": "תענית", "Megillah": "מגילה", "Moed Katan": "מועד קטן", "Chagigah": "חגיגה",
        "Yevamot": "יבמות", "Ketubot": "כתובות", "Nedarim": "נדרים", "Nazir": "נזיר",
        "Sotah": "סוטה", "Gittin": "גיטין", "Kiddushin": "קידושין",
        "Bava Kamma": "בבא קמא", "Bava Metzia": "בבא מציעא", "Bava Batra": "בבא בתרא",
        "Sanhedrin": "סנהדרין", "Makkot": "מכות", "Shevuot": "שבועות",
        "Eduyot": "עדיות", "Avodah Zarah": "עבודה זרה", "Avot": "אבות", "Horayot": "הוריות",
        "Zevachim": "זבחים", "Menachot": "מנחות", "Chullin": "חולין", "Bekhorot": "בכורות",
        "Arakhin": "ערכין", "Temurah": "תמורה", "Keritot": "כריתות", "Meilah": "מעילה",
        "Kinnim": "קנים", "Tamid": "תמיד", "Middot": "מדות", "Kelim": "כלים",
        "Oholot": "אהלות", "Negaim": "נגעים", "Parah": "פרה", "Tohorot": "טהרות",
        "Mikvaot": "מקואות", "Niddah": "נדה", "Makhshirin": "מכשירין", "Zavim": "זבים",
        "Tevul Yom": "טבול יום", "Yadayim": "ידים", "Uktzin": "עוקצין",
        "Mo'ed Katan": "מועד קטן"
    }

def get_hebrew_daf_from_number(daf_number_str: str) -> str:
    """Converts a Latin number string (e.g., '5') to a Hebrew Gematria daf string (e.g., 'ה')."""
    gematria = {
        1: 'א', 2: 'ב', 3: 'ג', 4: 'ד', 5: 'ה', 6: 'ו', 7: 'ז', 8: 'ח', 9: 'ט',
        10: 'י', 20: 'כ', 30: 'ל', 40: 'מ', 50: 'נ', 60: 'ס', 70: 'ע', 80: 'פ', 90: 'צ',
        100: 'ק', 200: 'ר', 300: 'ש', 400: 'ת'
    }
    num = int(daf_number_str)
    if num <= 0:
        return ""
    hebrew_str = ""
    for value in sorted(gematria.keys(), reverse=True):
        while num >= value:
            hebrew_str += gematria[value]
            num -= value
    return hebrew_str.replace("יה", "טו").replace("יו", "טז")

# -------------------------------
# 🌐 Sefaria API Integration
# -------------------------------

def get_sefaria_data(daf_reference: str) -> Dict[str, str]:
    """Queries Sefaria API to get canonical link and the first line of text in both English and Hebrew."""
    default_response = {"sefaria_link": "", "text_en": "", "text_he": ""}
    if not daf_reference:
        return default_response

    try:
        api_ref = f"{daf_reference.replace(' ', '.')}:1"
        api_url = f"https://www.sefaria.org/api/texts/{api_ref}"
        response = requests.get(api_url)
        response.raise_for_status()
        data = response.json()

        canonical_ref_full = data.get("ref")
        sefaria_link = ""
        if canonical_ref_full:
            canonical_ref = canonical_ref_full.rsplit(':', 1)[0]
            sefaria_link = f"https://www.sefaria.org/{canonical_ref.replace(' ', '_')}"
            print(f"      🔗 Found Sefaria link: {sefaria_link}")

        text_en = data.get("text", "")
        text_he = data.get("he", "")
        text_en_clean = re.sub('<[^<]+?>', '', text_en[0]).strip() if isinstance(text_en, list) and text_en else ""
        text_he_clean = re.sub('<[^<]+?>', '', text_he[0]).strip() if isinstance(text_he, list) and text_he else ""

        return {
            "sefaria_link": sefaria_link,
            "text_en": text_en_clean,
            "text_he": text_he_clean
        }

    except requests.exceptions.RequestException as e:
        print(f"      ⚠️ Could not fetch Sefaria data for '{daf_reference}'")
        return default_response

# -------------------------------
# 🎥 YouTube Embed Helper
# -------------------------------

def get_youtube_embed_url(url: str) -> str:
    """Extracts YouTube video ID and formats it for embedding."""
    if not url:
        return ""
    regex = r"(?:https?:\/\/)?(?:www\.)?(?:youtube\.com\/(?:[^\/\n\s]+\/\S+\/|(?:v|e(?:mbed)?)\/|\S*?[?&]v=)|youtu\.be\/)([a-zA-Z0-9_-]{11})"
    match = re.search(regex, url)
    return f"https://www.youtube.com/embed/{match.group(1)}?rel=0&showinfo=0" if match else ""

# -------------------------------
# 🧩 Core Processing Function
# -------------------------------

def process_prepared_data(input_file, daf_reaction_output_file, non_daf_reaction_output_file, limit: Optional[int] = None):
    """Reads prepared data, processes 'Daf Reaction' videos, and confirms 'non-Daf' classifications interactively."""
    print(f"\n📘 Loading data from: {input_file}")

    try:
        with open(input_file, 'r', encoding='utf-8') as f:
            prepared_data = json.load(f)
    except FileNotFoundError:
        print(f"❌ Error: Input file not found: {input_file}")
        print("Please ensure the file from Script 1 is in the same directory.")
        return
    except json.JSONDecodeError:
        print(f"❌ Error: Could not decode JSON from '{input_file}'.")
        return
    except Exception as e:
        print(f"❌ Error reading input file: {e}")
        return

    if limit:
        prepared_data = prepared_data[:limit]
        print(f"⚙️ Limiting run to the first {limit} items.\n")

    tractate_map = get_tractate_names_map()
    pattern = re.compile(rf'({"|".join(re.escape(k) for k in tractate_map)})\s+(\d{{1,3}})([ab])?\b', re.IGNORECASE)

    daf_reaction_data = []
    non_daf_reaction_data = []

    print(f"🚀 Processing {len(prepared_data)} video entries...\n")

    for idx, item in enumerate(prepared_data, start=1):
        original_title = item.get("title", "")
        if not original_title:
            continue

        print(f"\n{'-'*80}")
        print(f"🎞️  [{idx}] {original_title}")
        print(f"{'-'*80}")

        is_daf_reaction = (
                            "daf reaction" in original_title.lower() or
                            "#dafreaction" in original_title.lower()
                        )

        if is_daf_reaction:
            print("🧩 Detected as Daf Reaction.")
            
            # --- FIX 1: Handle potential NoneType ---
            original_description = item.get("paragraph") or ""
            # ----------------------------------------
            
            processed_item = {
                "daf_reference": "",
                "daf_reference_he": "",
                "original_title": original_title,
                "youtube_url": item.get("youtube_url"),
                "youtube_embed": get_youtube_embed_url(item.get("youtube_url")),
                "sefaria_link": "",
                "paragraph": original_description,
                "text_en": "",
                "text_he": ""
            }

            search_text = (original_title + " " + original_description).replace("’", "'").replace("”", "'")
            match = pattern.search(search_text)
            if match:
                tractate_en_raw = match.group(1)
                daf_number = match.group(2)
                daf_side = match.group(3)
                canonical_tractate_en = next((k for k in tractate_map if k.lower() == tractate_en_raw.lower()), tractate_en_raw)
                canonical_tractate_en = canonical_tractate_en.replace(" ", "_").replace("'", "")
                daf_reference_en = f"{canonical_tractate_en} {daf_number}{daf_side or 'a'}"
                daf_reference_he = f"{tractate_map.get(canonical_tractate_en, '')} {get_hebrew_daf_from_number(daf_number)} {'ב' if daf_side == 'b' else 'א'}"

                print(f"    📖 Found daf reference: {daf_reference_en} | {daf_reference_he}")
                sefaria_data = get_sefaria_data(daf_reference_en)

                processed_item.update({
                    "daf_reference": daf_reference_en,
                    "daf_reference_he": daf_reference_he,
                    "sefaria_link": sefaria_data["sefaria_link"],
                    "text_en": sefaria_data["text_en"],
                    "text_he": sefaria_data["text_he"]
                })
            else:
                print("    ⚠️ No daf reference found in text.")

            daf_reaction_data.append(processed_item)

        else:
            # --- FIX 2: Add y/n prompt to correctly sort files ---
            print("    ⚠️ Item not detected as 'Daf Reaction'.")
            reclassify = input("    -> Manually reclassify as Daf Reaction? (y/n): ").strip().lower()
            
            if reclassify == 'y':
                print("    🔁 Reclassified as Daf Reaction (manual override).")

                # Prompt user to provide daf reference manually if missing
                manual_ref = input("    🧾 Enter daf reference (e.g., 'Berakhot 2a') or press Enter to skip: ").strip()

                sefaria_data = {"sefaria_link": "", "text_en": "", "text_he": ""}
                daf_reference_en = ""
                daf_reference_he = ""

                if manual_ref:
                    # Try to find the matching Hebrew name and daf side
                    match = re.match(r"([\w\s']+)\s+(\d{1,3})([ab])?", manual_ref)
                    if match:
                        tractate_en_raw = match.group(1).strip()
                        daf_number = match.group(2)
                        daf_side = match.group(3) or "a"
                        # tractate_map is already loaded
                        canonical_tractate_en = next((k for k in tractate_map if k.lower() == tractate_en_raw.lower()), tractate_en_raw)
                        daf_reference_en = f"{canonical_tractate_en} {daf_number}{daf_side}"
                        daf_reference_he = f"{tractate_map.get(canonical_tractate_en, '')} {get_hebrew_daf_from_number(daf_number)} {'ב' if daf_side == 'b' else 'א'}"
                        print(f"      📘 Using manual daf reference: {daf_reference_en} | {daf_reference_he}")
                        sefaria_data = get_sefaria_data(daf_reference_en)
                    else:
                        print("      ⚠️ Could not parse manual reference format. Skipping Sefaria lookup.")
                else:
                    print("      ⚠️ No daf reference provided. Skipping Sefaria lookup.")

                processed_item = {
                    "daf_reference": daf_reference_en,
                    "daf_reference_he": daf_reference_he,
                    "original_title": original_title,
                    "youtube_url": item.get("youtube_url"),
                    "youtube_embed": get_youtube_embed_url(item.get("youtube_url")),
                    "sefaria_link": sefaria_data.get("sefaria_link", ""),
                    "paragraph": item.get("paragraph") or "", # Also fix NoneType here
                    "text_en": sefaria_data.get("text_en", ""),
                    "text_he": sefaria_data.get("text_he", "")
                }
                # Add to the *Daf Reaction* list
                daf_reaction_data.append(processed_item)
            
            else:
                # If 'n' or anything else, add the original item to the *non-Daf* list
                print("    🚫 Skipped. Adding to non-Daf Reaction file.")
                non_daf_reaction_data.append(item)
            # --- END OF FIX 2 ---


    # -------------------------------
    # 💾 Save Results
    # -------------------------------
    try:
        with open(daf_reaction_output_file, 'w', encoding='utf-8') as f:
            json.dump(daf_reaction_data, f, indent=4, ensure_ascii=False)
        print(f"\n✅ Saved {len(daf_reaction_data)} Daf Reaction entries → {daf_reaction_output_file}")
    except Exception as e:
        print(f"❌ Error saving Daf Reaction file: {e}")

    try:
        with open(non_daf_reaction_output_file, 'w', encoding='utf-8') as f:
            json.dump(non_daf_reaction_data, f, indent=4, ensure_ascii=False)
        print(f"✅ Saved {len(non_daf_reaction_data)} non-Daf Reaction entries → {non_daf_reaction_output_file}")
    except Exception as e:
        print(f"❌ Error saving non-Daf Reaction file: {e}")


# -------------------------------
# 🏁 Script Entry Point
# -------------------------------

if __name__ == "__main__":
    INPUT_JSON_FILE = "2025-11-04_preparedata_Dafreactions.json"
    OUTPUT_DAF_FILE = "2025-11-04_processed_data_Dafreactions.json"
    OUTPUT_NON_DAF_FILE = "2025-11-04_notdafreaction.json"

    print("\n📂 Sefaria Classification Processor")
    print("========================================")
    
    # Added a check to see if the input file exists before starting
    try:
        with open(INPUT_JSON_FILE, 'r', encoding='utf-8') as f:
            pass # Just check if it can be opened
        print(f"Found input file: {INPUT_JSON_FILE}\n")
    except FileNotFoundError:
        print(f"❌ ERROR: Input file not found: {INPUT_JSON_FILE}")
        print("Please make sure the file from Script 1 is in the same directory and named correctly.")
        exit() # Exit the script if no input file is found
        
    print("Options:")
    print("  1️⃣  Process entire JSON file")
    print("  2️⃣  Process first 10 items (for testing)")
    choice = input("\nEnter choice (1 or 2): ").strip()

    limit = 20 if choice == '2' else None
    process_prepared_data(INPUT_JSON_FILE, OUTPUT_DAF_FILE, OUTPUT_NON_DAF_FILE, limit)