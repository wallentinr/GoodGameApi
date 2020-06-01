from django.urls import include, path
from rest_framework import routers
from app import views
from rest_framework.authtoken.views import ObtainAuthToken

router = routers.DefaultRouter()
router.register(r'users', views.UserViewSet)
router.register(r'messages', views.MessageViewSet)
router.register(r'brackets', views.BracketViewSet)
router.register(r'parties', views.PartyViewSet)


# Wire up our API using automatic URL routing.
# Additionally, we include login URLs for the browsable API.
urlpatterns = [
    path('', include(router.urls)),
    path('auth/', include('djoser.urls')),
    path('auth/', include('djoser.urls.authtoken')),
    #path('ws/chat/<str:ticket>', consumers.ChatConsumer, name=chat)

] 