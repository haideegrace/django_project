from django.contrib import admin
from django.urls import path
from django.shortcuts import redirect, render
from django.contrib import messages
from django.utils import timezone
from . import views
from .forms import ActivityLogForm

class FarmAdminSite(admin.AdminSite):
    site_header = "Batac Farm Administration"
    site_title = "Batac Farm Admin"
    index_title = "Welcome to Batac Farm Dashboard"

    def get_urls(self):
        urls = super().get_urls()
        custom_urls = [
            path('dashboard/', views.dashboard, name='dashboard'),
            path('add-activity/', self.add_activity_view, name='add_activity'),
        ]
        return custom_urls + urls

    def add_activity_view(self, request):
        if request.method == 'POST':
            form = ActivityLogForm(request.POST, request.FILES)
            if form.is_valid():
                activity = form.save()
                messages.success(request, f'Activity "{activity.activity_type}" recorded successfully with photo proof!')
                return redirect('admin:farm_activitylog_changelist')
        else:
            form = ActivityLogForm()
        return render(request, 'admin/add_activity.html', {
            'form': form,
            'title': 'Add Activity with Photo Proof'
        })

    def index(self, request, extra_context=None):
        # Redirect to dashboard
        return redirect('admin:dashboard')

farm_admin = FarmAdminSite(name='farm_admin')

# Register your models here.
from .models import Animal, EggProduction, Feed, FeedUsage, Mortality, Employee, ActivityLog

@admin.register(Animal)
class AnimalAdmin(admin.ModelAdmin):
    list_display = ['name', 'category', 'total_count', 'updated_at']
    list_filter = ['category']
    search_fields = ['name']

@admin.register(EggProduction)
class EggProductionAdmin(admin.ModelAdmin):
    list_display = ['animal', 'date', 'quantity', 'collected_by']
    list_filter = ['date', 'animal']
    date_hierarchy = 'date'

@admin.register(Feed)
class FeedAdmin(admin.ModelAdmin):
    list_display = ['name', 'type', 'current_stock', 'unit', 'low_stock_threshold']
    list_filter = ['type']

@admin.register(FeedUsage)
class FeedUsageAdmin(admin.ModelAdmin):
    list_display = ['feed', 'date', 'quantity_used', 'animal']
    list_filter = ['date', 'feed', 'animal']
    date_hierarchy = 'date'
    fieldsets = (
        ('Feed Usage Information', {
            'fields': ('feed', 'date', 'animal', 'quantity_used')
        }),
    )
    
    def get_form(self, request, obj=None, **kwargs):
        form = super().get_form(request, obj, **kwargs)
        # Enhance the quantity_used field widget with help text
        if 'quantity_used' in form.base_fields:
            form.base_fields['quantity_used'].widget.attrs.update({
                'placeholder': 'Enter kilograms (e.g., 25.50)',
                'step': '0.01',
                'min': '0'
            })
            form.base_fields['quantity_used'].help_text = 'Enter the amount of feed used in kilograms (kg)'
        return form

@admin.register(Mortality)
class MortalityAdmin(admin.ModelAdmin):
    list_display = ['animal', 'date', 'count', 'reason', 'reported_by']
    list_filter = ['date', 'animal']
    date_hierarchy = 'date'

@admin.register(Employee)
class EmployeeAdmin(admin.ModelAdmin):
    list_display = ['user', 'name', 'hire_date']
    search_fields = ['user__username', 'user__first_name', 'user__last_name']

@admin.register(ActivityLog)
class ActivityLogAdmin(admin.ModelAdmin):
    list_display = ['activity_type', 'employee', 'animal', 'date', 'time', 'has_photo', 'created_at']
    list_filter = ['activity_type', 'date', 'employee', 'animal']
    date_hierarchy = 'date'
    readonly_fields = ['created_at']
    fields = ['activity_type', 'employee', 'animal', 'date', 'time', 'quantity', 'unit', 'notes', 'photo']

    def has_photo(self, obj):
        return bool(obj.photo)
    has_photo.boolean = True
    has_photo.short_description = 'Photo Proof'

# Register with the custom admin site
farm_admin.register(Animal, AnimalAdmin)
farm_admin.register(EggProduction, EggProductionAdmin)
farm_admin.register(Feed, FeedAdmin)
farm_admin.register(FeedUsage, FeedUsageAdmin)
farm_admin.register(Mortality, MortalityAdmin)
farm_admin.register(Employee, EmployeeAdmin)
farm_admin.register(ActivityLog, ActivityLogAdmin)
