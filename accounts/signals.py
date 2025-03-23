# accounts/signals.py
from django.db.models.signals import post_save
from django.contrib.auth.models import User
from django.dispatch import receiver
from .models import Profile

@receiver(post_save, sender=User)
def create_profile(sender, instance, created, **kwargs):
    if created:
        Profile.objects.create(user=instance)
        print("Сигнал: профиль создан для пользователя", instance)

@receiver(post_save, sender=User)
def save_profile(sender, instance, **kwargs):
    try:
        instance.profile.save()
        print("Сигнал: профиль сохранён для пользователя", instance)
    except Exception as e:
        print("Сигнал: Ошибка при сохранении профиля для пользователя", instance, ":", e)