import logging
import hashlib
import hmac
import time
from django.shortcuts import render, redirect
from django.contrib.auth import login, get_user_model
from django.conf import settings

logger = logging.getLogger(__name__)

def telegram_login(request):
    if request.method == 'GET' and request.GET:
        logger.info("Получены GET-параметры от Telegram: %s", request.GET.dict())
        auth_data = request.GET.dict()
        received_hash = auth_data.pop('hash', None)
        logger.info("Полученный hash: %s", received_hash)

        # Формирование строки для проверки подписи
        sorted_data = sorted(auth_data.items())
        data_check_string = "\n".join([f"{k}={v}" for k, v in sorted_data])
        logger.info("Сформированная строка для проверки: %s", data_check_string)

        # Вычисление HMAC с использованием токена бота
        secret_key = hashlib.sha256(settings.TELEGRAM_BOT_TOKEN.encode()).digest()
        computed_hash = hmac.new(secret_key, data_check_string.encode(), hashlib.sha256).hexdigest()
        logger.info("Вычисленный hash: %s", computed_hash)

        if computed_hash != received_hash:
            logger.error("Ошибка: hash не совпадает. Данные недействительны.")
            return render(request, 'accounts/error.html', {'message': 'Неверные данные авторизации.'})

        # Проверка срока действия данных (24 часа)
        auth_date = int(auth_data.get('auth_date', 0))
        if time.time() - auth_date > 86400:
            logger.error("Ошибка: данные устарели.")
            return render(request, 'accounts/error.html', {'message': 'Срок действия данных истёк.'})

        telegram_id = auth_data.get('id')
        logger.info("Telegram ID: %s", telegram_id)
        username = auth_data.get('username')
        logger.info("Telegram username: %s", username)

        UserModel = get_user_model()
        try:
            user = UserModel.objects.get(username=telegram_id)
            logger.info("Пользователь найден в базе: %s", user)
        except UserModel.DoesNotExist:
            logger.info("Пользователь не найден. Создаём нового...")
            user = UserModel.objects.create_user(username=telegram_id)
            logger.info("Новый пользователь создан: %s", user)
            user.refresh_from_db()
            logger.info("Данные пользователя после обновления: %s", user)
            try:
                profile = user.profile
                logger.info("Профиль создан автоматически: %s", profile)
            except Exception as e:
                logger.error("Ошибка при получении профиля: %s", e)
            user.profile.alias = username
            user.profile.save()
            logger.info("Профиль обновлён с alias: %s", user.profile.alias)

        login(request, user)
        logger.info("Пользователь авторизован: %s", user)
        user_from_db = UserModel.objects.get(username=telegram_id)
        logger.info("Данные пользователя из базы: %s, alias: %s", user_from_db, user_from_db.profile.alias)
        return redirect('profile')
    else:
        logger.info("сработал else в telegram_login")
        return render(request, 'accounts/telegram_login.html')

def profile(request):
    return render(request, 'accounts/profile.html')
