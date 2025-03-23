# accounts/views.py
import hashlib
import hmac
import time
from django.shortcuts import render, redirect
from django.contrib.auth import login, get_user_model

def telegram_login(request):
    if request.method == 'GET' and request.GET:
        # 1. Выводим полученные GET-параметры
        print("Получены GET-параметры от Telegram:", request.GET.dict())
        auth_data = request.GET.dict()
        received_hash = auth_data.pop('hash', None)
        print("Полученный hash:", received_hash)

        # 2. Формирование data_check_string (отсортированные параметры)
        sorted_data = sorted(auth_data.items())
        data_check_string = "\n".join([f"{k}={v}" for k, v in sorted_data])
        print("Сформированная строка для проверки:", data_check_string)

        # 3. Вычисляем хэш для проверки подлинности
        # Предполагается, что в settings.py у вас есть TELEGRAM_BOT_TOKEN
        from django.conf import settings
        secret_key = hashlib.sha256(settings.TELEGRAM_BOT_TOKEN.encode()).digest()
        computed_hash = hmac.new(secret_key, data_check_string.encode(), hashlib.sha256).hexdigest()
        print("Вычисленный hash:", computed_hash)

        if computed_hash != received_hash:
            print("Ошибка: hash не совпадает. Данные недействительны.")
            return render(request, 'accounts/error.html', {'message': 'Неверные данные авторизации.'})

        # 4. Проверка срока действия данных
        auth_date = int(auth_data.get('auth_date', 0))
        if time.time() - auth_date > 86400:  # 24 часа
            print("Ошибка: данные устарели.")
            return render(request, 'accounts/error.html', {'message': 'Срок действия данных истёк.'})

        # 5. Попытка найти пользователя по telegram id
        telegram_id = auth_data.get('id')
        print("Telegram ID:", telegram_id)
        username = auth_data.get('username')
        print("Telegram username:", username)

        UserModel = get_user_model()
        try:
            user = UserModel.objects.get(username=telegram_id)
            print("Пользователь найден в базе:", user)
        except UserModel.DoesNotExist:
            print("Пользователь не найден. Создаём нового...")
            user = UserModel.objects.create_user(username=telegram_id)
            print("Новый пользователь создан:", user)
            # После создания, предполагается, что сигнал создаст профиль.
            # Немного подождем, чтобы профиль точно создался.
            user.refresh_from_db()  # Обновляем данные пользователя из базы
            print("Данные пользователя после обновления:", user)
            try:
                profile = user.profile
                print("Профиль создан автоматически:", profile)
            except Exception as e:
                print("Ошибка при получении профиля:", e)
            # Если профиль существует, можно обновить alias:
            user.profile.alias = username
            user.profile.save()
            print("Профиль обновлён с alias:", user.profile.alias)

        # 6. Авторизация пользователя
        login(request, user)
        print("Пользователь авторизован:", user)
        # Для проверки можно сразу вывести данные из базы
        user_from_db = UserModel.objects.get(username=telegram_id)
        print("Данные пользователя из базы:", user_from_db, user_from_db.profile.alias)
        return redirect('profile')
    else:
        # Если GET-параметры отсутствуют, просто показываем страницу с виджетом
        return render(request, 'accounts/telegram_login.html')

def profile(request):
    return render(request, 'accounts/profile.html')