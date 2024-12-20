from django.urls import path
from django.contrib.auth.views import LogoutView
from . import views
from django.conf import settings
from django.conf.urls.static import static
from .views import (
    RoomListView,
    RoomCreateView,
    RoomUpdateView,
    RoomDeleteView,
    RoomDetailView,
    index,
    room_list_ajax,
)

app_name = 'core'

# Room management URLs
urlpatterns = [
    # Home page
    path('', index, name='home'),  # Serves the homepage

    # Dashboard
    path('dashboard/', views.dashboard, name='dashboard'),  # Unique path for the dashboard

    # Room management URLs
    path('rooms/', RoomListView.as_view(), name='room_list'),  # List all rooms
    path('rooms/add/', RoomCreateView.as_view(), name='room_add'),  # Add a new room
    path('rooms/<int:pk>/edit/', RoomUpdateView.as_view(), name='room_update'),
    path('rooms/<int:pk>/delete/', RoomDeleteView.as_view(), name='room_delete'),  # Delete a specific room
    path('rooms/ajax/', room_list_ajax, name='room_list_ajax'),
    path('rooms/<int:pk>/', RoomDetailView.as_view(), name='room_detail'),  # Detail view for a specific room

    #Booking URls
    path('booking/<int:booking_id>/details/', views.booking_detail, name='booking_detail'),
    path('booking/<int:booking_id>/delete/', views.booking_delete, name='booking_delete'),
    path('bookings/', views.booking_list, name='booking_list'),


    # Reports and analytics view
    path('reporting/', views.reporting_view, name='reporting'),
    path('reports/', views.ReportsView.as_view(), name='reports'),

    # Contact
    path('contact/', views.contact, name='contact'),

    # Logout
    path('logout/', LogoutView.as_view(), name='logout'),


]

# Serve media files during development
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
