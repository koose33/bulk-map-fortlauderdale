#!/usr/bin/env python3
"""
Extract individual city zone files from Broward County official boundaries.
This script reads Broward_County_Cities.geojson and creates individual zone files
for each city with their bulk pickup schedules.
"""

import json
import sys

# City schedules and zone configurations
CITY_CONFIGS = {
    "OAKLAND PARK": {
        "zones": [
            {"name": "1st Monday", "schedule_2025": "Jan 6, Feb 3, Mar 3, Apr 7, May 5, Jun 2, Jul 7, Aug 4, Sep 1, Oct 6, Nov 3, Dec 1"},
            {"name": "2nd Monday", "schedule_2025": "Jan 13, Feb 10, Mar 10, Apr 14, May 12, Jun 9, Jul 14, Aug 11, Sep 8, Oct 13, Nov 10, Dec 8"},
            {"name": "3rd Monday", "schedule_2025": "Jan 20, Feb 17, Mar 17, Apr 21, May 19, Jun 16, Jul 21, Aug 18, Sep 15, Oct 20, Nov 17, Dec 15"},
            {"name": "4th Monday", "schedule_2025": "Jan 27, Feb 24, Mar 24, Apr 28, May 26, Jun 23, Jul 28, Aug 25, Sep 22, Oct 27, Nov 24, Dec 22"}
        ],
        "divide": "quadrants",  # Divide city into 4 equal parts
        "filename": "oakland-park-zones.geojson"
    },
    "POMPANO BEACH": {
        "zones": [
            {"name": "Monday & Thursday", "schedule_2025": "Weekly - Every Monday and Thursday"},
            {"name": "Tuesday & Friday", "schedule_2025": "Weekly - Every Tuesday and Friday"},
            {"name": "Wednesday & Saturday", "schedule_2025": "Weekly - Every Wednesday and Saturday"}
        ],
        "divide": "thirds",  # Divide city into 3 equal parts
        "filename": "pompano-beach-zones.geojson"
    },
    "SUNRISE": {
        "zones": [{"name": "City-wide", "schedule_2025": "Weekly bulk pickup - follows regular trash schedule"}],
        "divide": "whole",
        "filename": "sunrise-zones.geojson"
    },
    "DAVIE": {
        "zones": [{"name": "City-wide", "schedule_2025": "Monthly bulk pickup"}],
        "divide": "whole",
        "filename": "davie-zones.geojson"
    },
    "HOLLYWOOD": {
        "zones": [{"name": "City-wide", "schedule_2025": "Monthly bulk pickup"}],
        "divide": "whole",
        "filename": "hollywood-zones.geojson"
    },
    "PEMBROKE PINES": {
        "zones": [{"name": "City-wide", "schedule_2025": "Twice monthly bulk pickup"}],
        "divide": "whole",
        "filename": "pembroke-pines-zones.geojson"
    },
    "CORAL SPRINGS": {
        "zones": [{"name": "City-wide", "schedule_2025": "Weekly bulk pickup"}],
        "divide": "whole",
        "filename": "coral-springs-zones.geojson"
    },
    "PLANTATION": {
        "zones": [{"name": "City-wide", "schedule_2025": "Weekly bulk pickup"}],
        "divide": "whole",
        "filename": "plantation-zones.geojson"
    },
    "MIRAMAR": {
        "zones": [{"name": "City-wide", "schedule_2025": "Weekly bulk pickup"}],
        "divide": "whole",
        "filename": "miramar-zones.geojson"
    },
    "LAUDERHILL": {
        "zones": [{"name": "City-wide", "schedule_2025": "Weekly bulk pickup"}],
        "divide": "whole",
        "filename": "lauderhill-zones.geojson"
    },
    "TAMARAC": {
        "zones": [{"name": "City-wide", "schedule_2025": "Weekly bulk pickup"}],
        "divide": "whole",
        "filename": "tamarac-zones.geojson"
    },
    "COCONUT CREEK": {
        "zones": [{"name": "City-wide", "schedule_2025": "Weekly bulk pickup"}],
        "divide": "whole",
        "filename": "coconut-creek-zones.geojson"
    },
    "DEERFIELD BEACH": {
        "zones": [{"name": "City-wide", "schedule_2025": "Weekly bulk pickup"}],
        "divide": "whole",
        "filename": "deerfield-beach-zones.geojson"
    }
}

def divide_geometry_quadrants(geometry):
    """Divide a polygon geometry into 4 equal quadrants"""
    coords = geometry['coordinates'][0]
    
    # Find bounding box
    lons = [p[0] for p in coords]
    lats = [p[1] for p in coords]
    min_lon, max_lon = min(lons), max(lons)
    min_lat, max_lat = min(lats), max(lats)
    mid_lon = (min_lon + max_lon) / 2
    mid_lat = (min_lat + max_lat) / 2
    
    # Create 4 quadrants
    quadrants = [
        {  # NW
            "type": "Polygon",
            "coordinates": [[[min_lon, mid_lat], [mid_lon, mid_lat], [mid_lon, max_lat], [min_lon, max_lat], [min_lon, mid_lat]]]
        },
        {  # NE
            "type": "Polygon",
            "coordinates": [[[mid_lon, mid_lat], [max_lon, mid_lat], [max_lon, max_lat], [mid_lon, max_lat], [mid_lon, mid_lat]]]
        },
        {  # SW
            "type": "Polygon",
            "coordinates": [[[min_lon, min_lat], [mid_lon, min_lat], [mid_lon, mid_lat], [min_lon, mid_lat], [min_lon, min_lat]]]
        },
        {  # SE
            "type": "Polygon",
            "coordinates": [[[mid_lon, min_lat], [max_lon, min_lat], [max_lon, mid_lat], [mid_lon, mid_lat], [mid_lon, min_lat]]]
        }
    ]
    return quadrants

def divide_geometry_thirds(geometry):
    """Divide a polygon geometry into 3 equal vertical strips"""
    coords = geometry['coordinates'][0]
    
    # Find bounding box
    lons = [p[0] for p in coords]
    lats = [p[1] for p in coords]
    min_lon, max_lon = min(lons), max(lons)
    min_lat, max_lat = min(lats), max(lats)
    third = (max_lon - min_lon) / 3
    
    # Create 3 vertical strips
    thirds = [
        {
            "type": "Polygon",
            "coordinates": [[[min_lon, min_lat], [min_lon + third, min_lat], [min_lon + third, max_lat], [min_lon, max_lat], [min_lon, min_lat]]]
        },
        {
            "type": "Polygon",
            "coordinates": [[[min_lon + third, min_lat], [min_lon + 2*third, min_lat], [min_lon + 2*third, max_lat], [min_lon + third, max_lat], [min_lon + third, min_lat]]]
        },
        {
            "type": "Polygon",
            "coordinates": [[[min_lon + 2*third, min_lat], [max_lon, min_lat], [max_lon, max_lat], [min_lon + 2*third, max_lat], [min_lon + 2*third, min_lat]]]
        }
    ]
    return thirds

def extract_city(broward_data, city_name, config):
    """Extract a city from Broward data and create zone file"""
    
    # Find the city in Broward data
    city_feature = None
    for feature in broward_data['features']:
        if feature['properties'].get('CITYNAME', '').upper() == city_name.upper():
            city_feature = feature
            break
    
    if not city_feature:
        print(f"❌ City not found: {city_name}")
        return None
    
    print(f"✅ Found {city_name}")
    
    # Create zone features
    zones_features = []
    geometry = city_feature['geometry']
    
    if config['divide'] == 'whole':
        # Use entire city boundary as one zone
        for zone_info in config['zones']:
            zone_feature = {
                "type": "Feature",
                "properties": {
                    "CITYNAME": city_name.title(),
                    "name": zone_info['name'],
                    "schedule_2025": zone_info['schedule_2025']
                },
                "geometry": geometry
            }
            zones_features.append(zone_feature)
    
    elif config['divide'] == 'quadrants':
        # Divide into 4 quadrants
        quadrants = divide_geometry_quadrants(geometry)
        for i, zone_info in enumerate(config['zones']):
            zone_feature = {
                "type": "Feature",
                "properties": {
                    "CITYNAME": city_name.title(),
                    "BULKDAY": zone_info['name'],
                    "schedule_2025": zone_info['schedule_2025']
                },
                "geometry": quadrants[i]
            }
            zones_features.append(zone_feature)
    
    elif config['divide'] == 'thirds':
        # Divide into 3 strips
        thirds = divide_geometry_thirds(geometry)
        for i, zone_info in enumerate(config['zones']):
            zone_feature = {
                "type": "Feature",
                "properties": {
                    "CITYNAME": city_name.title(),
                    "pickup_day": zone_info['name'],
                    "schedule_2025": zone_info['schedule_2025']
                },
                "geometry": thirds[i]
            }
            zones_features.append(zone_feature)
    
    # Create GeoJSON
    zone_geojson = {
        "type": "FeatureCollection",
        "features": zones_features
    }
    
    return zone_geojson

def main():
    # Load Broward County data
    print("Loading Broward_County_Cities.geojson...")
    try:
        with open('Broward_County_Cities.geojson', 'r') as f:
            broward_data = json.load(f)
    except FileNotFoundError:
        print("❌ Error: Broward_County_Cities.geojson not found!")
        print("   Make sure this script is in the same directory as the GeoJSON file.")
        sys.exit(1)
    
    print(f"✅ Loaded {len(broward_data['features'])} cities from Broward County\n")
    
    # Extract each city
    print("Extracting cities...\n")
    for city_name, config in CITY_CONFIGS.items():
        zone_data = extract_city(broward_data, city_name, config)
        if zone_data:
            filename = config['filename']
            with open(filename, 'w') as f:
                json.dump(zone_data, f, indent=2)
            print(f"   📄 Created {filename}")
    
    print(f"\n✅ Done! Created {len(CITY_CONFIGS)} city zone files")
    print("\nNext steps:")
    print("1. Upload all .geojson files to your GitHub repo")
    print("2. Update index.html to load these cities")

if __name__ == "__main__":
    main()
