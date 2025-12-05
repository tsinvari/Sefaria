import json
import requests
import time
import re
import urllib.parse
import datetime
import os
import sys
from typing import Dict, Any, Optional, List

COOKIE_STR = "_user=%7B%22_uid%22%3A30698%7D; guide_overlay_seen_editor=2025-10-20T11:38:40.366Z; csrftoken=xM0xFd8tri34sh361gH0sFuYyHDHJWPYk4OZ4Sy1Ke8rg46ORma2GQsjp1DSl0wh; sessionid=0owgw6aoal3cn3vvzkkwnfdfr2upt3tz; version_preferences_by_corpus=%7B%22Bavli%22%3A%7B%22en%22%3A%22William%20Davidson%20Edition%20-%20English%22%7D%7D"

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

def extract_user_id(cookie_dict: Dict[str, str]) -> int:
    """Extracts the Sefaria User ID from the cookie dictionary."""
    user_cookie_str = cookie_dict.get("_user")
    if not user_cookie_str:
        raise ValueError("Could not find '_user' cookie. Is it part of your COOKIE_STR?")
    
    try:
        decoded_str = urllib.parse.unquote(user_cookie_str)
        user_data = json.loads(decoded_str)
        user_id = user_data.get("_uid")
        if not user_id:
            raise ValueError("Found '_user' cookie but it doesn't contain '_uid'.")
        return int(user_id)
    except (json.JSONDecodeError, TypeError, ValueError) as e:
        print(f"Error parsing user cookie: {e}")
        raise ValueError(f"Could not parse user ID from cookie: {user_cookie_str}")

def get_unpublished_sheet_summaries(session: requests.Session, user_id: int) -> List[Dict[str, Any]]:
    """
    Fetches the summary list of all unlisted sheets for a user.
    """
    api_url = f"https://www.sefaria.org/api/sheets/user/{user_id}"
    print(f"Fetching sheet list for user {user_id} from {api_url}...")
    
    try:
        response = session.get(api_url)
        response.raise_for_status()
        data = response.json()
        
        all_sheets = data.get("sheets", [])
        if not all_sheets:
            print("No sheets found for this user.")
            return []

        unpublished = []
        for sheet in all_sheets:
            if sheet.get("status") == "unlisted":
                unpublished.append({
                    "id": sheet.get("id"),
                    "title": sheet.get("title", "Untitled")
                })
        
        return unpublished
        
    except requests.exceptions.RequestException as e:
        print(f"Error fetching sheet list: {e}")
        return []

def fetch_and_save_unpublished(session: requests.Session, user_id: int):
    """
    Workflow Step 1: Fetches all unpublished sheets and saves them to a file.
    """
    # 1. Get summaries
    summaries = get_unpublished_sheet_summaries(session, user_id)
    if not summaries:
        print("No unpublished sheets to fetch.")
        return

    print(f"\nFound {len(summaries)} unpublished sheets. Fetching full content...")
    
    # 2. Get full content
    full_data_list = []
    for idx, sheet_info in enumerate(summaries, 1):
        sheet_id = sheet_info['id']
        title = sheet_info['title']
        print(f"  [{idx}/{len(summaries)}] Fetching: '{title}' (ID: {sheet_id})...")
        
        try:
            response = session.get(f"https://www.sefaria.org/api/sheets/{sheet_id}")
            response.raise_for_status()
            sheet_data = response.json()
            full_data_list.append(sheet_data)
        except Exception as e:
            print(f"    ❌ Failed to fetch data: {e}")
            continue
            
        time.sleep(0.5)

    # 3. Save to file
    today = datetime.date.today().isoformat()
    filename = f"{today}_latestversion.json"
    
    try:
        with open(filename, 'w', encoding='utf-8') as f:
            json.dump(full_data_list, f, indent=4, ensure_ascii=False)
        print(f"\n✅ All unpublished sheets saved to: {filename}")
    except Exception as e:
        print(f"❌ Failed to write backup file: {e}")

def process_single_sheet_publish(session: requests.Session, csrf_token: str, sheet_data: Dict[str, Any]) -> Dict[str, Any]:
    """
    Handles the delete + recreate logic for a single sheet.
    Returns a result dict describing what happened.
    """
    old_id = sheet_data.get("id")
    title = sheet_data.get("title", "Untitled")
    status = sheet_data.get("status", "unknown")
    
    result = {
        "original_id": old_id,
        "title": title,
        "original_status": status,
        "outcome": "skipped",
        "details": "",
        "new_url": None
    }

    # SAFETY CHECK: If already public, SKIP
    if status == "public":
        result["details"] = "Sheet is already public. Skipped."
        print(f"  ⚠️  Skipping '{title}' (ID: {old_id}) - Already public.")
        return result

    print(f"  Processing '{title}' (Old ID: {old_id})...")

    delete_url = f"https://www.sefaria.org/api/sheets/{old_id}/delete"
    create_url = "https://www.sefaria.org/api/sheets/"

    common_headers = {
        'accept': '*/*',
        'accept-language': 'en-US,en;q=0.9',
        'content-type': 'application/x-www-form-urlencoded; charset=UTF-8',
        'origin': 'https://www.sefaria.org',
        'referer': 'https://www.sefaria.org/sheets/',
        'user-agent': 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/141.0.0.0 Safari/537.36',
        'x-csrftoken': csrf_token,
        'x-requested-with': 'XMLHttpRequest',
    }

    try:
        # 1. Modify Data in Memory
        new_data = sheet_data.copy()
        
        # KEY CHANGE: Only force status to public. Do NOT touch other metadata.
        new_data["status"] = "public"
        
        # Ensure collaboration settings (optional, but good practice for "public" usually)
        if "options" not in new_data:
             new_data["options"] = {}
        new_data["options"]["collaboration"] = "group-can-edit"

        # Clean keys for creation
        for key in ["_id", "id", "dateCreated", "dateModified", "owner", "views", "promptedToPublish"]:
            new_data.pop(key, None)
        
        # 2. DELETE Old Sheet
        delete_headers = common_headers.copy()
        owner_data = sheet_data.get("owner")
        owner_id = owner_data if isinstance(owner_data, int) else (owner_data.get("id") if isinstance(owner_data, dict) else "")
        if owner_id:
            delete_headers['referer'] = f'https://www.sefaria.org/profile/{owner_id}?tab=sheets'
        
        print(f"    -> Deleting... ", end="", flush=True)
        del_res = session.post(delete_url, headers=delete_headers)
        if del_res.status_code == 404:
             print("Not found (already deleted?) -> Proceeding.")
        else:
            del_res.raise_for_status()
            print("Done.")

        # 3. CREATE New Sheet
        print(f"    -> Creating/Redeploying... ", end="", flush=True)
        form_data = {"json": json.dumps(new_data)}
        create_res = session.post(create_url, headers=common_headers, data=form_data)
        create_res.raise_for_status()
        
        new_info = create_res.json()
        new_url = new_info.get("url")
        
        print(f"Success! URL: {new_url}")
        
        result["outcome"] = "success"
        result["details"] = "Published successfully."
        result["new_url"] = new_url
        
        # Update the sheet object itself for the outcome file
        sheet_data["status"] = "public"
        sheet_data["url"] = new_url
        if "id" in new_info:
            sheet_data["id"] = new_info["id"]

        return result

    except Exception as e:
        print(f"FAILED: {e}")
        result["outcome"] = "error"
        result["details"] = str(e)
        return result

def publish_from_file(session: requests.Session, csrf_token: str):
    """
    Workflow Step 2: Reads a JSON file and publishes the sheets within.
    """
    filename = input("\nEnter the filename to load (e.g. 2025-12-05_latestversion.json): ").strip()
    
    if not os.path.exists(filename):
        print(f"❌ File '{filename}' not found.")
        return

    try:
        with open(filename, 'r', encoding='utf-8') as f:
            sheets_to_process = json.load(f)
    except Exception as e:
        print(f"❌ Error reading file: {e}")
        return

    print(f"\n--- 🚀 Starting Publish Process for {len(sheets_to_process)} sheets from '{filename}' ---")
    print("NOTE: This will DELETE the original sheet and RECREATE it as Public.")
    confirm = input("Are you sure?: ").strip().lower()
    
    if confirm != 'lets fucking golem':
        print("Aborted.")
        return

    publication_results = []
    stats = {"success": 0, "skipped": 0, "error": 0}
    
    # Process sheets
    for sheet in sheets_to_process:
        res = process_single_sheet_publish(session, csrf_token, sheet)
        publication_results.append(sheet) 
        
        outcome = res.get("outcome", "error")
        if outcome in stats:
            stats[outcome] += 1
            
        time.sleep(1.5) # Rate limiting

    # Show Summary
    print("\n--- 🏁 Publication Summary ---")
    print(f"Total Processed: {len(sheets_to_process)}")
    print(f"✅ Published: {stats['success']}")
    print(f"⚠️  Skipped:   {stats['skipped']}")
    print(f"❌ Failed:    {stats['error']}")
    print("------------------------------")

    # Save outcome report
    today = datetime.date.today().isoformat()
    outcome_filename = f"{today}_publishedoutcome.json"
    
    try:
        with open(outcome_filename, 'w', encoding='utf-8') as f:
            json.dump(publication_results, f, indent=4, ensure_ascii=False)
        print(f"\n✅ Outcome report saved to: {outcome_filename}")
    except Exception as e:
        print(f"❌ Failed to save outcome report: {e}")

def main():
    if "PASTE_ENTIRE_COOKIE_STRING_HERE" in COOKIE_STR:
        print("ERROR: Please update the script with your full COOKIE_STR.")
        return

    try:
        cookie_dict = parse_cookie_string(COOKIE_STR)
        session = create_session_with_cookies(COOKIE_STR)
        csrf_token = extract_csrf_token(cookie_dict)
        user_id = extract_user_id(cookie_dict)
    except ValueError as e:
        print(f"Error initializing: {e}")
        return

    while True:
        print("\n=== Publisher-Recreate Menu ===")
        print("1. Fetch Unpublished Sheets (Save to file)")
        print("2. Publish from File")
        print("3. Exit")
        
        choice = input("Select an option (1-3): ").strip()
        
        if choice == '1':
            fetch_and_save_unpublished(session, user_id)
        elif choice == '2':
            publish_from_file(session, csrf_token)
        elif choice == '3':
            print("Lehitraot!!!")
            break
        else:
            print("Invalid choice.")

if __name__ == "__main__":
    main()