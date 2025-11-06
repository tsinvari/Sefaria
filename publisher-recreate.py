import json
import requests
import time
import re
import urllib.parse
from typing import Dict, Any, Optional, List

# --- PASTE THE SAME COOKIE STRING FROM poster.py ---
COOKIE_STR = "_user=%7B%22_uid%22%3A30698%7D; version_preferences_by_corpus=%7B%22Bavli%22%3A%7B%22en%22%3A%22William%20Davidson%20Edition%20-%20English%22%7D%7D; interfaceLang=english; user_history=%5B%7B%22ref%22%3A%22Klein%20Dictionary%2C%20%D7%92%D7%95%D7%A3%201%22%2C%22versions%22%3A%7B%22en%22%3A%7B%22languageFamilyName%22%3A%22%22%2C%22versionTitle%22%3A%22%22%7D%2C%22he%22%3A%7B%22languageFamilyName%22%3A%22%22%2C%22versionTitle%22%3A%22%22%7D%7D%2C%22book%22%3A%22Klein%20Dictionary%2C%20%D7%92%D7%95%D7%A3%22%2C%22language%22%3A%22bilingual%22%2C%22time_stamp%22%3A1759748745%2C%22he_ref%22%3A%22%D7%9E%D7%99%D7%9C%D7%95%D7%9F%20%D7%A7%D7%9C%D7%99%D7%99%D7%9F%2C%20%D7%92%D7%95%D7%A3%20%D7%90%D7%B3%22%7D%2C%7B%22ref%22%3A%22Klein%20Dictionary%2C%20%D7%92%D7%95%D7%A3%201%22%2C%22versions%22%3A%7B%22en%22%3A%7B%22languageFamilyName%22%3A%22%22%2C%22versionTitle%22%3A%22%22%7D%2C%22he%22%3A%7B%22languageFamilyName%22%3A%22%22%2C%22versionTitle%22%3A%22%22%7D%7D%2C%22book%22%3A%22Klein%20Dictionary%2C%20%D7%92%D7%95%D7%A3%22%2C%22language%22%3A%22bilingual%22%2C%22time_stamp%22%3A1759748741%2C%22he_ref%22%3A%22%D7%9E%D7%99%D7%9C%D7%95%D7%9F%20%D7%A7%D7%9C%D7%99%D7%99%D7%9F%2C%20%D7%92%D7%95%D7%A3%20%D7%90%D7%B3%22%7D%2C%7B%22ref%22%3A%22Rashi%20on%20Deuteronomy%2032%3A2%3A1%22%2C%22versions%22%3A%7B%22en%22%3A%7B%22languageFamilyName%22%3A%22%22%2C%22versionTitle%22%3A%22%22%7D%2C%22he%22%3A%7B%22languageFamilyName%22%3A%22%22%2C%22versionTitle%22%3A%22%22%7D%7D%2C%22book%22%3A%22Rashi%20on%20Deuteronomy%22%2C%22language%22%3A%22hebrew%22%2C%22time_stamp%22%3A1759403090%2C%22he_ref%22%3A%22%D7%A8%D7%A9%5C%22%D7%99%20%D7%A2%D7%9C%20%D7%93%D7%91%D7%A8%D7%99%D7%9D%20%D7%9C%D7%B4%D7%91%3A%D7%91%D7%B3%3A%D7%90%D7%B3%22%7D%2C%7B%22ref%22%3A%22Judaism\'s%20Life%20Changing%20Ideas%3B%20A%20Weekly%20Reading%20of%20the%20Jewish%20Bible%2C%20Haazinu%3B%20Emotional%20Intelligence%2019%22%2C%22versions%22%3A%7B%22en%22%3A%7B%22languageFamilyName%22%3A%22%22%2C%22versionTitle%22%3A%22%22%7D%2C%22he%22%3A%7B%22languageFamilyName%22%3A%22%22%2C%22versionTitle%22%3A%22%22%7D%7D%2C%22book%22%3A%22Judaism\'s%20Life%20Changing%20Ideas%3B%20A%20Weekly%20Reading%20of%20the%20Jewish%20Bible%2C%20Haazinu%3B%20Emotional%20Intelligence%22%2C%22language%22%3A%22hebrew%22%2C%22time_stamp%22%3A1759403088%2C%22he_ref%22%3A%22%D7%A8%D7%A2%D7%99%D7%95%D7%A0%D7%95%D7%AA%20%D7%9E%D7%A9%D7%A0%D7%99%20%D7%97%D7%99%D7%99%D7%9D%3B%20%D7%A7%D7%A8%D7%99%D7%90%D7%95%D7%AA%20%D7%97%D7%93%D7%A9%D7%95%D7%AA%20%D7%91%D7%A4%D7%A8%D7%A9%D7%AA%20%D7%94%D7%A9%D7%91%D7%95%D7%A2%2C%20%D7%94%D7%90%D7%96%D7%99%D7%A0%D7%95%20%D7%99%D7%B4%D7%98%22%7D%2C%7B%22ref%22%3A%22Rashi%20on%20Deuteronomy%2032%3A2%3A1%22%2C%22versions%22%3A%7B%22en%22%3A%7B%22languageFamilyName%22%3A%22%22%2C%22versionTitle%22%3A%22%22%7D%2C%22he%22%3A%7B%22languageFamilyName%22%3A%22%22%2C%22versionTitle%22%3A%22%22%7D%7D%2C%22book%22%3A%22Rashi%20on%20Deuteronomy%22%2C%22language%22%3A%22hebrew%22%2C%22time_stamp%22%3A1759401932%2C%22he_ref%22%3A%22%D7%A8%D7%A9%5C%22%D7%99%20%D7%A2%D7%9C%20%D7%93%D7%91%D7%A8%D7%99%D7%9D%20%D7%9C%D7%B4%D7%91%3A%D7%91%D7%B3%3A%D7%90%D7%B3%22%7D%2C%7B%22ref%22%3A%22Judaism\'s%20Life%20Changing%20Ideas%3B%20A%20Weekly%20Reading%20of%20the%20Jewish%20Bible%2C%20Haazinu%3B%20Emotional%20Intelligence%2019%22%2C%22versions%22%3A%7B%22en%22%3A%7B%22languageFamilyName%22%3A%22%22%2C%22versionTitle%22%3A%22%22%7D%2C%22he%22%3A%7B%22languageFamilyName%22%3A%22%22%2C%22versionTitle%22%3A%22%22%7D%7D%2C%22book%22%3A%22Judaism\'s%20Life%20Changing%20Ideas%3B%20A%20Weekly%20Reading%20of%20the%20Jewish%20Bible%2C%20Haazinu%3B%20Emotional%20Intelligence%22%2C%22language%22%3A%22hebrew%22%2C%22time_stamp%22%3A1759390965%2C%22he_ref%22%3A%22%D7%A8%D7%A2%D7%99%D7%95%D7%A0%D7%95%D7%AA%20%D7%9E%D7%A9%D7%A0%D7%99%20%D7%97%D7%99%D7%99%D7%9D%3B%20%D7%A7%D7%A8%D7%99%D7%90%D7%95%D7%AA%20%D7%97%D7%93%D7%A9%D7%95%D7%AA%20%D7%91%D7%A4%D7%A8%D7%A9%D7%AA%20%D7%94%D7%A9%D7%91%D7%95%D7%A2%2C%20%D7%94%D7%90%D7%96%D7%99%D7%A0%D7%95%20%D7%99%D7%B4%D7%98%22%7D%5D; guide_overlay_seen_editor=2025-10-20T11:38:40.366Z; csrftoken=ql3KgZ2YfoC9ZaevU75oYKs2pfIaJ3gcALuX03Y9WFrXMxn8gEAEBqRYlQG88p6G; sessionid=aw4yay7divnnkkiyb3ukl8awngael91r; open_trans_banner_shown=1; contentLang=bilingual; language=bilingual"
# -------------------------------------------

# --- Re-used functions from poster.py ---

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

# --- New functions for publisher.py ---

def extract_user_id(cookie_dict: Dict[str, str]) -> int:
    """Extracts the Sefaria User ID from the cookie dictionary."""
    user_cookie_str = cookie_dict.get("_user")
    if not user_cookie_str:
        raise ValueError("Could not find '_user' cookie. Is it part of your COOKIE_STR?")
    
    try:
        # URL-decode the cookie string (e.g., %7B -> {)
        decoded_str = urllib.parse.unquote(user_cookie_str)
        # Load the decoded string as JSON
        user_data = json.loads(decoded_str)
        
        user_id = user_data.get("_uid")
        if not user_id:
            raise ValueError("Found '_user' cookie but it doesn't contain '_uid'.")
        
        return int(user_id)
    except (json.JSONDecodeError, TypeError, ValueError) as e:
        print(f"Error parsing user cookie: {e}")
        raise ValueError(f"Could not parse user ID from cookie: {user_cookie_str}")

def get_unpublished_sheets(session: requests.Session, user_id: int) -> List[Dict[str, Any]]:
    """
    Fetches all sheets for a user.
    Prints details of the first public and first unlisted sheet found.
    Returns a list of the 'unlisted' ones for processing.
    """
    api_url = f"https://www.sefaria.org/api/sheets/user/{user_id}"
    print(f"Fetching sheets for user {user_id} from {api_url}...")
    
    try:
        response = session.get(api_url)
        response.raise_for_status()
        data = response.json()
        
        all_sheets = data.get("sheets", [])
        if not all_sheets:
            print("No sheets found for this user.")
            return []

        unpublished_sheets = []
        published_sheets = []
        
        # Filter sheets into two lists
        for sheet in all_sheets:
            if sheet.get("status") == "unlisted": # Sefaria uses "unlisted" for private
                unpublished_sheets.append({
                    "id": sheet.get("id"),
                    "title": sheet.get("title", "Untitled")
                })
            elif sheet.get("status") == "public":
                published_sheets.append({
                    "id": sheet.get("id"),
                    "title": sheet.get("title", "Untitled")
                })
        """
        print("\n--- Debugging: Full Sheet Data Inspection ---")
       
        # 1. Print data for the first PUBLIC sheet found
        if published_sheets:
            print(f"\nFound {len(published_sheets)} PUBLIC sheets.")
            first_public_id = published_sheets[0]['id']
            print(f"Fetching full details for first public sheet (ID: {first_public_id}) for comparison...")
            try:
                sheet_detail_res = session.get(f"https://www.sefaria.org/api/sheets/{first_public_id}")
                sheet_detail_res.raise_for_status()
                public_sheet_data = sheet_detail_res.json()
                print(f"--- Data for PUBLIC sheet '{published_sheets[0]['title']}' ---")
                print(json.dumps(public_sheet_data, indent=2))
                print("--------------------------------------------------")
            except requests.exceptions.RequestException as e:
                print(f"  - Could not fetch details for public sheet {first_public_id}: {e}")
        else:
            print("\nFound 0 PUBLIC sheets.")

        # 2. Print data for the first UNLISTED sheet found
        if unpublished_sheets:
            print(f"\nFound {len(unpublished_sheets)} UNLISTED sheets.")
            first_unlisted_id = unpublished_sheets[0]['id']
            print(f"Fetching full details for first unlisted sheet (ID: {first_unlisted_id}) for inspection...")
            try:
                sheet_detail_res = session.get(f"https://www.sefaria.org/api/sheets/{first_unlisted_id}")
                sheet_detail_res.raise_for_status()
                unlisted_sheet_data = sheet_detail_res.json()
                print(f"--- Data for UNLISTED sheet '{unpublished_sheets[0]['title']}' ---")
                print(json.dumps(unlisted_sheet_data, indent=2))
                print("----------------------------------------------------")
            except requests.exceptions.RequestException as e:
                print(f"  - Could not fetch details for unlisted sheet {first_unlisted_id}: {e}")
        else:
            print("\nFound 0 UNLISTED sheets.")
        
        print("\n--- End of Debugging Inspection ---")"""
        
        # Return only the list of sheets we want to process
        return unpublished_sheets
        
    except requests.exceptions.RequestException as e:
        print(f"Error fetching sheets: {e}")
        return []

def publish_single_sheet_by_recreate(session: requests.Session, csrf_token: str, sheet_id: int, title: str):
    """
    Publishes a sheet by GETTING its data, DELETING it, and RE-CREATING it as public.
    """
    print(f"  Re-creating '{title}' (ID: {sheet_id}) as public...")
    
    get_url = f"https://www.sefaria.org/api/sheets/{sheet_id}"
    # --- FIX 1: Use the /delete URL ---
    delete_url = f"https://www.sefaria.org/api/sheets/{sheet_id}/delete"
    create_url = "https://www.sefaria.org/api/sheets/"

    # Headers for GET and CREATE
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
        # 1. GET the full sheet data
        get_response = session.get(get_url)
        get_response.raise_for_status()
        sheet_data = get_response.json()
        print(f"    -> Got data for sheet {sheet_id}")

        # 2. Modify the data in-memory to be "create-ready"
        sheet_data["status"] = "public"
        sheet_data["collectionName"] = "DafReactions"
        sheet_data["collectionImage"] = None
        
        if "options" in sheet_data:
            sheet_data["options"]["collaboration"] = "group-can-edit"
        
        if "tags" not in sheet_data or sheet_data["tags"] is None:
            sheet_data["tags"] = []
        if "DafReactions" not in sheet_data["tags"]:
            sheet_data["tags"].append("DafReactions")
            
        if "topics" not in sheet_data or not sheet_data["topics"]:
             sheet_data["topics"] = [{"asTyped": "Talmud", "slug": "talmud", "en": "Talmud","he": "תלמוד"}]
        
        if "summary" not in sheet_data or not sheet_data["summary"]:
             sheet_data["summary"] = "A Daf Reactions sheet."

        # Remove keys that should not be sent on CREATE
        if "_id" in sheet_data:
            del sheet_data["_id"]
        if "id" in sheet_data:
            del sheet_data["id"] # Don't send the old numeric ID
        
        print(f"    -> Prepared new public payload for '{title}'")

        # 3. DELETE the old sheet
        print(f"    -> Deleting old sheet {sheet_id}...")
        
        # --- FIX 2: Create delete_headers based on user's cURL ---
        delete_headers = {
            'User-Agent': common_headers['user-agent'],
            'accept': 'application/json, text/javascript, */*; q=0.01',
            'accept-language': 'en-US,en;q=0.9,es-419;q=0.8,es;q=0.7,fr-FR;q=0.6,fr;q=0.5,he;q=0.4',
            'x-csrftoken': csrf_token, 
            'x-requested-with': 'XMLHttpRequest', 
            'sec-fetch-dest': 'empty',
            'sec-fetch-mode': 'cors',
            'sec-fetch-site': 'same-origin',
            'referer': 'https://www.sefaria.org/profile/rene-michel?tab=sheets', # From cURL
            'dnt': '1',
            'priority': 'u=1, i',
        }
        
        # --- FIX 3: Use session.post() for the delete request ---
        delete_response = session.post(delete_url, headers=delete_headers)
        delete_response.raise_for_status()
        print(f"    -> Successfully deleted old sheet {sheet_id}.")

        # 4. CREATE the new sheet
        print(f"    -> Creating new public sheet for '{title}'...")
        form_data = {"json": json.dumps(sheet_data)}
        create_response = session.post(create_url, headers=common_headers, data=form_data)
        create_response.raise_for_status()
        
        new_sheet_data = create_response.json()
        new_url = new_sheet_data.get("url")
        print(f"  + Successfully RE-CREATED sheet. New URL: {new_url}")
        return True

    except requests.exceptions.RequestException as e:
        print(f"  - FAILED to re-create '{title}'. Error: {e}")
        if e.response is not None:
            print(f"    Response Status: {e.response.status_code}")
            print(f"    Response Content: {e.response.text}")
        print("    !!! The original sheet may have been DELETED but not re-created. !!!")
        print(f"    !!! Find the data for '{title}' (ID: {sheet_id}) in your logs and re-create it manually. !!!")
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

    unpublished_sheets = get_unpublished_sheets(session, user_id)
    
    if not unpublished_sheets:
        print("No unpublished sheets found. All done!")
        return

    print(f"\nFound {len(unpublished_sheets)} unpublished sheets:")
    for i, sheet in enumerate(unpublished_sheets, 1):
        print(f"  {i}. {sheet['title']} (ID: {sheet['id']})")
    
    print("\n---")
    print("WARNING: This script will DELETE and then RE-CREATE each sheet.")
    print("This will change their URLs and creation dates.")
    choice = input(f"Do you want to publish all {len(unpublished_sheets)} sheets this way? (yes/no): ").strip().lower()
    
    if choice in ['yes', 'y']:
        print("\nStarting publishing process (Delete & Re-create)...")
        success_count = 0
        fail_count = 0
        
        for sheet in unpublished_sheets:
            # Pass the new function name here
            if publish_single_sheet_by_recreate(session, csrf_token, sheet['id'], sheet['title']):
                success_count += 1
            else:
                fail_count += 1
            time.sleep(2) # Be extra nice to the API since we're doing 3 requests
        
        print("\n---")
        print("Publishing complete.")
        print(f"  Successfully re-created: {success_count}")
        print(f"  Failed to re-create:     {fail_count}")
        
    else:
        print("Aborting. No sheets were published.")

if __name__ == "__main__":
    main()