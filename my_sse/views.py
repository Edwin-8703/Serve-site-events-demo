import time
import json
from django.http import StreamingHttpResponse
from django.shortcuts import render
from django.views.decorators.csrf import csrf_exempt
from .models import Notification

def index(request):
    return render(request, 'core-html/index.html')

@csrf_exempt
def create_notification(request):
    if request.method == 'POST':
        message = request.POST.get('message', '')
        if message:
            Notification.objects.create(message=message)
    return render(request, 'core-html/index.html')

def sse_stream(request):
    def event_stream():
        last_id = 0
        while True:
            # get only NEW notifications since last check
            notifications = Notification.objects.filter(id__gt=last_id).order_by('id')
            for notification in notifications:
                data = json.dumps({
                    'id': notification.id,
                    'message': notification.message,
                    'time': notification.created_at.strftime('%H:%M:%S')
                })
                yield f"data: {data}\n\n"
                last_id = notification.id
            time.sleep(2)

    return StreamingHttpResponse(event_stream(), content_type='text/event-stream')