"""
Django REST Framework serializers for the farm app.
These serializers convert model instances to/from JSON.
"""

from rest_framework import serializers
from django.contrib.auth.models import User
from .models import (
    Animal, EggProduction, Feed, FeedUsage, Mortality,
    Employee, ActivityLog, UserProfile, Notification, SoldEgg
)


class UserSerializer(serializers.ModelSerializer):
    """Serializer for User model"""
    class Meta:
        model = User
        fields = ['id', 'username', 'email', 'first_name', 'last_name']
        read_only_fields = ['id']


class UserProfileSerializer(serializers.ModelSerializer):
    """Serializer for UserProfile model"""
    user = UserSerializer(read_only=True)
    
    class Meta:
        model = UserProfile
        fields = ['id', 'user', 'phone_number', 'photo', 'theme']
        read_only_fields = ['id', 'user']


class AnimalSerializer(serializers.ModelSerializer):
    """Serializer for Animal model"""
    category_display = serializers.CharField(source='get_category_display', read_only=True)
    
    class Meta:
        model = Animal
        fields = ['id', 'category', 'category_display', 'name', 'total_count', 'created_at', 'updated_at']
        read_only_fields = ['id', 'created_at', 'updated_at']


class EggProductionSerializer(serializers.ModelSerializer):
    """Serializer for EggProduction model"""
    animal_name = serializers.CharField(source='animal.name', read_only=True)
    collected_by_username = serializers.CharField(source='collected_by.username', read_only=True)
    remaining_stock = serializers.SerializerMethodField()
    
    class Meta:
        model = EggProduction
        fields = ['id', 'animal', 'animal_name', 'date', 'quantity', 'collected_by', 'collected_by_username', 'remaining_stock']
        read_only_fields = ['id', 'remaining_stock']
    
    def get_remaining_stock(self, obj):
        """Calculate remaining eggs after sales"""
        return obj.remaining_stock


class FeedSerializer(serializers.ModelSerializer):
    """Serializer for Feed model"""
    class Meta:
        model = Feed
        fields = ['id', 'name', 'type', 'current_stock', 'unit', 'low_stock_threshold', 'created_at', 'updated_at']
        read_only_fields = ['id', 'created_at', 'updated_at']


class FeedUsageSerializer(serializers.ModelSerializer):
    """Serializer for FeedUsage model"""
    feed_name = serializers.CharField(source='feed.name', read_only=True)
    animal_name = serializers.CharField(source='animal.name', read_only=True)
    
    class Meta:
        model = FeedUsage
        fields = ['id', 'feed', 'feed_name', 'date', 'quantity_used', 'animal', 'animal_name']
        read_only_fields = ['id']


class MortalitySerializer(serializers.ModelSerializer):
    """Serializer for Mortality model"""
    animal_name = serializers.CharField(source='animal.name', read_only=True)
    animal_category = serializers.CharField(source='animal.category', read_only=True)
    reported_by_username = serializers.CharField(source='reported_by.username', read_only=True)
    
    class Meta:
        model = Mortality
        fields = ['id', 'animal', 'animal_name', 'animal_category', 'date', 'count', 'reason', 'reported_by', 'reported_by_username']
        read_only_fields = ['id']


class EmployeeSerializer(serializers.ModelSerializer):
    """Serializer for Employee model"""
    user = UserSerializer(read_only=True)
    
    class Meta:
        model = Employee
        fields = ['id', 'user', 'photo', 'name', 'phone_number', 'hire_date']
        read_only_fields = ['id']


class ActivityLogSerializer(serializers.ModelSerializer):
    """Serializer for ActivityLog model"""
    activity_type_display = serializers.CharField(source='get_activity_type_display', read_only=True)
    employee_name = serializers.CharField(source='employee.name', read_only=True)
    animal_name = serializers.CharField(source='animal.name', read_only=True, allow_null=True)
    
    class Meta:
        model = ActivityLog
        fields = [
            'id', 'activity_type', 'activity_type_display', 'employee', 'employee_name',
            'animal', 'animal_name', 'date', 'time', 'quantity', 'unit', 'notes', 'photo'
        ]
        read_only_fields = ['id']


class NotificationSerializer(serializers.ModelSerializer):
    """Serializer for Notification model"""
    user = UserSerializer(read_only=True)
    
    class Meta:
        model = Notification
        fields = ['id', 'user', 'title', 'message', 'notification_type', 'is_read', 'created_at', 'related_model', 'related_id']
        read_only_fields = ['id', 'created_at']


class SoldEggSerializer(serializers.ModelSerializer):
    """Serializer for SoldEgg model"""
    egg_production = EggProductionSerializer(read_only=True)
    
    class Meta:
        model = SoldEgg
        fields = ['id', 'egg_production', 'quantity_sold', 'price_per_unit', 'total_amount', 'buyer_name', 'sold_date']
        read_only_fields = ['id']


# Dashboard Summary Serializer (combines multiple data points)
class DashboardSummarySerializer(serializers.Serializer):
    """Serializer for dashboard summary data"""
    total_animals = serializers.IntegerField()
    total_eggs_today = serializers.IntegerField()
    total_eggs_week = serializers.IntegerField()
    recent_mortality = serializers.IntegerField()
    total_feed_stock = serializers.DecimalField(max_digits=10, decimal_places=2)
    feed_status = serializers.CharField()  # 'normal', 'warning', 'critical'
    low_feed_alerts = serializers.IntegerField()
    sick_animals_count = serializers.IntegerField()
    analytics = serializers.DictField()


# Real-time Update Serializer
class RealtimeUpdateSerializer(serializers.Serializer):
    """Serializer for real-time update messages via WebSocket"""
    event_type = serializers.CharField()  # 'egg_added', 'mortality_recorded', 'feed_used', etc.
    timestamp = serializers.DateTimeField()
    data = serializers.JSONField()
    message = serializers.CharField(required=False)
