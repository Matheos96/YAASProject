from django.db import models
from django.contrib.auth.models import User
# Create your models here.


class UserLanguage(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, unique=True)
    LANG_EN = 1
    LANG_SV = 2
    LANG_CHOICES = ((LANG_EN, 'English'), (LANG_SV, 'Swedish'))
    lang_pref = models.IntegerField(choices=LANG_CHOICES, default=LANG_EN)

    def __str__(self):
        return self.user.username
