# Дополнение к main/urls.py для интеграции с Google Cloud Storage

from django.urls import path
from . import views
from . import gcs_views 
from django.conf import settings

urlpatterns = [
    path('', views.index, name='index'),  # Главная страница
    path('video/<int:video_id>/', views.video_detail, name='video_detail'),  # Страница отдельного видео
    path('search/', views.search_results, name='search_results'),  # Страница результатов поиска
    path('register/', views.register_view, name='register'),  # Страница регистрации
    path('login/', views.login_view, name='login'),  # Страница входа
    path('logout/', views.logout_view, name='logout'),  # Обработка выхода
    path('profile/', views.profile_view, name='profile'),  # Профиль пользователя

    path('studio/', gcs_views.studio_view, name='studio'),  # Использует новое представление с интеграцией GCS

    path('become-author/', views.author_application, name='become_author'),  # Заявка на авторство
    
    # API для работы с Google Cloud Storage
    path('api/upload-video/', gcs_views.upload_video_to_gcs, name='upload_video_to_gcs'),
    path('api/list-videos/', gcs_views.list_videos_from_gcs, name='list_videos_from_gcs'),
    path('api/delete-video/<str:video_id>/', gcs_views.delete_video_from_gcs, name='delete_video_from_gcs'),
    path('api/get-video-url/<str:video_id>/', gcs_views.get_video_url, name='get_video_url'),
]

if settings.DEBUG:
    from django.views.defaults import page_not_found
    urlpatterns.append(path('404/', lambda request: page_not_found(request, None)))