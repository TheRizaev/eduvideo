
from django.shortcuts import render, redirect
from .models import Video, Category
import random
from django.contrib.auth import authenticate, login, logout
from django.shortcuts import redirect
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from .forms import UserRegistrationForm, UserLoginForm, UserProfileForm, AuthorApplicationForm, EmailVerificationForm, UserDetailsForm
from django.core.paginator import Paginator
from django.core.mail import send_mail
from django.conf import settings
import random

def custom_page_not_found(request, exception):
    return render(request, 'main/404.html', status=404)

def index(request):
    categories = Category.objects.all()
    return render(request, 'main/index.html', {'categories': categories})

def video_detail(request, video_id):
    # В реальном проекте вы будете искать видео по ID
    # Для демонстрации используем статические данные
    # Предполагаем, что video_id от 1 до 20 соответствует видеоданным из main.js
    video_data = None
    
    # Пример данных для одного видео
    if 1 <= video_id <= 20:
        sample_titles = {
            1: "Основы машинного обучения: Введение в нейронные сети",
            2: "Интегральное исчисление: Основные методы и примеры",
            3: "Python для анализа данных: Pandas и NumPy",
            4: "Квантовая физика: Принцип неопределенности Гейзенберга",
            5: "Основы генетики: От Менделя до современности",
            6: "История Древнего Рима: От республики к империи",
            7: "Микро- и макроэкономика: Основные концепции и модели",
            8: "Основы органической химии: Функциональные группы",
            9: "JavaScript продвинутый уровень: Асинхронное программирование",
            10: "Астрономия: Черные дыры и их свойства",
            11: "Линейная алгебра: Векторные пространства",
            12: "React и Redux: Управление состоянием приложения",
            13: "Биохимия: Метаболические пути в клетке", 
            14: "Дифференциальные уравнения: Практическое применение",
            15: "Искусственный интеллект: Глубокое обучение",
            16: "SQL для начинающих: Работа с базами данных",
            17: "Античная философия: От Сократа до Аристотеля", 
            18: "Теория вероятностей: Основные концепции",
            19: "Анатомия человека: Нервная система",
            20: "HTML и CSS: Создание адаптивных веб-страниц"
        }
        
        sample_channels = {
            1: "ИИ Академия",
            2: "Математический канал", 
            3: "Python Практикум",
            4: "Физика для всех",
            5: "Биология и генетика",
            6: "Исторический лекторий",
            7: "Экономика для всех", 
            8: "Химия и жизнь",
            9: "WebDev Мастер",
            10: "Космос и наука",
            11: "Математический канал",
            12: "Frontend разработка",
            13: "Биомед",
            14: "Инженерные науки",
            15: "ИИ Академия", 
            16: "Программирование с нуля",
            17: "Философские беседы",
            18: "Статистика и анализ",
            19: "Медицинский портал",
            20: "WebDev Мастер"
        }
        
        # Используем сопоставление или значение по умолчанию
        title = sample_titles.get(video_id, f"Видео #{video_id}")
        channel = sample_channels.get(video_id, "Канал видео")
        
        video_data = {
            'id': video_id,
            'title': title,
            'channel': channel,
            'views': f"{random.randint(10, 500)}K просмотров",
            'age': f"{random.randint(1, 14)} дней назад",
            'duration': f"{random.randint(10, 59)}:{random.randint(10, 59)}"
        }
    else:
        # Если ID не соответствует известным видео
        video_data = {
            'id': video_id,
            'title': f"Видео #{video_id}",
            'channel': "Канал видео",
            'views': "10K просмотров",
            'age': "1 неделя назад",
            'duration': "10:30"
        }
    
    return render(request, 'main/video.html', {'video': video_data})

def search_results(request):
    query = request.GET.get('query', '')
    
    # В реальном проекте здесь будет запрос к базе данных
    # для поиска видео по запросу
    videos = []
    
    # Пример соответствий ключевых слов и видео
    search_mappings = {
        'машин': [1, 15],
        'обучен': [1, 15],
        'нейрон': [1],
        'python': [3],
        'pandas': [3],
        'numpy': [3],
        'матем': [2, 11, 14, 18],
        'интеграл': [2],
        'алгебр': [11],
        'физик': [4],
        'квант': [4],
        'биолог': [5, 13],
        'генетик': [5],
        'истор': [6, 17],
        'рим': [6],
        'эконом': [7],
        'хими': [8, 13],
        'javascript': [9],
        'js': [9],
        'программирован': [3, 9, 12, 16],
        'астроном': [10],
        'космос': [10],
        'react': [12],
        'redux': [12],
        'уравнен': [14],
        'искусственн': [1, 15],
        'sql': [16],
        'баз данных': [16],
        'философ': [17],
        'вероятност': [18],
        'статистик': [18],
        'анатом': [19],
        'нерв': [19],
        'html': [20],
        'css': [20],
        'веб': [9, 12, 20]
    }
    
    # Список соответствий видео из main.js
    video_list = [
        {
            'id': 1,
            'title': "Основы машинного обучения: Введение в нейронные сети",
            'channel': "ИИ Академия",
            'views': "245K просмотров",
            'age': "1 неделя назад",
            'duration': "28:45"
        },
        {
            'id': 2,
            'title': "Интегральное исчисление: Основные методы и примеры",
            'channel': "Математический канал",
            'views': "189K просмотров",
            'age': "2 недели назад",
            'duration': "42:18"
        },
        {
            'id': 3,
            'title': "Python для анализа данных: Pandas и NumPy",
            'channel': "Python Практикум",
            'views': "423K просмотров",
            'age': "3 дня назад",
            'duration': "35:12"
        },
        {
            'id': 4,
            'title': "Квантовая физика: Принцип неопределенности Гейзенберга",
            'channel': "Физика для всех",
            'views': "156K просмотров",
            'age': "1 день назад",
            'duration': "45:23"
        },
        {
            'id': 5,
            'title': "Основы генетики: От Менделя до современности",
            'channel': "Биология и генетика",
            'views': "112K просмотров",
            'age': "5 дней назад",
            'duration': "32:49"
        },
        {
            'id': 6,
            'title': "История Древнего Рима: От республики к империи",
            'channel': "Исторический лекторий",
            'views': "174K просмотров",
            'age': "2 дня назад",
            'duration': "38:17"
        },
        {
            'id': 7,
            'title': "Микро- и макроэкономика: Основные концепции и модели",
            'channel': "Экономика для всех",
            'views': "145K просмотров",
            'age': "4 дня назад",
            'duration': "26:35"
        },
        {
            'id': 8,
            'title': "Основы органической химии: Функциональные группы",
            'channel': "Химия и жизнь",
            'views': "132K просмотров",
            'age': "6 дней назад",
            'duration': "41:52"
        },
        {
            'id': 9,
            'title': "JavaScript продвинутый уровень: Асинхронное программирование",
            'channel': "WebDev Мастер",
            'views': "210К просмотров",
            'age': "2 дня назад",
            'duration': "47:21"
        },
        {
            'id': 10,
            'title': "Астрономия: Черные дыры и их свойства",
            'channel': "Космос и наука",
            'views': "328К просмотров",
            'age': "5 дней назад",
            'duration': "34:17"
        },
        {
            'id': 11,
            'title': "Линейная алгебра: Векторные пространства",
            'channel': "Математический канал",
            'views': "167K просмотров",
            'age': "3 дня назад",
            'duration': "39:45"
        },
        {
            'id': 12,
            'title': "React и Redux: Управление состоянием приложения",
            'channel': "Frontend разработка",
            'views': "198K просмотров",
            'age': "1 неделя назад",
            'duration': "53:28"
        },
        {
            'id': 13,
            'title': "Биохимия: Метаболические пути в клетке",
            'channel': "Биомед",
            'views': "98K просмотров",
            'age': "4 дня назад",
            'duration': "46:39"
        },
        {
            'id': 14,
            'title': "Дифференциальные уравнения: Практическое применение",
            'channel': "Инженерные науки",
            'views': "147K просмотров",
            'age': "2 недели назад",
            'duration': "57:12"
        },
        {
            'id': 15,
            'title': "Искусственный интеллект: Глубокое обучение",
            'channel': "ИИ Академия",
            'views': "287K просмотров",
            'age': "3 дня назад",
            'duration': "41:05"
        },
        {
            'id': 16,
            'title': "SQL для начинающих: Работа с базами данных",
            'channel': "Программирование с нуля",
            'views': "201K просмотров",
            'age': "1 неделя назад",
            'duration': "32:56"
        },
        {
            'id': 17,
            'title': "Античная философия: От Сократа до Аристотеля",
            'channel': "Философские беседы",
            'views': "114K просмотров",
            'age': "5 дней назад",
            'duration': "48:34"
        },
        {
            'id': 18,
            'title': "Теория вероятностей: Основные концепции",
            'channel': "Статистика и анализ",
            'views': "132K просмотров",
            'age': "6 дней назад",
            'duration': "37:18"
        },
        {
            'id': 19,
            'title': "Анатомия человека: Нервная система",
            'channel': "Медицинский портал",
            'views': "178K просмотров",
            'age': "4 дня назад",
            'duration': "44:10"
        },
        {
            'id': 20,
            'title': "HTML и CSS: Создание адаптивных веб-страниц",
            'channel': "WebDev Мастер",
            'views': "224K просмотров",
            'age': "2 недели назад",
            'duration': "36:45"
        }
    ]
    
    if query:
        # Простой поиск: проверяем содержание каждого ключевого слова в запросе
        matching_video_ids = set()
        
        query_lower = query.lower()
        for keyword, video_ids in search_mappings.items():
            if keyword.lower() in query_lower:
                matching_video_ids.update(video_ids)
                
        # Если ничего не нашли, ищем по заголовкам и каналам
        if not matching_video_ids:
            for i, video in enumerate(video_list, 1):
                if (query_lower in video['title'].lower() or 
                    query_lower in video['channel'].lower()):
                    matching_video_ids.add(i)
        
        # Собираем результаты
        videos = [video_list[id-1] for id in matching_video_ids if 1 <= id <= len(video_list)]
    
    return render(request, 'main/search.html', {
        'query': query,
        'videos': videos
    })

def send_verification_code(request, email):
    # Generate verification code (6 digits)
    verification_code = ''.join([str(random.randint(0, 9)) for _ in range(6)])
    request.session['verification_code'] = verification_code
    
    # Send verification email
    subject = 'KRONIK - Email Verification'
    message = f'Your verification code is: {verification_code}'
    send_mail(
        subject,
        message,
        settings.DEFAULT_FROM_EMAIL,
        [email],
        fail_silently=False
    )
    return verification_code

def register_view(request):
    if request.user.is_authenticated:
        # Check if email is verified
        if not request.user.profile.email_verified:
            # If not verified, redirect to verification page
            return redirect('verify_email')
        # Check if user details are completed
        if not request.user.first_name or not request.user.last_name:
            return redirect('user_details')
        return redirect('index')
    
    # Check if we're in email verification phase
    if 'registration_data' in request.session:
        return redirect('verify_email')
        
    # Initial registration form
    if request.method == 'POST':
        form = UserRegistrationForm(request.POST)
        if form.is_valid():
            # Don't save yet, store in session and send verification email
            request.session['registration_data'] = request.POST.dict()
            
            # Send verification code
            email = form.cleaned_data.get('email')
            send_verification_code(request, email)
            
            messages.info(request, f'Verification code sent to {email}. Please check your email.')
            return redirect('verify_email')
    else:
        form = UserRegistrationForm()
    
    return render(request, 'accounts/register.html', {'form': form})

def verify_email_view(request):
    # If not in registration process and not logged in, redirect to register
    if 'registration_data' not in request.session and not request.user.is_authenticated:
        return redirect('register')
        
    # If logged in but email already verified, check if we need user details
    if request.user.is_authenticated and request.user.profile.email_verified:
        if not request.user.first_name or not request.user.last_name:
            return redirect('user_details')
        return redirect('index')
        
    # Get email from session or user object
    if 'registration_data' in request.session:
        email = request.session['registration_data'].get('email')
    else:
        email = request.user.email
        
    if request.method == 'POST':
        verification_form = EmailVerificationForm(request.POST)
        if verification_form.is_valid():
            # Get stored verification code
            stored_code = request.session.get('verification_code')
            submitted_code = verification_form.cleaned_data['verification_code']
            
            # Verify the code
            if stored_code == submitted_code:
                # If in registration process
                if 'registration_data' in request.session:
                    # Get stored registration data
                    reg_data = request.session['registration_data']
                    
                    # Create user account
                    form = UserRegistrationForm(reg_data)
                    if form.is_valid():
                        user = form.save()
                        
                        # Set profile fields
                        if hasattr(user, 'profile'):
                            user.profile.date_of_birth = form.cleaned_data['date_of_birth']
                            user.profile.identification = form.cleaned_data['identification']
                            user.profile.email_verified = True
                            user.profile.save()
                        
                        # Clean up session
                        del request.session['registration_data']
                        del request.session['verification_code']
                        
                        # Log the user in
                        username = form.cleaned_data.get('username')
                        password = form.cleaned_data.get('password1')
                        user = authenticate(username=username, password=password)
                        login(request, user)
                        
                        messages.success(request, f'Email verified successfully!')
                        return redirect('user_details')
                else:
                    # For existing users verifying email
                    request.user.profile.email_verified = True
                    request.user.profile.save()
                    
                    # Clean up session
                    if 'verification_code' in request.session:
                        del request.session['verification_code']
                        
                    messages.success(request, 'Email successfully verified!')
                    
                    # Check if user details are completed
                    if not request.user.first_name or not request.user.last_name:
                        return redirect('user_details')
                    return redirect('index')
            else:
                messages.error(request, 'Invalid verification code. Please try again.')
        else:
            for field, errors in verification_form.errors.items():
                for error in errors:
                    messages.error(request, f"{error}")
                    
    else:
        verification_form = EmailVerificationForm()
        
    # Handle resend code button
    if request.GET.get('resend') == 'true':
        if email:
            send_verification_code(request, email)
            messages.info(request, f'New verification code sent to {email}. Please check your email.')
    
    return render(request, 'accounts/verify_email.html', {
        'form': verification_form,
        'email': email
    })

def user_details_view(request):
    # If not logged in, redirect to login
    if not request.user.is_authenticated:
        return redirect('login')
        
    # If email not verified, redirect to verification
    if not request.user.profile.email_verified:
        return redirect('verify_email')
        
    # If user details already completed, redirect to home
    if request.user.first_name and request.user.last_name:
        return redirect('index')
        
    if request.method == 'POST':
        form = UserDetailsForm(request.POST, instance=request.user)
        if form.is_valid():
            form.save()
            messages.success(request, 'Thank you! Your profile is now complete.')
            return redirect('index')
    else:
        form = UserDetailsForm(instance=request.user)
    
    return render(request, 'accounts/user_details.html', {'form': form})

def login_view(request):
    if request.user.is_authenticated:
        # Check if email is verified
        if not request.user.profile.email_verified:
            # If not verified, redirect to verification page
            return redirect('verify_email')
        # Check if user details are completed
        if not request.user.first_name or not request.user.last_name:
            return redirect('user_details')
        return redirect('index')
        
    if request.method == 'POST':
        form = UserLoginForm(request.POST)
        if form.is_valid():
            username = form.cleaned_data.get('username')
            password = form.cleaned_data.get('password')
            user = authenticate(username=username, password=password)
            if user is not None:
                login(request, user)
                
                # Check if email is verified
                if not user.profile.email_verified:
                    # Send a new verification code
                    send_verification_code(request, user.email)
                    messages.info(request, f'Please verify your email. A verification code has been sent to {user.email}.')
                    return redirect('verify_email')
                
                # Check if user details are completed
                if not user.first_name or not user.last_name:
                    return redirect('user_details')
                    
                next_page = request.GET.get('next', 'index')
                return redirect(next_page)
            else:
                messages.error(request, 'Incorrect username or password')
    else:
        form = UserLoginForm()
    
    return render(request, 'accounts/login.html', {'form': form})

def logout_view(request):
    logout(request)
    return redirect('login')

@login_required
def profile_view(request):
    # Check if email is verified
    if not request.user.profile.email_verified:
        # If not verified, redirect to verification page
        return redirect('verify_email')
    
    # Check if user details are completed
    if not request.user.first_name or not request.user.last_name:
        return redirect('user_details')
        
    if request.method == 'POST':
        form = UserProfileForm(request.POST, request.FILES, instance=request.user.profile)
        if form.is_valid():
            form.save()
            messages.success(request, 'Your profile has been updated!')
            return redirect('profile')
    else:
        form = UserProfileForm(instance=request.user.profile)
    
    return render(request, 'accounts/profile.html', {'form': form})

@login_required
def studio_view(request):
    """
    View for the creator studio page.
    Only authenticated users who are approved authors can access this page.
    """
    # Проверяем, является ли пользователь автором
    if not request.user.profile.is_author:
        messages.error(request, 'У вас нет доступа к Студии. Вы должны стать автором, чтобы получить доступ.')
        return redirect('become_author')
        
    # Для демонстрации, мы будем использовать пустой список видео
    videos = []
    
    return render(request, 'studio/studio.html', {
        'videos': videos
    })

@login_required
def author_application(request):
    # Проверяем, уже ли пользователь автор или подал заявку
    if request.user.profile.is_author:
        messages.info(request, 'Вы уже являетесь автором!')
        return redirect('studio')
        
    if request.user.profile.author_application_pending:
        messages.info(request, 'Ваша заявка на авторство уже находится на рассмотрении.')
        return redirect('profile')
    
    if request.method == 'POST':
        form = AuthorApplicationForm(request.POST, instance=request.user.profile)
        if form.is_valid():
            profile = form.save(commit=False)
            profile.author_application_pending = True
            profile.save()
            form.save_m2m()  # Сохраняем many-to-many поля
            
            # Отправляем уведомление администратору
            subject = f'Новая заявка на авторство от {request.user.username}'
            message = f"""
            Пользователь {request.user.username} ({request.user.email}) подал заявку на авторство.
            
            Области экспертизы: {', '.join(area.name for area in form.cleaned_data['expertise_areas'])}
            
            Данные о квалификации:
            {profile.credentials}
            
            Для подтверждения или отклонения заявки перейдите в админ-панель:
            {request.build_absolute_uri('/admin/main/userprofile/')}
            """
            
            send_mail(
                subject, 
                message, 
                settings.DEFAULT_FROM_EMAIL, 
                [settings.ADMIN_EMAIL],  # Добавьте свой email в settings.py
                fail_silently=False
            )
            
            messages.success(request, 'Ваша заявка на авторство успешно отправлена! Мы свяжемся с вами после рассмотрения.')
            return redirect('profile')
    else:
        form = AuthorApplicationForm(instance=request.user.profile)
    
    return render(request, 'accounts/author_application.html', {'form': form})