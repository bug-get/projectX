import logging
from django.db.models.signals import post_save
from django.contrib.auth.models import User
from django.dispatch import receiver
from .models import Profile

logger = logging.getLogger(__name__)

@receiver(post_save, sender=User)
def create_profile(sender, instance, created, **kwargs):
    if created:
        Profile.objects.create(user=instance)
        logger.info("Сигнал: профиль создан для пользователя %s", instance)

@receiver(post_save, sender=User)
def save_profile(sender, instance, **kwargs):
    try:
        instance.profile.save()
        logger.info("Сигнал: профиль сохранён для пользователя %s", instance)
    except Exception as e:
        logger.error("Ошибка при сохранении профиля для пользователя %s: %s", instance, e)