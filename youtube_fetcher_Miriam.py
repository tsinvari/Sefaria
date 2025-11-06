import json
import time
import random
import yt_dlp
from datetime import datetime

def prepare_data_from_youtube(channel_url, output_file_path):
    """
    Fetches video data from a YouTube channel and saves it to a JSON file.
    
    Args:
        channel_url (str): The URL of the YouTube channel's video page (e.g., https://www.youtube.com/@user/videos)
        output_file_path (str): Path to save the output JSON file.
    """
    print(f"🔍 Fetching video list from {channel_url}...")
    print("This may take a while (~45 minutes for ~450 videos). Please be patient.\n")

    # yt-dlp configuration for stable metadata-only extraction
    ydl_opts = {
        'quiet': False,                # Show progress info
        'ignoreerrors': True,          # Skip problematic videos
        'extract-flat': False,          # Metadata only (faster, avoids SABR)
        'sleep-interval': 10,           # Minimum delay between requests
        'retries': 10,                  # Retry a few times if a request fails
        'noplaylist': False,           # Allow full channel playlists
        'skip-download': True,
    }

    videos = []
    try:
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info_dict = ydl.extract_info(channel_url, download=False)
            videos = info_dict.get('entries', [])
    except Exception as e:
        print(f"❌ Error: Could not fetch video data from YouTube.\n{e}")
        return

    if not videos:
        print("⚠️ No videos found on the channel. Please check the URL or update yt-dlp.")
        return

    print(f"✅ Found {len(videos)} videos. Starting detailed extraction...\n")

    prepared_data = []
    total = len(videos)
    processed = 0

    for video in videos:
        if not video:
            continue

        title = video.get('title')
        if not title:
            continue

        youtube_url = video.get('url') or video.get('webpage_url')
        description = video.get('description', '')

        prepared_data.append({
            "title": title,
            "paragraph": description,
            "youtube_url": f"https://www.youtube.com/watch?v={video.get('id')}" if video.get('id') else youtube_url,
        })

        processed += 1
        print(f"[{processed}/{total}] ✅ Processed: {title[:70]}...")

        # Random delay between 5–8 seconds to average ~6s/video
        time.sleep(20)

    # Save results to JSON
    try:
        with open(output_file_path, 'w', encoding='utf-8') as f:
            json.dump(prepared_data, f, indent=4, ensure_ascii=False)
        print(f"\n🎉 Successfully saved data for {len(prepared_data)} videos to '{output_file_path}'")
    except Exception as e:
        print(f"💾 Error writing JSON file: {e}")


if __name__ == "__main__":
    # Channel to extract from
    #YOUTUBE_CHANNEL_URL = "https://www.youtube.com/playlist?list=UUAM7ylcgdb_dkvvrnEmLp0w"
    #first try
    #YOUTUBE_CHANNEL_URL = "https://www.youtube.com/@miriamanzovin/videos"

    #DafReactions
    #YOUTUBE_CHANNEL_URL = "https://www.youtube.com/playlist?list=PL3H5E_FUM3AflOq7R_bc78nJunkHxiVVz"
    
    #Jewish Lore Reactions
    #YOUTUBE_CHANNEL_URL = "https://www.youtube.com/watch?v=9w7KG0BbP9E&list=PL3H5E_FUM3AdJ_EWrUSXV9MD2BlsJJMXm"

    #The Reels Megillah
    #YOUTUBE_CHANNEL_URL = "https://www.youtube.com/watch?v=ESsoYqo0-ds&list=PL3H5E_FUM3AfwO38C6zlOy_InwdESGWB_"

    #Jewish Book Reactions
    #YOUTUBE_CHANNEL_URL = "https://www.youtube.com/watch?v=XkEUy90wRWU&list=PL3H5E_FUM3Afkbg4ZczJIy4MoG8imCYsC"

    #Chevruta
    #YOUTUBE_CHANNEL_URL = "https://www.youtube.com/watch?v=J3wbahwQLdI&list=PL3H5E_FUM3AeBUtQelCxRMvjQ7QJZD12S"

    #Jewish Holiday Reactions
    #YOUTUBE_CHANNEL_URL = "https://www.youtube.com/watch?v=ZKqdR5tzWw0&list=PL3H5E_FUM3AfM7l9XNT573C9kO9Y0k61D"

    #Exodus Reactions
    #YOUTUBE_CHANNEL_URL = "https://www.youtube.com/watch?v=WZn7Qu1PnD0&list=PL3H5E_FUM3Ac7PEPgFzfMr4sewvSTOn60"

    #Megillah Reactions
    #YOUTUBE_CHANNEL_URL = "https://www.youtube.com/watch?v=iik3Zh5tTAs&list=PL3H5E_FUM3AcWTlkLlQlD_ScLAYJMomgj"

    #Parsha Reactions
    YOUTUBE_CHANNEL_URL = "https://www.youtube.com/watch?v=IK8z6hW8Ols&list=PL3H5E_FUM3Ae0-vKOpgIdHchZAvfYfwSp"

    # Generate output filename using current date
    current_date = datetime.now().strftime("%Y-%m-%d")
    output_file_name = f"{current_date}_preparedata_ParshaReactions.json"

    print(f"🗓 Output file will be saved as: {output_file_name}\n")

    prepare_data_from_youtube(YOUTUBE_CHANNEL_URL, output_file_name)
