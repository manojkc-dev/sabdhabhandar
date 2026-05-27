import os
import csv
from django.shortcuts import render
from django.http import JsonResponse, HttpResponse
from django.conf import settings
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from .models import DictionaryWord

# --- Auto-Import Logic ---
def import_csv_if_needed():
    """Checks if the database is empty and populates it from words.csv if necessary."""
    try:
        if DictionaryWord.objects.count() == 0:
            file_path = os.path.join(settings.BASE_DIR, 'words.csv')
            if os.path.exists(file_path):
                print(f"DEBUG: Empty database found. Importing from {file_path}")
                with open(file_path, mode='r', encoding='utf-8') as file:
                    reader = csv.DictReader(file)
                    # Bulk create for performance
                    words = [DictionaryWord(
                        english_word=row['english_word'].lower().strip(), 
                        nepali_translation=row['nepali_translation'].strip()
                    ) for row in reader]
                    DictionaryWord.objects.bulk_create(words)
                    print("DEBUG: Import successful!")
            else:
                print(f"DEBUG ERROR: words.csv not found at {file_path}")
    except Exception as e:
        print(f"DEBUG ERROR: Import failed with: {str(e)}")

# --- API View for Search ---
class TranslateWordAPI(APIView):
    def get(self, request):
        word = request.query_params.get('word', None)
        if not word:
            return Response({"error": "No word provided"}, status=status.HTTP_400_BAD_REQUEST)
        
        clean_word = word.lower().strip()
        try:
            db_word = DictionaryWord.objects.get(english_word=clean_word)
            # Session history logic
            history = request.session.get('recent_searches', [])
            if clean_word not in history:
                history.insert(0, clean_word)
                request.session['recent_searches'] = history[:5]
                request.session.modified = True 
            
            return Response({
                "english_word": db_word.english_word,
                "nepali_translation": db_word.nepali_translation
            }, status=status.HTTP_200_OK)
        except DictionaryWord.DoesNotExist:
            return Response({"error": "Word not found"}, status=status.HTTP_404_NOT_FOUND)

# --- Debugging View ---
def debug_db(request):
    return HttpResponse(f"Database contains {DictionaryWord.objects.count()} words.")

# --- Standard Views ---
def homepage(request):
    import_csv_if_needed() # Ensure database is populated
    random_word = DictionaryWord.objects.order_by('?').first()
    recent_searches = request.session.get('recent_searches', [])
    context = {
        'random_word': random_word,
        'recent_searches': recent_searches
    }
    return render(request, 'index.html', context)

def translate_view(request):
    word = request.GET.get('word', '').lower().strip()
    if not word:
        return JsonResponse({'error': 'No word provided'}, status=400)
    try:
        db_word = DictionaryWord.objects.get(english_word=word)
        return JsonResponse({'english_word': db_word.english_word, 'nepali_translation': db_word.nepali_translation})
    except DictionaryWord.DoesNotExist:
        return JsonResponse({'error': 'Word not found'}, status=404)
    
def privacy_policy(request):
    return render(request, 'privacy.html')