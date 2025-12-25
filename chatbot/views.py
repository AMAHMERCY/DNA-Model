import json
from django.http import JsonResponse, HttpResponse
from django.views.decorators.csrf import csrf_exempt
from django.shortcuts import render

from .llm import generate_reply

def chat_page(request):
    return render(request, "chatbot/chat.html")

@csrf_exempt
def chat_api(request):
    if request.method != "POST":
        return JsonResponse({"error": "POST only"}, status=405)

    try:
        payload = json.loads(request.body.decode("utf-8"))
    except Exception:
        return JsonResponse({"error": "Invalid JSON"}, status=400)

    message = (payload.get("message") or "").strip()
    history = payload.get("history") or []

    if not message:
        return JsonResponse({"error": "message is required"}, status=400)

    try:
        reply = generate_reply(message=message, history=history)
        return JsonResponse({"reply": reply})
    except Exception as e:
        return HttpResponse(str(e), status=500)
