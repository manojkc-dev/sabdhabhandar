import os
import pandas as pd
from django.shortcuts import render
from django.http import JsonResponse
from django.conf import settings
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from .models import DictionaryWord

class TranslateWordAPI(APIView):
    def get(self, request):
        word = request.query_params.get('word', None)
        if not word:
            return Response({"error": "No word provided"}, status=status.HTTP_400_BAD_REQUEST)
        
        clean_word = word.lower().strip()
        
        try:
            db_word = DictionaryWord.objects.get(english_word=clean_word)
            
            # Update session history
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

def homepage(request):
    # 1. Fetch a random word for the Word of the Day
    random_word = DictionaryWord.objects.order_by('?').first()
    
    # 2. Fetch the recent searches from the session
    recent_searches = request.session.get('recent_searches', [])
    
    # Let's print this to the terminal every time you refresh the page
    print("DEBUG HOMEPAGE: Loading page. Current session history is:", recent_searches)

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
        # Look up the word in your SQLite Database
        db_word = DictionaryWord.objects.get(english_word=word)
        
        # --- THE MAGIC SESSION SAVING CODE ---
        history = request.session.get('recent_searches', [])
        if word not in history:
            history.insert(0, word)
            request.session['recent_searches'] = history[:5]
            request.session.modified = True 
        # -------------------------------------
        
        # Let's print this to the terminal to PROVE the session saved
        print(f"DEBUG TRANSLATE: User translated '{word}'. Saved history is now: {request.session['recent_searches']}")

        return JsonResponse({
            'english_word': db_word.english_word,
            'nepali_translation': db_word.nepali_translation
        })
        
    except DictionaryWord.DoesNotExist:
        return JsonResponse({'error': 'Word not found in dictionary'}, status=404)
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)
    
def privacy_policy(request):
    return render(request, 'privacy.html')