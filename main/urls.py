from django.urls import path
from . import views

urlpatterns = [
    path('', views.index, name='index'),
    path('video/<int:video_id>/', views.video_detail, name='video_detail'),
    path('search/', views.search_results, name='search_results'),
    path('register/', views.register_view, name='register'),
    path('login/', views.login_view, name='login'),
    path('logout/', views.logout_view, name='logout'),
    path('profile/', views.profile_view, name='profile'),
]
