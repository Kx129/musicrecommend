
from django.urls import path
from . import views

urlpatterns = [
    path('',views.indexView,name='index'),
    path('chat1',views.chat1),
    path('chat2',views.chat2),
    path('chat3',views.chat3),
    path('chat4',views.chat4),
    path('randomUser', views.random_user),
    path('randomData', views.random_data)
]