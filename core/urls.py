from django.urls import path
from .views import *

urlpatterns = [
        path('facebook-post/', facebook_post_view, name='facebook_post'),
        path('instagram-post/', instagram_post_view, name='instagram_post'),
        path('youtube-upload/', youtube_upload_view, name='youtube_upload'),
]
