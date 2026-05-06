from django.db.models.signals import post_save, post_delete
from django.dispatch import receiver
from django.utils import timezone
from .models import Employee, FeedUsage, ActivityLog, EggProduction, Mortality, Animal


def get_employee_for_user(user):
    if user is None:
        return Employee.objects.first()
    return Employee.objects.filter(user=user).first() or Employee.objects.first()


@receiver(post_save, sender=FeedUsage)
def update_feed_stock_on_usage(sender, instance, created, **kwargs):
    """Update feed stock when feed usage is recorded"""
    if created:
        feed = instance.feed
        feed.current_stock -= instance.quantity_used
        feed.save()

@receiver(post_delete, sender=FeedUsage)
def restore_feed_stock_on_usage_delete(sender, instance, **kwargs):
    """Restore feed stock when feed usage is deleted"""
    feed = instance.feed
    feed.current_stock += instance.quantity_used
    feed.save()

@receiver(post_save, sender=Mortality)
def update_animal_count_on_mortality(sender, instance, created, **kwargs):
    """Update animal count when mortality is recorded"""
    if created:
        animal = instance.animal
        animal.total_count -= instance.count
        animal.save()

@receiver(post_delete, sender=Mortality)
def restore_animal_count_on_mortality_delete(sender, instance, **kwargs):
    """Restore animal count when mortality is deleted"""
    animal = instance.animal
    animal.total_count += instance.count
    animal.save()

@receiver(post_save, sender=EggProduction)
def log_egg_production_activity(sender, instance, created, **kwargs):
    """Log activity when egg production is recorded"""
    if created:
        employee = get_employee_for_user(instance.collected_by)
        if employee is None:
            return

        ActivityLog.objects.create(
            activity_type='egg_collection',
            employee=employee,
            animal=instance.animal,
            date=instance.date,
            time=timezone.now().time(),
            quantity=instance.quantity,
            unit='eggs'
        )

@receiver(post_save, sender=FeedUsage)
def log_feed_usage_activity(sender, instance, created, **kwargs):
    """Log activity when feed is used"""
    if created:
        employee = get_employee_for_user(None)
        if employee is None:
            return

        ActivityLog.objects.create(
            activity_type='feeding',
            employee=employee,
            animal=instance.animal,
            date=instance.date,
            time=timezone.now().time(),
            quantity=instance.quantity_used,
            unit=instance.feed.unit
        )

@receiver(post_save, sender=Mortality)
def log_mortality_activity(sender, instance, created, **kwargs):
    """Log activity when mortality is recorded"""
    if created:
        employee = get_employee_for_user(instance.reported_by)
        if employee is None:
            return

        ActivityLog.objects.create(
            activity_type='health_check',
            employee=employee,
            animal=instance.animal,
            date=instance.date,
            time=timezone.now().time(),
            notes=f'Mortality: {instance.count} deaths - {instance.reason}'
        )
