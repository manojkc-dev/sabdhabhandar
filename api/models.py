from django.db import models

class DictionaryWord(models.Model):
    english_word = models.CharField(max_length=100, unique=True)
    
    nepali_translation = models.CharField(max_length=255)

    def __str__(self):
        return f"{self.english_word} -> {self.nepali_translation}"