import json
import requests
import time
import re
from typing import Dict, Any, Optional

COOKIE_STR = "_user=%7B%22_uid%22%3A30698%7D; guide_overlay_seen_editor=2025-10-20T11:38:40.366Z; csrftoken=xM0xFd8tri34sh361gH0sFuYyHDHJWPYk4OZ4Sy1Ke8rg46ORma2GQsjp1DSl0wh; sessionid=0owgw6aoal3cn3vvzkkwnfdfr2upt3tz; version_preferences_by_corpus=%7B%22Bavli%22%3A%7B%22en%22%3A%22William%20Davidson%20Edition%20-%20English%22%7D%7D"
# -------------------------------------------

CLOSING_PARAGRAPH_HTML = (
    "<p>Thanks for learning with me!</p>"
    "<p>What you just saw is part of <b>The Daf Reactions Project</b>, where I share my "
    "daily practice of studying the Babylonian Talmud (Daf Yomi) from the viewpoint "
    "of a formerly Orthodox, now secular, Millennial feminist.</p>"
    "<p>I'm Miriam Anzovin—a Jewish nerd, storyteller, and artist. My passion "
    "is putting this ancient discourse in direct communication with modern internet "
    "culture, pop culture, and current events.</p>"
    "<p>These videos are my authentic reactions, with commentary that's both heartfelt "
    "and comedic, and always centers Jewish joy.</p>"
    "<p>My profound gratitude to " 
    '<a href="https://tsinvari.com" target="_blank">René Michel</a>, '
    "for connecting all the Daf Reactions videos "
    "to Sefaria source sheets. To paraphrase Rabbi Tarfon in "
    '<a href="https://www.sefaria.org/Pirkei_Avot.2.16?" target="_blank">Pirkei Avot 2:16</a>: It is not '
    "your responsibility to finish the work, but you should really try or René might have "
    "coded it already!!</p>"
    "<p>You can find me @MiriamAnzovin on "
    '<a href="https://www.youtube.com/@MiriamAnzovin" target="_blank">YouTube</a>, '
    '<a href="https://www.instagram.com/MiriamAnzovin" target="_blank">Instagram</a>, '
    '<a href="https://www.tiktok.com/@MiriamAnzovin" target="_blank">TikTok</a>, '
    '<a href="https://bsky.app/profile/miriamanzovin.bsky.social" target="_blank">Bluesky</a>, '
    '<a href="https://www.threads.net/@MiriamAnzovin" target="_blank">Threads</a>, '
    '<a href="https://universeodon.com/@MiriamAnzovin" target="_blank">Mastodon</a>, and '
    '(And also in some people’s minds, where I live rent free.)</p>'
)

def parse_cookie_string(cookie_str: str) -> Dict[str, str]:
    """Parses a browser's cookie string into a dictionary."""
    cookie_dict = {}
    for part in cookie_str.split('; '):
        if '=' in part:
            key, val = part.split('=', 1)
            cookie_dict[key.strip()] = val.strip()
    return cookie_dict

def extract_csrf_token(cookie_dict: Dict[str, str]) -> str:
    """Extracts the CSRF token from a cookie dictionary."""
    token = cookie_dict.get("csrftoken")
    if not token:
        raise ValueError("Could not find 'csrftoken' in the provided cookie string.")
    return token

def create_session_with_cookies(cookie_str: str) -> requests.Session:
    """Creates a requests session and populates it with cookies."""
    session = requests.Session()
    cookie_dict = parse_cookie_string(cookie_str)
    for key, value in cookie_dict.items():
        session.cookies.set(key, value)
    return session

def post_sheet(session, csrf_token, item):
    """
    Posts a single sheet to Sefaria using the provided data item.
    """
    api_url = "https://www.sefaria.org/api/sheets/"
    
    title = item.get('original_title', 'Untitled Sheet')
    paragraph = item.get("paragraph")
    youtube_embed = item.get("youtube_embed")
    
    daf_name = item.get("daf_reference")

    daf_name_he = item.get('daf_reference_he') 
    
    # Use the guessed text if available, otherwise fall back to the 1st-line text
    text_en = item.get("text_en_guess") or item.get("text_en")
    text_he = item.get("text_he_guess") or item.get("text_he")
    # -----------------------------------------------------------

    if not daf_name: # Check if any reference exists
        print(f"  - Skipping item '{title}' due to missing 'daf_reference'.")
        return None

    # Construct the content of the sheet
    sources = []
    
    # 1. YouTube Description
    if paragraph:
        formatted_paragraph = "<p>" + paragraph.replace('\n', '</p><p>') + "</p>"
        sources.append({"comment": formatted_paragraph, "outsideText":""})
    
    # 2. YouTube Video
    # Use the 'daf_name' (which is either the guess or the original) for the API ref
    sefaria_api_ref = daf_name.replace(' ', '.', 1) 
    sources.append({ "media": youtube_embed, "mediaType": "video"})
    
    # 3. Sefaria Source
    sources.append({ "ref": sefaria_api_ref, "heRef": daf_name_he, "text":{"en": text_en, "he": text_he}}) 
    # 4. Closing Paragraph
    sources.append({"comment": CLOSING_PARAGRAPH_HTML, "outsideText": ""})

    DEFAULT_OPTIONS: Dict[str, Any] = {
        "layout": "stacked", "boxed": 0, "language": "bilingual",
        "numbered": 0, "assignable": 0, "divineNames": "noSub",
        "collaboration": "group-can-edit", "highlightMode": 0,
        "langLayout": "heRight", "bsd": 0,
    }
    
    sheet_content = {
        "title": title,
        "sources": sources,
        "options": DEFAULT_OPTIONS,
        "status": "unlisted",
        "collections": [],
         "topics": [{"asTyped": "Talmud", "slug": "talmud", "en": "Talmud","he": "תלמוד"}],
        "summary": paragraph,
        "collectionName": "DafReactions",
    }

    form_data = {"json": json.dumps(sheet_content)}
    headers = {
        'accept': '*/*', 'accept-language': 'en-US,en;q=0.9',
        'content-type': 'application/x-www-form-urlencoded; charset=UTF-8',
        'origin': 'https://www.sefaria.org',
        'referer': 'https://www.sefaria.org/sheets/new',
        'sec-ch-ua': '"Google Chrome";v="141", "Not?A_Brand";v="8", "Chromium";v="141"',
        'sec-ch-ua-mobile': '?0', 'sec-ch-ua-platform': '"Linux"',
        'sec-fetch-dest': 'empty', 'sec-fetch-mode': 'cors', 'sec-fetch-site': 'same-origin',
        'user-agent': 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/141.0.0.0 Safari/537.36',
        'x-csrftoken': csrf_token, 'x-requested-with': 'XMLHttpRequest',
    }

    try:
        response = session.post(api_url, headers=headers, data=form_data)
        response.raise_for_status()
        
        response_data = response.json()
        sheet_url = response_data.get("url")
        
        if sheet_url:
            print(f"  + Successfully created sheet: {sheet_url}")
            return sheet_url
        else:
            print(f"  - Sheet created, but no URL was returned. Response: {response_data}")
            return None
            
    except requests.exceptions.RequestException as e:
        print(f"  - FAILED to create sheet for '{title}'. Error: {e}")
        if e.response:
            print(f"    Response Status: {e.response.status_code}")
            print(f"    Response Content: {e.response.text}")
        return None

# --- CHANGE 3: Add 'limit' parameter ---
def create_sheets_from_json(json_file, limit: Optional[int] = None):
    """
    Main function to read a JSON file and create Sefaria sheets in a loop.
    """
    if "PASTE_ENTIRE_COOKIE_STRING_HERE" in COOKIE_STR:
        print("ERROR: Please update the script with your full COOKIE_STR.")
        return

    try:
        with open(json_file, 'r', encoding='utf-8') as f:
            data = json.load(f)
    except FileNotFoundError:
        print(f"Error: The input file '{json_file}' was not found.")
        return
    
    # --- CHANGE 4: Apply the limit if it exists ---
    if limit:
        print(f"--- Limiting run to the first {limit} items. ---")
        data = data[:limit]
    # -----------------------------------------------
    
    try:
        session = create_session_with_cookies(COOKIE_STR)
        csrf_token = extract_csrf_token(parse_cookie_string(COOKIE_STR))
    except ValueError as e:
        print(f"Error: {e}")
        return

    print(f"Starting to create {len(data)} sheets from '{json_file}'...")
    for i, item in enumerate(data, 1):
        print(f"\nProcessing item {i}/{len(data)}: {item.get('original_title')}")
        post_sheet(session, csrf_token, item)
        time.sleep(1) 
        
    print("\nProcess complete.")

if __name__ == "__main__":
    # This is the final, fully enriched file from our new script 2.5
    INPUT_JSON_FILE = "2025-11-28_dafreaction_llamafied.json"
    
    # --- CHANGE 5: Add user prompt for limit ---
    print("Select a processing option:")
    print("  1. Run entire JSON file")
    print("  2. Run first 5 items only (for testing)")
    choice = input("Enter choice (1 or 2): ")

    run_limit = None
    if choice == '2':
        run_limit = 5
    elif choice == '1':
        print("--- Will process the entire file. ---")
    else:
        print("--- Invalid choice. Defaulting to process the entire file. ---")
    
    create_sheets_from_json(INPUT_JSON_FILE, limit=run_limit)