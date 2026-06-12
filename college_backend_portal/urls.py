"""
URL configuration for college_backend_portal project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/5.0/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""

from django.contrib import admin
from django.urls import path, include
from django.http import HttpResponse
from django.views.generic import RedirectView
from rest_framework_simplejwt.views import (
    TokenObtainPairView,
    TokenRefreshView,
)

from django.conf import settings
from django.conf.urls.static import static


def health(request):
    return HttpResponse("OK")


urlpatterns = [
    path("health/", health),
    path(
        "admin/logout/",
        RedirectView.as_view(pattern_name="portal_logout", permanent=False),
    ),
    path("admin/", admin.site.urls),
    # path("api/v1/", include("apps.core.urls")),
    path("api/v1/", include("apps.academics.urls")),
    path("api/v1/", include("apps.faculty.urls")),
    path("api/v1/", include("apps.centres.urls")),
    path("api/v1/", include("apps.notices.urls")),
    path("api/v1/", include("apps.research.urls")),
    path("api/v1/", include("apps.staff.urls")),
    path("api/v1/", include("apps.authorities.urls")),
    path("api/v1/admission/", include("apps.admission.urls")),
    # Authentication (JWT for public API)
    path("api/v1/token/", TokenObtainPairView.as_view(), name="token_obtain_pair"),
    path("api/v1/token/refresh/", TokenRefreshView.as_view(), name="token_refresh"),
    # ERP Portal Login
    path("portal/", include("apps.accounts.urls")),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
