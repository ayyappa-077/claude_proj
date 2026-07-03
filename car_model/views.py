from rest_framework import status
from rest_framework.decorators import api_view,permission_classes
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from .db_pipeline import (
    get_all_cars,
    get_all_listings,
    get_fuel_type_stats,
    get_cars_by_fuel_type,
    get_listing_status_stats,
    search_owners,
    filter_cars,
    filter_listings,
)
from .models import CarModel, CarListing
from .serializers import CarModelSerializer, CarListingSerializer


# ─── CarModel ─────────────────────────────────────────────────────────────────

@api_view(['GET', 'POST'])
def car_model_list(request):
    if request.method == 'GET':
        data = filter_cars(
            fuel_type=request.query_params.get('fuel_type'),
            transmission=request.query_params.get('transmission'),
            brand=request.query_params.get('brand'),
            year=request.query_params.get('year'),
            min_price=request.query_params.get('min_price'),
            max_price=request.query_params.get('max_price'),
            seating_capacity=request.query_params.get('seating_capacity'),
        )
        return Response({'count': len(data), 'results': data})

    if request.method == 'POST':
        serializer = CarModelSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


@api_view(['GET', 'PUT', 'PATCH', 'DELETE'])
def car_model_detail(request, pk):
    try:
        car = CarModel.objects.get(pk=pk)
    except CarModel.DoesNotExist:
        return Response({'detail': 'Car not found.'}, status=status.HTTP_404_NOT_FOUND)

    if request.method == 'GET':
        serializer = CarModelSerializer(car)
        return Response(serializer.data)

    if request.method in ['PUT', 'PATCH']:
        partial = request.method == 'PATCH'
        serializer = CarModelSerializer(car, data=request.data, partial=partial)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    if request.method == 'DELETE':
        car.delete()
        return Response({'detail': 'Car deleted.'}, status=status.HTTP_204_NO_CONTENT)


# ─── CarListing ───────────────────────────────────────────────────────────────

@api_view(['GET', 'POST'])
def car_listing_list(request):
    if request.method == 'GET':
        data = filter_listings(
            status=request.query_params.get('status'),
            location=request.query_params.get('location'),
            fuel_type=request.query_params.get('fuel_type'),
            owner_name=request.query_params.get('owner_name'),
            dealer_name=request.query_params.get('dealer_name'),
            min_price=request.query_params.get('min_price'),
            max_price=request.query_params.get('max_price'),
        )
        return Response({'count': len(data), 'results': data})

    if request.method == 'POST':
        serializer = CarListingSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


@api_view(['GET', 'PUT', 'PATCH', 'DELETE'])
def car_listing_detail(request, pk):
    try:
        listing = CarListing.objects.select_related('car').get(pk=pk)
    except CarListing.DoesNotExist:
        return Response({'detail': 'Listing not found.'}, status=status.HTTP_404_NOT_FOUND)

    if request.method == 'GET':
        serializer = CarListingSerializer(listing)
        return Response(serializer.data)

    if request.method in ['PUT', 'PATCH']:
        partial = request.method == 'PATCH'
        serializer = CarListingSerializer(listing, data=request.data, partial=partial)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    if request.method == 'DELETE':
        listing.delete()
        return Response({'detail': 'Listing deleted.'}, status=status.HTTP_204_NO_CONTENT)


# ─── Stats & Filters ──────────────────────────────────────────────────────────

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def fuel_type_stats(request):
    return Response(get_fuel_type_stats())


@api_view(['GET'])
def cars_by_fuel_type(request, fuel_type):
    valid = ['petrol', 'diesel', 'electric', 'hybrid']
    if fuel_type not in valid:
        return Response(
            {'detail': f'Invalid fuel type. Choose from {valid}.'},
            status=status.HTTP_400_BAD_REQUEST,
        )
    data = get_cars_by_fuel_type(fuel_type)
    return Response({'fuel_type': fuel_type, 'total_cars': len(data), 'data': data})


@api_view(['GET'])
def listing_status_stats(request):
    return Response(get_listing_status_stats())


@api_view(['GET'])
def owner_details(request):
    owner_name = request.query_params.get('owner_name')
    location = request.query_params.get('location')
    registration = request.query_params.get('registration_number')

    if not any([owner_name, location, registration]):
        return Response(
            {'detail': 'Provide at least one: owner_name, location, registration_number.'},
            status=status.HTTP_400_BAD_REQUEST,
        )

    data = search_owners(owner_name, location, registration)
    return Response({'count': len(data), 'results': data})