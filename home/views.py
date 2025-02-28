from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.models import User
from django.db.utils import IntegrityError 
from django.contrib.auth import authenticate, login, logout
from django.http import HttpResponse
from django.conf import settings
from django.utils import timezone
from datetime import timedelta
import qrcode
from io import BytesIO
import os
from PIL import Image, ImageDraw
from home.models import qr_code, Subscribers

def render_home(request):
    selected_plan = request.session.get('selected_plan', None)
    
    if request.method == "POST":
        selected_plan = request.POST.get("selected_plan")
        if selected_plan in ['free', 'standard', 'pro', 'desktop']:
            request.session['selected_plan'] = selected_plan
            return redirect('authorization')
    
    return render(request, 'base.html', {'selected_plan': selected_plan})

def render_home_auth(request):
    selected_plan = request.session.get('selected_plan', None)
    
    if request.method == "POST":
        selected_plan = request.POST.get("selected_plan")
        if selected_plan in ['free', 'standard', 'pro', 'desktop']:
            request.session['selected_plan'] = selected_plan
            return redirect('authorization')
    
    return render(request, 'base_auth.html', {'selected_plan': selected_plan})

def render_registration(request: HttpResponse):
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


def render_authorization(request: HttpResponse):
    user = True
    if request.method == "POST":
        username = request.POST.get("name")
        password = request.POST.get("password")
        card_number = request.POST.get("card_number")
        expiry_date = request.POST.get("expiry_date")
        cvv = request.POST.get("cvv")

        print(f"Debug: Username: {username}, Password: {password}")

        user = authenticate(request, username=username, password=password)

        if user:
            login(request, user)
            print(f"Debug: User {username} logged in successfully")

            selected_plan = request.POST.get('selected_plan') or request.session.get('selected_plan')

            if selected_plan:
                request.session['selected_plan'] = selected_plan  
                if selected_plan == 'free':
                    return redirect('free')
                elif selected_plan == 'standard':
                    return redirect('standart')
                elif selected_plan == 'pro':
                    return redirect('pro')
                elif selected_plan == 'desktop':
                    return redirect('desktop')
            else:
                return redirect('generator')
        else:
            return render(request, "authorization.html", {"user": False, "error": "Невірні дані"})

    return render(request, "authorization.html", {"user": user})
def choose_plan(request):
    if request.method == 'POST':
        plan = request.POST.get('plan')  
        request.session['selected_plan'] = plan 
        return redirect('authorization') 
    return redirect('home') 


def render_contacts(request: HttpResponse):
    return render(request=request, template_name='contacts.html')


def render_generator(request: HttpResponse):
    if not request.user.is_authenticated:
        return redirect('authorization')
    
    subscriber, created = Subscribers.objects.get_or_create(user=request.user)
    
    if subscriber.plan == 'free' and subscriber.qr_code_count >= 1:
        return HttpResponse("Ви досягли ліміту генерації QR-кодів для безкоштовного тарифу.")
    elif subscriber.plan == 'standard' and subscriber.qr_code_count >= 50:
        return HttpResponse("Ви досягли ліміту генерації QR-кодів для стандартного тарифу.")
    elif subscriber.plan == 'pro' and subscriber.qr_code_count >= 100:
        return HttpResponse("Ви досягли ліміту генерації QR-кодів для Pro тарифу.")
    
    if request.method == "POST":
        name = request.POST.get("name")
        link = request.POST.get("link_or_text")
        size = int(request.POST.get("size", 300))
        qr_color = request.POST.get("qr_color", "#000000")
        bg_color = request.POST.get("bg_color", "#FFFFFF")
        logo_file = request.FILES.get("logo")
        use_gradient = request.POST.get("gradient") == "on"
        color1 = request.POST.get("color1", "#ff0000")
        color2 = request.POST.get("color2", "#00ff00")
        shape = request.POST.get("shape", "square")
        round_corners = shape == "rounded"
        element_shape = request.POST.get("element_shape", "square")

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

            img = qr.make_image(fill_color=qr_color, back_color=bg_color).convert("RGBA")

            if element_shape == "circle":
                mask = Image.new("L", img.size, 0)
                draw = ImageDraw.Draw(mask)
                for x in range(0, img.size[0], qr.box_size):
                    for y in range(0, img.size[1], qr.box_size):
                        box = (x, y, x + qr.box_size, y + qr.box_size)
                        draw.ellipse(box, fill=255)
                img.putalpha(mask)

            elif element_shape == "triangle":
                mask = Image.new("L", img.size, 0)
                draw = ImageDraw.Draw(mask)
                for x in range(0, img.size[0], qr.box_size):
                    for y in range(0, img.size[1], qr.box_size):
                        box = [(x, y + qr.box_size), (x + qr.box_size // 2, y), (x + qr.box_size, y + qr.box_size)]
                        draw.polygon(box, fill=255)
                img.putalpha(mask)

            if use_gradient:
                gradient = Image.new("RGBA", img.size)
                draw = ImageDraw.Draw(gradient)

                for y in range(img.size[1]):
                    r = int((1 - y / img.size[1]) * int(color1[1:3], 16) + (y / img.size[1]) * int(color2[1:3], 16))
                    g = int((1 - y / img.size[1]) * int(color1[3:5], 16) + (y / img.size[1]) * int(color2[3:5], 16))
                    b = int((1 - y / img.size[1]) * int(color1[5:7], 16) + (y / img.size[1]) * int(color2[5:7], 16))
                    draw.line([(0, y), (img.size[0], y)], fill=(r, g, b, 255))

                qr_data = img.getdata()
                gradient_data = gradient.getdata()
                new_data = []
                for i in range(len(qr_data)):
                    if qr_data[i][0] < 128:
                        new_data.append(gradient_data[i])
                    else:
                        new_data.append((255, 255, 255, 0))
                img.putdata(new_data)

            img = img.resize((size, size), Image.Resampling.LANCZOS)

            if round_corners:
                corner_radius = int(size * 0.1)
                qr_mask = Image.new('L', img.size, 0)
                draw = ImageDraw.Draw(qr_mask)
                qr_box = img.getbbox()
                draw.rounded_rectangle(qr_box, corner_radius, fill=255)
                output = Image.new('RGBA', img.size, (0, 0, 0, 0))
                output.paste(img, mask=qr_mask)
                img = output

            if logo_file:
                try:
                    logo = Image.open(logo_file).convert("RGBA")
                    logo_size = int(size * 0.25)
                    logo = logo.resize((logo_size, logo_size), Image.Resampling.LANCZOS)
                    pos_x = (size - logo_size) // 2
                    pos_y = (size - logo_size) // 2
                    logo_bg = Image.new('RGBA', (logo_size, logo_size), (255, 255, 255, 255))
                    img.paste(logo_bg, (pos_x, pos_y))
                    img.paste(logo, (pos_x, pos_y), logo)
                except Exception as e:
                    print(f"Error processing logo: {e}")

            buffer = BytesIO()
            img.save(buffer, format="PNG")

            user_folder = os.path.join(settings.MEDIA_ROOT, request.user.username)
            if not os.path.exists(user_folder):
                os.makedirs(user_folder)

            file_path = os.path.join(user_folder, f"{name}.png")
            with open(file_path, 'wb') as f:
                f.write(buffer.getvalue())

            qr_image_url = os.path.join(settings.MEDIA_URL, request.user.username, f"{name}.png")

            if qr_code.objects.filter(name=name).exists():
                return render(request, "generator.html", {"error": "QR-код із таким ім'ям вже існує"})


            creation_time = timezone.now() + timedelta(hours=2)

            qr_code_instance = qr_code(
                name=name,
                link=link,
                size=size,
                shape=1 if round_corners else 0,
                custom_style="gradient" if use_gradient else "default",
                data_create=creation_time,  
                expiry_date=(creation_time + timedelta(days=30)).timestamp(),
                image=qr_image_url
            )
            qr_code_instance.save()

            return render(request, "generator.html", {"qr_image_url": qr_image_url})

        except Exception as e:
            print(f"Error generating QR code: {e}")
            return render(request, "generator.html", {"error": "Произошла ошибка при генерации QR-кода"})
    subscriber.qr_code_count += 1
    subscriber.save()
    return render(request, 'generator.html')


def render_history_gen(request: HttpResponse):
    qr_codes = qr_code.objects.all()  
    selected_plan = request.POST.get('selected_plan') or request.session.get('selected_plan')
    return render(request, "history_gen.html", {"qr_codes": qr_codes})

def logout_user(request: HttpResponse):
    logout(request)
    return redirect('authorization')

# Фришная подписка
def render_free(request: HttpResponse):
    if not request.user.is_authenticated:
        return redirect("authorization") 

    subscriber, created = Subscribers.objects.get_or_create(user=request.user)

    if subscriber.plan == 'free' and subscriber.qr_code_count >= 1:

        return render(request, "free.html", {"show_limit_modal": True})

    if request.method == "POST":
        name = request.POST.get("name")
        link = request.POST.get("link_or_text")
        size = int(request.POST.get("size", 300))
        qr_color = request.POST.get("qr_color", "#000000")
        bg_color = request.POST.get("bg_color", "#FFFFFF")
        logo_file = request.FILES.get("logo")
        use_gradient = request.POST.get("gradient") == "on"
        color1 = request.POST.get("color1", "#ff0000")
        color2 = request.POST.get("color2", "#00ff00")
        shape = request.POST.get("shape", "square")
        round_corners = shape == "rounded"
        element_shape = request.POST.get("element_shape", "square")

        if not name or not link:
            return render(request, "free.html", {"error": "Заповніть всі поля"})

        try:

            qr = qrcode.QRCode(
                version=1,
                error_correction=qrcode.constants.ERROR_CORRECT_H,
                box_size=10,
                border=4,
            )
            qr.add_data(link)
            qr.make(fit=True)
            img = qr.make_image(fill_color=qr_color, back_color=bg_color).convert("RGBA")

            if element_shape == "circle":
                mask = Image.new("L", img.size, 0)
                draw = ImageDraw.Draw(mask)
                for x in range(0, img.size[0], qr.box_size):
                    for y in range(0, img.size[1], qr.box_size):
                        box = (x, y, x + qr.box_size, y + qr.box_size)
                        draw.ellipse(box, fill=255)
                img.putalpha(mask)
            elif element_shape == "triangle":
                mask = Image.new("L", img.size, 0)
                draw = ImageDraw.Draw(mask)
                for x in range(0, img.size[0], qr.box_size):
                    for y in range(0, img.size[1], qr.box_size):
                        box = [(x, y + qr.box_size), (x + qr.box_size // 2, y), (x + qr.box_size, y + qr.box_size)]
                        draw.polygon(box, fill=255)
                img.putalpha(mask)

            if use_gradient:
                gradient = Image.new("RGBA", img.size)
                draw = ImageDraw.Draw(gradient)
                for y in range(img.size[1]):
                    r = int((1 - y / img.size[1]) * int(color1[1:3], 16) + (y / img.size[1]) * int(color2[1:3], 16))
                    g = int((1 - y / img.size[1]) * int(color1[3:5], 16) + (y / img.size[1]) * int(color2[3:5], 16))
                    b = int((1 - y / img.size[1]) * int(color1[5:7], 16) + (y / img.size[1]) * int(color2[5:7], 16))
                    draw.line([(0, y), (img.size[0], y)], fill=(r, g, b, 255))
                qr_data = img.getdata()
                gradient_data = gradient.getdata()
                new_data = []
                for i in range(len(qr_data)):
                    if qr_data[i][0] < 128:
                        new_data.append(gradient_data[i])
                    else:
                        new_data.append((255, 255, 255, 0))
                img.putdata(new_data)

            img = img.resize((size, size), Image.Resampling.LANCZOS)

            if round_corners:
                corner_radius = int(size * 0.1)
                qr_mask = Image.new('L', img.size, 0)
                draw = ImageDraw.Draw(qr_mask)
                qr_box = img.getbbox()
                draw.rounded_rectangle(qr_box, corner_radius, fill=255)
                output = Image.new('RGBA', img.size, (0, 0, 0, 0))
                output.paste(img, mask=qr_mask)
                img = output

            if logo_file:
                try:
                    logo = Image.open(logo_file).convert("RGBA")
                    logo_size = int(size * 0.25)
                    logo = logo.resize((logo_size, logo_size), Image.Resampling.LANCZOS)
                    pos_x = (size - logo_size) // 2
                    pos_y = (size - logo_size) // 2
                    logo_bg = Image.new('RGBA', (logo_size, logo_size), (255, 255, 255, 255))
                    img.paste(logo_bg, (pos_x, pos_y))
                    img.paste(logo, (pos_x, pos_y), logo)
                except Exception as e:
                    print(f"Error processing logo: {e}")

            buffer = BytesIO()
            img.save(buffer, format="PNG")
            user_folder = os.path.join(settings.MEDIA_ROOT, request.user.username)
            if not os.path.exists(user_folder):
                os.makedirs(user_folder)
            file_path = os.path.join(user_folder, f"{name}.png")
            with open(file_path, 'wb') as f:
                f.write(buffer.getvalue())
            qr_image_url = os.path.join(settings.MEDIA_URL, request.user.username, f"{name}.png")

            if qr_code.objects.filter(name=name).exists():
                return render(request, "free.html", {"error": "QR-код із таким ім'ям вже існує"})

            creation_time = timezone.now() + timedelta(hours=2)
            qr_code_instance = qr_code(
                name=name,
                link=link,
                size=size,
                shape=1 if round_corners else 0,
                custom_style="gradient" if use_gradient else "default",
                data_create=creation_time,
                expiry_date=(creation_time + timedelta(days=30)).timestamp(),
                image=qr_image_url
            )
            qr_code_instance.save()

            subscriber.qr_code_count += 1
            subscriber.save()

            return render(request, "free.html", {"qr_image_url": qr_image_url})

        except Exception as e:
            print(f"Error generating QR code: {e}")
            return render(request, "free.html", {"error": "Помилка при генерації QR-коду"})

    return render(request, "free.html")

def delete_qr_code(request, qr_id):
    qr = get_object_or_404(qr_code, id=qr_id)
    if qr.image:
        image_path = os.path.join(settings.MEDIA_ROOT, qr.image.name)
        if os.path.isfile(image_path):
            os.remove(image_path)
    qr.delete()

    subscriber, created = Subscribers.objects.get_or_create(user=request.user)
    subscriber.qr_code_count = max(subscriber.qr_code_count - 1, 0) 
    subscriber.save()

    return redirect('history_generations')

        

# Стандартная подписка
def render_standard(request: HttpResponse):
    if not request.user.is_authenticated:
        return redirect("authorization") 

    subscriber, created = Subscribers.objects.get_or_create(user=request.user)

    if subscriber.plan == 'standard' and subscriber.qr_code_count >= 50:
        return HttpResponse("Ви досягли ліміту генерації QR-кодів для стандартного тарифу.")
    
    if request.method == "POST":
        name = request.POST.get("name")
        link = request.POST.get("link_or_text")
        size = int(request.POST.get("size", 300))
        qr_color = request.POST.get("qr_color", "#000000")
        bg_color = request.POST.get("bg_color", "#FFFFFF")
        logo_file = request.FILES.get("logo")
        use_gradient = request.POST.get("gradient") == "on"
        color1 = request.POST.get("color1", "#ff0000")
        color2 = request.POST.get("color2", "#00ff00")
        shape = request.POST.get("shape", "square")
        round_corners = shape == "rounded"
        element_shape = request.POST.get("element_shape", "square")
        
        if not name or not link:
            return render(request, "standart.html", {"error": "Заповніть всі поля"})
        
        try:

            qr = qrcode.QRCode(
                version=1,
                error_correction=qrcode.constants.ERROR_CORRECT_H,
                box_size=10,
                border=4,
            )
            qr.add_data(link)
            qr.make(fit=True)
            img = qr.make_image(fill_color=qr_color, back_color=bg_color).convert("RGBA")

            if element_shape == "circle":
                mask = Image.new("L", img.size, 0)
                draw = ImageDraw.Draw(mask)
                for x in range(0, img.size[0], qr.box_size):
                    for y in range(0, img.size[1], qr.box_size):
                        box = (x, y, x + qr.box_size, y + qr.box_size)
                        draw.ellipse(box, fill=255)
                img.putalpha(mask)
            elif element_shape == "triangle":
                mask = Image.new("L", img.size, 0)
                draw = ImageDraw.Draw(mask)
                for x in range(0, img.size[0], qr.box_size):
                    for y in range(0, img.size[1], qr.box_size):
                        box = [(x, y + qr.box_size), (x + qr.box_size // 2, y), (x + qr.box_size, y + qr.box_size)]
                        draw.polygon(box, fill=255)
                img.putalpha(mask)
            

            if use_gradient:
                gradient = Image.new("RGBA", img.size)
                draw = ImageDraw.Draw(gradient)
                for y in range(img.size[1]):
                    r = int((1 - y / img.size[1]) * int(color1[1:3], 16) + (y / img.size[1]) * int(color2[1:3], 16))
                    g = int((1 - y / img.size[1]) * int(color1[3:5], 16) + (y / img.size[1]) * int(color2[3:5], 16))
                    b = int((1 - y / img.size[1]) * int(color1[5:7], 16) + (y / img.size[1]) * int(color2[5:7], 16))
                    draw.line([(0, y), (img.size[0], y)], fill=(r, g, b, 255))
                
                qr_data = img.getdata()
                gradient_data = gradient.getdata()
                new_data = []
                for i in range(len(qr_data)):
                    if qr_data[i][0] < 128:
                        new_data.append(gradient_data[i])
                    else:
                        new_data.append((255, 255, 255, 0))
                img.putdata(new_data)

            img = img.resize((size, size), Image.Resampling.LANCZOS)

            if round_corners:
                corner_radius = int(size * 0.1)
                qr_mask = Image.new('L', img.size, 0)
                draw = ImageDraw.Draw(qr_mask)
                qr_box = img.getbbox()
                draw.rounded_rectangle(qr_box, corner_radius, fill=255)
                output = Image.new('RGBA', img.size, (0, 0, 0, 0))
                output.paste(img, mask=qr_mask)
                img = output

            if logo_file:
                try:
                    logo = Image.open(logo_file).convert("RGBA")
                    logo_size = int(size * 0.25)
                    logo = logo.resize((logo_size, logo_size), Image.Resampling.LANCZOS)
                    pos_x = (size - logo_size) // 2
                    pos_y = (size - logo_size) // 2
                    logo_bg = Image.new('RGBA', (logo_size, logo_size), (255, 255, 255, 255))
                    img.paste(logo_bg, (pos_x, pos_y))
                    img.paste(logo, (pos_x, pos_y), logo)
                except Exception as e:
                    print(f"Error processing logo: {e}")

            buffer = BytesIO()
            img.save(buffer, format="PNG")
            
            user_folder = os.path.join(settings.MEDIA_ROOT, request.user.username)
            if not os.path.exists(user_folder):
                os.makedirs(user_folder)
            
            file_path = os.path.join(user_folder, f"{name}.png")
            with open(file_path, 'wb') as f:
                f.write(buffer.getvalue())
            
            qr_image_url = os.path.join(settings.MEDIA_URL, request.user.username, f"{name}.png")

            if qr_code.objects.filter(name=name).exists():
                return render(request, "standart.html", {"error": "QR-код із таким ім'ям вже існує"})
            

            creation_time = timezone.now() + timedelta(hours=2)
            qr_code_instance = qr_code(
                name=name,
                link=link,
                size=size,
                shape=1 if round_corners else 0,
                custom_style="gradient" if use_gradient else "default",
                data_create=creation_time,
                expiry_date=(creation_time + timedelta(days=30)).timestamp(),
                image=qr_image_url
            )
            qr_code_instance.save()

            subscriber.qr_code_count += 1
            subscriber.save()
            
            return render(request, "standart.html", {"qr_image_url": qr_image_url})
        
        except Exception as e:
            print(f"Error generating QR code: {e}")
            return render(request, "standart.html", {"error": "Помилка при генерації QR-коду"})
    
    return render(request, "standart.html")


# Прошка 
def render_pro(request: HttpResponse):
    if not request.user.is_authenticated:
        return redirect("authorization")  

    subscriber, created = Subscribers.objects.get_or_create(user=request.user)

    if subscriber.plan == 'pro' and subscriber.qr_code_count >= 100:
        return HttpResponse("Ви досягли ліміту генерації QR-кодів для Pro тарифу.")
    
    if request.method == "POST":
        name = request.POST.get("name")
        link = request.POST.get("link_or_text")
        size = int(request.POST.get("size", 300))
        qr_color = request.POST.get("qr_color", "#000000")
        bg_color = request.POST.get("bg_color", "#FFFFFF")
        logo_file = request.FILES.get("logo")
        use_gradient = request.POST.get("gradient") == "on"
        color1 = request.POST.get("color1", "#ff0000")
        color2 = request.POST.get("color2", "#00ff00")
        shape = request.POST.get("shape", "square")
        round_corners = shape == "rounded"
        element_shape = request.POST.get("element_shape", "square")
        
        if not name or not link:
            return render(request, "pro.html", {"error": "Заповніть всі поля"})
        
        try:

            qr = qrcode.QRCode(
                version=1,
                error_correction=qrcode.constants.ERROR_CORRECT_H,
                box_size=10,
                border=4,
            )
            qr.add_data(link)
            qr.make(fit=True)
            img = qr.make_image(fill_color=qr_color, back_color=bg_color).convert("RGBA")

            if element_shape == "circle":
                mask = Image.new("L", img.size, 0)
                draw = ImageDraw.Draw(mask)
                for x in range(0, img.size[0], qr.box_size):
                    for y in range(0, img.size[1], qr.box_size):
                        box = (x, y, x + qr.box_size, y + qr.box_size)
                        draw.ellipse(box, fill=255)
                img.putalpha(mask)
            elif element_shape == "triangle":
                mask = Image.new("L", img.size, 0)
                draw = ImageDraw.Draw(mask)
                for x in range(0, img.size[0], qr.box_size):
                    for y in range(0, img.size[1], qr.box_size):
                        box = [(x, y + qr.box_size), (x + qr.box_size // 2, y), (x + qr.box_size, y + qr.box_size)]
                        draw.polygon(box, fill=255)
                img.putalpha(mask)

            if use_gradient:
                gradient = Image.new("RGBA", img.size)
                draw = ImageDraw.Draw(gradient)
                for y in range(img.size[1]):
                    r = int((1 - y / img.size[1]) * int(color1[1:3], 16) + (y / img.size[1]) * int(color2[1:3], 16))
                    g = int((1 - y / img.size[1]) * int(color1[3:5], 16) + (y / img.size[1]) * int(color2[3:5], 16))
                    b = int((1 - y / img.size[1]) * int(color1[5:7], 16) + (y / img.size[1]) * int(color2[5:7], 16))
                    draw.line([(0, y), (img.size[0], y)], fill=(r, g, b, 255))
                
                qr_data = img.getdata()
                gradient_data = gradient.getdata()
                new_data = []
                for i in range(len(qr_data)):
                    if qr_data[i][0] < 128:
                        new_data.append(gradient_data[i])
                    else:
                        new_data.append((255, 255, 255, 0))
                img.putdata(new_data)

            img = img.resize((size, size), Image.Resampling.LANCZOS)

            if round_corners:
                corner_radius = int(size * 0.1)
                qr_mask = Image.new('L', img.size, 0)
                draw = ImageDraw.Draw(qr_mask)
                qr_box = img.getbbox()
                draw.rounded_rectangle(qr_box, corner_radius, fill=255)
                output = Image.new('RGBA', img.size, (0, 0, 0, 0))
                output.paste(img, mask=qr_mask)
                img = output

            if logo_file:
                try:
                    logo = Image.open(logo_file).convert("RGBA")
                    logo_size = int(size * 0.25)
                    logo = logo.resize((logo_size, logo_size), Image.Resampling.LANCZOS)
                    pos_x = (size - logo_size) // 2
                    pos_y = (size - logo_size) // 2
                    logo_bg = Image.new('RGBA', (logo_size, logo_size), (255, 255, 255, 255))
                    img.paste(logo_bg, (pos_x, pos_y))
                    img.paste(logo, (pos_x, pos_y), logo)
                except Exception as e:
                    print(f"Error processing logo: {e}")

            buffer = BytesIO()
            img.save(buffer, format="PNG")
            
            user_folder = os.path.join(settings.MEDIA_ROOT, request.user.username)
            if not os.path.exists(user_folder):
                os.makedirs(user_folder)
            
            file_path = os.path.join(user_folder, f"{name}.png")
            with open(file_path, 'wb') as f:
                f.write(buffer.getvalue())
            
            qr_image_url = os.path.join(settings.MEDIA_URL, request.user.username, f"{name}.png")

            if qr_code.objects.filter(name=name).exists():
                return render(request, "pro.html", {"error": "QR-код із таким ім'ям вже існує"})

            creation_time = timezone.now() + timedelta(hours=2)
            qr_code_instance = qr_code(
                name=name,
                link=link,
                size=size,
                shape=1 if round_corners else 0,
                custom_style="gradient" if use_gradient else "default",
                data_create=creation_time,
                expiry_date=(creation_time + timedelta(days=30)).timestamp(),
                image=qr_image_url
            )
            qr_code_instance.save()
    
            subscriber.qr_code_count += 1
            subscriber.save()
            
            return render(request, "pro.html", {"qr_image_url": qr_image_url})
        
        except Exception as e:
            print(f"Error generating QR code: {e}")
            return render(request, "pro.html", {"error": "Помилка при генерації QR-коду"})
    
    return render(request, "pro.html")


# def delete_qr_code(request, qr_id):
#     qr = get_object_or_404(qr_code, id=qr_id)
#     if qr.image:
#         image_path = os.path.join(settings.MEDIA_ROOT, qr.image.name)
#         if os.path.isfile(image_path):
#             os.remove(image_path)
#     qr.delete()
#     return redirect('history_generations')

def render_desktop(request):
    if not request.user.is_authenticated:
        return redirect("authorization")

    subscriber, created = Subscribers.objects.get_or_create(user=request.user)

    # Устанавливаем лимит 10 по умолчанию для плана desktop
    if created or subscriber.plan == 'desktop':
        if subscriber.plan != 'desktop':
            subscriber.plan = 'desktop'
            subscriber.qr_code_limit = 10  # Лимит по умолчанию
            subscriber.qr_code_count = 0
            subscriber.save()

    # Подсчитываем количество занятых слотов (не пустых QR-кодов)
    used_slots = qr_code.objects.filter(user=request.user).exclude(name__isnull=True).count()

    # Обработка покупки дополнительных слотов
    if request.method == "POST" and request.POST.get("action") == "buy":
        try:
            additional_slots = int(request.POST.get("additional_slots", 0))
            if additional_slots > 0 and additional_slots <= 100:
                cost = additional_slots * 0.50
                # Добавляем пустые слоты в базу данных
                for _ in range(additional_slots):
                    qr_code.objects.create(
                        user=request.user  # Только пользователь
                    )
                subscriber.qr_code_limit += additional_slots
                subscriber.save()
                return render(request, "desktop.html", {
                    "qr_code_count": used_slots,
                    "qr_code_limit": subscriber.qr_code_limit,
                    "success": f"Ви успішно додали {additional_slots} ячейок за {cost}$!"
                })
            else:
                return render(request, "desktop.html", {
                    "error": "Введіть число від 1 до 100",
                    "qr_code_count": used_slots,
                    "qr_code_limit": subscriber.qr_code_limit
                })
        except ValueError:
            return render(request, "desktop.html", {
                "error": "Введіть коректне число",
                "qr_code_count": used_slots,
                "qr_code_limit": subscriber.qr_code_limit
            })

    # Проверка лимита перед генерацией
    if used_slots >= subscriber.qr_code_limit:
        return render(request, "desktop.html", {
            "qr_code_count": used_slots,
            "qr_code_limit": subscriber.qr_code_limit,
            "show_limit_modal": True
        })

    # Генерация QR-кода
    if request.method == "POST" and request.POST.get("action") == "generate":
        name = request.POST.get("name")
        link = request.POST.get("link_or_text")
        size = int(request.POST.get("size", 300))
        qr_color = request.POST.get("qr_color", "#000000")
        bg_color = request.POST.get("bg_color", "#FFFFFF")
        logo_file = request.FILES.get("logo")
        use_gradient = request.POST.get("gradient") == "on"
        color1 = request.POST.get("color1", "#ff0000")
        color2 = request.POST.get("color2", "#00ff00")
        shape = request.POST.get("shape", "square")
        round_corners = shape == "rounded"
        element_shape = request.POST.get("element_shape", "square")

        if not name or not link:
            return render(request, "desktop.html", {
                "qr_code_count": used_slots,
                "qr_code_limit": subscriber.qr_code_limit,
                "error": "Заповніть усі поля"
            })

        try:
            # Находим первый пустой слот
            qr_slot = qr_code.objects.filter(user=request.user, name__isnull=True).first()
            if not qr_slot and used_slots < subscriber.qr_code_limit:
                qr_slot = qr_code.objects.create(user=request.user)

            if not qr_slot:
                return render(request, "desktop.html", {
                    "qr_code_count": used_slots,
                    "qr_code_limit": subscriber.qr_code_limit,
                    "show_limit_modal": True
                })

            # Генерация QR-кода
            qr = qrcode.QRCode(
                version=1,
                error_correction=qrcode.constants.ERROR_CORRECT_H,
                box_size=10,
                border=4,
            )
            qr.add_data(link)
            qr.make(fit=True)
            img = qr.make_image(fill_color=qr_color, back_color=bg_color).convert("RGBA")

            # Обработка формы элементов
            if element_shape == "circle":
                mask = Image.new("L", img.size, 0)
                draw = ImageDraw.Draw(mask)
                for x in range(0, img.size[0], qr.box_size):
                    for y in range(0, img.size[1], qr.box_size):
                        box = (x, y, x + qr.box_size, y + qr.box_size)
                        draw.ellipse(box, fill=255)
                img.putalpha(mask)
            elif element_shape == "triangle":
                mask = Image.new("L", img.size, 0)
                draw = ImageDraw.Draw(mask)
                for x in range(0, img.size[0], qr.box_size):
                    for y in range(0, img.size[1], qr.box_size):
                        box = [(x, y + qr.box_size), (x + qr.box_size // 2, y), (x + qr.box_size, y + qr.box_size)]
                        draw.polygon(box, fill=255)
                img.putalpha(mask)

            # Градиент
            if use_gradient:
                gradient = Image.new("RGBA", img.size)
                draw = ImageDraw.Draw(gradient)
                for y in range(img.size[1]):
                    r = int((1 - y / img.size[1]) * int(color1[1:3], 16) + (y / img.size[1]) * int(color2[1:3], 16))
                    g = int((1 - y / img.size[1]) * int(color1[3:5], 16) + (y / img.size[1]) * int(color2[3:5], 16))
                    b = int((1 - y / img.size[1]) * int(color1[5:7], 16) + (y / img.size[1]) * int(color2[5:7], 16))
                    draw.line([(0, y), (img.size[0], y)], fill=(r, g, b, 255))
                qr_data = img.getdata()
                gradient_data = gradient.getdata()
                new_data = []
                for i in range(len(qr_data)):
                    if qr_data[i][0] < 128:
                        new_data.append(gradient_data[i])
                    else:
                        new_data.append((255, 255, 255, 0))
                img.putdata(new_data)

            img = img.resize((size, size), Image.Resampling.LANCZOS)

            # Закругленные углы
            if round_corners:
                corner_radius = int(size * 0.1)
                qr_mask = Image.new('L', img.size, 0)
                draw = ImageDraw.Draw(qr_mask)
                qr_box = img.getbbox()
                draw.rounded_rectangle(qr_box, corner_radius, fill=255)
                output = Image.new('RGBA', img.size, (0, 0, 0, 0))
                output.paste(img, mask=qr_mask)
                img = output

            # Добавление логотипа
            if logo_file:
                try:
                    logo = Image.open(logo_file).convert("RGBA")
                    logo_size = int(size * 0.25)
                    logo = logo.resize((logo_size, logo_size), Image.Resampling.LANCZOS)
                    pos_x = (size - logo_size) // 2
                    pos_y = (size - logo_size) // 2
                    logo_bg = Image.new('RGBA', (logo_size, logo_size), (255, 255, 255, 255))
                    img.paste(logo_bg, (pos_x, pos_y))
                    img.paste(logo, (pos_x, pos_y), logo)
                except Exception as e:
                    print(f"Error processing logo: {e}")

            # Сохранение изображения
            buffer = BytesIO()
            img.save(buffer, format="PNG")
            user_folder = os.path.join(settings.MEDIA_ROOT, request.user.username)
            if not os.path.exists(user_folder):
                os.makedirs(user_folder)
            file_path = os.path.join(user_folder, f"{name}.png")
            with open(file_path, 'wb') as f:
                f.write(buffer.getvalue())
            qr_image_url = os.path.join(settings.MEDIA_URL, request.user.username, f"{name}.png")

            # Проверка на уникальность имени
            if qr_code.objects.filter(user=request.user, name=name).exists():
                return render(request, "desktop.html", {
                    "qr_code_count": used_slots,
                    "qr_code_limit": subscriber.qr_code_limit,
                    "error": "QR-код із таким ім'ям уже існує"
                })

            # Обновляем пустой слот
            creation_time = timezone.now() + timedelta(hours=2)
            qr_slot.name = name
            qr_slot.link = link
            qr_slot.size = size
            qr_slot.shape = 1 if round_corners else 0
            qr_slot.custom_style = "gradient" if use_gradient else "default"
            qr_slot.data_create = creation_time
            qr_slot.expiry_date = int((creation_time + timedelta(days=30)).timestamp())
            qr_slot.image = qr_image_url
            qr_slot.save()

            return render(request, "desktop.html", {
                "qr_image_url": qr_image_url,
                "qr_code_count": used_slots + 1,  # Увеличиваем после успеха
                "qr_code_limit": subscriber.qr_code_limit
            })

        except Exception as e:
            print(f"Error generating QR code: {e}")
            return render(request, "desktop.html", {
                "qr_code_count": used_slots,
                "qr_code_limit": subscriber.qr_code_limit,
                "error": "Помилка при генерації QR-коду"
            })

    return render(request, "desktop.html", {
        "qr_code_count": used_slots,
        "qr_code_limit": subscriber.qr_code_limit
    })