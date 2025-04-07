from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from django.contrib import messages
from .models import Category
from django.views.decorators.http import require_http_methods
from django.conf import settings
import os
import json
from datetime import datetime
import uuid

# Импортируем GCS модуль из нашего файла
from .gcs_storage import (
    create_user_folder_structure,
    upload_video,
    upload_thumbnail,
    list_user_videos,
    get_video_metadata,
    generate_video_url,
    delete_video
)

@login_required
@require_http_methods(["POST"])
def upload_video_to_gcs(request):
    """
    Обработчик загрузки видео в Google Cloud Storage
    """
    try:
        # Получаем файлы и данные из запроса
        video_file = request.FILES.get('video_file')
        thumbnail = request.FILES.get('thumbnail')
        title = request.POST.get('title')
        description = request.POST.get('description', '')
        category_id = request.POST.get('category')
        
        if not video_file or not title:
            return JsonResponse({'error': 'Видео и название обязательны'}, status=400)
        
        # Сохраняем файлы временно на сервере
        user_id = f"user_{request.user.id}"
        temp_video_path = os.path.join(settings.MEDIA_ROOT, 'temp', video_file.name)
        os.makedirs(os.path.dirname(temp_video_path), exist_ok=True)
        
        with open(temp_video_path, 'wb+') as destination:
            for chunk in video_file.chunks():
                destination.write(chunk)
        
        # Загружаем видео в GCS
        video_id = upload_video(
            user_id=user_id,
            video_file_path=temp_video_path,
            title=title,
            description=description
        )
        
        # Если есть превью, загружаем его тоже
        if thumbnail:
            temp_thumbnail_path = os.path.join(settings.MEDIA_ROOT, 'temp', thumbnail.name)
            with open(temp_thumbnail_path, 'wb+') as destination:
                for chunk in thumbnail.chunks():
                    destination.write(chunk)
            
            upload_thumbnail(user_id, video_id, temp_thumbnail_path)
            
            # Удаляем временный файл превью
            if os.path.exists(temp_thumbnail_path):
                os.remove(temp_thumbnail_path)
        
        # Удаляем временный файл видео
        if os.path.exists(temp_video_path):
            os.remove(temp_video_path)
        
        # Получаем метаданные загруженного видео
        video_metadata = get_video_metadata(user_id, video_id)
        
        # Генерируем временную ссылку для доступа к видео
        video_url = generate_video_url(user_id, video_id, expiration_time=3600)
        
        # Добавляем URL к метаданным
        video_metadata['url'] = video_url
        
        return JsonResponse({
            'success': True,
            'video_id': video_id,
            'metadata': video_metadata
        })
        
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)

@login_required
def list_videos_from_gcs(request):
    """
    Получение списка видео пользователя из GCS
    """
    try:
        user_id = f"user_{request.user.id}"
        videos = list_user_videos(user_id)
        
        # Добавляем временные URL к каждому видео
        for video in videos:
            video_id = video.get('video_id')
            if video_id:
                video['url'] = generate_video_url(user_id, video_id, expiration_time=3600)
        
        return JsonResponse({
            'success': True,
            'videos': videos
        })
        
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)

@login_required
@require_http_methods(["DELETE"])
def delete_video_from_gcs(request, video_id):
    """
    Удаление видео из GCS
    """
    try:
        user_id = f"user_{request.user.id}"
        success = delete_video(user_id, video_id)
        
        if success:
            return JsonResponse({'success': True})
        else:
            return JsonResponse({'error': 'Не удалось удалить видео'}, status=400)
            
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)

@login_required
@require_http_methods(["GET"])
def get_video_url(request, video_id):
    """
    Получение временной ссылки на видео
    """
    try:
        user_id = f"user_{request.user.id}"
        url = generate_video_url(user_id, video_id, expiration_time=3600)
        
        if url:
            return JsonResponse({
                'success': True,
                'url': url
            })
        else:
            return JsonResponse({'error': 'Не удалось сгенерировать ссылку'}, status=400)
            
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)

@login_required
def studio_view(request):
    """
    View для страницы студии с интеграцией GCS
    """
    # Проверяем, является ли пользователь автором
    if not request.user.profile.is_author:
        messages.error(request, 'У вас нет доступа к Студии. Вы должны стать автором, чтобы получить доступ.')
        return redirect('become_author')
    
    # Получаем список видео пользователя из GCS
    user_id = f"user_{request.user.id}"
    
    try:
        # Создаем структуру папок пользователя, если она не существует
        create_user_folder_structure(user_id)
        
        # Получаем список видео пользователя
        videos = list_user_videos(user_id)
        
        # Получаем список категорий для формы загрузки
        categories = Category.objects.all()
        
        return render(request, 'studio/studio.html', {
            'videos': videos,
            'categories': categories
        })
    except Exception as e:
        messages.error(request, f'Ошибка при получении данных: {e}')
        videos = []
        
    return render(request, 'studio/studio.html', {
        'videos': videos
    })