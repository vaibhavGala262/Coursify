from googleapiclient.discovery import build
import os


api_key = os.getenv('YOUTUBE_API_KEY')

def get_yt_links():
    youtube = build("youtube", "v3", developerKey=api_key)
    query = "Parabola Math" 
    max_results= 5
    response = youtube.search().list(
        q=query,
        part="snippet",
        type="video",
        videoDuration="long",
        maxResults=max_results
    ).execute()

    results = []
    
    for item in response["items"]:
        title = item["snippet"]["title"]
        video_id = item["id"]["videoId"]
        video_url = f"https://www.youtube.com/watch?v={video_id}"
        results.append({"title": title, "url": video_url})

    return results
