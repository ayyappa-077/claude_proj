from django.urls import path
from . import views

app_name = 'car_model'

urlpatterns = [
    path('cars/', views.car_model_list, name='car-list'),
    path('cars/<int:pk>/', views.car_model_detail, name='car-detail'),
    path('listings/', views.car_listing_list, name='listing-list'),
    path('listings/<int:pk>/', views.car_listing_detail, name='listing-detail'),
    path('stats/fuel-type/', views.fuel_type_stats, name='fuel-type-stats'),
    path('stats/listing-status/', views.listing_status_stats, name='listing-status-stats'),
    path('cars/fuel/<str:fuel_type>/', views.cars_by_fuel_type, name='cars-by-fuel'),
    path('owners/', views.owner_details, name='owner-details'),
]

