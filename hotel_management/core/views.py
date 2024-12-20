from django.shortcuts import render, get_object_or_404, redirect
from django.urls import reverse_lazy
from django.views.generic import ListView, CreateView, UpdateView, DeleteView, DetailView
from django.http import JsonResponse
from django.template.loader import render_to_string
from django.db.models import Q
from django.core.paginator import Paginator  # Add the paginator import here
from datetime import datetime  # For date filtering
from .models import Room, Booking  # Make sure Booking is imported
from .forms import RoomForm, BookingForm
from django.contrib import messages
from django.db.models import Count, Sum, F
from django.views import View


class RoomListView(ListView):
    model = Room
    template_name = 'core/room_list.html'
    context_object_name = 'page_obj'
    paginate_by = 6  # Adjust the number of rooms per page

    def get_queryset(self):
        queryset = Room.objects.all()

        # Apply search filter
        search_query = self.request.GET.get('search', '')
        if search_query:
            queryset = queryset.filter(
                Q(name__icontains=search_query) |
                Q(room_type__icontains=search_query) |
                Q(description__icontains=search_query)
            )

        # Apply type filter
        room_type = self.request.GET.get('type')
        if room_type:
            queryset = queryset.filter(room_type=room_type)

        # Apply status filter
        status = self.request.GET.get('status')
        if status:
            queryset = queryset.filter(status=status)

        # Apply price range filter
        min_price = self.request.GET.get('min_price')
        if min_price:
            queryset = queryset.filter(price_per_night__gte=min_price)

        max_price = self.request.GET.get('max_price')
        if max_price:
            queryset = queryset.filter(price_per_night__lte=max_price)

        return queryset

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['search_query'] = self.request.GET.get('search', '')  # Pass search query to context
        context['room_type'] = self.request.GET.get('type', '')  # Pass room type to context
        context['status'] = self.request.GET.get('status', '')  # Pass room status to context
        context['min_price'] = self.request.GET.get('min_price', '')  # Pass min price to context
        context['max_price'] = self.request.GET.get('max_price', '')  # Pass max price to context
        return context


# AJAX handling for room list filtering
def room_list_ajax(request):
    search_query = request.GET.get('search', '')
    rooms = Room.objects.filter(
        Q(name__icontains=search_query) | Q(room_type__icontains=search_query)
    )
    html = render_to_string('core/room_list_partial.html', {'rooms': rooms}, request=request)
    return JsonResponse({'html': html})


class RoomCreateView(CreateView):
    model = Room
    form_class = RoomForm
    template_name = 'core/room_form.html'
    success_url = reverse_lazy('core:room_list')

    def form_valid(self, form):
        response = super().form_valid(form)
        return response


class RoomUpdateView(UpdateView):
    model = Room
    form_class = RoomForm
    template_name = 'core/room_form.html'
    context_object_name = 'room'
    success_url = reverse_lazy('core:room_list')

    def form_valid(self, form):
        response = super().form_valid(form)
        return response


class RoomDeleteView(DeleteView):
    model = Room
    template_name = 'core/room_confirm_delete.html'
    context_object_name = 'room'
    success_url = reverse_lazy('core:room_list')


def index(request):
    return render(request, 'core/index.html')


class RoomDetailView(DetailView):
    model = Room
    template_name = 'core/room_detail.html'
    context_object_name = 'room'


def dashboard(request):
    return render(request, 'core/dashboard.html')


# View for deleting a booking
def booking_delete(request, booking_id):
    booking = get_object_or_404(Booking, id=booking_id)
    
    if request.method == "POST":
        booking.delete()
        messages.success(request, f"Booking for {booking.guest_name} has been deleted.")
        return redirect('core:dashboard')  # Redirect to the dashboard or any other page you prefer

    return redirect('core:dashboard')  # Redirect if the request method is not POST

# View to list all bookings
def booking_list(request):
    # Initialize filters from GET parameters
    guest_name = request.GET.get('guest_name', '')
    check_in_date = request.GET.get('check_in_date', '')
    check_out_date = request.GET.get('check_out_date', '')
    status = request.GET.get('status', '')

    # Build the filter conditions
    bookings = Booking.objects.all()

    if guest_name:
        bookings = bookings.filter(guest_name__icontains=guest_name)
    
    if check_in_date:
        check_in_date = datetime.strptime(check_in_date, '%Y-%m-%d').date()  # Convert to date
        bookings = bookings.filter(check_in_date__gte=check_in_date)
    
    if check_out_date:
        check_out_date = datetime.strptime(check_out_date, '%Y-%m-%d').date()  # Convert to date
        bookings = bookings.filter(check_out_date__lte=check_out_date)
    
    if status:
        bookings = bookings.filter(status=status)

    # Pagination
    page_number = request.GET.get('page')
    paginator = Paginator(bookings, 6)  # Adjust per page as needed
    page_obj = paginator.get_page(page_number)

    # Return the context for rendering the template
    return render(request, 'core/booking_list.html', {
        'bookings': page_obj,
        'guest_name': guest_name,
        'check_in_date': check_in_date,
        'check_out_date': check_out_date,
        'status': status,
    })


# NEW: Add the booking_detail view
def booking_detail(request, booking_id):
    # Fetch the booking object or return a 404 error if not found
    booking = get_object_or_404(Booking, id=booking_id)
    return render(request, 'core/booking_detail.html', {'booking': booking})


def reporting_view(request):
    # Room occupancy report
    total_rooms = Room.objects.count()
    occupied_rooms = Booking.objects.filter(status='Confirmed').values('room').distinct().count()
    available_rooms = total_rooms - occupied_rooms

    # Booking statistics
    total_bookings = Booking.objects.count()
    confirmed_bookings = Booking.objects.filter(status='Confirmed').count()
    cancelled_bookings = Booking.objects.filter(status='Cancelled').count()
    completed_bookings = Booking.objects.filter(status='Completed').count()

    # Revenue report
    total_revenue = Booking.objects.filter(status='Confirmed').aggregate(total_revenue=Sum(F('room__price_per_night') * F('nights_stayed')))['total_revenue'] or 0
    revenue_by_room_type = Booking.objects.filter(status='Confirmed').values('room__room_type').annotate(revenue=Sum(F('room__price_per_night') * F('nights_stayed')))
    
    # Customer analytics
    most_frequent_customers = Booking.objects.values('guest_name').annotate(total_bookings=Count('guest_name')).order_by('-total_bookings')[:5]

    # Booking history over time
    bookings_over_time = Booking.objects.extra(select={'month': 'EXTRACT(MONTH FROM check_in_date)'}).values('month').annotate(total=Count('id')).order_by('month')

    context = {
        'total_rooms': total_rooms,
        'occupied_rooms': occupied_rooms,
        'available_rooms': available_rooms,
        'total_bookings': total_bookings,
        'confirmed_bookings': confirmed_bookings,
        'cancelled_bookings': cancelled_bookings,
        'completed_bookings': completed_bookings,
        'total_revenue': total_revenue,
        'revenue_by_room_type': revenue_by_room_type,
        'most_frequent_customers': most_frequent_customers,
        'bookings_over_time': bookings_over_time
    }

    return render(request, 'core/reporting.html', context)


class ReportsView(View):
    def get(self, request):
        return render(request, 'core/reports.html')

def contact(request):
    return render(request, 'core/contact.html')