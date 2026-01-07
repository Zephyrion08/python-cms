from django.urls import path
from . import views

urlpatterns = [
    path('', views.article_list, name='article_list'),
    path('create/', views.article_create, name='article_create'),
    path('edit/<int:pk>/', views.article_edit, name='article_edit'),
    path('<int:pk>/delete/', views.article_delete, name='article_delete'),
    path('articles/<int:pk>/toggle-status/', views.article_toggle_status, name='article_toggle_status'),

]