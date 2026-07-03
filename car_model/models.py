from django.db import models

# Create your models here.


class CarModel(models.Model):
    FUEL_CHOICES = [
        ('petrol', 'Petrol'),
        ('diesel', 'Diesel'),
        ('electric', 'Electric'),
        ('hybrid', 'Hybrid'),
    ]

    TRANSMISSION_CHOICES = [
        ('manual', 'Manual'),
        ('automatic', 'Automatic'),
    ]

    brand = models.CharField(max_length=50)
    model_name = models.CharField(max_length=50)
    year = models.IntegerField()
    fuel_type = models.CharField(max_length=10, choices=FUEL_CHOICES)
    transmission = models.CharField(max_length=10, choices=TRANSMISSION_CHOICES)
    engine_capacity_cc = models.IntegerField()
    mileage_kmpl = models.DecimalField(max_digits=5, decimal_places=2)
    seating_capacity = models.IntegerField()
    color = models.CharField(max_length=30)
    price = models.DecimalField(max_digits=10, decimal_places=2)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'car_catalog'

    def __str__(self):
        return f"{self.brand} {self.model_name} ({self.year})"


class CarListing(models.Model):
    STATUS_CHOICES = [
        ('available', 'Available'),
        ('sold', 'Sold'),
        ('reserved', 'Reserved'),
    ]

    car = models.ForeignKey(CarModel, on_delete=models.CASCADE, related_name='listings')
    dealer_name = models.CharField(max_length=100)
    registration_number = models.CharField(max_length=20, unique=True)
    owner_name = models.CharField(max_length=100)
    contact_number = models.CharField(max_length=15)
    odometer_reading_km = models.IntegerField()
    location = models.CharField(max_length=100)
    listing_price = models.DecimalField(max_digits=10, decimal_places=2)
    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default='available')
    listed_date = models.DateField(auto_now_add=True)
    description = models.TextField(blank=True)

    class Meta:
        db_table = 'car_listing'

    def __str__(self):
        return f"{self.registration_number} - {self.car}"