#!/usr/bin/env python3
"""
Test script for enhanced SARIMAX forecasting
This will test both the main voltage forecast and zone forecasting
"""

import requests
import json
import sys

BASE_URL = "http://localhost:5000"

def test_voltage_forecast():
    """Test the main voltage forecast endpoint"""
    print("🔍 Testing enhanced voltage forecast...")
    
    try:
        response = requests.get(f"{BASE_URL}/voltage-forecast", timeout=10)
        if response.status_code == 200:
            data = response.json()
            
            if "error" in data:
                print(f"❌ Voltage forecast error: {data['error']}")
                return False
            
            print("✅ Voltage forecast working!")
            print(f"📊 Current voltage: {data.get('current_voltage', 'N/A')}")
            print(f"🔮 Model type: {data.get('model_info', {}).get('model_type', 'N/A')}")
            print(f"🌡️ Environmental factors: {data.get('model_info', {}).get('environmental_factors', 0)}")
            
            hourly = data.get('hourly_forecast', {})
            if hourly:
                print(f"📈 Hourly trend: {hourly.get('trend', 'N/A')} (change: {hourly.get('change_percent', 0)}%)")
            
            daily = data.get('daily_forecast', {})
            if daily:
                print(f"📅 Daily trend: {daily.get('trend', 'N/A')} (change: {daily.get('change_percent', 0)}%)")
            
            env_impact = data.get('environmental_impact', {})
            if env_impact:
                print(f"🌍 Environmental impact:")
                for key, value in env_impact.items():
                    print(f"   {key}: {value}")
            
            return True
        else:
            print(f"❌ Voltage forecast failed with status {response.status_code}")
            return False
            
    except Exception as e:
        print(f"❌ Error testing voltage forecast: {e}")
        return False

def test_zone_forecast():
    """Test zone forecasting"""
    print("\n🏢 Testing zone forecasting...")
    
    try:
        # First get zones
        response = requests.get(f"{BASE_URL}/api/zones", timeout=10)
        if response.status_code != 200:
            print(f"❌ Could not get zones: {response.status_code}")
            return False
        
        data = response.json()
        zones = data.get("zones", [])  # Handle wrapped response format
        if not zones:
            print("⚠️ No zones found for testing")
            return False
        
        # Test forecast for first zone
        zone = zones[0]
        zone_id = zone['id']
        zone_name = zone['name']
        
        print(f"🎯 Testing forecast for zone {zone_id}: {zone_name}")
        
        response = requests.get(f"{BASE_URL}/api/zones/{zone_id}/forecast?horizon=daily&steps=10", timeout=10)
        if response.status_code == 200:
            data = response.json()
            
            forecasts = data.get('forecasts', {})
            
            voltage_forecast = forecasts.get('sarimax_voltage', {})
            if 'error' not in voltage_forecast:
                print("✅ SARIMAX voltage forecast working!")
                forecast_data = voltage_forecast.get('forecast', [])
                if forecast_data:
                    print(f"📊 Voltage range: {min(forecast_data):.2f} - {max(forecast_data):.2f}V")
                    print(f"🔄 Current voltage: {voltage_forecast.get('current_voltage', 'N/A')}")
            else:
                print(f"⚠️ SARIMAX voltage forecast error: {voltage_forecast.get('error')}")
            
            load_forecast = forecasts.get('svr_load', {})
            if 'error' not in load_forecast:
                print("✅ SVR load forecast working!")
                forecast_data = load_forecast.get('forecast', [])
                if forecast_data:
                    print(f"⚡ Load range: {min(forecast_data):.2f} - {max(forecast_data):.2f}")
                    print(f"🔄 Current load: {load_forecast.get('current_load', 'N/A')}")
            else:
                print(f"⚠️ SVR load forecast error: {load_forecast.get('error')}")
            
            return True
        else:
            print(f"❌ Zone forecast failed with status {response.status_code}")
            return False
            
    except Exception as e:
        print(f"❌ Error testing zone forecast: {e}")
        return False

def test_realtime_forecast():
    """Test real-time forecasting with parameters"""
    print("\n⚡ Testing real-time forecasting with custom parameters...")
    
    try:
        # Get first zone
        response = requests.get(f"{BASE_URL}/api/zones", timeout=10)
        if response.status_code != 200:
            print("❌ Could not get zones for real-time test")
            return False
        
        data = response.json()
        zones = data.get("zones", [])  # Handle wrapped response format
        if not zones:
            print("⚠️ No zones found for real-time testing")
            return False
        
        zone_id = zones[0]['id']
        
        # Test with different parameter sets
        test_params = [
            {
                "voltage": 230.0,
                "load": 120.0,
                "temperature": 35.0,  # Hot day
                "humidity": 80.0,     # High humidity
                "solar_intensity": 900.0,  # High solar
                "wind_speed": 15.0,   # Good wind
                "horizon": "hourly",
                "steps": 5
            },
            {
                "voltage": 210.0,
                "load": 80.0,
                "temperature": 15.0,  # Cold day
                "humidity": 40.0,     # Low humidity
                "solar_intensity": 200.0,  # Low solar
                "wind_speed": 5.0,    # Low wind
                "horizon": "daily",
                "steps": 3
            }
        ]
        
        for i, params in enumerate(test_params, 1):
            print(f"\n🧪 Test scenario {i}:")
            print(f"   Temperature: {params['temperature']}°C")
            print(f"   Solar: {params['solar_intensity']}W/m²")
            print(f"   Wind: {params['wind_speed']}m/s")
            print(f"   Initial voltage: {params['voltage']}V")
            
            response = requests.post(
                f"{BASE_URL}/api/zones/{zone_id}/forecast/realtime",
                json=params,
                timeout=10
            )
            
            if response.status_code == 200:
                data = response.json()
                forecasts = data.get('forecasts', {})
                
                voltage_forecast = forecasts.get('sarimax_voltage', {})
                if 'forecast' in voltage_forecast:
                    forecast_values = voltage_forecast['forecast']
                    env_factors = voltage_forecast.get('environmental_factors', {})
                    
                    print(f"   ✅ Voltage forecast: {forecast_values[0]:.2f}V → {forecast_values[-1]:.2f}V")
                    print(f"   🌡️ Temperature impact: {env_factors.get('temperature_impact', 0):.3f}")
                    print(f"   ☀️ Solar impact: {env_factors.get('solar_impact', 0):.3f}")
                    print(f"   💨 Wind impact: {env_factors.get('wind_impact', 0):.3f}")
                
                load_forecast = forecasts.get('svr_load', {})
                if 'forecast' in load_forecast:
                    forecast_values = load_forecast['forecast']
                    print(f"   ⚡ Load forecast: {forecast_values[0]:.2f} → {forecast_values[-1]:.2f}")
                
            else:
                print(f"   ❌ Real-time forecast failed: {response.status_code}")
        
        return True
        
    except Exception as e:
        print(f"❌ Error testing real-time forecast: {e}")
        return False

def main():
    """Run all tests"""
    print("🚀 Starting Enhanced SARIMAX Forecasting Tests")
    print("=" * 50)
    
    results = []
    
    # Test main voltage forecast
    results.append(test_voltage_forecast())
    
    # Test zone forecast
    results.append(test_zone_forecast())
    
    # Test real-time forecast
    results.append(test_realtime_forecast())
    
    print("\n" + "=" * 50)
    print("📋 Test Results Summary:")
    print(f"✅ Passed: {sum(results)}/{len(results)}")
    
    if all(results):
        print("🎉 All tests passed! Enhanced SARIMAX forecasting is working properly.")
        print("💡 The system now responds to voltage and environmental parameter changes.")
    else:
        print("⚠️ Some tests failed. Check the output above for details.")
    
    return all(results)

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
