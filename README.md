# Інтернет-магазин

## Список учасників команди:
- Артем Власов(TEAMLEAD)/Artem Vlasov(TEAMLEAD) - [GitHub](https://github.com/ArtemVlasov2009)
- Ткач Богдан/Tkach Bogdan - [GitHub](https://github.com/Bogdantkach12)
- Іван Єжов/Ivan Yezhov - [GitHub]
---
## Що робить наш проект/What our project does

##### Наш проект це гнучкий генератор qr кодів / Our project is a flexible qr code generator
---
У нашому проекті використовується багато технологій, а саме:

- **Django** — фреймворк, який слугує основою для створення всього проєкту;  
- **SQLite3** — використовується для роботи з базою даних SQLite;  
- **Requests** — застосовується для обробки HTTP-запитів;  
- **GitHub** — платформа для управління кодом і спільної розробки;  
- **PIL** — бібліотека для обробки зображень;  
- **HTML, CSS, JavaScript** — базові технології для створення інтерфейсу користувача.

![alt text](https://github.com/ArtemVlasov2009/qr_working_project/blob/main/FigJam.png "FigJam")
---
#### Щоб запустити наш проект локально на компьютері, треба відкрити проект у IDE, та встановити всі модулі, які вказані вище, та запустити файл manage.py / To run our project locally on your computer, you need to open the project in the IDE, install all the modules listed above, and run the manage.py file
---
#### Щоб запустити проект віддалено, на сервері, треба використовувати хост [PythonAnywhere](https://www.pythonanywhere.com) / To run the project remotely on the server, you need to use the [PythonAnywhere] host (https://www.pythonanywhere.com)  
---
## В нашому проекті є декілька окремих застосунків, а саме / Our project has several specific applications, namely:

- **base.html** - Це початкова сторінка
- **registration.html** - Це сторінка яка відповідає за реєстрацію
- **authorization.html** - Це сторінка яка відповідає за авторизацію
- **free.html**, **standart.html**, **pro.html**, **desktop.html** - Це сторінки які відповідають за генерацію кодів з різною пропискою
---
--
Приклад функції рендеру сторінок, наприклад render_home:
```python
def render_home(request):
    selected_plan = request.session.get('selected_plan', None)
    
    if request.method == "POST":
        selected_plan = request.POST.get("selected_plan")
        if selected_plan in ['free', 'standard', 'pro', 'desktop']:
            request.session['selected_plan'] = selected_plan
            return redirect('authorization')
    
    return render(request, 'base.html', {'selected_plan': selected_plan})
```
---
Приклад нашого html, наприклад authorization:
```html
{% load static %}

<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{% block title %}Сторінка авторизації{% endblock %}</title>
    <link rel="stylesheet" href="{% static 'css/authorization.css' %}">
    <link rel="icon" href="{% static 'images/Logo.png' %}" type="image/png">
</head>
<body>
    {% block content %}
    <header class="header_main">
        <a class = 'home_url' href="{% url 'home' %}">
            <img class="Logo_img" src="{% static 'images/Logo.png' %}" alt="Logo">
        </a>
        <a href="{% url 'home' %}" class="{% if request.resolver_match.url_name == 'home' %}current-page{% endif %}">Головна</a>
        <a href="{% url 'registration' %}" class="{% if request.resolver_match.url_name == 'registration' %}current-page{% endif %}">Реєстрація</a>
        <a href="{% url 'authorization' %}" class="{% if request.resolver_match.url_name == 'authorization' %}current-page{% endif %}">Авторизація</a>
        <a href="{% url 'contacts' %}" class="{% if request.resolver_match.url_name == 'contacts' %}current-page{% endif %}">Контакти</a>
    </header>
    <div class="registration-container">
        <h1>Авторизація</h1>
        <form method="POST" action="{% url 'authorization' %}">
            {% csrf_token %}
            <div class="form-group">
                <label for="name">Ім'я користувача:</label>
                <input type="text" id="name" name="name" required>
            </div>
            <div class="form-group">
                <label for="password">Пароль:</label>
                <input type="password" id="password" name="password" required>
            </div>
            <div class="form-group">
                <label for="email-confirm">Підтвердження через Email:</label>
                <input type="email" id="email-confirm" name="email-confirm" required>
                {% if user == None %}
                <p class = "Proverka_login_password">Логін або пароль некоректні</p>
                {% endif %}
            </div>
            <p class = "Not_reg">Не маєте аккаунта? <a class = "reg_reg_btn" href="{% url 'registration' %}">Зареєструйтесь</a></p>
            <button type="submit" class="register-btn">Авторизуватися</button>
        </form>
    </div>
    {% endblock %}
</body>    
</html>
```
---
Наші моделі:
```python
from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone  
import time

class Subscribers(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    subscriber = models.CharField(max_length=255)
    qr_code_count = models.IntegerField(default=0)  
    plan = models.CharField(max_length=10, default='free')
    qr_code_limit = models.IntegerField(default=10)  
    balance = models.DecimalField(max_digits=10, decimal_places=2, default=0.00)

    def __str__(self):
        return self.subscriber

class qr_code(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, null=True, blank=True)
    name = models.CharField(max_length=255, null=True, blank=True)
    link = models.URLField(max_length=2000, default='http://127.0.0.1:8000/')  
    size = models.IntegerField(default=300)
    shape = models.IntegerField(default=0)  
    custom_style = models.CharField(max_length=50, default="default")
    data_create = models.DateTimeField(default=timezone.now, null=False)
    expiry_date = models.FloatField(default=time.time)  
    image = models.CharField(max_length=500, null=True, blank=True)
    plan_created = models.CharField(max_length=50, default="free")

    def __str__(self):
        return self.name or "Unnamed QR Code"
```
---
Наші urls:
```python
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
    path('qr-expired/', views.qr_expired, name='qr_expired'),
    path('create_code/<int:pk>/', views.render_redirect, name='render_redirect'),
]
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
```
---
Приклад сторінки підписок, наприклад pro:
```html
{% load static %}
<html lang="uk">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Сторінка генерації</title>
    <link rel="stylesheet" href="{% static 'css/pro.css' %}">
    <link rel="icon" href="{% static 'images/Logo.png' %}" type="image/png">
</head>
<body>
    <header class="header_main">
        <a class='home_url' href="http://127.0.0.1:8000/home_auth">
            <img class="Logo_img" src="{% static 'images/Logo.png' %}" alt="Logo" />
        </a>
        <a href="http://127.0.0.1:8000/home_auth" class="{% if request.path == '/' %}current-page{% endif %}">Головна</a>
        <a href="{% url 'generator' %}" class="{% if request.path == '/generator/' %}current-page{% endif %}">Кодогенерація</a>
        <a href="{% url 'history_generations' %}" class="{% if request.path == '/history_generations/' %}current-page{% endif %}">Генерації</a>
        <a href="{% url 'contacts' %}" class="{% if request.path == '/contacts/' %}current-page{% endif %}">Контакти</a>
        <div class="logout">
            <a class="logout_кнопка" href="{% url 'logout' %}">Вийти: {{ request.user.username }}</a>
        </div>
    </header>
    <div class="Generator_frame">
        <div class="Generator_header">
            <p>Згенеруйте ваш QR code</p>
        </div>
        <div class="Generator_internal_frame">
            <form method="POST" enctype="multipart/form-data">
                {% csrf_token %}
                <label for="name">Ім'я:</label>
                <input type="text" id="name" name="name" required><br><br>
                <label for="link_or_text">Посилання або текст:</label>
                <input type="text" id="link_or_text" name="link_or_text" required><br><br>
                <label for="size">Розмір генерації QR-коду:</label>
                <select id="size" name="size">
                    <option value="200">200x200</option>
                    <option value="300">300x300</option>
                    <option value="400">400x400</option>
                    <option value="500">500x500</option>
                </select><br><br>
                <label for="qr_color">Колір QR-коду:</label>
                <input type="color" id="qr_color" name="qr_color" value="#000000"><br><br>
                <label for="bg_color">Колір фону:</label>
                <input type="color" id="bg_color" name="bg_color" value="#FFFFFF"><br><br>
                <label for="logo">Додати логотип:</label>
                <input type="file" id="logo" name="logo" accept="image/*"><br><br>
                <label for="gradient">Налаштувати градієнт:</label>
                <input type="checkbox" id="gradient" name="gradient"><br><br>
                <div id="gradient-colors" style="display: none;">
                    <label for="color1">Колір 1 градієнту:</label>
                    <input type="color" id="color1" name="color1" value="#ff0000"><br><br>
                    <label for="color2">Колір 2 градієнту:</label>
                    <input type="color" id="color2" name="color2" value="#00ff00"><br><br>
                </div>
                <label for="shape">Форма QR-коду:</label><br>
                <label>
                    <input type="radio" name="shape" value="rounded" checked>
                    З закругленими кутами
                </label><br>
                <label>
                    <input type="radio" name="shape" value="square">
                    Квадратна форма
                </label><br><br>
                <label for="element_shape">Форма елементів QR-коду:</label><br>
                <label>
                    <input type="radio" name="element_shape" value="circle" checked>
                    Кружки
                </label><br>
                <label>
                    <input type="radio" name="element_shape" value="triangle">
                    Трикутники
                </label><br>
                <label>
                    <input type="radio" name="element_shape" value="square">
                    Квадрати
                </label><br><br>
                <button class="Buttom_Down" type="submit">Генерувати</button>
            </form>
            <div class="qr-code-overlay">
                <h2>Ваш QR-код:</h2>
                <div style="width: 200px; height: 200px; overflow: hidden;">
                    {% if qr_image_url %}
                        <img src="{{ qr_image_url }}" alt="QR-код" id="qr-code-img" style="width: 200px; height: 200px; object-fit: contain;">
                    {% else %}
                        <img src="{% static 'images/qrCodeExample.png' %}" alt="Placeholder" id="qr-code-placeholder" style="width: 200px; height: 200px; object-fit: contain;">
                    {% endif %}
                </div>
            </div>
        </div>
    </div>
    <script>
        document.getElementById('gradient').addEventListener('change', function() {
            const gradientColors = document.getElementById('gradient-colors');
            gradientColors.style.display = this.checked ? 'block' : 'none';
        });
    </script>
</body>
</html>
```
### Чому саме SQLite3: / Why SQLite3:

##### SQLite3 вбудована в Python, що спрощує її використання. Ми вже знайомі з цією базою даних з попереднього досвіду. Для роботи SQLite3 потрібен лише один файл, що містить всю базу даних. При використанні з Flask можуть знадобитися додаткові файли міграцій, але це не обов'язково для базового функціонування SQLite3. / SQLite3 is built into Python, which makes it easy to use. We are already familiar with this database from previous experience. SQLite3 requires only one file containing the entire database. When used with Flask, additional migration files may be required, but this is not necessary for the basic functioning of SQLite3.
---
# Висновки: / Conclusions:
### Під час роботи над цим проектом ми дізналися багато цікавої та корисної інформації, для розробки сайтів, та вивчили багато нових технологій, покращили комунікацію розуміння коду / While working on this project, we learnt a lot of interesting and useful information for website development, and learned a lot of new technologies, improved communication and understanding of the code.
