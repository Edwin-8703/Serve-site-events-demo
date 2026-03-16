import time
import json
from django.http import StreamingHttpResponse
from django.shortcuts import render
from django.views.decorators.csrf import csrf_exempt
from .models import Notification

def index(request):
    return render(request, 'core-html/index.html')

@csrf_exempt #disables CSRF protection for this view, allowing it to accept POST requests without a CSRF token
def create_notification(request):
    if request.method == 'POST':#checks if the request is a POST (form submission)
        message = request.POST.get('message', '')#grabs the message text from the form
        if message:
            Notification.objects.create(message=message)#saves the message to the database
    return render(request, 'core-html/index.html')#renders the index page again after processing the form submission

def sse_stream(request):#defines a view that will handle the Server-Sent Events stream
    def event_stream():#generator function that will yield new notifications as they are created
        last_id = 0 #keeps track of the last notification ID that was sent to the client
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

             # keepalive ping — prevents Railway from killing the connection
            yield ": ping\n\n"
            time.sleep(2)#waits for 2 seconds before checking for new notifications again to avoid overwhelming the server with too many database queries

    response = StreamingHttpResponse(event_stream(), content_type='text/event-stream')#returns a StreamingHttpResponse that will continuously stream new notifications to the client as they are created, using the Server-Sent Events protocol. The content type is set to 'text/event-stream' to indicate that this is an SSE stream.
    response['Cache-Control'] = 'no-cache'
    response['X-Accel-Buffering'] = 'no'   #tells Railway not to buffer
    return response