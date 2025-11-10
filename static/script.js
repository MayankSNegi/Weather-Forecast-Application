// DOM Elements
const cityInput = document.getElementById('cityInput');
const searchBtn = document.getElementById('searchBtn');
const errorMsg = document.getElementById('errorMsg');
const loadingMsg = document.getElementById('loadingMsg');
const currentWeatherContainer = document.getElementById('currentWeatherContainer');
const forecastContainer = document.getElementById('forecastContainer');

// Event Listeners
searchBtn.addEventListener('click', handleSearch);
cityInput.addEventListener('keypress', (e) => {
    if (e.key === 'Enter') {
        handleSearch();
    }
});

/**
 * Handle search button click
 */
function handleSearch() {
    const city = cityInput.value.trim();
    
    if (!city) {
        showError('Please enter a city name');
        return;
    }
    
    fetchWeather(city);
}

/**
 * Fetch weather data from backend
 */
async function fetchWeather(city) {
    clearMessages();
    showLoading(`Fetching weather for ${city}...`);
    
    try {
        const response = await fetch(`/weather?city=${encodeURIComponent(city)}`);
        const data = await response.json();
        
        if (!response.ok) {
            showError(data.error || 'An error occurred');
            return;
        }
        
        displayCurrentWeather(data);
        displayForecast(data.forecast);
        clearMessages();
        
    } catch (error) {
        showError('Failed to fetch weather data. Please try again.');
        console.error('Error:', error);
    }
}

/**
 * Display current weather
 */
function displayCurrentWeather(data) {
    const current = data.current;
    
    document.getElementById('cityName').textContent = 
        `${data.city}, ${data.country}`;
    document.getElementById('weatherDescription').textContent = 
        current.description;
    document.getElementById('currentTemp').textContent = 
        `${current.temperature}°`;
    document.getElementById('feelsLike').textContent = 
        current.feels_like;
    document.getElementById('humidity').textContent = 
        `${current.humidity}%`;
    document.getElementById('windSpeed').textContent = 
        `${current.wind_speed} m/s`;
    document.getElementById('pressure').textContent = 
        `${current.pressure} hPa`;
    document.getElementById('uvi').textContent = 
        current.uvi;
    
    // Set weather icon
    const iconUrl = `https://openweathermap.org/img/wn/${current.icon}@4x.png`;
    document.getElementById('weatherIcon').src = iconUrl;
    document.getElementById('weatherIcon').alt = current.description;
    
    // Show container
    currentWeatherContainer.classList.remove('hidden');
}

/**
 * Display 7-day forecast
 */
function displayForecast(forecast) {
    const forecastCards = document.getElementById('forecastCards');
    forecastCards.innerHTML = '';
    
    forecast.forEach((day) => {
        const date = new Date(day.date * 1000);
        const dayName = date.toLocaleDateString('en-US', { weekday: 'short' });
        const dateStr = date.toLocaleDateString('en-US', { month: 'short', day: 'numeric' });
        
        const iconUrl = `https://openweathermap.org/img/wn/${day.icon}@2x.png`;
        
        const card = document.createElement('div');
        card.className = 'forecast-card';
        card.innerHTML = `
            <div class="forecast-date">${dayName}<br>${dateStr}</div>
            <img src="${iconUrl}" alt="${day.description}" class="forecast-icon">
            <div class="forecast-description">${day.description}</div>
            <div class="forecast-temps">
                <span class="temp-max">${day.temp_max}°</span>
                <span class="temp-min">${day.temp_min}°</span>
            </div>
            <div class="forecast-humidity">💧 ${day.humidity}%</div>
            <div class="forecast-rain">🌧️ ${day.rain_chance}%</div>
        `;
        
        forecastCards.appendChild(card);
    });
    
    forecastContainer.classList.remove('hidden');
}

/**
 * Show error message
 */
function showError(message) {
    errorMsg.textContent = `❌ ${message}`;
    errorMsg.classList.add('show');
    loadingMsg.classList.remove('show');
}

/**
 * Show loading message
 */
function showLoading(message) {
    loadingMsg.textContent = `⏳ ${message}`;
    loadingMsg.classList.add('show');
    errorMsg.classList.remove('show');
}

/**
 * Clear all messages
 */
function clearMessages() {
    errorMsg.classList.remove('show');
    loadingMsg.classList.remove('show');
}

// Load default city on page load
window.addEventListener('load', () => {
    cityInput.value = 'London';
    fetchWeather('London');
});