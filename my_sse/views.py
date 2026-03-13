import time
from django.http import StreamingHttpResponse
from django.shortcuts import render

def index(request):
    return render(request, 'core-html/index.html')

def sse_stream(request):
    def event_stream():
        count = 1
        while True:
            yield f"data: Message {count} — {time.strftime('%H:%M:%S')}\n\n"
            count += 1
            time.sleep(10) # Send a message every 10 seconds

    return StreamingHttpResponse(event_stream(), content_type='text/event-stream')