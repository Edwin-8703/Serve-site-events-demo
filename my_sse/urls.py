from django.urls import path
from . import views

urlpatterns = [
    path('', views.index, name='index'),
    path('stream/', views.sse_stream, name='stream'),
    path('notify/', views.create_notification, name='notify'),
]