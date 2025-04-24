from channels.routing import ProtocolTypeRouter, URLRouter
from django.core.asgi import get_asgi_application
from channels.auth import AuthMiddlewareStack
import chat.routing  # Ensure these are correct
import notifications.routing  # Ensure these are correct
import Meeting.routing
application = ProtocolTypeRouter({
    "http": get_asgi_application(),
    "websocket": AuthMiddlewareStack(
        URLRouter(  # URLRouter only takes one argument: a list of urlpatterns
            chat.routing.websocket_urlpatterns + notifications.routing.websocket_urlpatterns+Meeting.routing.websocket_urlpatterns
        )
    ),
})
