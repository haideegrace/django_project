from django.core.management.base import BaseCommand
from farm.models import Animal, EggProduction, Feed, FeedUsage, Mortality, ActivityLog, Employee
from django.contrib.auth.models import User
from datetime import date, timedelta
import random

class Command(BaseCommand):
    help = 'Generate sample data for testing and demo purposes'

    def handle(self, *args, **options):
        self.stdout.write('Generating sample data...')

        # Create sample user if none exists
        if not User.objects.filter(username='demo_owner').exists():
            user = User.objects.create_user(
                username='demo_owner',
                email='owner@farm.com',
                password='demo123',
                first_name='Demo',
                last_name='Owner'
            )
            user.is_staff = True
            user.save()

        # Create sample animals
        categories = ['Chicken', 'Duck', 'Turkey', 'Quail']
        animals = []
        for i in range(15):
            animal = Animal.objects.create(
                category=random.choice(categories),
                name=f'{random.choice(categories)} {i+1}',
                total_count=random.randint(20, 150),
                description=f'Sample {random.choice(categories)} for demo'
            )
            animals.append(animal)

        # Create sample employees
        employees = []
        for i in range(5):
            employee = Employee.objects.create(
                name=f'Worker {i+1}',
                phone_number=f'091234567{i}',
                position=random.choice(['Farm Hand', 'Supervisor', 'Veterinarian'])
            )
            employees.append(employee)

        # Create sample feeds
        feeds = []
        feed_types = ['Corn', 'Wheat', 'Soybean', 'Rice Bran']
        for feed_type in feed_types:
            feed = Feed.objects.create(
                name=f'{feed_type} Feed',
                unit='kg',
                current_stock=random.randint(100, 500),
                low_stock_threshold=random.randint(20, 50)
            )
            feeds.append(feed)

        # Generate data for last 30 days
        for days_ago in range(30):
            prod_date = date.today() - timedelta(days=days_ago)

            # Egg production
            for animal in animals:
                if animal.category in ['Chicken', 'Duck', 'Quail']:
                    EggProduction.objects.create(
                        animal=animal,
                        quantity=random.randint(5, 30),
                        date=prod_date
                    )

            # Feed usage
            for feed in feeds:
                FeedUsage.objects.create(
                    feed=feed,
                    quantity_used=random.uniform(10, 50),
                    date=prod_date
                )

            # Mortality (occasional)
            if random.random() < 0.1:  # 10% chance per day
                animal = random.choice(animals)
                Mortality.objects.create(
                    animal=animal,
                    count=random.randint(1, 3),
                    date=prod_date,
                    cause=random.choice(['Disease', 'Accident', 'Age', 'Unknown'])
                )

            # Activity logs
            for _ in range(random.randint(2, 5)):
                ActivityLog.objects.create(
                    employee=random.choice(employees),
                    animal=random.choice(animals),
                    activity_type=random.choice(['feeding', 'health_check', 'cleaning', 'egg_collection']),
                    date=prod_date,
                    time=f'{random.randint(6,18):02d}:{random.randint(0,59):02d}',
                    quantity=random.randint(1, 20) if random.random() > 0.5 else None,
                    unit='kg' if random.random() > 0.5 else None,
                    notes=f'Sample activity for {prod_date}'
                )

        self.stdout.write(self.style.SUCCESS('Sample data generated successfully!'))
        self.stdout.write(f'Created {len(animals)} animals, {len(employees)} employees, {len(feeds)} feeds')
        self.stdout.write('Demo user: demo_owner / demo123')