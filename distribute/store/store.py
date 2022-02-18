from django.db import models

class StoreType(models.TextChoices):
    RawLink = 'RawLink'
    AppStore = 'AppStore'
    GooglePlay = 'GooglePlay'
    MicrosoftStore = 'MicrosoftStore'
    Vivo = 'Vivo'
