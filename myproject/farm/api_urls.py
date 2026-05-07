"""
URL configuration for Django REST Framework API endpoints.
"""

from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .api_views import (
    AnimalViewSet, EggProductionViewSet, FeedViewSet, FeedUsageViewSet,
    MortalityViewSet, ActivityLogViewSet, EmployeeViewSet, NotificationViewSet,
    UserProfileViewSet, DashboardViewSet
)

# Create a router and register viewsets
router = DefaultRouter()
router.register(r'animals', AnimalViewSet, basename='animal')
router.register(r'egg-production', EggProductionViewSet, basename='egg-production')
router.register(r'feeds', FeedViewSet, basename='feed')
router.register(r'feed-usage', FeedUsageViewSet, basename='feed-usage')
router.register(r'mortality', MortalityViewSet, basename='mortality')
router.register(r'activities', ActivityLogViewSet, basename='activity')
router.register(r'employees', EmployeeViewSet, basename='employee')
router.register(r'notifications', NotificationViewSet, basename='notification')
router.register(r'profile', UserProfileViewSet, basename='profile')
router.register(r'dashboard', DashboardViewSet, basename='dashboard')

# API URLs
urlpatterns = [
    path('', include(router.urls)),
    path('auth/', include('rest_framework.urls')),
]
