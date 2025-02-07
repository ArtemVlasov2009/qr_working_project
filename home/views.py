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
from django.core.files.base import ContentFile
from PIL import Image, ImageDraw, ImageFilter



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
    if not request.user.is_authenticated:
        return redirect("registration")

    qr_image_url = None

    if request.method == "POST":
        name = request.POST.get("name")
        link = request.POST.get("link_or_text")
        size = int(request.POST.get("size", 300))
        color = request.POST.get("color", "#000000")
        logo_file = request.FILES.get("logo")
        use_gradient = request.POST.get("gradient") == "on"
        color1 = request.POST.get("color1", "#ff0000")
        color2 = request.POST.get("color2", "#00ff00")
        shape = request.POST.get("shape", "square")  
        round_corners = shape == "rounded"  

        
        if not name or not link:
            return render(request, "generator.html", {"error": "Заполните все поля"})

        try:
            qr = qrcode.QRCode(
                version=1,
                error_correction=qrcode.constants.ERROR_CORRECT_H,
                box_size=10,
                border=4,
            )
            qr.add_data(link)
            qr.make(fit=True)

            img = qr.make_image(fill_color="black", back_color="white").convert("RGBA")

            if use_gradient:
                gradient = Image.new("RGBA", img.size)
                draw = ImageDraw.Draw(gradient)

                for y in range(img.size[1]):
                    r = int((1 - y / img.size[1]) * int(color1[1:3], 16) + (y / img.size[1]) * int(color2[1:3], 16))
                    g = int((1 - y / img.size[1]) * int(color1[3:5], 16) + (y / img.size[1]) * int(color2[3:5], 16))
                    b = int((1 - y / img.size[1]) * int(color1[5:7], 16) + (y / img.size[1]) * int(color2[5:7], 16))
                    draw.line([(0, y), (img.size[0], y)], fill=(r, g, b))

                qr_data = img.getdata()
                gradient_data = gradient.getdata()

                new_data = []
                for i in range(len(qr_data)):
                    if qr_data[i][0] == 0:  
                        new_data.append(gradient_data[i])
                    else:
                        new_data.append(qr_data[i])

                img.putdata(new_data)

            else:
                qr_data = img.getdata()
                new_data = []
                fill_color = tuple(int(color[i:i+2], 16) for i in (1, 3, 5)) + (255,)  

                for item in qr_data:
                    if item[0] == 0:  
                        new_data.append(fill_color)
                    else:
                        new_data.append(item)

                img.putdata(new_data)

            if round_corners:
                corner_radius = int(size * 0.05)  
                mask = Image.new("L", img.size, 255)  

                draw = ImageDraw.Draw(mask)
                for x in range(img.size[0]):
                    for y in range(img.size[1]):
                        if img.getpixel((x, y))[0] == 0:  
                            if (
                                (x < corner_radius and y < corner_radius) or 
                                (x < corner_radius and y > img.size[1] - corner_radius - 1) or  
                                (x > img.size[0] - corner_radius - 1 and y < corner_radius) or  
                                (x > img.size[0] - corner_radius - 1 and y > img.size[1] - corner_radius - 1)  
                            ):
                                distance = ((x - corner_radius)**2 + (y - corner_radius)**2)**0.5
                                if distance > corner_radius:
                                    mask.putpixel((x, y), 0)  

                img.putalpha(mask)

            if logo_file:
                try:
                    logo = Image.open(logo_file).convert("RGBA")

                    logo_size = int(size * 0.2)
                    logo = logo.resize((logo_size, logo_size))

                    position = ((img.size[0] - logo.size[0]) // 2, (img.size[1] - logo.size[1]) // 2)

                    img_with_logo = img.copy()

                    img_with_logo.paste(logo, position, mask=logo)

                    img = img_with_logo

                except Exception as e:
                    print(f"Ошибка при обработке логотипа: {e}")

            buffer = BytesIO()
            img.save(buffer, format="PNG")
            image_content = ContentFile(buffer.getvalue(), f"{name}.png")

            if qr_code.objects.filter(name=name).exists():
                return render(request, "generator.html", {"error": "QR-код с таким именем уже существует"})

            qr_code_instance = qr_code(
                name=name,
                link=link,
                size=size,
                shape=1 if round_corners else 0,  
                custom_style="gradient" if use_gradient else "default",
                data_create=timezone.now(),
                expiry_date=(timezone.now() + timezone.timedelta(days=30)).timestamp(),
                image=image_content
            )

            qr_code_instance.save()

            qr_image_url = qr_code_instance.image.url
            print(f"QR-код успешно сохранен. Имя: {name}, URL: {qr_image_url}")

        except Exception as e:
            print(f"Ошибка при создании QR-кода: {e}")
            return render(request, "generator.html", {"error": "Произошла ошибка при генерации QR-кода"})

    return render(request, "generator.html", {"qr_image_url": qr_image_url})




def render_history_gen(request):
    qr_codes = qr_code.objects.all() 
    return render(request, "history_gen.html", {"qr_codes": qr_codes})

def logout_user(request):
    logout(request)
    return redirect('authorization')







