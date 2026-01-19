from django.urls import path
from . import views

urlpatterns = [
    path('', views.blog_list, name='blog_list'),
    path('sort-articles/', views.sort_articles, name='sort_articles'),

]