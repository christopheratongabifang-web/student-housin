import random
from django.core.management.base import BaseCommand
from django.contrib.auth import get_user_model
from properties.models import Property
from reviews.models import Review

User = get_user_model()

class Command(BaseCommand):
    help = 'Seeds the database with dummy property data'

    def handle(self, *args, **kwargs):
        self.stdout.write('Seeding database...')

        # Ensure landlord exists
        landlord, created = User.objects.get_or_create(
            username='landlord1',
            defaults={'email': 'landlord@test.com', 'role': 'LANDLORD'}
        )
        if created:
            landlord.set_password('password')
            landlord.save()

        # Ensure student exists
        student, created = User.objects.get_or_create(
            username='student1',
            defaults={'email': 'student@test.com', 'role': 'STUDENT'}
        )
        if created:
            student.set_password('password')
            student.save()

        # Clear existing properties to avoid duplicates
        Property.objects.all().delete()

        # Campus coordinate (Let's use University of London coordinates as an example: 51.5223, -0.1308)
        base_lat = 51.5223
        base_lng = -0.1308

        amenities_list = ['WiFi', 'Washing Machine', 'Gym', 'Parking', 'Study Room', 'All Bills Included']
        titles = ['Cozy Studio Near Campus', 'Ensuite Room in Shared Flat', 'Modern 2-Bed Apartment', 'Budget Student Room', 'Luxury Studio']

        properties = []
        for i in range(15):
            # Generate random offset for coordinates (approx 1-3km radius)
            lat = base_lat + random.uniform(-0.03, 0.03)
            lng = base_lng + random.uniform(-0.03, 0.03)
            distance = round(random.uniform(0.1, 4.0), 1)
            
            p = Property(
                landlord=landlord,
                title=f"{random.choice(titles)} {i+1}",
                description=f"A fantastic place for students. Fully furnished and ready to move in. Located very close to local amenities. Heating and water included.",
                price_per_month=random.randint(500, 1500),
                latitude=lat,
                longitude=lng,
                amenities=random.sample(amenities_list, k=random.randint(2, 5)),
                distance_to_campus=distance
            )
            p.save()
            properties.append(p)

        # Create some reviews
        for p in properties:
            if random.choice([True, False]):
                Review.objects.create(
                    property=p,
                    student=student,
                    rating=random.randint(3, 5),
                    comment="Great place, landlord is very responsive."
                )

        self.stdout.write(self.style.SUCCESS('Successfully seeded 15 properties with reviews!'))
