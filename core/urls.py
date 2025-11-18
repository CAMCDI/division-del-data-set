from django.urls import path
from . import views

urlpatterns = [
    path('', views.process_arff, name='upload'),  # ← usa process_arff
]