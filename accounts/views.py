import hashlib
import hmac
import time
from django.conf import settings
from django.shortcuts import render, redirect
from django.contrib.auth import login, get_user_model
from django.contrib.auth.models import User

def telegram_login(request):
    if request.method == 'GET' and request.GET:
        data_check_string = ''
        auth_data = request.GET.dict()
        received_hash = auth_data.pop('hash', None)

        # Сортируем ключи и формируем строку
        sorted_data = sorted(auth_data.items())
        data_check_string = "\n".join([f"{k}={v}" for k, v in sorted_data])

        # Вычисляем хэш
        secret_key = hashlib.sha256(settings.TELEGRAM_BOT_TOKEN.encode()).digest()
        computed_hash = hmac.new(secret_key, data_check_string.encode(), hashlib.sha256).hexdigest()

        # Проверка на подлинность
        if computed_hash != received_hash:
            return render(request, 'accounts/error.html', {'message': 'Неверные данные авторизации.'})

        # (Опционально) можно проверить, не истёк ли срок действия данных:
        auth_date = int(auth_data.get('auth_date', 0))
        if time.time() - auth_date > 86400:  # 24 часа
            return render(request, 'accounts/error.html', {'message': 'Срок действия данных истёк.'})

        # Авторизуем пользователя или создаём нового
        telegram_id = auth_data.get('id')
        username = auth_data.get('username')  # это и будет нашим алиасом

        UserModel = get_user_model()
        try:
            user = UserModel.objects.get(username=telegram_id)
        except UserModel.DoesNotExist:
            # Создаем нового пользователя
            user = UserModel.objects.create_user(username=telegram_id)
            # Записываем alias в профиль
            user.profile.alias = username
            user.profile.save()

        # Авторизуем пользователя
        login(request, user)
        return redirect('profile')
    else:
        # Если нет GET-параметров, отобразим страницу с виджетом
        return render(request, 'accounts/telegram_login.html')

def profile(request):
    return render(request, 'accounts/profile.html')