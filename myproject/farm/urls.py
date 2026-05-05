from django.urls import path
from . import views

app_name = 'farm'

urlpatterns = [
    path('dashboard/', views.dashboard, name='dashboard'),
    path('login/', views.user_login, name='user_login'),
    path('register/', views.user_register, name='user_register'),
    path('logout/', views.user_logout, name='user_logout'),
    path('home/', views.user_dashboard, name='user_dashboard'),
    path('reports/', views.user_reports, name='user_reports'),
    path('profile/', views.user_profile, name='user_profile'),
    path('employees/', views.employee_list, name='employee_list'),
    path('animals/', views.animals, name='animals'),
    path('animals/add/', views.add_animal, name='add_animal'),
    path('egg_production/', views.egg_production, name='egg_production'),
    path('egg_production/record/', views.record_egg_production, name='record_egg_production'),
    path('feed_inventory/', views.feed_inventory, name='feed_inventory'),
    path('feed_inventory/add/', views.add_feed, name='add_feed'),
    path('mortality_records/', views.mortality_records, name='mortality_records'),
    path('mortality_records/record/', views.record_mortality, name='record_mortality'),
    path('animal/<int:animal_id>/', views.animal_detail, name='animal_detail'),
    path('notifications/mark-read/<int:notification_id>/', views.mark_notification_read, name='mark_notification_read'),
    path('notifications/mark-all-read/', views.mark_all_notifications_read, name='mark_all_notifications_read'),
    path('notifications/clear/', views.clear_notifications, name='clear_notifications'),
    path('export/animal/<int:animal_id>/pdf/', views.export_animal_pdf, name='export_animal_pdf'),
    path('export/feed/pdf/', views.export_feed_pdf, name='export_feed_pdf'),
    path('export/mortality/pdf/', views.export_mortality_pdf, name='export_mortality_pdf'),
    path('export/egg-production/pdf/', views.export_egg_production_pdf, name='export_egg_production_pdf'),
    path('export/activity/pdf/', views.export_activity_pdf, name='export_activity_pdf'),
    path('export/reports/pdf/', views.export_reports_pdf, name='export_reports_pdf'),
    path('', views.home, name='home'),
]