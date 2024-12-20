from django import forms
from .models import Room
from .models import Booking
class RoomForm(forms.ModelForm):
    class Meta:
        model = Room
        fields = ['name', 'capacity', 'room_type', 'price_per_night', 'description']
        widgets = {
            'description': forms.Textarea(attrs={'rows': 3}),
        }

class BookingForm(forms.ModelForm):
    class Meta:
        model = Booking
        fields = ['guest_name', 'check_in_date', 'check_out_date', 'room', 'status']