from django.urls import path
from . import views

urlpatterns = [
    path('', views.home, name='home'),
    path('upload-excel/', views.upload_excel, name='upload_excel'),
    path('upload-images/', views.upload_images, name='upload_images'),
    path('assign-labels/', views.assign_labels, name='assign_labels'),
    path('upload-cover/', views.upload_cover, name='upload_cover'),
    path('generate-pdf/', views.generate_pdf, name='generate_pdf'),
]
