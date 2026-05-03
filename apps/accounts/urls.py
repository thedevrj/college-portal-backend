from django.urls import path
from .views import PortalLoginView, PortalLogoutView, portal_profile, get_entities_api

urlpatterns = [
    path("login/",   PortalLoginView.as_view(),  name="portal_login"),
    path("logout/",  PortalLogoutView.as_view(), name="portal_logout"),
    path("profile/", portal_profile,             name="portal_profile"),
    path("api/get-entities/", get_entities_api,  name="get_entities_api"),
]
