"""
Django REST Framework API views for the farm app.
These views provide REST API endpoints for the React frontend.
"""

from rest_framework import viewsets, status, filters
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from rest_framework.pagination import PageNumberPagination
from django.db.models import Sum, Count, Q
from django.utils import timezone
from datetime import timedelta
from decimal import Decimal

from .models import (
    Animal, EggProduction, Feed, FeedUsage, Mortality,
    Employee, ActivityLog, UserProfile, Notification, SoldEgg
)
from .serializers import (
    AnimalSerializer, EggProductionSerializer, FeedSerializer,
    FeedUsageSerializer, MortalitySerializer, EmployeeSerializer,
    ActivityLogSerializer, NotificationSerializer, SoldEggSerializer,
    UserProfileSerializer, DashboardSummarySerializer
)


class StandardResultsSetPagination(PageNumberPagination):
    """Standard pagination for API responses"""
    page_size = 50
    page_size_query_param = 'page_size'
    max_page_size = 100


class AnimalViewSet(viewsets.ModelViewSet):
    """
    API endpoint for viewing and editing Animals.
    Supports filtering by category.
    """
    queryset = Animal.objects.all().order_by('category', 'name')
    serializer_class = AnimalSerializer
    permission_classes = [IsAuthenticated]
    pagination_class = StandardResultsSetPagination
    filter_backends = [filters.SearchFilter, filters.OrderingFilter]
    search_fields = ['name', 'category']
    ordering_fields = ['name', 'category', 'created_at']

    @action(detail=False, methods=['get'])
    def by_category(self, request):
        """Get animals grouped by category"""
        category = request.query_params.get('category')
        if category:
            animals = Animal.objects.filter(category=category).order_by('name')
        else:
            animals = Animal.objects.all().order_by('category', 'name')
        
        serializer = self.get_serializer(animals, many=True)
        return Response(serializer.data)

    @action(detail=True, methods=['get'])
    def statistics(self, request, pk=None):
        """Get statistics for a specific animal"""
        animal = self.get_object()
        
        today = timezone.now().date()
        week_ago = today - timedelta(days=7)
        month_ago = today - timedelta(days=30)
        
        # Egg production stats
        today_eggs = EggProduction.objects.filter(animal=animal, date=today).aggregate(
            total=Sum('quantity')
        )['total'] or 0
        
        week_eggs = EggProduction.objects.filter(
            animal=animal, date__gte=week_ago
        ).aggregate(total=Sum('quantity'))['total'] or 0
        
        month_eggs = EggProduction.objects.filter(
            animal=animal, date__gte=month_ago
        ).aggregate(total=Sum('quantity'))['total'] or 0
        
        # Mortality stats
        week_mortality = Mortality.objects.filter(
            animal=animal, date__gte=week_ago
        ).aggregate(total=Sum('count'))['total'] or 0
        
        return Response({
            'animal_id': animal.id,
            'animal_name': animal.name,
            'today_eggs': today_eggs,
            'week_eggs': week_eggs,
            'month_eggs': month_eggs,
            'week_mortality': week_mortality,
        })


class EggProductionViewSet(viewsets.ModelViewSet):
    """
    API endpoint for viewing and editing Egg Production.
    Supports filtering by date range and animal.
    """
    queryset = EggProduction.objects.all().select_related('animal', 'collected_by').order_by('-date')
    serializer_class = EggProductionSerializer
    permission_classes = [IsAuthenticated]
    pagination_class = StandardResultsSetPagination
    filter_backends = [filters.SearchFilter, filters.OrderingFilter]
    search_fields = ['animal__name']
    ordering_fields = ['date', 'quantity']

    def perform_create(self, serializer):
        """Set collected_by to current user on create"""
        serializer.save(collected_by=self.request.user)

    @action(detail=False, methods=['get'])
    def by_date_range(self, request):
        """Get egg production for a date range"""
        start_date = request.query_params.get('start_date')
        end_date = request.query_params.get('end_date')
        
        queryset = self.get_queryset()
        
        if start_date:
            queryset = queryset.filter(date__gte=start_date)
        if end_date:
            queryset = queryset.filter(date__lte=end_date)
        
        serializer = self.get_serializer(queryset, many=True)
        return Response(serializer.data)

    @action(detail=False, methods=['get'])
    def today_total(self, request):
        """Get total eggs collected today"""
        today = timezone.now().date()
        total = EggProduction.objects.filter(date=today).aggregate(
            total=Sum('quantity')
        )['total'] or 0
        
        return Response({'date': today, 'total': total})

    @action(detail=False, methods=['get'])
    def weekly_summary(self, request):
        """Get weekly egg production summary"""
        today = timezone.now().date()
        week_ago = today - timedelta(days=7)
        
        daily_data = []
        for i in range(7):
            date = today - timedelta(days=i)
            total = EggProduction.objects.filter(date=date).aggregate(
                total=Sum('quantity')
            )['total'] or 0
            daily_data.append({
                'date': date.isoformat(),
                'total': total
            })
        
        return Response(daily_data)


class FeedViewSet(viewsets.ModelViewSet):
    """
    API endpoint for viewing and editing Feed inventory.
    Supports filtering by stock status.
    """
    queryset = Feed.objects.all().order_by('name')
    serializer_class = FeedSerializer
    permission_classes = [IsAuthenticated]
    pagination_class = StandardResultsSetPagination
    filter_backends = [filters.SearchFilter, filters.OrderingFilter]
    search_fields = ['name', 'type']
    ordering_fields = ['name', 'current_stock']

    @action(detail=False, methods=['get'])
    def low_stock(self, request):
        """Get feeds with low stock"""
        feeds = Feed.objects.filter(
            current_stock__lte=F('low_stock_threshold')
        ).order_by('current_stock')
        
        serializer = self.get_serializer(feeds, many=True)
        return Response(serializer.data)

    @action(detail=False, methods=['get'])
    def stock_summary(self, request):
        """Get feed stock summary"""
        feeds = Feed.objects.all()
        total_stock = feeds.aggregate(total=Sum('current_stock'))['total'] or Decimal('0')
        low_stock_count = feeds.filter(
            current_stock__lte=F('low_stock_threshold')
        ).count()
        critical_stock_count = feeds.filter(
            current_stock__lte=F('low_stock_threshold') * Decimal('0.5')
        ).count()
        
        return Response({
            'total_stock': float(total_stock),
            'low_stock_count': low_stock_count,
            'critical_stock_count': critical_stock_count,
            'total_feed_types': feeds.count(),
        })


class FeedUsageViewSet(viewsets.ModelViewSet):
    """
    API endpoint for viewing feed usage records.
    """
    queryset = FeedUsage.objects.all().select_related('feed', 'animal').order_by('-date')
    serializer_class = FeedUsageSerializer
    permission_classes = [IsAuthenticated]
    pagination_class = StandardResultsSetPagination
    filter_backends = [filters.SearchFilter, filters.OrderingFilter]
    search_fields = ['feed__name', 'animal__name']
    ordering_fields = ['date', 'quantity_used']

    @action(detail=False, methods=['get'])
    def by_date_range(self, request):
        """Get feed usage for a date range"""
        start_date = request.query_params.get('start_date')
        end_date = request.query_params.get('end_date')
        
        queryset = self.get_queryset()
        
        if start_date:
            queryset = queryset.filter(date__gte=start_date)
        if end_date:
            queryset = queryset.filter(date__lte=end_date)
        
        serializer = self.get_serializer(queryset, many=True)
        return Response(serializer.data)


class MortalityViewSet(viewsets.ModelViewSet):
    """
    API endpoint for viewing mortality records.
    """
    queryset = Mortality.objects.all().select_related('animal', 'reported_by').order_by('-date')
    serializer_class = MortalitySerializer
    permission_classes = [IsAuthenticated]
    pagination_class = StandardResultsSetPagination
    filter_backends = [filters.SearchFilter, filters.OrderingFilter]
    search_fields = ['animal__name', 'reason']
    ordering_fields = ['date', 'count']

    def perform_create(self, serializer):
        """Set reported_by to current user on create"""
        serializer.save(reported_by=self.request.user)

    @action(detail=False, methods=['get'])
    def by_date_range(self, request):
        """Get mortality records for a date range"""
        start_date = request.query_params.get('start_date')
        end_date = request.query_params.get('end_date')
        
        queryset = self.get_queryset()
        
        if start_date:
            queryset = queryset.filter(date__gte=start_date)
        if end_date:
            queryset = queryset.filter(date__lte=end_date)
        
        serializer = self.get_serializer(queryset, many=True)
        return Response(serializer.data)

    @action(detail=False, methods=['get'])
    def weekly_summary(self, request):
        """Get weekly mortality summary"""
        today = timezone.now().date()
        week_ago = today - timedelta(days=7)
        
        total_mortality = Mortality.objects.filter(
            date__gte=week_ago
        ).aggregate(total=Sum('count'))['total'] or 0
        
        by_animal = Mortality.objects.filter(
            date__gte=week_ago
        ).values('animal__name', 'animal__category').annotate(
            total_count=Sum('count')
        ).order_by('-total_count')[:10]
        
        return Response({
            'total_mortality': total_mortality,
            'by_animal': list(by_animal)
        })


class ActivityLogViewSet(viewsets.ReadOnlyModelViewSet):
    """
    API endpoint for viewing activity logs (read-only).
    Activity creation is handled through specific endpoints.
    """
    queryset = ActivityLog.objects.all().select_related('employee', 'animal').order_by('-date', '-time')
    serializer_class = ActivityLogSerializer
    permission_classes = [IsAuthenticated]
    pagination_class = StandardResultsSetPagination
    filter_backends = [filters.SearchFilter, filters.OrderingFilter]
    search_fields = ['employee__name', 'animal__name', 'activity_type']
    ordering_fields = ['date', 'time']

    @action(detail=False, methods=['get'])
    def today(self, request):
        """Get today's activities"""
        today = timezone.now().date()
        activities = self.get_queryset().filter(date=today)
        
        serializer = self.get_serializer(activities, many=True)
        return Response(serializer.data)

    @action(detail=False, methods=['get'])
    def by_date_range(self, request):
        """Get activities for a date range"""
        start_date = request.query_params.get('start_date')
        end_date = request.query_params.get('end_date')
        activity_type = request.query_params.get('activity_type')
        
        queryset = self.get_queryset()
        
        if start_date:
            queryset = queryset.filter(date__gte=start_date)
        if end_date:
            queryset = queryset.filter(date__lte=end_date)
        if activity_type:
            queryset = queryset.filter(activity_type=activity_type)
        
        serializer = self.get_serializer(queryset, many=True)
        return Response(serializer.data)


class EmployeeViewSet(viewsets.ReadOnlyModelViewSet):
    """
    API endpoint for viewing employees (read-only).
    """
    queryset = Employee.objects.all().select_related('user').order_by('name')
    serializer_class = EmployeeSerializer
    permission_classes = [IsAuthenticated]
    pagination_class = StandardResultsSetPagination
    filter_backends = [filters.SearchFilter, filters.OrderingFilter]
    search_fields = ['name', 'user__username']
    ordering_fields = ['name', 'hire_date']


class NotificationViewSet(viewsets.ModelViewSet):
    """
    API endpoint for viewing and managing user notifications.
    """
    serializer_class = NotificationSerializer
    permission_classes = [IsAuthenticated]
    pagination_class = StandardResultsSetPagination
    filter_backends = [filters.OrderingFilter]
    ordering_fields = ['-created_at']

    def get_queryset(self):
        """Return notifications for the current user only"""
        return Notification.objects.filter(user=self.request.user).order_by('-created_at')

    @action(detail=True, methods=['post'])
    def mark_as_read(self, request, pk=None):
        """Mark a notification as read"""
        notification = self.get_object()
        notification.is_read = True
        notification.save()
        return Response({'status': 'notification marked as read'})

    @action(detail=False, methods=['post'])
    def mark_all_as_read(self, request):
        """Mark all notifications as read"""
        Notification.objects.filter(user=request.user, is_read=False).update(is_read=True)
        return Response({'status': 'all notifications marked as read'})

    @action(detail=False, methods=['post'])
    def clear_all(self, request):
        """Delete all notifications for current user"""
        Notification.objects.filter(user=request.user).delete()
        return Response({'status': 'all notifications deleted'})

    @action(detail=False, methods=['get'])
    def unread_count(self, request):
        """Get count of unread notifications"""
        count = Notification.objects.filter(user=request.user, is_read=False).count()
        return Response({'unread_count': count})


class UserProfileViewSet(viewsets.ViewSet):
    """
    API endpoint for viewing and updating user profile.
    """
    permission_classes = [IsAuthenticated]

    @action(detail=False, methods=['get'])
    def me(self, request):
        """Get current user's profile"""
        try:
            profile = UserProfile.objects.get(user=request.user)
        except UserProfile.DoesNotExist:
            return Response({'error': 'Profile not found'}, status=status.HTTP_404_NOT_FOUND)
        
        serializer = UserProfileSerializer(profile)
        return Response(serializer.data)

    @action(detail=False, methods=['put', 'patch'])
    def update_profile(self, request):
        """Update current user's profile"""
        try:
            profile = UserProfile.objects.get(user=request.user)
        except UserProfile.DoesNotExist:
            return Response({'error': 'Profile not found'}, status=status.HTTP_404_NOT_FOUND)
        
        serializer = UserProfileSerializer(profile, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class DashboardViewSet(viewsets.ViewSet):
    """
    API endpoint for dashboard summary data.
    Combines data from multiple models for the dashboard view.
    """
    permission_classes = [IsAuthenticated]

    @action(detail=False, methods=['get'])
    def summary(self, request):
        """Get dashboard summary"""
        today = timezone.now().date()
        week_ago = today - timedelta(days=7)
        
        # Calculate all metrics
        total_animals = Animal.objects.aggregate(total=Sum('total_count'))['total'] or 0
        
        today_eggs = EggProduction.objects.filter(date=today).aggregate(
            total=Sum('quantity')
        )['total'] or 0
        
        week_eggs = EggProduction.objects.filter(date__gte=week_ago).aggregate(
            total=Sum('quantity')
        )['total'] or 0
        
        recent_mortality = Mortality.objects.filter(date__gte=week_ago).aggregate(
            total=Sum('count')
        )['total'] or 0
        
        feeds = Feed.objects.all()
        total_feed_stock = feeds.aggregate(total=Sum('current_stock'))['total'] or Decimal('0')
        
        # Determine feed status
        critical_feeds = feeds.filter(
            current_stock__lte=F('low_stock_threshold') * Decimal('0.5')
        ).count()
        low_feeds = feeds.filter(
            current_stock__lte=F('low_stock_threshold')
        ).exclude(
            current_stock__lte=F('low_stock_threshold') * Decimal('0.5')
        ).count()
        
        feed_status = 'normal'
        if critical_feeds > 0:
            feed_status = 'critical'
        elif low_feeds > 0:
            feed_status = 'warning'
        
        low_feed_alerts = feeds.filter(
            current_stock__lte=F('low_stock_threshold')
        ).count()
        
        # Sick animals
        sick_animals_count = ActivityLog.objects.filter(
            activity_type='health_check',
            notes__icontains='sick',
            date__gte=today - timedelta(days=1)
        ).count()
        
        # Analytics
        analytics = {
            'egg_trend': 'Available',
            'feed_trend': 'Available',
            'mortality_rate': f"{(recent_mortality / total_animals * 100) if total_animals > 0 else 0:.2f}%",
            'productivity': f"{week_eggs / 7:.1f} eggs/day"
        }
        
        return Response({
            'total_animals': total_animals,
            'total_eggs_today': today_eggs,
            'total_eggs_week': week_eggs,
            'recent_mortality': recent_mortality,
            'total_feed_stock': float(total_feed_stock),
            'feed_status': feed_status,
            'low_feed_alerts': low_feed_alerts,
            'sick_animals_count': sick_animals_count,
            'analytics': analytics,
        })

    @action(detail=False, methods=['get'])
    def recent_activity(self, request):
        """Get recent activities for dashboard"""
        today = timezone.now().date()
        activities = ActivityLog.objects.filter(date=today).select_related(
            'employee', 'animal'
        ).order_by('-time')[:10]
        
        serializer = ActivityLogSerializer(activities, many=True)
        return Response(serializer.data)


# Import F for filtering
from django.db.models import F
