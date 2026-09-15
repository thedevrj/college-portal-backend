from django.urls import path
from .views import (
    PortalLoginView,
    PortalLogoutView,
    portal_profile,
    get_entities_api,
    CustomTokenObtainPairView,
    ChangePasswordView,
    SessionStatusView,
    AdminDashboardStatsView,
)

urlpatterns = [
    path("login/", PortalLoginView.as_view(), name="portal_login"),
    path("logout/", PortalLogoutView.as_view(), name="portal_logout"),
    path("profile/", portal_profile, name="portal_profile"),
    path("api/get-entities/", get_entities_api, name="get_entities_api"),
    path("api/login/", CustomTokenObtainPairView.as_view(), name="api_login"),
    path(
        "api/change-password/", ChangePasswordView.as_view(), name="api_change_password"
    ),
    path("api/session/", SessionStatusView.as_view(), name="api_session"),
    path(
        "api/dashboard-stats/",
        AdminDashboardStatsView.as_view(),
        name="admin_dashboard_stats",
    ),
]
