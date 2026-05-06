from django.shortcuts import render, get_object_or_404
from django.contrib.admin.views.decorators import staff_member_required
from django.db.models import Sum, Count, Q, F
from django.utils import timezone
from datetime import datetime, timedelta
from decimal import Decimal
from .models import Animal, EggProduction, Feed, FeedUsage, Mortality, ActivityLog, Employee, UserProfile, Notification, SoldEgg
import json
from django.http import HttpResponse, JsonResponse
from reportlab.lib import colors
from reportlab.lib.pagesizes import letter
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch
from reportlab.pdfgen import canvas
import openpyxl
from io import BytesIO
from PIL import Image
from django.core.files.base import ContentFile
import os
from django.contrib.auth.models import User
from django.contrib.auth.decorators import login_required
from django.contrib.auth import login, authenticate, logout
from django.shortcuts import redirect
from django.contrib import messages
from django.contrib.auth.forms import UserCreationForm, PasswordChangeForm
from django import forms

# ===== UTILITY FUNCTIONS =====
def create_notification(user, title, message, notification_type='info', related_model='', related_id=None):
    """Create a notification for a user"""
    Notification.objects.create(
        user=user,
        title=title,
        message=message,
        notification_type=notification_type,
        related_model=related_model,
        related_id=related_id
    )

def check_feed_stock_alerts():
    """Check for low feed stock and create notifications"""
    from django.contrib.auth.models import User
    feeds = Feed.objects.filter(current_stock__lte=F('low_stock_threshold'))
    users = User.objects.filter(is_staff=True)  # Notify staff users
    
    for feed in feeds:
        for user in users:
            # Check if notification already exists for this feed in last 24 hours
            recent_notification = Notification.objects.filter(
                user=user,
                related_model='feed',
                related_id=feed.id,
                created_at__gte=timezone.now() - timedelta(hours=24)
            ).exists()
            
            if not recent_notification:
                create_notification(
                    user=user,
                    title=f"Low Feed Stock Alert",
                    message=f"{feed.name} stock is low: {feed.current_stock} {feed.unit} remaining (threshold: {feed.low_stock_threshold} {feed.unit})",
                    notification_type='warning',
                    related_model='feed',
                    related_id=feed.id
                )

def check_mortality_alerts():
    """Check for recent mortality and create notifications"""
    from django.contrib.auth.models import User
    week_ago = timezone.now().date() - timedelta(days=7)
    recent_mortality = Mortality.objects.filter(date__gte=week_ago).aggregate(total=Sum('count'))['total'] or 0
    
    if recent_mortality > 10:  # Threshold for alert
        users = User.objects.filter(is_staff=True)
        for user in users:
            recent_notification = Notification.objects.filter(
                user=user,
                title__icontains='mortality',
                created_at__gte=timezone.now() - timedelta(hours=24)
            ).exists()
            
            if not recent_notification:
                create_notification(
                    user=user,
                    title="High Mortality Alert",
                    message=f"{recent_mortality} animal deaths recorded in the last 7 days. Please review mortality records.",
                    notification_type='warning',
                    related_model='mortality'
                )

def check_egg_production_alerts():
    """Check for unusual egg production patterns"""
    from django.contrib.auth.models import User
    today = timezone.now().date()
    yesterday = today - timedelta(days=1)
    week_ago = today - timedelta(days=7)
    
    # Get today's and yesterday's production
    today_eggs = EggProduction.objects.filter(date=today).aggregate(total=Sum('quantity'))['total'] or 0
    yesterday_eggs = EggProduction.objects.filter(date=yesterday).aggregate(total=Sum('quantity'))['total'] or 0
    
    # Get weekly average
    weekly_eggs = EggProduction.objects.filter(date__gte=week_ago).aggregate(total=Sum('quantity'))['total'] or 0
    weekly_avg = weekly_eggs / 7 if weekly_eggs > 0 else 0
    
    users = User.objects.filter(is_staff=True)
    
    # Alert if production dropped significantly
    if yesterday_eggs > 0 and today_eggs < yesterday_eggs * 0.5:
        for user in users:
            create_notification(
                user=user,
                title="Egg Production Alert",
                message=f"Egg production dropped significantly today ({today_eggs}) compared to yesterday ({yesterday_eggs}).",
                notification_type='warning',
                related_model='egg_production'
            )
    
    # Alert if production is unusually high
    if weekly_avg > 0 and today_eggs > weekly_avg * 1.5:
        for user in users:
            create_notification(
                user=user,
                title="High Egg Production",
                message=f"Egg production is unusually high today ({today_eggs}) compared to weekly average ({weekly_avg:.0f}).",
                notification_type='info',
                related_model='egg_production'
            )

class CustomUserCreationForm(forms.ModelForm):
    password = forms.CharField(widget=forms.PasswordInput)
    email = forms.CharField(required=False)
    first_name = forms.CharField(required=False)
    last_name = forms.CharField(required=False)
    phone_number = forms.CharField(required=False)

    class Meta:
        model = User
        fields = ('username', 'email', 'first_name', 'last_name')

    def save(self, commit=True):
        user = super().save(commit=False)
        user.set_password(self.cleaned_data['password'])
        if commit:
            user.save()
            UserProfile.objects.create(user=user, phone_number=self.cleaned_data.get('phone_number', ''))
        return user

@staff_member_required
def dashboard(request):
    today = timezone.now().date()
    week_ago = today - timedelta(days=7)

    # Today's egg production
    today_eggs = EggProduction.objects.filter(date=today).aggregate(total=Sum('quantity'))['total'] or 0

    # Total animals
    total_animals = Animal.objects.aggregate(total=Sum('total_count'))['total'] or 0

    # Feed stock status
    feeds = Feed.objects.all()
    low_feed_alerts = [feed for feed in feeds if feed.current_stock <= feed.low_stock_threshold]

    # Mortality counts
    recent_mortality = Mortality.objects.filter(date__gte=week_ago).aggregate(total=Sum('count'))['total'] or 0

    # Egg production data for chart (last 7 days)
    egg_data = []
    for i in range(7):
        date = today - timedelta(days=i)
        total = EggProduction.objects.filter(date=date).aggregate(total=Sum('quantity'))['total'] or 0
        egg_data.append({'date': date.strftime('%Y-%m-%d'), 'total': total})

    # Feed consumption trends (last 7 days)
    from .models import FeedUsage
    feed_usage_data = []
    for i in range(7):
        date = today - timedelta(days=i)
        total = FeedUsage.objects.filter(date=date).aggregate(total=Sum('quantity_used'))['total'] or 0
        feed_usage_data.append({'date': date.strftime('%Y-%m-%d'), 'total': float(total)})

    # Quick alerts
    alerts = []
    if low_feed_alerts:
        alerts.append(f"Low feed stock: {', '.join([f.name for f in low_feed_alerts])}")
    sick_animals = ActivityLog.objects.filter(activity_type='health_check', notes__icontains='sick', date__gte=week_ago).count()
    if sick_animals > 0:
        alerts.append(f"Sick animals reported: {sick_animals}")

    # Animal categories
    animal_categories = Animal.objects.values('category').annotate(total=Sum('total_count')).order_by('category')

    context = {
        'total_animals': total_animals,
        'today_eggs': today_eggs,
        'recent_mortality': recent_mortality,
        'low_feed_alerts': low_feed_alerts,
        'alerts': alerts,
        'egg_data': json.dumps(egg_data[::-1]),  # reverse for chart
        'feed_usage_data': json.dumps(feed_usage_data[::-1]),
        'animal_categories': animal_categories,
    }
    return render(request, 'admin/dashboard.html', context)

def user_login(request):
    if request.method == 'POST':
        login_credential = request.POST['username']  # This can be username or email
        password = request.POST['password']
        
        # Try to authenticate with username first
        user = authenticate(request, username=login_credential, password=password)
        
        # If that fails, try with email
        if user is None:
            try:
                user_obj = User.objects.get(email__iexact=login_credential)
                user = authenticate(request, username=user_obj.username, password=password)
            except User.DoesNotExist:
                user = None
        
        if user is not None:
            login(request, user)
            return redirect('/home/')
        else:
            messages.error(request, 'Invalid username/email or password.')
    return render(request, 'farm/login.html')

def user_register(request):
    if request.method == 'POST':
        form = CustomUserCreationForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            return redirect('/home/')
    else:
        form = CustomUserCreationForm()
    return render(request, 'farm/register.html', {'form': form})

def user_logout(request):
    logout(request)
    return redirect('farm:user_login')

@login_required
def add_animal(request):
    """Add a new animal"""
    if request.method == 'POST':
        category = request.POST.get('category')
        name = request.POST.get('name')
        description = request.POST.get('description', '')
        total_count = int(request.POST.get('total_count', 0))
        
        Animal.objects.create(
            category=category,
            name=name,
            description=description,
            total_count=total_count
        )
        
        messages.success(request, f'Animal "{name}" added successfully!')
        return redirect('farm:animals')
    
    return redirect('farm:animals')

@login_required
def animals(request):
    """Display list of all animals"""
    animals = Animal.objects.all().order_by('category', 'name')
    animal_ids = [animal.id for animal in animals]

    mortality_qs = Mortality.objects.filter(animal_id__in=animal_ids).values('animal_id').annotate(total=Sum('count'))
    mortality_totals = {
        item['animal_id']: item['total']
        for item in mortality_qs
    }

    activity_summary = {}
    recent_activities = ActivityLog.objects.filter(animal_id__in=animal_ids).exclude(activity_type='egg_collection').order_by('-date', '-time').select_related('animal')
    for activity in recent_activities:
        current = activity_summary.setdefault(activity.animal_id, [])
        if len(current) >= 2:
            continue
        if activity.notes:
            detail = activity.notes
        elif activity.quantity and activity.unit:
            detail = f"{activity.get_activity_type_display()}: {activity.quantity} {activity.unit}"
        else:
            detail = activity.get_activity_type_display()
        current.append(detail)

    animals_by_category = {}
    for animal in animals:
        animals_by_category.setdefault(animal.category, []).append({
            'animal': animal,
            'recent_mortality': mortality_totals.get(animal.id, 0),
            'activity_summary': activity_summary.get(animal.id, []),
        })

    context = {
        'animals_by_category': animals_by_category,
        'total_animals': animals.count(),
    }
    return render(request, 'farm/animals.html', context)

@login_required
def egg_production(request):
    """Display activity summary and today's egg production"""
    today = timezone.now().date()
    week_ago = today - timedelta(days=7)

    # Filter to show only egg collection activities
    recent_activities = ActivityLog.objects.filter(
        date__gte=week_ago,
        activity_type='egg_collection'
    ).select_related('employee', 'animal').order_by('-date', '-time')

    today_total = EggProduction.objects.filter(date=today).aggregate(total=Sum('quantity'))['total'] or 0
    weekly_total = EggProduction.objects.filter(date__gte=week_ago).aggregate(total=Sum('quantity'))['total'] or 0

    context = {
        'recent_activities': recent_activities,
        'today_total': today_total,
        'weekly_total': weekly_total,
    }
    return render(request, 'farm/egg_production.html', context)

@login_required
def feed_inventory(request):
    """Display feed inventory"""
    feeds = Feed.objects.all().order_by('name')
    
    # Calculate total feed stock
    total_stock = feeds.aggregate(total=Sum('current_stock'))['total'] or 0
    
    # Check for low stock alerts
    low_feed_alerts = [feed for feed in feeds if feed.current_stock <= feed.low_stock_threshold]
    
    context = {
        'feeds': feeds,
        'total_stock': total_stock,
        'low_feed_alerts': low_feed_alerts,
    }
    return render(request, 'farm/feed_inventory.html', context)

@login_required
def mortality_records(request):
    """Display mortality records"""
    # Get date range from request or default to last 30 days
    end_date = timezone.now().date()
    start_date = end_date - timedelta(days=30)

    if request.GET.get('start_date'):
        start_date = timezone.datetime.strptime(request.GET['start_date'], '%Y-%m-%d').date()
    if request.GET.get('end_date'):
        end_date = timezone.datetime.strptime(request.GET['end_date'], '%Y-%m-%d').date()

    # Get mortality records for the date range
    mortality_records = Mortality.objects.filter(date__range=[start_date, end_date]).select_related('animal', 'reported_by').order_by('-date')

    # Calculate statistics
    total_mortality = mortality_records.aggregate(total=Sum('count'))['total'] or 0
    mortality_by_animal = mortality_records.values('animal__name', 'animal__category').annotate(
        total_count=Sum('count')
    ).order_by('-total_count')[:10]  # Top 10 animals with highest mortality

    context = {
        'mortality_records': mortality_records,
        'start_date': start_date,
        'end_date': end_date,
        'total_mortality': total_mortality,
        'mortality_by_animal': mortality_by_animal,
        'animals': Animal.objects.all().order_by('name'),
        'today': timezone.now().date(),
    }
    return render(request, 'farm/mortality_records.html', context)

@login_required
def record_mortality(request):
    """Record animal mortality"""
    if request.method == 'POST':
        animal_id = request.POST.get('animal')
        date = request.POST.get('date')
        count = request.POST.get('count')
        reason = request.POST.get('reason', '')

        try:
            animal = Animal.objects.get(id=animal_id)
            count = int(count)
            date = timezone.datetime.strptime(date, '%Y-%m-%d').date()

            if count <= 0:
                messages.error(request, 'Count must be greater than 0')
                return redirect('farm:mortality_records')

            # Create mortality record
            mortality = Mortality.objects.create(
                animal=animal,
                date=date,
                count=count,
                reason=reason,
                reported_by=request.user
            )

            # Log the activity
            ActivityLog.objects.create(
                activity_type='mortality',
                employee=request.user.employee_profile if hasattr(request.user, 'employee_profile') else None,
                animal=animal,
                date=date,
                quantity=count,
                unit='deaths',
                notes=f'Mortality recorded: {reason}'
            )

            messages.success(request, f'Mortality recorded: {count} death(s) for {animal.name}')
            return redirect('farm:mortality_records')

        except Animal.DoesNotExist:
            messages.error(request, 'Animal not found')
            return redirect('farm:mortality_records')
        except (ValueError, TypeError):
            messages.error(request, 'Invalid data provided')
            return redirect('farm:mortality_records')

    return redirect('farm:mortality_records')

@login_required
def animals(request):
    """Display all animals"""
    # Total animals count
    animals = Animal.objects.all().order_by('category', 'name')
    total_animals = animals.aggregate(total=Sum('total_count'))['total'] or 0

    animal_ids = [animal.id for animal in animals]
    mortality_totals = {
        item['animal_id']: item['total']
        for item in Mortality.objects.filter(animal_id__in=animal_ids).values('animal_id').annotate(total=Sum('count'))
    }

    activity_summary = {}
    recent_activities = ActivityLog.objects.filter(animal_id__in=animal_ids).exclude(activity_type='egg_collection').order_by('-date', '-time').select_related('animal')
    for activity in recent_activities:
        current = activity_summary.setdefault(activity.animal_id, [])
        if len(current) >= 2:
            continue
        if activity.notes:
            detail = activity.notes
        elif activity.quantity and activity.unit:
            detail = f"{activity.get_activity_type_display()}: {activity.quantity} {activity.unit}"
        else:
            detail = activity.get_activity_type_display()
        current.append(detail)

    animals_by_category = {}
    for animal in animals:
        category = animal.category
        animals_by_category.setdefault(category, []).append({
            'animal': animal,
            'recent_mortality': mortality_totals.get(animal.id, 0),
            'activity_summary': activity_summary.get(animal.id, []),
        })

    context = {
        'total_animals': total_animals,
        'animals_by_category': animals_by_category,
    }
    return render(request, 'farm/animals.html', context)

@login_required
def record_egg_production(request):
    """Record egg production"""
    if request.method == 'POST':
        animal_id = request.POST.get('animal_id')
        quantity = int(request.POST.get('quantity', 0))
        date = request.POST.get('date')
        
        try:
            animal = Animal.objects.get(id=animal_id)
            EggProduction.objects.create(
                animal=animal,
                quantity=quantity,
                date=date,
                employee=request.user.employee_profile if hasattr(request.user, 'employee_profile') else None
            )
            messages.success(request, f'Egg production recorded: {quantity} eggs from {animal.name}')
        except Animal.DoesNotExist:
            messages.error(request, 'Animal not found')
        
        return redirect('farm:egg_production')
    
    return redirect('farm:egg_production')

@login_required
def add_feed(request):
    """Add new feed item"""
    if request.method == 'POST':
        name = request.POST.get('name')
        current_stock = float(request.POST.get('current_stock', 0))
        low_stock_threshold = float(request.POST.get('low_stock_threshold', 0))
        unit = request.POST.get('unit', 'kg')
        description = request.POST.get('description', '')
        
        Feed.objects.create(
            name=name,
            current_stock=current_stock,
            low_stock_threshold=low_stock_threshold,
            unit=unit,
            description=description
        )
        
        messages.success(request, f'Feed "{name}" added successfully!')
        return redirect('farm:feed_inventory')
    
    return redirect('farm:feed_inventory')

@login_required
def user_dashboard(request):
    today = timezone.now().date()
    week_ago = today - timedelta(days=7)
    month_ago = today - timedelta(days=30)

    # Run alert checks to create notifications
    check_feed_stock_alerts()
    check_mortality_alerts()
    check_egg_production_alerts()

    # Run alert checks to create notifications
    check_feed_stock_alerts()
    check_mortality_alerts()
    check_egg_production_alerts()

    # Today's egg production
    today_eggs = EggProduction.objects.filter(date=today).aggregate(total=Sum('quantity'))['total'] or 0

    # Total animals
    total_animals = Animal.objects.aggregate(total=Sum('total_count'))['total'] or 0

    # Animals by category
    animals_by_category = Animal.objects.values('category').annotate(total=Sum('total_count')).order_by('category')

    # All animals for forms
    animals = Animal.objects.all().order_by('name')

    # Feed stock level and status
    feeds = Feed.objects.all()
    total_feed_stock = feeds.aggregate(total=Sum('current_stock'))['total'] or 0
    
    # Calculate feed status
    feed_status = 'normal'
    if feeds:
        critical_feeds = [f for f in feeds if f.current_stock <= f.low_stock_threshold * Decimal('0.5')]
        low_feeds = [f for f in feeds if f.low_stock_threshold * Decimal('0.5') < f.current_stock <= f.low_stock_threshold]
        
        if critical_feeds:
            feed_status = 'critical'
        elif low_feeds:
            feed_status = 'warning'
    
    # Low feed alerts
    low_feed_alerts = [feed for feed in feeds if feed.current_stock <= feed.low_stock_threshold]

    # Mortality counts and details
    recent_mortality = Mortality.objects.filter(date__gte=week_ago).aggregate(total=Sum('count'))['total'] or 0
    mortality_details = list(Mortality.objects.filter(date__gte=week_ago).select_related('animal'))

    # Sick animals alerts
    sick_animals = ActivityLog.objects.filter(
        activity_type='health_check', 
        notes__icontains='sick', 
        date__gte=today - timedelta(days=1)
    ).count()

    # Today's activities
    today_activities = ActivityLog.objects.filter(date=today).select_related('employee', 'animal')

    # Egg production history (last 7 days) - ordered newest first
    egg_history = []
    for i in range(7):
        date = today - timedelta(days=i)
        total = EggProduction.objects.filter(date=date).aggregate(total=Sum('quantity'))['total'] or 0
        egg_history.append({'date': date.strftime('%Y-%m-%d'), 'date_obj': date, 'total': total})

    # Weekly egg production total
    weekly_eggs = EggProduction.objects.filter(date__gte=week_ago).aggregate(total=Sum('quantity'))['total'] or 0

    # Feed consumption history (last 7 days) - ordered newest first
    feed_history = []
    for i in range(7):
        date = today - timedelta(days=i)
        total = FeedUsage.objects.filter(date=date).aggregate(total=Sum('quantity_used'))['total'] or 0
        feed_history.append({
            'date': date.strftime('%Y-%m-%d'), 
            'date_obj': date, 
            'total': float(total) if total else 0,
            'remaining': total_feed_stock
        })

    # Basic Analytics
    analytics = {}
    
    # Egg production trend
    last_week_eggs = EggProduction.objects.filter(date__gte=week_ago - timedelta(days=7), date__lt=week_ago).aggregate(total=Sum('quantity'))['total'] or 0
    if last_week_eggs > 0:
        egg_change_percent = ((weekly_eggs - last_week_eggs) / last_week_eggs) * 100
        analytics['egg_trend'] = f"Egg production {'increased' if egg_change_percent > 0 else 'decreased'} by {abs(egg_change_percent):.1f}% this week"
    else:
        analytics['egg_trend'] = "Egg production data available for trend analysis"
    
    # Feed consumption trend
    last_week_feed = FeedUsage.objects.filter(date__gte=week_ago - timedelta(days=7), date__lt=week_ago).aggregate(total=Sum('quantity_used'))['total'] or 0
    this_week_feed = FeedUsage.objects.filter(date__gte=week_ago).aggregate(total=Sum('quantity_used'))['total'] or 0
    if last_week_feed > 0:
        feed_change_percent = ((this_week_feed - last_week_feed) / last_week_feed) * 100
        analytics['feed_trend'] = f"Feed consumption {'increased' if feed_change_percent > 0 else 'decreased'} by {abs(feed_change_percent):.1f}% this week"
    else:
        analytics['feed_trend'] = "Feed consumption data available for trend analysis"
    
    # Mortality rate
    total_animals_count = total_animals or 1  # Avoid division by zero
    mortality_rate = (recent_mortality / total_animals_count) * 100
    analytics['mortality_rate'] = f"Mortality rate: {mortality_rate:.2f}% over last 7 days"
    
    # Productivity insights
    avg_daily_eggs = weekly_eggs / 7 if weekly_eggs > 0 else 0
    analytics['productivity'] = f"Average daily egg production: {avg_daily_eggs:.1f} eggs"
    
    # Get user notifications
    user_notifications = Notification.objects.filter(user=request.user).order_by('-created_at')[:10]
    
    # Format notifications for template
    notifications = []
    for notif in user_notifications:
        icon_map = {
            'info': 'ⓘ',
            'warning': '⚠️',
            'success': '✅',
            'error': '✕'
        }
        notifications.append({
            'type': notif.notification_type,
            'icon': icon_map.get(notif.notification_type, 'ⓘ'),
            'message': notif.title,
            'detail': notif.message,
            'date': notif.created_at.strftime('%Y-%m-%d %H:%M'),
            'id': notif.id,
            'is_read': notif.is_read
        })
    
    # Unread notification count
    unread_count = Notification.objects.filter(user=request.user, is_read=False).count()

    context = {
        'total_animals': total_animals,
        'today_eggs': today_eggs,
        'animals_by_category': animals_by_category,
        'animals': animals,
        'total_feed_stock': total_feed_stock,
        'feed_status': feed_status,
        'low_feed_alerts': low_feed_alerts,
        'recent_mortality': recent_mortality,
        'mortality_details': mortality_details,
        'sick_animals': sick_animals,
        'today_activities': today_activities,
        'notifications': notifications,
        'unread_notifications': unread_count,
        'egg_history': egg_history,
        'weekly_eggs': weekly_eggs,
        'feed_history': feed_history,
        'analytics': analytics,
    }
    return render(request, 'farm/user_dashboard.html', context)

@login_required
def user_reports(request):
    # Get date range from request or default to last 7 days
    end_date = timezone.now().date()
    start_date = end_date - timedelta(days=7)

    if request.GET.get('start_date'):
        start_date = timezone.datetime.strptime(request.GET['start_date'], '%Y-%m-%d').date()
    if request.GET.get('end_date'):
        end_date = timezone.datetime.strptime(request.GET['end_date'], '%Y-%m-%d').date()

    # Get egg collection activities with photos for the date range
    activities = ActivityLog.objects.filter(
        date__range=[start_date, end_date],
        activity_type='egg_collection',
        photo__isnull=False
    ).select_related('employee', 'animal').order_by('-date', '-time')

    # Group activities by date
    activities_by_date = {}
    for activity in activities:
        date_str = activity.date.strftime('%Y-%m-%d')
        if date_str not in activities_by_date:
            activities_by_date[date_str] = []
        activities_by_date[date_str].append(activity)

    # Get egg collection counts per day
    daily_activity_counts = ActivityLog.objects.filter(
        date__range=[start_date, end_date],
        activity_type='egg_collection'
    ).values('date').annotate(
        total_activities=Count('id'),
        activities_with_photos=Count('id', filter=Q(photo__isnull=False))
    ).order_by('-date')

    context = {
        'start_date': start_date,
        'end_date': end_date,
        'activities_by_date': activities_by_date,
        'daily_activity_counts': daily_activity_counts,
    }
    return render(request, 'farm/user_reports.html', context)

def resize_profile_photo(uploaded_file, max_width=600, max_height=840):
    try:
        image = Image.open(uploaded_file)
    except Exception:
        raise ValueError('Please upload a valid image file.')

    if image.mode in ('RGBA', 'LA', 'P'):
        image = image.convert('RGB')

    image.thumbnail((max_width, max_height), Image.LANCZOS)
    image_format = image.format or 'JPEG'
    output = BytesIO()
    save_format = 'JPEG' if image_format.upper() in ['JPEG', 'JPG'] else image_format

    if save_format.upper() == 'JPEG':
        image.save(output, format=save_format, quality=90)
        extension = '.jpg'
    else:
        image.save(output, format=save_format)
        extension = '.png'

    output.seek(0)
    file_root, _ = os.path.splitext(uploaded_file.name)
    filename = f"{file_root}{extension}"
    return filename, ContentFile(output.read())

@login_required
def user_profile(request):
    profile, created = UserProfile.objects.get_or_create(user=request.user)
    if request.method == 'POST':
        if 'change_password' in request.POST:
            form = PasswordChangeForm(request.user, request.POST)
            if form.is_valid():
                form.save()
                messages.success(request, 'Password changed successfully.')
                return redirect('farm:user_profile')
        else:
            user = request.user
            user.first_name = request.POST.get('first_name', '').strip()
            user.last_name = request.POST.get('last_name', '').strip()
            user.email = request.POST.get('email', user.email).strip()
            user.save()

            profile.phone_number = request.POST.get('phone_number', '')
            profile.photo_url = request.POST.get('photo_url', '')

            if request.POST.get('delete_photo') == 'on':
                if profile.photo:
                    profile.photo.delete(save=False)
                profile.photo = None

            if request.FILES.get('photo'):
                try:
                    filename, photo_content = resize_profile_photo(request.FILES['photo'])
                    profile.photo.save(filename, photo_content, save=False)
                except ValueError as err:
                    messages.error(request, str(err))
                    return redirect('farm:user_profile')

            profile.save()
            messages.success(request, 'Profile updated successfully.')
            return redirect('farm:user_profile')
    else:
        form = PasswordChangeForm(request.user)
    return render(request, 'farm/profile.html', {'form': form, 'profile': profile, 'user': request.user})

@login_required
def employee_list(request):
    employees = Employee.objects.select_related('user').all()

    # Get additional data for each employee
    employee_data = []
    for employee in employees:
        # Get recent activities (last 7 days)
        recent_activities = ActivityLog.objects.filter(
            employee=employee,
            date__gte=timezone.now().date() - timedelta(days=7)
        ).order_by('-date', '-time')[:5]

        # Get activity counts
        total_activities = ActivityLog.objects.filter(employee=employee).count()
        activities_this_month = ActivityLog.objects.filter(
            employee=employee,
            date__gte=timezone.now().date() - timedelta(days=30)
        ).count()

        # Get activities with photos
        photos_count = ActivityLog.objects.filter(
            employee=employee,
            photo__isnull=False
        ).count()

        employee_data.append({
            'employee': employee,
            'recent_activities': recent_activities,
            'total_activities': total_activities,
            'activities_this_month': activities_this_month,
            'photos_count': photos_count,
        })

    return render(request, 'farm/employees.html', {
        'employee_data': employee_data,
    })

@login_required
def animal_detail(request, animal_id):
    animal = get_object_or_404(Animal, id=animal_id)
    # Get recent activity history excluding poultry-only egg collection records
    activities = ActivityLog.objects.filter(animal=animal).exclude(activity_type='egg_collection').order_by('-date', '-time')[:20]
    # Get recent mortality records
    mortalities = Mortality.objects.filter(animal=animal).order_by('-date')[:10]
    return render(request, 'farm/animal_detail.html', {
        'animal': animal,
        'activities': activities,
        'mortalities': mortalities,
    })

def home(request):
    if request.user.is_authenticated:
        return redirect('/home/')
    else:
        return redirect('/login/')

# ===== NOTIFICATION MANAGEMENT VIEWS =====
@login_required
def mark_notification_read(request, notification_id):
    """Mark a specific notification as read"""
    notification = get_object_or_404(Notification, id=notification_id, user=request.user)
    notification.is_read = True
    notification.save()
    return JsonResponse({'success': True})

@login_required
def mark_all_notifications_read(request):
    """Mark all notifications as read for the current user"""
    Notification.objects.filter(user=request.user, is_read=False).update(is_read=True)
    return JsonResponse({'success': True})

@login_required
def clear_notifications(request):
    """Delete all notifications for the current user"""
    Notification.objects.filter(user=request.user).delete()
    return JsonResponse({'success': True})

# ===== FORM HANDLING VIEWS =====
@login_required
def add_animal(request):
    """Add a new animal"""
    if request.method == 'POST':
        category = request.POST.get('category')
        name = request.POST.get('name')
        total_count = request.POST.get('total_count')

        try:
            total_count = int(total_count)
            if total_count <= 0 or total_count > 10000:
                messages.error(request, 'Count must be between 1 and 10,000')
                return redirect('farm:user_dashboard')

            animal = Animal.objects.create(
                category=category,
                name=name,
                total_count=total_count
            )

            # Log the activity
            ActivityLog.objects.create(
                activity_type='add_animal',
                employee=request.user,
                animal=animal,
                date=timezone.now().date(),
                notes=f'Added {total_count} {category}(s) - {name}'
            )

            messages.success(request, 'Animal added successfully!')
            return redirect('farm:user_dashboard')

        except (ValueError, TypeError):
            messages.error(request, 'Invalid data provided')
            return redirect('farm:user_dashboard')

    return redirect('farm:user_dashboard')

@login_required
def record_egg_production(request):
    """Record egg production"""
    if request.method == 'POST':
        animal_id = request.POST.get('animal')
        quantity = request.POST.get('quantity')
        date = request.POST.get('date')

        try:
            animal = Animal.objects.get(id=animal_id)
            quantity = int(quantity)
            date = timezone.datetime.strptime(date, '%Y-%m-%d').date()

            if quantity <= 0:
                messages.error(request, 'Quantity must be greater than 0')
                return redirect('farm:user_dashboard')

            # Create egg production record
            egg_production = EggProduction.objects.create(
                animal=animal,
                date=date,
                quantity=quantity,
                collected_by=request.user
            )

            # Log the activity
            ActivityLog.objects.create(
                activity_type='egg_collection',
                employee=request.user,
                animal=animal,
                date=date,
                quantity=quantity,
                unit='eggs'
            )

            messages.success(request, 'Egg production recorded successfully!')
            return redirect('farm:user_dashboard')

        except Animal.DoesNotExist:
            messages.error(request, 'Animal not found')
            return redirect('farm:user_dashboard')
        except (ValueError, TypeError):
            messages.error(request, 'Invalid data provided')
            return redirect('farm:user_dashboard')

    return redirect('farm:user_dashboard')

@login_required
def add_feed(request):
    """Add new feed stock"""
    if request.method == 'POST':
        name = request.POST.get('name')
        quantity = request.POST.get('quantity')
        low_stock_threshold = request.POST.get('low_stock_threshold')
        unit = request.POST.get('unit', 'kg')

        try:
            quantity = float(quantity)
            low_stock_threshold = float(low_stock_threshold)

            if quantity <= 0 or low_stock_threshold < 0:
                messages.error(request, 'Invalid quantity or threshold values')
                return redirect('farm:user_dashboard')

            # Check if feed already exists
            feed, created = Feed.objects.get_or_create(
                name=name,
                defaults={
                    'type': 'mixed',  # Default type
                    'current_stock': quantity,
                    'unit': unit,
                    'low_stock_threshold': low_stock_threshold
                }
            )

            if not created:
                # Update existing feed stock
                feed.current_stock += quantity
                feed.save()

            # Log the activity
            ActivityLog.objects.create(
                activity_type='add_feed',
                employee=request.user,
                date=timezone.now().date(),
                quantity=quantity,
                unit=unit,
                notes=f'Added {quantity}{unit} of {name}'
            )

            messages.success(request, 'Feed added successfully!')
            return redirect('farm:user_dashboard')

        except (ValueError, TypeError):
            messages.error(request, 'Invalid data provided')
            return redirect('farm:user_dashboard')

    return redirect('farm:user_dashboard')

# ===== PDF EXPORT VIEWS =====

@login_required
def export_animal_pdf(request, animal_id):
    """Export individual animal data to PDF"""
    animal = get_object_or_404(Animal, id=animal_id)

    # Get recent mortality and activity data
    recent_mortality = Mortality.objects.filter(animal=animal).order_by('-date')[:10]
    activities = ActivityLog.objects.filter(animal=animal).exclude(activity_type='egg_collection').order_by('-date', '-time')[:20]

    # Create PDF response
    response = HttpResponse(content_type='application/pdf')
    response['Content-Disposition'] = f'attachment; filename="{animal.name}_report.pdf"'

    # Create PDF document
    doc = SimpleDocTemplate(response, pagesize=letter)
    styles = getSampleStyleSheet()
    elements = []

    # Title
    title_style = ParagraphStyle(
        'CustomTitle',
        parent=styles['Heading1'],
        fontSize=16,
        spaceAfter=30,
    )
    elements.append(Paragraph(f"Animal Report - {animal.name}", title_style))
    elements.append(Paragraph(f"Generated on: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}", styles['Normal']))
    elements.append(Spacer(1, 12))

    # Animal Overview
    elements.append(Paragraph("Animal Overview", styles['Heading2']))
    overview_data = [
        ['Animal Type', animal.get_category_display()],
        ['Total Count', str(animal.total_count)],
        ['Created', animal.created_at.strftime('%Y-%m-%d')],
    ]
    overview_table = Table(overview_data, colWidths=[2*inch, 4*inch])
    overview_table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.lightgrey),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.black),
        ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('FONTSIZE', (0, 0), (-1, 0), 12),
        ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
        ('BACKGROUND', (0, 1), (-1, -1), colors.white),
        ('GRID', (0, 0), (-1, -1), 1, colors.black)
    ]))
    elements.append(overview_table)
    elements.append(Spacer(1, 20))

    # Recent Mortality
    elements.append(Paragraph("Recent Mortality Records", styles['Heading2']))
    if recent_mortality:
        mortality_data = [['Date', 'Count', 'Reason', 'Reported By']]
        for mortality in recent_mortality:
            mortality_data.append([
                mortality.date.strftime('%Y-%m-%d'),
                str(mortality.count),
                mortality.reason or 'N/A',
                mortality.reported_by.get_full_name() if mortality.reported_by else 'N/A'
            ])
        mortality_table = Table(mortality_data, colWidths=[1.5*inch, 1*inch, 2.5*inch, 2*inch])
        mortality_table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.lightgrey),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.black),
            ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, 0), 12),
            ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
            ('BACKGROUND', (0, 1), (-1, -1), colors.white),
            ('GRID', (0, 0), (-1, -1), 1, colors.black)
        ]))
        elements.append(mortality_table)
    else:
        elements.append(Paragraph("No mortality records found.", styles['Normal']))
    elements.append(Spacer(1, 20))

    # Activity History
    elements.append(Paragraph("Activity History", styles['Heading2']))
    if activities:
        activity_data = [['Date', 'Time', 'Activity Type', 'Details', 'Recorded By']]
        for activity in activities:
            detail = activity.notes or f"{activity.quantity or ''} {activity.unit or ''}".strip() or 'N/A'
            activity_data.append([
                activity.date.strftime('%Y-%m-%d'),
                activity.time.strftime('%H:%M'),
                activity.get_activity_type_display(),
                detail,
                activity.employee.name or activity.employee.user.username
            ])
        activity_table = Table(activity_data, colWidths=[1.2*inch, 0.8*inch, 1.5*inch, 2*inch, 1.5*inch])
        activity_table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.lightgrey),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.black),
            ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, 0), 12),
            ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
            ('BACKGROUND', (0, 1), (-1, -1), colors.white),
            ('GRID', (0, 0), (-1, -1), 1, colors.black)
        ]))
        elements.append(activity_table)
    else:
        elements.append(Paragraph("No activity records found.", styles['Normal']))

    doc.build(elements)
    return response

@login_required
def export_feed_pdf(request):
    """Export feed inventory to PDF"""
    feeds = Feed.objects.all().order_by('name')

    response = HttpResponse(content_type='application/pdf')
    response['Content-Disposition'] = 'attachment; filename="feed_inventory_report.pdf"'

    doc = SimpleDocTemplate(response, pagesize=letter)
    styles = getSampleStyleSheet()
    elements = []

    # Title
    title_style = ParagraphStyle(
        'CustomTitle',
        parent=styles['Heading1'],
        fontSize=16,
        spaceAfter=30,
    )
    elements.append(Paragraph("Feed Inventory Report", title_style))
    elements.append(Paragraph(f"Generated on: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}", styles['Normal']))
    elements.append(Spacer(1, 12))

    if feeds:
        feed_data = [['Feed Name', 'Type', 'Current Stock', 'Unit', 'Status']]
        for feed in feeds:
            status = "Low Stock" if feed.current_stock <= feed.low_stock_threshold else "Normal"
            feed_data.append([
                feed.name,
                feed.type,
                f"{feed.current_stock}",
                feed.unit,
                status
            ])

        feed_table = Table(feed_data, colWidths=[2*inch, 1.5*inch, 1.5*inch, 1*inch, 1*inch])
        feed_table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.lightgrey),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.black),
            ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, 0), 12),
            ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
            ('BACKGROUND', (0, 1), (-1, -1), colors.white),
            ('GRID', (0, 0), (-1, -1), 1, colors.black)
        ]))
        elements.append(feed_table)
    else:
        elements.append(Paragraph("No feed records found.", styles['Normal']))

    doc.build(elements)
    return response

@login_required
def export_mortality_pdf(request):
    """Export mortality records to PDF"""
    mortality_records = Mortality.objects.select_related('animal', 'reported_by').order_by('-date')[:50]

    response = HttpResponse(content_type='application/pdf')
    response['Content-Disposition'] = 'attachment; filename="mortality_report.pdf"'

    doc = SimpleDocTemplate(response, pagesize=letter)
    styles = getSampleStyleSheet()
    elements = []

    # Title
    title_style = ParagraphStyle(
        'CustomTitle',
        parent=styles['Heading1'],
        fontSize=16,
        spaceAfter=30,
    )
    elements.append(Paragraph("Mortality Report", title_style))
    elements.append(Paragraph(f"Generated on: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}", styles['Normal']))
    elements.append(Spacer(1, 12))

    if mortality_records:
        mortality_data = [['Date', 'Animal', 'Count', 'Reason', 'Reported By']]
        for record in mortality_records:
            mortality_data.append([
                record.date.strftime('%Y-%m-%d'),
                record.animal.name,
                str(record.count),
                record.reason or 'N/A',
                record.reported_by.get_full_name() if record.reported_by else 'N/A'
            ])

        mortality_table = Table(mortality_data, colWidths=[1.2*inch, 2*inch, 0.8*inch, 2.5*inch, 1.5*inch])
        mortality_table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.lightgrey),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.black),
            ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, 0), 12),
            ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
            ('BACKGROUND', (0, 1), (-1, -1), colors.white),
            ('GRID', (0, 0), (-1, -1), 1, colors.black)
        ]))
        elements.append(mortality_table)
    else:
        elements.append(Paragraph("No mortality records found.", styles['Normal']))

    doc.build(elements)
    return response

@login_required
def export_egg_production_pdf(request):
    """Export egg production summary to PDF"""
    productions = EggProduction.objects.select_related('animal', 'collected_by').order_by('-date')

    response = HttpResponse(content_type='application/pdf')
    response['Content-Disposition'] = 'attachment; filename="egg_production_report.pdf"'

    doc = SimpleDocTemplate(response, pagesize=letter)
    styles = getSampleStyleSheet()
    elements = []

    title_style = ParagraphStyle(
        'CustomTitle',
        parent=styles['Heading1'],
        fontSize=16,
        spaceAfter=20,
    )
    elements.append(Paragraph("Egg Production Report", title_style))
    elements.append(Paragraph(f"Generated on: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}", styles['Normal']))
    elements.append(Spacer(1, 12))

    today_total = EggProduction.objects.filter(date=timezone.now().date()).aggregate(total=Sum('quantity'))['total'] or 0
    week_ago = timezone.now().date() - timedelta(days=7)
    weekly_total = EggProduction.objects.filter(date__gte=week_ago).aggregate(total=Sum('quantity'))['total'] or 0

    summary_data = [
        ['Metric', 'Value'],
        ['Today Total', f'{today_total} eggs'],
        ['7-Day Total', f'{weekly_total} eggs'],
    ]
    summary_table = Table(summary_data, colWidths=[2.5 * inch, 3.5 * inch])
    summary_table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.lightgrey),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.black),
        ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
        ('GRID', (0, 0), (-1, -1), 0.5, colors.grey),
        ('FONTNAME', (0, 0), (-1, -1), 'Helvetica'),
    ]))
    elements.append(summary_table)
    elements.append(Spacer(1, 18))

    if productions:
        production_data = [['Date', 'Animal', 'Quantity', 'Collected By']]
        for production in productions:
            production_data.append([
                production.date.strftime('%Y-%m-%d'),
                production.animal.name,
                str(production.quantity),
                production.collected_by.get_full_name() if production.collected_by else 'System',
            ])

        production_table = Table(production_data, colWidths=[1.5 * inch, 2.5 * inch, 1.2 * inch, 1.8 * inch])
        production_table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.lightgrey),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.black),
            ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
            ('GRID', (0, 0), (-1, -1), 0.5, colors.grey),
            ('FONTNAME', (0, 0), (-1, -1), 'Helvetica'),
        ]))
        elements.append(production_table)
    else:
        elements.append(Paragraph("No egg production records are available.", styles['Normal']))

    doc.build(elements)
    return response


@login_required
def export_activity_pdf(request):
    """Export activity summary to PDF"""
    activities = ActivityLog.objects.select_related('animal', 'employee').order_by('-date', '-time')[:50]

    response = HttpResponse(content_type='application/pdf')
    response['Content-Disposition'] = 'attachment; filename="activity_report.pdf"'

    doc = SimpleDocTemplate(response, pagesize=letter)
    styles = getSampleStyleSheet()
    elements = []

    # Title
    title_style = ParagraphStyle(
        'CustomTitle',
        parent=styles['Heading1'],
        fontSize=16,
        spaceAfter=30,
    )
    elements.append(Paragraph("Activity Report", title_style))
    elements.append(Paragraph(f"Generated on: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}", styles['Normal']))
    elements.append(Spacer(1, 12))

    if activities:
        activity_data = [['Date', 'Time', 'Animal', 'Activity Type', 'Details', 'Employee']]
        for activity in activities:
            detail = activity.notes or f"{activity.quantity or ''} {activity.unit or ''}".strip() or 'N/A'
            activity_data.append([
                activity.date.strftime('%Y-%m-%d'),
                activity.time.strftime('%H:%M'),
                activity.animal.name if activity.animal else 'N/A',
                activity.get_activity_type_display(),
                detail,
                activity.employee.name or activity.employee.user.username
            ])

        activity_table = Table(activity_data, colWidths=[1*inch, 0.8*inch, 1.5*inch, 1.5*inch, 2*inch, 1.2*inch])
        activity_table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.lightgrey),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.black),
            ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, 0), 12),
            ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
            ('BACKGROUND', (0, 1), (-1, -1), colors.white),
            ('GRID', (0, 0), (-1, -1), 1, colors.black)
        ]))
        elements.append(activity_table)
    else:
        elements.append(Paragraph("No activity records found.", styles['Normal']))

    doc.build(elements)
    return response

@login_required
def export_reports_pdf(request):
    """Export comprehensive system reports to PDF"""
    # Get summary data
    total_animals = Animal.objects.aggregate(total=Sum('total_count'))['total'] or 0
    total_feeds = Feed.objects.aggregate(total=Sum('current_stock'))['total'] or 0
    recent_mortality = Mortality.objects.filter(date__gte=timezone.now().date() - timedelta(days=30)).aggregate(total=Sum('count'))['total'] or 0
    recent_activities = ActivityLog.objects.filter(date__gte=timezone.now().date() - timedelta(days=30)).count()

    response = HttpResponse(content_type='application/pdf')
    response['Content-Disposition'] = 'attachment; filename="system_report.pdf"'

    doc = SimpleDocTemplate(response, pagesize=letter)
    styles = getSampleStyleSheet()
    elements = []

    # Title
    title_style = ParagraphStyle(
        'CustomTitle',
        parent=styles['Heading1'],
        fontSize=16,
        spaceAfter=30,
    )
    elements.append(Paragraph("Farm Management System Report", title_style))
    elements.append(Paragraph(f"Generated on: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}", styles['Normal']))
    elements.append(Spacer(1, 12))

    # System Overview
    elements.append(Paragraph("System Overview (Last 30 Days)", styles['Heading2']))
    overview_data = [
        ['Total Animals', str(total_animals)],
        ['Total Feed Stock', f"{total_feeds} kg"],
        ['Recent Mortality', str(recent_mortality)],
        ['Recent Activities', str(recent_activities)],
    ]
    overview_table = Table(overview_data, colWidths=[3*inch, 3*inch])
    overview_table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.lightgrey),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.black),
        ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('FONTSIZE', (0, 0), (-1, 0), 12),
        ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
        ('BACKGROUND', (0, 1), (-1, -1), colors.white),
        ('GRID', (0, 0), (-1, -1), 1, colors.black)
    ]))
    elements.append(overview_table)
    elements.append(Spacer(1, 20))

    # Animals by Category
    elements.append(Paragraph("Animals by Category", styles['Heading2']))
    animal_categories = Animal.objects.values('category').annotate(total=Sum('total_count')).order_by('category')
    if animal_categories:
        category_data = [['Category', 'Total Count']]
        for category in animal_categories:
            category_data.append([
                dict(Animal.CATEGORY_CHOICES)[category['category']],
                str(category['total'])
            ])
        category_table = Table(category_data, colWidths=[3*inch, 3*inch])
        category_table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.lightgrey),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.black),
            ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, 0), 12),
            ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
            ('BACKGROUND', (0, 1), (-1, -1), colors.white),
            ('GRID', (0, 0), (-1, -1), 1, colors.black)
        ]))
        elements.append(category_table)
    else:
        elements.append(Paragraph("No animal records found.", styles['Normal']))

    doc.build(elements)
    return response
