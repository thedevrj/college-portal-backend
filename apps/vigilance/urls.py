from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import (
    ComplaintCreateView,
    ComplaintStatusView,
    FAQListView,
    PolicyDocumentListView,
    AdminComplaintViewSet
)

router = DefaultRouter()
router.register(r'admin/complaints', AdminComplaintViewSet, basename='admin-complaints')

urlpatterns = [
    path('complaints/', ComplaintCreateView.as_view(), name='complaint-create'),
    path('complaints/status/<str:tracking_id>/', ComplaintStatusView.as_view(), name='complaint-status'),
    path('faqs/', FAQListView.as_view(), name='faq-list'),
    path('documents/', PolicyDocumentListView.as_view(), name='document-list'),
    path('', include(router.urls)),
]
