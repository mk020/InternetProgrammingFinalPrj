from django.urls import path
from . import views

urlpatterns = [ # IP주소/
    path('', views.landing), # IP주소/
    path('about_company/', views.about_company) # IP주소/about_company/
]