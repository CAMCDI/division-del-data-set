from django.urls import path
from . import views

urlpatterns = [
    path('', views.upload_page, name='upload'),
    path('process/', views.process_arff, name='process_arff'),
]