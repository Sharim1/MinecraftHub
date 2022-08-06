from apiclient.discovery import build
from googleapiclient.errors import HttpError
import logging
import os
from pathlib import Path
from dotenv import load_dotenv


logger = logging.getLogger(__name__)

dotenv_path = Path(__file__).resolve().parent.parent / 'bulkystar.env'
load_dotenv(dotenv_path=dotenv_path)

api_key = os.getenv('API_KEY')

class YouTube:
    def get_data(self):
        try:
            youtube = build('youtube', 'v3', developerKey=api_key, cache_discovery=False)
            res = youtube.channels().list(id='UC8ZzyNuoZDFeXGDJsB0o-8A', part='contentDetails').execute()
            playlist_id = res['items'][0]['contentDetails']['relatedPlaylists']['uploads']
            logger.info("Got the playlist id - {}".format(playlist_id))
            videos = []
            data=[]
            next_page_token = None
            logger.info("Looping over playlist items i.e., all the latest videos.")
            while True:
                res = youtube.playlistItems().list(playlistId=playlist_id, part='snippet', maxResults=50, pageToken=next_page_token).execute()
                videos += res['items']
                next_page_token = res.get('nextPageToken')
                if next_page_token is None:
                    break
            videos += res['items']
            next_page_token = res.get('nextPageToken')
            for video in videos:
                vid_data={
                    "id": video["id"],
                    "title":video["snippet"]["title"],
                    "thumbnail":video["snippet"]["thumbnails"]["high"]["url"],
                    "iframe":video["snippet"]["resourceId"]["videoId"],
                }
                data.append(vid_data)
            logger.info("Successfully got the youtube data, returning it now.")
            return data
        except HttpError as e:
            logger.error("HTTPError - Unable to get a proper response. \
                Response Status - {}, Content - {}, Error - {}".format(e.resp.status, e.content, e))
            return (e.resp.status, e.content)
        except Exception as e:
            logger.error("Unable to get a proper response. Error - {}").format(e)
