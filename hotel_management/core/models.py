from django.db import models

class Room(models.Model):
    ROOM_TYPE_CHOICES = [
        ('Single', 'Single'),
        ('Double', 'Double'),
        ('Suite', 'Suite'),
    ]

    STATUS_CHOICES = [
        ('Available', 'Available'),
        ('Occupied', 'Occupied'),
        ('Maintenance', 'Maintenance'),
    ]

    name = models.CharField(max_length=100)
    capacity = models.IntegerField()
    room_type = models.CharField(max_length=10, choices=ROOM_TYPE_CHOICES)
    price_per_night = models.DecimalField(max_digits=10, decimal_places=2)
    description = models.TextField()
    status = models.CharField(max_length=15, choices=STATUS_CHOICES, default='Available')  # New field
    image = models.ImageField(upload_to='room_images/', blank=True, null=True)  # Optional image field

    def __str__(self):
        return self.name


class Booking(models.Model):
    STATUS_CHOICES = [
        ('Pending', 'Pending'),
        ('Confirmed', 'Confirmed'),
        ('Completed', 'Completed'),
        ('Cancelled', 'Cancelled'),
    ]

    room = models.ForeignKey(Room, on_delete=models.CASCADE, related_name='bookings')
    guest_name = models.CharField(max_length=100)
    guest_email = models.EmailField()
    check_in_date = models.DateField()
    check_out_date = models.DateField()
    status = models.CharField(max_length=15, choices=STATUS_CHOICES, default='Pending')
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Booking for {self.guest_name} in {self.room.name}"
