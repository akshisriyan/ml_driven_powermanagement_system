#!/usr/bin/env python3
"""
Simple test for zone forecasting
"""

import requests
import json

def test_zones():
    print("Testing zones endpoint...")
    try:
        response = requests.get("http://localhost:5000/api/zones", timeout=5)
        print(f"Zones status: {response.status_code}")
        if response.status_code == 200:
            data = response.json()
            zones = data.get("zones", [])  # Handle wrapped response
            print(f"Number of zones: {len(zones)}")
            if zones and len(zones) > 0:
                print(f"First zone: {zones[0]}")
                return zones[0]['id']
            else:
                print("No zones in response")
                return None
        else:
            print(f"Bad status: {response.text}")
            return None
    except Exception as e:
        print(f"Zones error: {e}")
        return None

def test_zone_forecast(zone_id):
    print(f"\nTesting zone {zone_id} forecast...")
    try:
        url = f"http://localhost:5000/api/zones/{zone_id}/forecast?horizon=daily&steps=5"
        print(f"URL: {url}")
        response = requests.get(url, timeout=10)
        print(f"Forecast status: {response.status_code}")
        
        if response.status_code == 200:
            data = response.json()
            print("✅ Zone forecast working!")
            print(f"Zone name: {data.get('zone_name')}")
            
            forecasts = data.get('forecasts', {})
            voltage = forecasts.get('sarimax_voltage', {})
            load = forecasts.get('svr_load', {})
            
            print(f"Voltage forecast: {voltage.get('forecast', [])[:3]}...")
            print(f"Load forecast: {load.get('forecast', [])[:3]}...")
            print(f"Current voltage: {voltage.get('current_voltage')}")
            print(f"Current load: {load.get('current_load')}")
            return True
        else:
            print(f"❌ Status {response.status_code}: {response.text}")
            return False
            
    except Exception as e:
        print(f"❌ Forecast error: {e}")
        return False

def test_realtime_forecast(zone_id):
    print(f"\nTesting real-time forecast for zone {zone_id}...")
    try:
        url = f"http://localhost:5000/api/zones/{zone_id}/forecast/realtime"
        params = {
            "voltage": 225.0,
            "load": 100.0,
            "temperature": 30.0,
            "humidity": 70.0,
            "solar_intensity": 700.0,
            "wind_speed": 12.0,
            "horizon": "hourly",
            "steps": 3
        }
        
        response = requests.post(url, json=params, timeout=10)
        print(f"Real-time status: {response.status_code}")
        
        if response.status_code == 200:
            data = response.json()
            print("✅ Real-time forecast working!")
            print(f"Input voltage: {data.get('input_parameters', {}).get('voltage')}")
            
            forecasts = data.get('forecasts', {})
            voltage = forecasts.get('sarimax_voltage', {})
            print(f"Voltage forecast: {voltage.get('forecast', [])}")
            return True
        else:
            print(f"❌ Status {response.status_code}: {response.text}")
            return False
            
    except Exception as e:
        print(f"❌ Real-time error: {e}")
        return False

if __name__ == "__main__":
    print("🚀 Simple Zone Forecast Test")
    print("=" * 40)
    
    zone_id = test_zones()
    if zone_id:
        success1 = test_zone_forecast(zone_id)
        success2 = test_realtime_forecast(zone_id)
        
        print("\n" + "=" * 40)
        print(f"Results: Zone forecast: {'✅' if success1 else '❌'}, Real-time: {'✅' if success2 else '❌'}")
    else:
        print("❌ Could not get zones for testing")
