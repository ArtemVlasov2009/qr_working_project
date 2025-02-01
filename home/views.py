from django.shortcuts import render, redirect
from django.contrib.auth.models import User
from django.db.utils import IntegrityError 
from django.contrib.auth import authenticate, login, logout
from django.core.files.base import ContentFile
import qrcode
from io import BytesIO
from home.models import qr_code  
from django.conf import settings
import os
from django.utils import timezone


def render_home(request):
    return render(request=request, template_name='base.html')

def render_registration(request):
    show_text_passwords_dont_match = False
    show_text_not_unique_name = False

    if request.method == "POST":
        username = request.POST.get("name")
        password = request.POST.get("password")
        confirm_password = request.POST.get("confirm_password")

        if password and confirm_password and password != confirm_password:
            show_text_passwords_dont_match = True
        else:
            try:
                User.objects.create_user(username=username, password=password)
                return redirect("authorization")
            except IntegrityError:
                show_text_not_unique_name = True

    return render(
        request=request,
        template_name="registration.html",
        context={
            "show_text_passwords_dont_match": show_text_passwords_dont_match,
            "show_text_not_unique_name": show_text_not_unique_name
        }
    )

def render_authorization(request):
    user = True
    if request.method == "POST":
        username = request.POST.get("name")
        password = request.POST.get("password")

        print(f"Debug: Username: {username}, Password: {password}")

        user = authenticate(request, username=username, password=password)
        
        if user:
            login(request, user)
            print(f"Debug: Username: {username}, Password: {password}")
            return redirect('generator')

    return render(request, "authorization.html", {"user": user})

def render_contacts(request):
    return render(request=request, template_name='contacts.html')


def render_generator(request):
    qr_image_url = None  

    if not request.user.is_authenticated:
        return redirect("registration") 

    if request.method == "POST":
        name = request.POST.get("name")
        link = request.POST.get("link_or_text")

        if not name or not link:
            return render(request, "generator.html", {"error": "Заполните все поля"})

        print(f"Генерация QR-кода для: {link}")

        try:
            qr = qrcode.make(link)
            buffer = BytesIO()
            qr.save(buffer, format="PNG")

            media_path = os.path.join("media", "images")
            if not os.path.exists(media_path):
                os.makedirs(media_path)
                print(f"Создана папка: {media_path}")

            filename = f"{name}.png"  
            file_path = os.path.join(media_path, filename)

            with open(file_path, "wb") as f:
                f.write(buffer.getvalue())

            qr_code_instance, created = qr_code.objects.get_or_create(name=name)
            
            qr_code_instance.link = link
            qr_code_instance.size = 300 
            qr_code_instance.shape = 1 
            qr_code_instance.custom_style = "default" 
            qr_code_instance.data_create = int(timezone.now().timestamp())
            qr_code_instance.expiry_date = int(timezone.now().timestamp()) + 3600 * 24 * 30
            qr_code_instance.image.name = os.path.join("images", filename)
            qr_code_instance.save()

            qr_image_url = qr_code_instance.image.url
            print(f"QR-код сохранен и доступен по пути: {qr_image_url}")

        except Exception as e:
            print(f"Ошибка при создании QR-кода: {e}")
            qr_image_url = None 

    return render(request, "generator.html", {"qr_image_url": qr_image_url})

def render_history_gen(request):
    return render(request=request, template_name='history_gen.html')

def logout_user(request):
    logout(request)
    return redirect('authorization')







