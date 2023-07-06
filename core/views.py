from django.http import HttpResponse
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_POST
from InstagramAPI import InstagramAPI
import facebook
import os
import google.auth
from googleapiclient.discovery import build
from googleapiclient.http import MediaFileUpload
from google.oauth2 import service_account



@csrf_exempt
@require_POST
def facebook_post_view(request):
    access_token = ''
    graph = facebook.GraphAPI(access_token)

    def post_to_facebook(message, media_url=None, media_type=None):
        post_data = {'message': message}

        if media_url and media_type:
            post_data[media_type] = media_url

        try:
            response = graph.put_object('me', 'feed', **post_data)
            post_id = response['id']
            return post_id
        except facebook.GraphAPIError as e:
            return None

    def fetch_post_likes_comments(post_id):
        try:
            likes = graph.get_connections(post_id, 'likes')['data']
            comments = graph.get_connections(post_id, 'comments')['data']
            return likes, comments
        except facebook.GraphAPIError:
            return None, None

    if request.method == 'POST':
        post_message = request.POST.get('message', '')
        post_media_url = request.POST.get('media_url', '')
        post_media_type = request.POST.get('media_type', '')

        post_id = post_to_facebook(post_message, post_media_url, post_media_type)

        if post_id:
            post_likes, post_comments = fetch_post_likes_comments(post_id)
            likes_count = len(post_likes) if post_likes else 0
            comments_count = len(post_comments) if post_comments else 0

            response_data = {
                'post_id': post_id,
                'likes_count': likes_count,
                'comments_count': comments_count
            }
            return HttpResponse(response_data, content_type='application/json')

    return HttpResponse(status=400)


@csrf_exempt
@require_POST
def instagram_post_view(request):
    username = 'YOUR_USERNAME'
    password = 'YOUR_PASSWORD'
    media_path = 'PATH_TO_MEDIA_FILE'

    api = InstagramAPI(username, password)
    api.login()

    def post_to_instagram(caption, media_path):
        api.uploadPhoto(media_path, caption=caption)
        response = api.LastJson
        if response.get('status') == 'ok':
            post_id = response['media']['id']
            return post_id
        else:
            return None

    def fetch_post_likes_comments(post_id):
        api.getMediaComments(post_id)
        response = api.LastJson
        if response.get('status') == 'ok':
            likes = response['comments']
            comments = response['comments']
            return likes, comments
        else:
            return None, None

    if request.method == 'POST':
        post_caption = request.POST.get('caption', '')

        post_id = post_to_instagram(post_caption, media_path)

        if post_id:
            post_likes, post_comments = fetch_post_likes_comments(post_id)
            likes_count = len(post_likes) if post_likes else 0
            comments_count = len(post_comments) if post_comments else 0

            response_data = {
                'post_id': post_id,
                'likes_count': likes_count,
                'comments_count': comments_count
            }
            return HttpResponse(response_data, content_type='application/json')

    return HttpResponse(status=400)

@csrf_exempt
@require_POST
def youtube_upload_view(request):
    video_title = request.POST.get('video_title', 'My YouTube Video')
    video_description = request.POST.get('video_description', 'This is a demo video uploaded through the YouTube Data API')
    video_tags = request.POST.getlist('video_tags[]', ['youtube', 'api', 'python'])
    video_path = request.FILES.get('video_file')
    credentials_path = "PATH_TO_JSON_KEY_FILE"

    credentials = service_account.Credentials.from_service_account_file(credentials_path)
    youtube = build('youtube', 'v3', credentials=credentials)

    videos_insert_request = youtube.videos().insert(
        part='snippet,status',
        body={
            'snippet': {
                'title': video_title,
                'description': video_description,
                'tags': video_tags
            },
            'status': {
                'privacyStatus': 'private'
            }
        }
    )

    media = MediaFileUpload(video_path, chunksize=-1, resumable=True)
    upload_response = videos_insert_request.execute(http=credentials.authorize(httplib2.Http()), media_body=media)

    video_id = upload_response.get('id')

    if video_id:
        response_data = {
            'video_id': video_id
        }
        return JsonResponse(response_data)
    else:
        return HttpResponse(status=400)