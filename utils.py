import json
import requests
import base64

class SpotifyExtractor():
    def __init__(self, client_id, client_secret):
        self.REDIRECT_URI = "http://localhost:8888/callback"
        self.AUTH_URL = "https://accounts.spotify.com/authorize"
        self.TOKEN_URL = "https://accounts.spotify.com/api/token"
        self.API_BASE_URL = "https://api.spotify.com/v1"

        self.CLIENT_ID = client_id
        self.CLIENT_SECRET = client_secret

        # Create payload to obtain token using CLIENT_ID and CLIENT_SECRET
        auth_string = self.CLIENT_ID + ':' + self.CLIENT_SECRET
        auth_bytes = auth_string.encode('utf-8')
        auth_base64 = base64.b64encode(auth_bytes).decode('utf8')

        headers = {
            'Authorization': f'Basic  {auth_base64}',
            'Content-Type': 'application/x-www-form-urlencoded'
        }
        data = {
            'grant_type': 'client_credentials',
            'client_id': self.CLIENT_ID,
            'client_secret': self.CLIENT_SECRET
        }

        # Obtain token using created payload
        result = requests.post(self.TOKEN_URL, headers=headers, data=data)
        json_result = json.loads(result.content)
        token = json_result['access_token']

        # Use the token for authorization in subsequent functions
        self.headers = {
            'Authorization': f'Bearer {token}' 
        }

    def use_api(self, service:str, id:str='', sub_service:str='', query:str=''):
        url = f"{self.API_BASE_URL}/{service}"
        if id:
            url += f'/{id}'
        if sub_service:
            url += f'/{sub_service}'
        if query:
            url += f'?{query}'

        # print(url)
        result = requests.get(url, headers=self.headers)
        # print(result, result.content, result.headers)
        json_result = json.loads(result.content)
        # print(json_result)
        
        return json_result
       
    def get_album(self, album_id:str):
        json_result = self.use_api(service='albums', id=album_id)

        dict_result = {
            'release_date': json_result.get('release_date', None),
            'album_popularity': json_result.get('popularity', None),
            'image_url': json_result.get('images', {})[0].get('url', None)
        }
        
        return dict_result
    
    def get_albums(self, album_ids:list):
        query = 'ids=' + ','.join(album_ids)
        json_result = self.use_api(service='albums', query=query)
        
        albums = json_result.get('albums', [])

        list_result = list()

        for album in albums:
            images_list = album.get('images', [])
            image = images_list[1] if len(images_list) > 0 else {}

            dict_result_temp = {
                'release_date': album.get('release_date', None),
                'release_date_precision': album.get('release_date_precision', None),
                'album_popularity': album.get('popularity', None),
                'image_url': image.get('url', None)
            }
            
            list_result.append(dict_result_temp)
        
        return list_result
        
    def get_track(self, track_id:str):
        json_result = self.use_api(service='tracks', id=track_id)
        
        dict_result = {
            'album_id': json_result.get('album', {}).get('id', None),
            'duration_ms': json_result.get('duration_ms', None),
            'track_popularity': json_result.get('popularity', None)
        }
        
        return dict_result
    
    def get_tracks(self, track_ids:list):
        query = 'ids=' + ','.join(track_ids)
        json_result = self.use_api(service='tracks', query=query)

        tracks = json_result.get('tracks', [])

        list_result = list()

        for track in tracks:
            dict_result_temp = {
                'album_id': track.get('album', {}).get('id', None),
                'duration_ms': track.get('duration_ms', None),
                'track_popularity': track.get('popularity', None)
            }
            
            list_result.append(dict_result_temp)
        
        return list_result