from flask import Flask, render_template, request, jsonify
import requests
import os
from dotenv import load_dotenv
from datetime import datetime, timedelta

load_dotenv()

app = Flask(__name__)

# OpenWeatherMap API Configuration
# Load API key from file safely
try:
    with open('api_key.txt', 'r') as file:
        API_KEY = file.read().strip()
except FileNotFoundError:
    API_KEY = None
    print("⚠️ API key file not found! Please create 'api_key.txt' with your key.")
BASE_URL = "https://api.openweathermap.org/data/2.5"

@app.route('/')
def index():
    """Render the main page"""
    return render_template('index.html')

@app.route('/weather', methods=['GET'])
def get_weather():
    """
    Fetch weather and 5-day forecast for a city using FREE API
    Query params: city (required)
    """
    city = request.args.get('city', '').strip()
    
    # Validation
    if not city:
        return jsonify({'error': 'City name is required'}), 400
    
    if not API_KEY:
        print("ERROR: API key not set!")
        return jsonify({'error': 'API key not configured. Please set OPENWEATHER_API_KEY environment variable.'}), 500
    
    try:
        print(f"\n📍 Searching for city: {city}")
        
        # Step 1: Get current weather
        weather_url = f"{BASE_URL}/weather"
        weather_params = {
            'q': city,
            'appid': API_KEY,
            'units': 'metric'
        }
        
        print(f"🌤️ Calling Weather API: {weather_url}")
        weather_response = requests.get(weather_url, params=weather_params, timeout=5)
        print(f"Weather Response Status: {weather_response.status_code}")
        
        if weather_response.status_code == 404:
            print(f"❌ City '{city}' not found")
            return jsonify({'error': f'City "{city}" not found. Please check spelling.'}), 404
        
        weather_response.raise_for_status()
        
        weather_data = weather_response.json()
        print(f"✅ Current weather data received")
        
        # Extract current weather info
        current = weather_data
        lat = current['coord']['lat']
        lon = current['coord']['lon']
        city_name = current['name']
        country = current.get('sys', {}).get('country', '')
        
        print(f"✅ Found: {city_name}, {country} (Lat: {lat}, Lon: {lon})")
        
        # Step 2: Get 5-day forecast (FREE endpoint)
        forecast_url = f"{BASE_URL}/forecast"
        forecast_params = {
            'lat': lat,
            'lon': lon,
            'appid': API_KEY,
            'units': 'metric'
        }
        
        print(f"📅 Calling 5-Day Forecast API: {forecast_url}")
        forecast_response = requests.get(forecast_url, params=forecast_params, timeout=5)
        print(f"Forecast Response Status: {forecast_response.status_code}")
        
        forecast_response.raise_for_status()
        
        forecast_data = forecast_response.json()
        print(f"✅ Forecast data received successfully")
        
        # Process current weather
        current_weather = {
            'temperature': round(current['main']['temp']),
            'feels_like': round(current['main']['feels_like']),
            'humidity': current['main']['humidity'],
            'pressure': current['main']['pressure'],
            'wind_speed': round(current['wind']['speed'], 1),
            'description': current['weather'][0]['main'],
            'icon': current['weather'][0]['icon'],
            'uvi': 0,  # Not available in free tier
        }
        
        # Process 5-day forecast (group by day)
        daily_forecast = {}
        for forecast_item in forecast_data['list']:
            dt = datetime.fromtimestamp(forecast_item['dt'])
            day_key = dt.strftime('%Y-%m-%d')
            
            # Store only one entry per day (noon time)
            if day_key not in daily_forecast:
                daily_forecast[day_key] = {
                    'date': forecast_item['dt'],
                    'temp_max': forecast_item['main']['temp_max'],
                    'temp_min': forecast_item['main']['temp_min'],
                    'humidity': forecast_item['main']['humidity'],
                    'description': forecast_item['weather'][0]['main'],
                    'icon': forecast_item['weather'][0]['icon'],
                    'wind_speed': round(forecast_item['wind']['speed'], 1),
                    'rain_chance': round(forecast_item.get('pop', 0) * 100)
                }
            else:
                # Update min/max temps
                daily_forecast[day_key]['temp_max'] = max(
                    daily_forecast[day_key]['temp_max'],
                    forecast_item['main']['temp_max']
                )
                daily_forecast[day_key]['temp_min'] = min(
                    daily_forecast[day_key]['temp_min'],
                    forecast_item['main']['temp_min']
                )
        
        # Convert to list and take first 7 days
        forecast_list = sorted(daily_forecast.values(), key=lambda x: x['date'])[:7]
        
        print(f"✅ All data processed successfully\n")
        
        return jsonify({
            'success': True,
            'city': city_name,
            'country': country,
            'current': current_weather,
            'forecast': forecast_list
        }), 200
    
    except requests.exceptions.Timeout:
        print("❌ Request timeout")
        return jsonify({'error': 'Request timeout. Please try again.'}), 500
    except requests.exceptions.HTTPError as e:
        print(f"❌ HTTP Error: {e.response.status_code}")
        print(f"Response: {e.response.text}")
        if e.response.status_code == 401:
            return jsonify({'error': 'Invalid API key. Please check your OPENWEATHER_API_KEY.'}), 401
        elif e.response.status_code == 404:
            return jsonify({'error': 'City not found. Please check spelling.'}), 404
        return jsonify({'error': f'API error: {e.response.status_code}'}), 500
    except Exception as e:
        print(f"❌ Exception: {str(e)}")
        import traceback
        traceback.print_exc()
        return jsonify({'error': f'An error occurred: {str(e)}'}), 500

@app.errorhandler(404)
def not_found(error):
    """Handle 404 errors"""
    return jsonify({'error': 'Endpoint not found'}), 404

if __name__ == '__main__':
    print("\n" + "="*50)
    print("🌤️  WEATHER APP STARTING...")
    print("="*50)
    print(f"API Key loaded: {'✅ YES' if API_KEY else '❌ NO'}")
    print(f"Base URL: {BASE_URL}")
    print("Using FREE tier APIs (Weather + 5-Day Forecast)")
    print("="*50 + "\n")
    app.run(debug=True, port=5000)