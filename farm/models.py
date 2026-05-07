from django.db import models
from django.db.models import Sum
from django.contrib.auth.models import User

class Animal(models.Model):
    CATEGORY_CHOICES = [
        ('chicken', 'Chicken'),
        ('duck', 'Duck'),
        ('goose', 'Goose'),
        ('turkey', 'Turkey'),
        ('quail', 'Quail'),
        ('pigs', 'Pigs'),
        ('goat', 'Goat'),
        ('fish', 'Fish'),
    ]
    category = models.CharField(max_length=20, choices=CATEGORY_CHOICES)
    name = models.CharField(max_length=100, unique=True)
    total_count = models.PositiveIntegerField(default=0)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.name} ({self.category})"

class EggProduction(models.Model):
    animal = models.ForeignKey(Animal, on_delete=models.CASCADE)
    date = models.DateField()
    quantity = models.PositiveIntegerField()
    collected_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True)

    class Meta:
        unique_together = ('animal', 'date')

    def __str__(self):
        return f"{self.animal} - {self.date}: {self.quantity}"

    @property
    def remaining_stock(self):
        """Calculate remaining eggs after sales"""
        sold = self.soldegg_set.aggregate(total_sold=Sum('quantity_sold'))['total_sold'] or 0
        return self.quantity - sold

class Feed(models.Model):
    name = models.CharField(max_length=100)
    type = models.CharField(max_length=50)  # e.g., 'grain', 'pellets'
    current_stock = models.DecimalField(max_digits=10, decimal_places=2)  # in kg
    unit = models.CharField(max_length=10, default='kg')
    low_stock_threshold = models.DecimalField(max_digits=10, decimal_places=2, default=100)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.name} ({self.type})"

class FeedUsage(models.Model):
    feed = models.ForeignKey(Feed, on_delete=models.CASCADE)
    date = models.DateField()
    quantity_used = models.DecimalField(max_digits=10, decimal_places=2, verbose_name='Kilograms used (kg)')
    animal = models.ForeignKey(Animal, on_delete=models.CASCADE)

    def __str__(self):
        return f"{self.feed} - {self.date}: {self.quantity_used} {self.feed.unit}"

class Mortality(models.Model):
    animal = models.ForeignKey(Animal, on_delete=models.CASCADE)
    date = models.DateField()
    count = models.PositiveIntegerField()
    reason = models.TextField(blank=True)
    reported_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True)

    def __str__(self):
        return f"{self.animal} - {self.date}: {self.count}"

class Employee(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    photo = models.ImageField(upload_to='employee_photos/', blank=True, null=True)
    name = models.CharField(max_length=100)
    phone_number = models.CharField(max_length=15, blank=True)
    hire_date = models.DateField()

    def __str__(self):
        return self.user.get_full_name() or self.user.username

class ActivityLog(models.Model):
    ACTIVITY_CHOICES = [
        ('feeding', 'Feeding'),
        ('cleaning', 'Cleaning'),
        ('egg_collection', 'Egg Collection'),
        ('health_check', 'Health Check'),
        ('mortality', 'Mortality'),
    ]
    activity_type = models.CharField(max_length=20, choices=ACTIVITY_CHOICES)
    employee = models.ForeignKey(Employee, on_delete=models.CASCADE)
    animal = models.ForeignKey(Animal, on_delete=models.CASCADE, null=True, blank=True)
    date = models.DateField()
    time = models.TimeField()
    quantity = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    unit = models.CharField(max_length=10, blank=True)
    notes = models.TextField(blank=True)
    photo = models.ImageField(upload_to='activity_photos/', blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.activity_type} - {self.employee} - {self.date} {self.time}"

class UserProfile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    phone_number = models.CharField(max_length=15, blank=True)
    photo = models.ImageField(upload_to='profile_photos/', blank=True, null=True)
    photo_url = models.URLField(blank=True)

    def __str__(self):
        return f"{self.user.username}'s profile"

class Notification(models.Model):
    NOTIFICATION_TYPES = [
        ('info', 'Info'),
        ('warning', 'Warning'),
        ('success', 'Success'),
        ('error', 'Error'),
    ]
    
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    title = models.CharField(max_length=200)
    message = models.TextField()
    notification_type = models.CharField(max_length=20, choices=NOTIFICATION_TYPES, default='info')
    is_read = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    related_model = models.CharField(max_length=50, blank=True)  # e.g., 'feed', 'animal', 'egg'
    related_id = models.PositiveIntegerField(null=True, blank=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.user.username}: {self.title}"

class SoldEgg(models.Model):
    egg_production = models.ForeignKey(EggProduction, on_delete=models.CASCADE)
    quantity_sold = models.PositiveIntegerField()
    price_per_unit = models.DecimalField(max_digits=8, decimal_places=2)
    sold_date = models.DateField()
    buyer = models.CharField(max_length=100, blank=True)
    notes = models.TextField(blank=True)
    sold_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Sold {self.quantity_sold} eggs on {self.sold_date}"

    @property
    def total_revenue(self):
        return self.quantity_sold * self.price_per_unit
