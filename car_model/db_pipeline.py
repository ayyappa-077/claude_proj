from urllib.parse import quote_plus

import pandas as pd
from sqlalchemy import create_engine
from django.conf import settings

def get_engine():
    """Create SQLAlchemy engine from Django settings safely."""
    db = settings.DATABASES['default']
    # Encode password so special characters like #, @, etc. don’t break the URI
    password = quote_plus(db['PASSWORD'])
    engine = create_engine(
        f"postgresql+psycopg2://{db['USER']}:{password}@{db['HOST']}:{db['PORT']}/{db['NAME']}"
    )
    return engine

def load_dataframes():
    """Load both tables from PostgreSQL into pandas DataFrames."""
    engine = get_engine()

    car_df = pd.read_sql('SELECT * FROM car_catalog', engine)
    listing_df = pd.read_sql('SELECT * FROM car_listing', engine)

    return car_df, listing_df


def get_all_cars():
    """Return all cars as list of dicts."""
    car_df, _ = load_dataframes()
    return car_df.to_dict(orient='records')


def get_all_listings():
    """Return all listings joined with car details."""
    car_df, listing_df = load_dataframes()

    merged = listing_df.merge(car_df, left_on='car_id', right_on='id', suffixes=('_listing', '_car'))
    return merged.to_dict(orient='records')


def get_fuel_type_stats():
    """Count, avg price, min/max price grouped by fuel type."""
    car_df, _ = load_dataframes()

    stats = car_df.groupby('fuel_type').agg(
        count=('id', 'count'),
        avg_price=('price', 'mean'),
        min_price=('price', 'min'),
        max_price=('price', 'max'),
    ).reset_index()

    stats['avg_price'] = stats['avg_price'].round(2)
    return stats.to_dict(orient='records')


def get_cars_by_fuel_type(fuel_type):
    """All cars and owner details for a given fuel type."""
    car_df, listing_df = load_dataframes()

    filtered_cars = car_df[car_df['fuel_type'] == fuel_type]

    if filtered_cars.empty:
        return []

    merged = filtered_cars.merge(listing_df, left_on='id', right_on='car_id', suffixes=('_car', '_listing'))

    result = []
    for car_id, group in merged.groupby('id_car'):
        car_row = group.iloc[0]
        result.append({
            'car': {
                'id': int(car_row['id_car']),
                'brand': car_row['brand'],
                'model_name': car_row['model_name'],
                'year': int(car_row['year']),
                'fuel_type': car_row['fuel_type'],
                'transmission': car_row['transmission'],
                'price': float(car_row['price']),
            },
            'total_listings': len(group),
            'owners': group[[
                'owner_name', 'contact_number', 'dealer_name',
                'registration_number', 'location', 'listing_price',
                'status', 'odometer_reading_km',
            ]].to_dict(orient='records'),
        })

    return result


def get_listing_status_stats():
    """Count and avg price grouped by listing status."""
    _, listing_df = load_dataframes()

    stats = listing_df.groupby('status').agg(
        count=('id', 'count'),
        avg_price=('listing_price', 'mean'),
    ).reset_index()

    stats['avg_price'] = stats['avg_price'].round(2)
    return stats.to_dict(orient='records')


def search_owners(owner_name=None, location=None, registration_number=None):
    """Search owner details by name, location or registration number."""
    car_df, listing_df = load_dataframes()

    merged = listing_df.merge(car_df, left_on='car_id', right_on='id', suffixes=('_listing', '_car'))

    if owner_name:
        merged = merged[merged['owner_name'].str.contains(owner_name, case=False, na=False)]
    if location:
        merged = merged[merged['location'].str.contains(location, case=False, na=False)]
    if registration_number:
        merged = merged[merged['registration_number'].str.contains(registration_number, case=False, na=False)]

    return merged.to_dict(orient='records')


def filter_cars(fuel_type=None, transmission=None, brand=None, year=None,
                min_price=None, max_price=None, seating_capacity=None):
    """Filter cars with multiple optional params."""
    car_df, _ = load_dataframes()

    if fuel_type:
        car_df = car_df[car_df['fuel_type'] == fuel_type]
    if transmission:
        car_df = car_df[car_df['transmission'] == transmission]
    if brand:
        car_df = car_df[car_df['brand'].str.contains(brand, case=False, na=False)]
    if year:
        car_df = car_df[car_df['year'] == int(year)]
    if min_price:
        car_df = car_df[car_df['price'] >= float(min_price)]
    if max_price:
        car_df = car_df[car_df['price'] <= float(max_price)]
    if seating_capacity:
        car_df = car_df[car_df['seating_capacity'] == int(seating_capacity)]

    return car_df.to_dict(orient='records')


def filter_listings(status=None, location=None, fuel_type=None,
                    owner_name=None, dealer_name=None,
                    min_price=None, max_price=None):
    """Filter listings with multiple optional params."""
    car_df, listing_df = load_dataframes()

    merged = listing_df.merge(car_df, left_on='car_id', right_on='id', suffixes=('_listing', '_car'))

    if status:
        merged = merged[merged['status'] == status]
    if location:
        merged = merged[merged['location'].str.contains(location, case=False, na=False)]
    if fuel_type:
        merged = merged[merged['fuel_type'] == fuel_type]
    if owner_name:
        merged = merged[merged['owner_name'].str.contains(owner_name, case=False, na=False)]
    if dealer_name:
        merged = merged[merged['dealer_name'].str.contains(dealer_name, case=False, na=False)]
    if min_price:
        merged = merged[merged['listing_price'] >= float(min_price)]
    if max_price:
        merged = merged[merged['listing_price'] <= float(max_price)]

    return merged.to_dict(orient='records')