import cohere
import json
import traceback # To see exactly where it breaks
from django.shortcuts import render, get_object_or_404
from django.http import JsonResponse
from django.contrib.auth.decorators import login_required
from decouple import config
from .models import ChatSession, ChatMessage

# Initialize Cohere
try:
    co = cohere.Client(config('COHERE_API_KEY'))
except Exception as e:
    print(f"COHERE INIT ERROR: {e}")

SYSTEM_PREAMBLE = "You are AutoTube AI, an expert YouTube Optimization strategist and transcript analysis engine. Your core function is to transform raw video transcripts into structured, high-value reports, including summaries, tone analysis, audience profiling, engaging titles, and SEO tags. Maintain a professional, highly analytical, and versatile tone, adapting seamlessly to any content niche or out-of-context query while maintaining your identity as a content coach."

def home(request):
    return render(
        request,
        {},
        'ToolkitApp/index.html'
    )

@login_required
def chat_home(request):
    sessions = ChatSession.objects.filter(user=request.user).order_by('-created_at')
    return render(request, 'NexusAIApp/chat.html', {'sessions': sessions})

@login_required
def chat_api(request):
    if request.method == "POST":
        try:
            data = json.loads(request.body)
            user_msg = data.get('message')
            session_id = data.get('session_id')

            # Handle Session Logic
            if session_id and session_id != "null":
                session = get_object_or_404(ChatSession, id=session_id, user=request.user)
            else:
                title = (user_msg[:30] + '...') if len(user_msg) > 30 else user_msg
                session = ChatSession.objects.create(user=request.user, title=title)

            # Save User Message
            ChatMessage.objects.create(session=session, role='user', content=user_msg)

            # Call Cohere (Using 'command' for maximum compatibility)
            response = co.chat(
                message=user_msg,
                preamble=SYSTEM_PREAMBLE,
                model="command-a-03-2025", 
                temperature=0.3
            )
            
            bot_response = response.text

            # Save Bot Message
            ChatMessage.objects.create(session=session, role='bot', content=bot_response)

            return JsonResponse({
                "response": bot_response,
                "session_id": session.id,
                "title": session.title
            })

        except Exception as e:
            # THIS WILL PRINT THE ERROR IN YOUR TERMINAL
            print("--- CHAT API CRASH ---")
            print(traceback.format_exc()) 
            return JsonResponse({"error": str(e)}, status=500)

    return JsonResponse({"error": "Invalid request"}, status=400)

@login_required
def get_session_history(request, session_id):
    # Retrieve the session, ensuring it belongs to the logged-in user
    session = get_object_or_404(ChatSession, id=session_id, user=request.user)
    
    # CRITICAL: We fetch ALL messages linked to this session ID
    messages = ChatMessage.objects.filter(session=session).order_by('timestamp')
    
    history = []
    for msg in messages:
        history.append({
            'role': msg.role,
            'content': msg.content
        })
    
    return JsonResponse({
        'title': session.title,
        'history': history
    })
    
from django.db.models import Q

@login_required
def search_chats(request):
    query = request.GET.get('q', '').strip()
    if not query:
        return JsonResponse({'results': []})

    # Tier 1: Match Session Titles
    sessions_by_title = ChatSession.objects.filter(
        user=request.user, 
        title__icontains=query
    )

    # Tier 2 & 3: Match Message Content (User or Bot)
    # We find messages that match, then get their unique parent sessions
    messages_matching = ChatMessage.objects.filter(
        session__user=request.user,
        content__icontains=query
    ).select_related('session')

    # Combine them into a unique set of sessions
    results = []
    seen_ids = set()

    # Add Title matches first (Highest Priority)
    for s in sessions_by_title:
        results.append({'id': s.id, 'title': s.title, 'type': 'Title Match'})
        seen_ids.add(s.id)

    # Add Content matches
    for m in messages_matching:
        if m.session.id not in seen_ids:
            match_type = "Question Match" if m.role == 'user' else "Answer Match"
            results.append({
                'id': m.session.id, 
                'title': m.session.title, 
                'type': match_type
            })
            seen_ids.add(m.session.id)

    return JsonResponse({'results': results})    