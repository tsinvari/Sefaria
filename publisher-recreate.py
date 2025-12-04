import json
import requests
import time
import re
import urllib.parse
import datetime
import os
from typing import Dict, Any, Optional, List

COOKIE_STR = "_user=%7B%22_uid%22%3A30698%7D; _vwo_uuid_v2=DAEF75EA9F5AA9A8942BF68D2048B82BA|0fde10cd8b44b61b08adcced7a7ff985; _ga=GA1.1.1685663087.1737284307; _ga_P6B48B03CT=GS1.2.1737793214.2.0.1737793214.60.0.0; _ga_5S6RP1RFZ2=GS1.1.1737793214.2.1.1737793214.60.0.0; _hjSessionUser_2695522=eyJpZCI6Ijc0MDgzZTYxLTRhMTItNWVjMi05MTMwLTlkNTYyYjU0M2YyMSIsImNyZWF0ZWQiOjE3MzcyODQzMDcwMjgsImV4aXN0aW5nIjp0cnVlfQ==; learned_about_new_editor=1; user_history=%5B%7B%22ref%22%3A%22Genesis%201%3A3%22%2C%22versions%22%3A%7B%22en%22%3A%7B%22languageFamilyName%22%3A%22%22%2C%22versionTitle%22%3A%22%22%7D%2C%22he%22%3A%7B%22languageFamilyName%22%3A%22%22%2C%22versionTitle%22%3A%22%22%7D%7D%2C%22book%22%3A%22Genesis%22%2C%22language%22%3A%22bilingual%22%2C%22time_stamp%22%3A1760642812%2C%22he_ref%22%3A%22%D7%91%D7%A8%D7%90%D7%A9%D7%99%D7%AA%20%D7%90%D7%B3%3A%D7%92%D7%B3%22%7D%2C%7B%22ref%22%3A%22Deuteronomy%2032%3A1%22%2C%22versions%22%3A%7B%22en%22%3A%7B%22languageFamilyName%22%3A%22%22%2C%22versionTitle%22%3A%22%22%7D%2C%22he%22%3A%7B%22languageFamilyName%22%3A%22%22%2C%22versionTitle%22%3A%22%22%7D%7D%2C%22book%22%3A%22Deuteronomy%22%2C%22language%22%3A%22bilingual%22%2C%22time_stamp%22%3A1759519790%2C%22he_ref%22%3A%22%D7%93%D7%91%D7%A8%D7%99%D7%9D%20%D7%9C%D7%B4%D7%91%3A%D7%90%D7%B3%22%7D%2C%7B%22ref%22%3A%22Deuteronomy%2032%22%2C%22versions%22%3A%7B%22en%22%3A%7B%22languageFamilyName%22%3A%22%22%2C%22versionTitle%22%3A%22%22%7D%2C%22he%22%3A%7B%22languageFamilyName%22%3A%22%22%2C%22versionTitle%22%3A%22%22%7D%7D%2C%22book%22%3A%22Deuteronomy%22%2C%22language%22%3A%22bilingual%22%2C%22time_stamp%22%3A1759344578%2C%22he_ref%22%3A%22%D7%93%D7%91%D7%A8%D7%99%D7%9D%20%D7%9C%D7%B4%D7%91%22%7D%2C%7B%22ref%22%3A%22Deuteronomy.32.1-52%22%2C%22versions%22%3A%7B%22en%22%3A%7B%22languageFamilyName%22%3A%22%22%2C%22versionTitle%22%3A%22%22%7D%2C%22he%22%3A%7B%22languageFamilyName%22%3A%22%22%2C%22versionTitle%22%3A%22%22%7D%7D%2C%22book%22%3A%22Deuteronomy%22%2C%22language%22%3A%22bilingual%22%2C%22time_stamp%22%3A1759171208%2C%22he_ref%22%3A%22%D7%93%D7%91%D7%A8%D7%99%D7%9D%20%D7%9C%D7%B4%D7%91%3A%D7%90%D7%B3-%D7%A0%D7%B4%D7%91%22%7D%2C%7B%22ref%22%3A%22Deuteronomy%2032%3A1-52%22%2C%22versions%22%3A%7B%22en%22%3A%7B%7D%2C%22he%22%3A%7B%7D%7D%2C%22book%22%3A%22Deuteronomy%22%2C%22language%22%3A%22bilingual%22%2C%22time_stamp%22%3A1759080365%2C%22he_ref%22%3A%22%D7%93%D7%91%D7%A8%D7%99%D7%9D%20%D7%9C%D7%B4%D7%91%3A%D7%90%D7%B3-%D7%A0%D7%B4%D7%91%22%7D%2C%7B%22ref%22%3A%22Deuteronomy%2029%22%2C%22versions%22%3A%7B%22en%22%3A%7B%7D%2C%22he%22%3A%7B%7D%7D%2C%22book%22%3A%22Deuteronomy%22%2C%22language%22%3A%22bilingual%22%2C%22time_stamp%22%3A1757866566%2C%22he_ref%22%3A%22%D7%93%D7%91%D7%A8%D7%99%D7%9D%20%D7%9B%D7%B4%D7%98%22%7D%2C%7B%22ref%22%3A%22Deuteronomy%2029%22%2C%22versions%22%3A%7B%22en%22%3A%7B%7D%2C%22he%22%3A%7B%7D%7D%2C%22book%22%3A%22Deuteronomy%22%2C%22language%22%3A%22bilingual%22%2C%22time_stamp%22%3A1757866562%2C%22he_ref%22%3A%22%D7%93%D7%91%D7%A8%D7%99%D7%9D%20%D7%9B%D7%B4%D7%98%22%7D%2C%7B%22ref%22%3A%22Deuteronomy%2030%3A1-20%22%2C%22versions%22%3A%7B%22en%22%3A%7B%7D%2C%22he%22%3A%7B%7D%7D%2C%22book%22%3A%22Deuteronomy%22%2C%22language%22%3A%22bilingual%22%2C%22time_stamp%22%3A1757866556%2C%22he_ref%22%3A%22%D7%93%D7%91%D7%A8%D7%99%D7%9D%20%D7%9C%D7%B3%3A%D7%90%D7%B3-%D7%9B%D7%B3%22%7D%2C%7B%22ref%22%3A%22Deuteronomy%2029%3A9-30%3A20%22%2C%22versions%22%3A%7B%22en%22%3A%7B%7D%2C%22he%22%3A%7B%7D%7D%2C%22book%22%3A%22Deuteronomy%22%2C%22language%22%3A%22bilingual%22%2C%22time_stamp%22%3A1757866555%2C%22he_ref%22%3A%22%D7%93%D7%91%D7%A8%D7%99%D7%9D%20%D7%9B%D7%B4%D7%98%3A%D7%98%D7%B3-%D7%9C%D7%B3%3A%D7%9B%D7%B3%22%7D%5D; guide_overlay_seen_editor=2025-10-27T20:08:14.761Z; csrftoken=qSa3i9GgsAnrqF9XrU6GTnrPtltoShE5J9EboBT6ZCx9n758bCa2epS3Dcbid64Z; sessionid=ph68w5pmrnkzqky1dfqw5c625zx1damu; contentLang=bilingual; language=bilingual; version_preferences_by_corpus=%7B%22Bavli%22%3A%7B%22en%22%3A%22William%20Davidson%20Edition%20-%20English%22%7D%7D"

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
    Returns a list of dictionaries containing basic info (id, title).
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

def create_backup(session: requests.Session, sheets_to_backup: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    """
    Fetches full data for every sheet in the list and saves to a local JSON file.
    Returns the list of full sheet data objects.
    """
    print(f"\n--- 💾 Starting Backup of {len(sheets_to_backup)} sheets ---")
    full_data_list = []
    
    for idx, sheet_info in enumerate(sheets_to_backup, 1):
        sheet_id = sheet_info['id']
        title = sheet_info['title']
        print(f"  [{idx}/{len(sheets_to_backup)}] Fetching data for: '{title}' (ID: {sheet_id})...")
        
        try:
            response = session.get(f"https://www.sefaria.org/api/sheets/{sheet_id}")
            response.raise_for_status()
            sheet_data = response.json()
            full_data_list.append(sheet_data)
        except Exception as e:
            print(f"    ❌ Failed to fetch data for {title}: {e}")
            # Skipping backup for this item, which effectively skips processing
            continue
            
        time.sleep(0.5) # Rate limiting

    # Generate filename with today's date
    today = datetime.date.today().isoformat()
    filename = f"{today}_backup.json"
    
    try:
        with open(filename, 'w', encoding='utf-8') as f:
            json.dump(full_data_list, f, indent=4, ensure_ascii=False)
        print(f"✅ Backup successfully saved to: {filename}")
        print(f"--- Backup Complete ---\n")
    except Exception as e:
        print(f"❌ Failed to write backup file: {e}")
        return []
        
    return full_data_list

def publish_sheet_from_data(session: requests.Session, csrf_token: str, sheet_data: Dict[str, Any]) -> bool:
    """
    Takes full sheet data (from backup), modifies it in-memory, deletes the old ID, 
    and creates a new public sheet.
    Returns True on success, False on failure.
    """
    old_id = sheet_data.get("id")
    title = sheet_data.get("title", "Untitled")
    
    print(f"  Processing '{title}' (Old ID: {old_id})...")

    delete_url = f"https://www.sefaria.org/api/sheets/{old_id}/delete"
    create_url = "https://www.sefaria.org/api/sheets/"

    common_headers = {
        'accept': '*/*',
        'accept-language': 'en-US,en;q=0.9',
        'content-type': 'application/x-www-form-urlencoded; charset=UTF-8',
        'origin': 'https://www.sefaria.org',
        'referer': 'https://www.sefaria.org/sheets/',
        'sec-ch-ua': '"Google Chrome";v="141", "Not?A_Brand";v="8", "Chromium";v="141"',
        'sec-ch-ua-mobile': '?0',
        'sec-ch-ua-platform': '"Linux"',
        'sec-fetch-dest': 'empty',
        'sec-fetch-mode': 'cors',
        'sec-fetch-site': 'same-origin',
        'user-agent': 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/141.0.0.0 Safari/537.36',
        'x-csrftoken': csrf_token,
        'x-requested-with': 'XMLHttpRequest',
    }

    try:
        # 1. Modify Data in Memory (Working on a copy)
        new_data = sheet_data.copy()
        
        new_data["status"] = "public"
        new_data["collectionName"] = "DafReactions"
        new_data["collectionImage"] = None
        
        if "options" in new_data:
            new_data["options"]["collaboration"] = "group-can-edit"
        else:
            new_data["options"] = {"collaboration": "group-can-edit"}
        
        if "tags" not in new_data or new_data["tags"] is None:
            new_data["tags"] = []
        if "DafReactions" not in new_data["tags"]:
            new_data["tags"].append("DafReactions")
            
        if "topics" not in new_data or not new_data["topics"]:
             new_data["topics"] = [{"asTyped": "Talmud", "slug": "talmud", "en": "Talmud","he": "תלמוד"}]
        
        if "summary" not in new_data or not new_data["summary"]:
             new_data["summary"] = "A Daf Reactions sheet."

        # Clean keys strictly for creation
        new_data.pop("_id", None)
        new_data.pop("id", None)
        new_data.pop("dateCreated", None)
        new_data.pop("dateModified", None)
        
        # 2. DELETE Old Sheet
        # We try to delete using specific headers to mimic browser behavior
        delete_headers = common_headers.copy()
        
        # --- FIX: Handle 'owner' whether it is a dict or an int ---
        owner_data = sheet_data.get("owner")
        owner_id = ""
        
        if isinstance(owner_data, dict):
            owner_id = owner_data.get("id", "")
        elif isinstance(owner_data, int):
            owner_id = owner_data
            
        if owner_id:
            delete_headers['referer'] = f'https://www.sefaria.org/profile/{owner_id}?tab=sheets'
        
        print(f"    -> Deleting old sheet {old_id}...")
        del_res = session.post(delete_url, headers=delete_headers)
        
        # If 404, it means it's already deleted (perhaps from a previous failed run). 
        # We can proceed to create.
        if del_res.status_code == 404:
            print("    -> Sheet not found (404). Assuming already deleted. Proceeding...")
        else:
            del_res.raise_for_status()
            print("    -> Delete successful.")

        # 3. CREATE New Sheet
        print(f"    -> Creating new public sheet...")
        form_data = {"json": json.dumps(new_data)}
        create_res = session.post(create_url, headers=common_headers, data=form_data)
        create_res.raise_for_status()
        
        new_info = create_res.json()
        new_url = new_info.get("url", "Unknown URL")
        print(f"    + Created successfully! New URL: {new_url}")
        return True

    except Exception as e:
        print(f"    ❌ FAILED to publish '{title}': {e}")
        return False

def main():
    """Main execution function."""
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

    # 1. Identify sheets
    unpublished_summaries = get_unpublished_sheet_summaries(session, user_id)
    
    if not unpublished_summaries:
        print("No unpublished sheets found. All done!")
        return

    print(f"\nFound {len(unpublished_summaries)} unpublished sheets.")
    for i, sheet in enumerate(unpublished_summaries, 1):
        print(f"  {i}. {sheet['title']} (ID: {sheet['id']})")
    
    print("\n---")
    print("WARNING: This script will:")
    print("1. BACKUP all these sheets to a local file.")
    print("2. DELETE the originals from Sefaria.")
    print("3. RE-CREATE them as public sheets (generating new URLs).")
    choice = input(f"Do you want to proceed? (yes/no): ").strip().lower()
    
    if choice not in ['yes', 'y']:
        print("Aborting.")
        return

    # 2. Backup full data
    full_sheets_data = create_backup(session, unpublished_summaries)
    
    if not full_sheets_data:
        print("Backup failed or returned no data. Aborting to be safe.")
        return

    # 3. Process (Delete -> Create)
    failed_sheets = []
    print("\n--- 🚀 Starting Publishing Process ---")
    
    for sheet in full_sheets_data:
        success = publish_sheet_from_data(session, csrf_token, sheet)
        if not success:
            failed_sheets.append(sheet)
        
        # Be nice to API
        time.sleep(2)

    # 4. Retry Logic
    if failed_sheets:
        print(f"\n⚠️  Finished, but {len(failed_sheets)} sheets FAILED to process.")
        retry_choice = input("Do you want to retry the failed sheets using the backup data? (yes/no): ").strip().lower()
        
        if retry_choice in ['yes', 'y']:
            print("\n--- 🔄 Retrying Failed Sheets ---")
            still_failed = []
            
            for sheet in failed_sheets:
                if not publish_sheet_from_data(session, csrf_token, sheet):
                    still_failed.append(sheet)
                time.sleep(2)
            
            if still_failed:
                print(f"\n❌ Retry complete. {len(still_failed)} sheets still failed. Please check logs/backup.")
            else:
                print("\n✅ All retries successful!")
        else:
            print("Skipping retry. Data for failed sheets is safe in your backup file.")
    else:
        print("\n✨ Success! All sheets published.")

if __name__ == "__main__":
    main()