from django.db import migrations
import csv
import os

def load_data(apps, schema_editor):
    # Get the model from the app
    DictionaryWord = apps.get_model('api', 'DictionaryWord')
    
    # Path to your CSV file
    file_path = 'words.csv'
    
    if os.path.exists(file_path):
        with open(file_path, mode='r', encoding='utf-8') as file:
            reader = csv.DictReader(file)
            for row in reader:
                # Use get_or_create to avoid duplicate errors
                DictionaryWord.objects.get_or_create(
                    english_word=row['english_word'].lower().strip(),
                    nepali_translation=row['nepali_translation'].strip()
                )

class Migration(migrations.Migration):
    dependencies = [
        ('api', '0001_initial'), # This ensures 0001 runs first
    ]

    operations = [
        migrations.RunPython(load_data),
    ]