"""main URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/3.2/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path
from home.views import *
from django.conf import settings
from django.conf.urls.static import static
from home import views

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', render_home, name='home'),
    path('registration/', render_registration, name='registration'),
    path('authorization/', render_authorization, name='authorization'),
    path('logout/', logout_user, name = "logout"),
    path('contacts/', render_contacts, name='contacts'),
    path('generator/', render_generator, name='generator'),
    path('history_gen/', render_history_gen, name='history_generations'),
    path('free/', render_free, name='free'),
    path('standart/', render_standard, name='standart'),
    path('pro/', render_pro, name='pro'),
    path('delete_qr_code/<int:qr_id>/', views.delete_qr_code, name='delete_qr_code'),
    path('choose_plan/', choose_plan, name='choose_plan'),
    path('desktop/', render_desktop, name='desktop'),
    path('home_auth/', render_home_auth, name='home_auth'),
]
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
