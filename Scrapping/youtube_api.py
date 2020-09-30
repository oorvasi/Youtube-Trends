import os
import pickle
import json
import pprint
import requests
import pandas as pd
import google.oauth2.credentials
 
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request

pp = pprint.PrettyPrinter(indent=4)

# The CLIENT_SECRETS_FILE variable specifies the name of a file that contains
# the OAuth 2.0 information for this application, including its client_id and
# client_secret.
CLIENT_SECRETS_FILE = "client_secret.json" # upload your own key API	

# This OAuth 2.0 access scope allows for full read/write access to the
# authenticated user's account and requires requests to use an SSL connection.
SCOPES = ['https://www.googleapis.com/auth/youtube.force-ssl']
API_SERVICE_NAME = 'youtube'
API_VERSION = 'v3'

def get_authenticated_service():
    credentials = None
    if os.path.exists('token.pickle'):
        with open('token.pickle', 'rb') as token:
            credentials = pickle.load(token)
    #  Check if the credentials are invalid or do not exist
    if not credentials or not credentials.valid:
        # Check if the credentials have expired
        if credentials and credentials.expired and credentials.refresh_token:
            credentials.refresh(Request())
        else:
            flow = InstalledAppFlow.from_client_secrets_file(
                CLIENT_SECRETS_FILE, SCOPES)
            credentials = flow.run_console()

        # Save the credentials for the next run
        with open('token.pickle', 'wb') as token:
            pickle.dump(credentials, token)

    return build(API_SERVICE_NAME, API_VERSION, credentials = credentials)

def get_ID_query(service, query):
    """
    Get a video ID & channel ID with a query
    """

    request = service.search().list(
        part="snippet",
        q= query, #"Jay Chou Mojito"
        maxResults = 1 # get the first resultat => channel of Youtuber
    )
    response = request.execute()

    #pp.pprint(response)
    #pp.pprint(d['items'][0]['id']['channelId'])

    save_to_json('../data/response_from_query.json', response)
    return response

def get_videoList(service, channelId):
    """
    Search results are constrained to a maximum of 500 videos 
    if your request specifies a value for the channelId parameter
    """
    
    request = service.search().list(
        part="snippet",
        channelId= channelId, #"-biOGdYiF-I"
        maxResults = 50
    )
    response = request.execute()

    pp.pprint(response)

    save_to_json('../data/videoList_of_channelID.json', response)
    return response

def get_video_data(service, videoId):
    """
    Get a video’s statistics data with a video ID
    """

    request = service.videos().list(
        part="snippet, statistics, topicDetails",
        id= videoId #"-biOGdYiF-I"
    )
    response = request.execute()

    pp.pprint(response)

    save_to_json('../data/video_data.json', response)
    return response

def get_video_comments(service, videoId):
    """
    Get a video’s comments

    Note - maxResults: This parameter is not supported for use in conjunction with the id parameter. 
    Acceptable values are 1 to 100, inclusive. The default value is 20.
    """

    request = service.commentThreads().list(
        part="snippet",
        videoId= videoId, #"-biOGdYiF-I"
        maxResults = 50
    )
    response = request.execute()

    pp.pprint(response)

    save_to_json('../data/video_comments.json', response)
    return response

def get_channel_info(service, channelId):
    """
    Get a channel’s information with channel ID
    """

    request = service.channels().list(
        part="snippet,statistics",
        id= channelId #"UC8CU5nVhCQIdAGrFFp4loOQ"
    )
    response = request.execute()

    pp.pprint(response)

    save_to_json('../data/channel_info.json', response)
    return response

def get_channel_playlist(service, channelId):
    """
    Get a channel’s playlist

    The maxResults parameter specifies the maximum number of items that should be returned in the result set. 
    Acceptable values are 0 to 50, inclusive. The default value is 5.
    """

    request = service.playlists().list(
        part="snippet",
        channelId= channelId, #"UC8CU5nVhCQIdAGrFFp4loOQ"
        maxResults = 20
    )
    response = request.execute()

    pp.pprint(response)

    save_to_json('../data/channel_playlist.json', response)
    return response

def get_channel_playlist_items(service, playlistIds):
    """
    Get a channel’s playlist

    The maxResults parameter specifies the maximum number of items that should be returned in the result set. 
    Acceptable values are 0 to 50, inclusive. The default value is 5.
    """

    request = service.playlists().list(
        part="snippet",
        id= playlistIds, #"UC8CU5nVhCQIdAGrFFp4loOQ"
        maxResults = 20
    )
    response = request.execute()

    pp.pprint(response)

    save_to_json('../data/channel_playlist_items.json', response)
    return response

def save_to_json(files_name, files):
    """
    Save to Json files format
    """
    with open(files_name, 'w') as json_file:
        json.dump(files, json_file)
        print('Your files is saved!')


def get_profil_info(name_list):
    """
    Collect all channel ID and profil Youtuber name by query search
    """
    results = []
    profils = []
    channelIDs = []
    channelinfos = []
    playlistIds = []
    channelplaylists = []
    playlist_items = [] 
    

    for i in name_list:
        result = get_ID_query(service, query= i)
        results.append(result)
        #print(results)
    
    for item in results:
        profil = item['items'][0]['snippet']['channelTitle']
        channelID = item['items'][0]['snippet']['channelId']
        profils.append(profil)
        channelIDs.append(channelID)

    for i in channelIDs:
        channelinfo = get_channel_info(service, channelId= i)
        channelplaylist = get_channel_playlist(service, channelId= i)
        channelinfos.append(channelinfo)
        channelplaylists.append(channelplaylist)

    for item in channelplaylists:
        for ids in item['items']:
            playlistId = ids['id']
            playlistIds.append(playlistId)

    for i in playlistIds:
        playlist_item = get_channel_playlist_items(service, playlistIds)
        playlist_items.append(playlist_item)

    # print(profils, channelIDs)        

    return profils, channelIDs, channelinfos, channelplaylists, playlistIds, playlist_items

def get_video_info(channelIDs):

    videoIDLists = []
    videoIDs = []
    videostats = []
    comments = []
    
    for i in channelIDs:
        videoIDList = get_videoList(service, channelId= i)
        videoIDLists.append(videoIDList)
        #print(videoIDLists)

    for item in videoIDLists:
        for data in item['items']:
            try:
                videoID = data['id']['videoId']
            except:
                pass
            videoIDs.append(videoID)
        #print(videoIDs)

    for i in videoIDs:
        videostat = get_video_data(service, videoId = i)
        comment = get_video_comments(service, videoId = i)
        videostats.append(videostat)
        comments.append(comment)


    return videoIDLists, videoIDs, videostats, comments

def save_info(name_list,channelIDs):
    profils, channelIDs, channelinfos, channelplaylists, playlistIds, playlist_items = get_profil_info(name_list)
    videoIDLists, videoIDs, videostats, comments = get_video_info(channelIDs)

    data={
        'profils':profils,
        'channelIDs':channelIDs,
        'channelinfos':channelinfos,
        'playlistIds':playlistIds,
        'channelplaylists':channelplaylists,
        'playlist_items':playlist_items,
        'videoIDLists':videoIDLists,
        'videoIDs':videoIDs,
        'videostats':videostats,
        'comment':comments,
        }

    d = save_to_json('../data/data_all_info.json', data)

if __name__ == '__main__':
    # When running locally, disable OAuthlib's HTTPs verification. When
    # running in production *do not* leave this option enabled.
    os.environ['OAUTHLIB_INSECURE_TRANSPORT'] = '1'
    service = get_authenticated_service()

    #get_ID_query(service, query= "Machine Learnia")
    #get_videoList(service, 'UCmpptkXu8iIFe6kfDK5o7VQ')
    #get_video_info(['UCmpptkXu8iIFe6kfDK5o7VQ'])
    #get_video_data(service, 'EUD07IiviJg')
    #get_video_comments(service, 'EUD07IiviJg')
    #get_channel_info(service, 'UCmpptkXu8iIFe6kfDK5o7VQ')
    #get_channel_playlist(service, 'UCmpptkXu8iIFe6kfDK5o7VQ')
    #get_channel_playlist_items(service, 'PLO_fdPEVlfKoHQ3Ua2NtDL4nmynQC8YiS')

    profils, channelIDs, channelinfos, channelplaylists, playlistIds, playlist_items = get_profil_info(['Machine Learnia', 'Science4All'])
    videoIDLists, videoIDs, videostats, comments = get_video_info(channelIDs)

