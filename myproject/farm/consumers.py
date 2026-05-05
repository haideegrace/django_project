"""
Django Channels WebSocket consumers for real-time updates.
These consumers handle WebSocket connections for live data updates.
"""

import json
from channels.db import database_sync_to_async
from channels.generic.websocket import AsyncWebsocketConsumer
from django.utils import timezone
from django.db.models import Sum
from decimal import Decimal

from .models import (
    Animal, EggProduction, Feed, Mortality, ActivityLog, Notification
)


class FarmDashboardConsumer(AsyncWebsocketConsumer):
    """
    WebSocket consumer for real-time dashboard updates.
    Broadcasts dashboard metrics to all connected clients.
    """
    
    async def connect(self):
        """Handle WebSocket connection"""
        self.user = self.scope["user"]
        
        # Only allow authenticated users
        if not self.user.is_authenticated:
            await self.close()
            return
        
        self.room_name = f"dashboard_{self.user.id}"
        self.room_group_name = f"farm_dashboard_{self.user.id}"
        
        # Join room group
        await self.channel_layer.group_add(
            self.room_group_name,
            self.channel_name
        )
        
        await self.accept()
        
        # Send initial dashboard data
        dashboard_data = await self.get_dashboard_data()
        await self.send(text_data=json.dumps({
            'type': 'dashboard_update',
            'data': dashboard_data
        }))

    async def disconnect(self, close_code):
        """Handle WebSocket disconnection"""
        # Leave room group
        if hasattr(self, 'room_group_name'):
            await self.channel_layer.group_discard(
                self.room_group_name,
                self.channel_name
            )

    async def receive(self, text_data):
        """Receive message from WebSocket"""
        try:
            data = json.loads(text_data)
            command = data.get('command')
            
            if command == 'get_dashboard':
                dashboard_data = await self.get_dashboard_data()
                await self.send(text_data=json.dumps({
                    'type': 'dashboard_update',
                    'data': dashboard_data
                }))
            
            elif command == 'get_activities':
                activities = await self.get_today_activities()
                await self.send(text_data=json.dumps({
                    'type': 'activities_update',
                    'data': activities
                }))
            
            elif command == 'get_alerts':
                alerts = await self.get_alerts()
                await self.send(text_data=json.dumps({
                    'type': 'alerts_update',
                    'data': alerts
                }))
        
        except json.JSONDecodeError:
            await self.send(text_data=json.dumps({
                'type': 'error',
                'message': 'Invalid JSON'
            }))

    async def dashboard_update(self, event):
        """Send dashboard update to WebSocket"""
        await self.send(text_data=json.dumps({
            'type': 'dashboard_update',
            'data': event['data']
        }))

    async def activity_created(self, event):
        """Broadcast new activity to WebSocket"""
        await self.send(text_data=json.dumps({
            'type': 'activity_created',
            'data': event['data'],
            'timestamp': event['timestamp']
        }))

    async def egg_production_recorded(self, event):
        """Broadcast new egg production to WebSocket"""
        await self.send(text_data=json.dumps({
            'type': 'egg_production_recorded',
            'data': event['data'],
            'timestamp': event['timestamp']
        }))

    async def mortality_recorded(self, event):
        """Broadcast new mortality record to WebSocket"""
        await self.send(text_data=json.dumps({
            'type': 'mortality_recorded',
            'data': event['data'],
            'timestamp': event['timestamp']
        }))

    async def feed_alert(self, event):
        """Broadcast feed alert to WebSocket"""
        await self.send(text_data=json.dumps({
            'type': 'feed_alert',
            'data': event['data'],
            'timestamp': event['timestamp']
        }))

    @database_sync_to_async
    def get_dashboard_data(self):
        """Get current dashboard data"""
        from datetime import timedelta
        
        today = timezone.now().date()
        week_ago = today - timedelta(days=7)
        
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
        
        critical_feeds = feeds.filter(
            current_stock__lte=Decimal('50')
        ).count()
        
        return {
            'total_animals': total_animals,
            'today_eggs': today_eggs,
            'week_eggs': week_eggs,
            'recent_mortality': recent_mortality,
            'total_feed_stock': float(total_feed_stock),
            'critical_feeds': critical_feeds,
            'timestamp': timezone.now().isoformat()
        }

    @database_sync_to_async
    def get_today_activities(self):
        """Get today's activities"""
        today = timezone.now().date()
        activities = ActivityLog.objects.filter(date=today).select_related(
            'employee', 'animal'
        ).order_by('-time').values(
            'id', 'activity_type', 'employee__name', 'animal__name',
            'quantity', 'unit', 'time'
        )[:10]
        
        return list(activities)

    @database_sync_to_async
    def get_alerts(self):
        """Get current alerts"""
        alerts = []
        
        # Low feed alerts
        low_feeds = Feed.objects.filter(
            current_stock__lte=F('low_stock_threshold')
        ).values('name', 'current_stock', 'low_stock_threshold')
        
        for feed in low_feeds:
            alerts.append({
                'type': 'low_feed',
                'title': f"Low Feed Stock: {feed['name']}",
                'message': f"Current stock: {feed['current_stock']} kg",
                'severity': 'warning'
            })
        
        # Recent mortality
        today = timezone.now().date()
        recent_mortality = Mortality.objects.filter(date=today).aggregate(
            total=Sum('count')
        )['total'] or 0
        
        if recent_mortality > 5:
            alerts.append({
                'type': 'high_mortality',
                'title': 'High Mortality Today',
                'message': f'{recent_mortality} deaths recorded today',
                'severity': 'danger'
            })
        
        return alerts


class NotificationConsumer(AsyncWebsocketConsumer):
    """
    WebSocket consumer for real-time notifications.
    Sends notifications to individual users.
    """
    
    async def connect(self):
        """Handle WebSocket connection"""
        self.user = self.scope["user"]
        
        if not self.user.is_authenticated:
            await self.close()
            return
        
        self.room_name = f"notifications_{self.user.id}"
        self.room_group_name = f"farm_notifications_{self.user.id}"
        
        await self.channel_layer.group_add(
            self.room_group_name,
            self.channel_name
        )
        
        await self.accept()

    async def disconnect(self, close_code):
        """Handle WebSocket disconnection"""
        if hasattr(self, 'room_group_name'):
            await self.channel_layer.group_discard(
                self.room_group_name,
                self.channel_name
            )

    async def notification_created(self, event):
        """Send notification to WebSocket"""
        await self.send(text_data=json.dumps({
            'type': 'notification',
            'id': event['notification_id'],
            'title': event['title'],
            'message': event['message'],
            'notification_type': event['notification_type'],
            'timestamp': event['timestamp']
        }))


# Import F for filtering
from django.db.models import F


# Helper function to broadcast updates
async def broadcast_dashboard_update(user_id, event_type, data):
    """
    Broadcast dashboard update to a specific user's dashboard consumers.
    """
    from channels.layers import get_channel_layer
    
    channel_layer = get_channel_layer()
    await channel_layer.group_send(
        f"farm_dashboard_{user_id}",
        {
            'type': event_type.lower(),
            'data': data,
            'timestamp': timezone.now().isoformat()
        }
    )


async def broadcast_notification(user_id, title, message, notification_type='info'):
    """
    Broadcast notification to a specific user.
    """
    from channels.layers import get_channel_layer
    
    channel_layer = get_channel_layer()
    await channel_layer.group_send(
        f"farm_notifications_{user_id}",
        {
            'type': 'notification_created',
            'title': title,
            'message': message,
            'notification_type': notification_type,
            'timestamp': timezone.now().isoformat()
        }
    )
