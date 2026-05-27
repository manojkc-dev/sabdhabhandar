import os
import django
import csv

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'sabdhabhandar.settings')
django.setup()

from api.models import DictionaryWord

def run_import():
    if DictionaryWord.objects.exists():
        print("Data already exists in database. Skipping import.")
        return
    
    file_path = 'words.csv'
    
    if not os.path.exists(file_path):
        print(f"Error: Could not find {file_path}")
        return

    print("Reading words from CSV...")
    words_to_create = []

    with open(file_path, 'r', encoding='utf-8') as file:
        reader = csv.DictReader(file)
        for row in reader:
            english = row['english_word'].lower().strip()
            nepali = row['nepali_translation'].strip()
            
            word_obj = DictionaryWord(english_word=english, nepali_translation=nepali)
            words_to_create.append(word_obj)

    print(f"Found {len(words_to_create)} words. Blasting them into the database...")
    
    DictionaryWord.objects.bulk_create(words_to_create, ignore_conflicts=True)
    
    print("✅ Successfully imported all words!")

if __name__ == "__main__":
    run_import()