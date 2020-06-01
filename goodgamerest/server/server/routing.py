# mysite/routing.py
from channels.auth import AuthMiddlewareStack
from channels.routing import ProtocolTypeRouter, URLRouter
import app.routing
from channels.security.websocket import AllowedHostsOriginValidator

application = ProtocolTypeRouter({
    # (http->django views is added by default)
    'websocket':AuthMiddlewareStack(
        URLRouter(
            app.routing.websocket_urlpatterns
        )
    ),

})