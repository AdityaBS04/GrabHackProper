"""
API Integration Utilities for Grab Food Orchestration
Provides Google Maps API and Weather API integration for predictive analysis
"""

import os
import requests
import logging
from typing import Dict, Any, Optional, Tuple, List
from dataclasses import dataclass
from datetime import datetime, timedelta
import json
import asyncio
import aiohttp

logger = logging.getLogger(__name__)

@dataclass
class LocationData:
    """Location information for API calls"""
    latitude: float
    longitude: float
    address: str
    place_id: Optional[str] = None

@dataclass
class TrafficData:
    """Traffic analysis data"""
    current_delay: int  # minutes
    traffic_density: str  # light, moderate, heavy, severe
    alternative_routes: List[Dict[str, Any]]
    estimated_duration: int  # minutes
    distance: float  # km
    suggested_departure_time: Optional[datetime] = None

@dataclass
class WeatherData:
    """Weather information for delivery predictions"""
    temperature: float  # celsius
    condition: str  # clear, rain, snow, etc
    precipitation_probability: float  # 0-1
    wind_speed: float  # km/h
    visibility: float  # km
    weather_impact_score: float  # 0-1 (1 = severe impact)


class GoogleMapsAPI:
    """Google Maps API integration for route optimization and traffic analysis"""
    
    def __init__(self, api_key: str = None):
        self.api_key = api_key or os.getenv('GOOGLE_MAPS_API_KEY')
        self.base_url = "https://maps.googleapis.com/maps/api"
        
        if not self.api_key:
            logger.warning("Google Maps API key not provided. Using mock data.")
            self.use_mock = True
        else:
            self.use_mock = False
    
    async def get_traffic_data(self, origin: LocationData, destination: LocationData) -> TrafficData:
        """Get real-time traffic data between two locations"""
        if self.use_mock:
            return self._get_mock_traffic_data()
        
        try:
            # Directions API with traffic model
            directions_url = f"{self.base_url}/directions/json"
            params = {
                'origin': f"{origin.latitude},{origin.longitude}",
                'destination': f"{destination.latitude},{destination.longitude}",
                'departure_time': 'now',
                'traffic_model': 'best_guess',
                'key': self.api_key
            }
            
            async with aiohttp.ClientSession() as session:
                async with session.get(directions_url, params=params) as response:
                    if response.status == 200:
                        data = await response.json()
                        return self._parse_traffic_data(data)
                    else:
                        logger.error(f"Google Maps API error: {response.status}")
                        return self._get_mock_traffic_data()
        
        except Exception as e:
            logger.error(f"Error getting traffic data: {str(e)}")
            return self._get_mock_traffic_data()
    
    async def get_alternative_routes(self, origin: LocationData, destination: LocationData, avoid_traffic: bool = True) -> List[Dict[str, Any]]:
        """Get alternative routes avoiding traffic"""
        if self.use_mock:
            return self._get_mock_alternative_routes()
        
        try:
            directions_url = f"{self.base_url}/directions/json"
            params = {
                'origin': f"{origin.latitude},{origin.longitude}",
                'destination': f"{destination.latitude},{destination.longitude}",
                'alternatives': 'true',
                'departure_time': 'now',
                'traffic_model': 'best_guess',
                'key': self.api_key
            }
            
            if avoid_traffic:
                params['avoid'] = 'tolls|highways'  # Can be adjusted based on traffic conditions
            
            async with aiohttp.ClientSession() as session:
                async with session.get(directions_url, params=params) as response:
                    if response.status == 200:
                        data = await response.json()
                        return self._parse_alternative_routes(data)
                    else:
                        return self._get_mock_alternative_routes()
        
        except Exception as e:
            logger.error(f"Error getting alternative routes: {str(e)}")
            return self._get_mock_alternative_routes()
    
    async def verify_address(self, address: str) -> Tuple[bool, LocationData]:
        """Verify and geocode an address"""
        if self.use_mock:
            return True, self._get_mock_location_data()
        
        try:
            geocode_url = f"{self.base_url}/geocode/json"
            params = {
                'address': address,
                'key': self.api_key
            }
            
            async with aiohttp.ClientSession() as session:
                async with session.get(geocode_url, params=params) as response:
                    if response.status == 200:
                        data = await response.json()
                        if data['results']:
                            result = data['results'][0]
                            location = result['geometry']['location']
                            return True, LocationData(
                                latitude=location['lat'],
                                longitude=location['lng'],
                                address=result['formatted_address'],
                                place_id=result.get('place_id')
                            )
                        else:
                            return False, None
                    else:
                        return False, None
        
        except Exception as e:
            logger.error(f"Error verifying address: {str(e)}")
            return False, None
    
    async def predict_delivery_time(self, origin: LocationData, destination: LocationData, buffer_minutes: int = 5) -> Dict[str, Any]:
        """Predict accurate delivery time with traffic and route analysis"""
        traffic_data = await self.get_traffic_data(origin, destination)
        
        # Add buffer for pickup/delivery time
        total_time = traffic_data.estimated_duration + buffer_minutes
        
        # Calculate confidence based on traffic conditions
        confidence_map = {
            'light': 0.95,
            'moderate': 0.85,
            'heavy': 0.70,
            'severe': 0.60
        }
        confidence = confidence_map.get(traffic_data.traffic_density, 0.80)
        
        return {
            'estimated_minutes': total_time,
            'confidence': confidence,
            'traffic_delay': traffic_data.current_delay,
            'traffic_condition': traffic_data.traffic_density,
            'suggested_departure': traffic_data.suggested_departure_time,
            'alternative_routes_available': len(traffic_data.alternative_routes) > 0
        }
    
    def _parse_traffic_data(self, api_response: Dict[str, Any]) -> TrafficData:
        """Parse Google Maps API response to TrafficData"""
        if not api_response.get('routes'):
            return self._get_mock_traffic_data()
        
        route = api_response['routes'][0]
        leg = route['legs'][0]
        
        duration = leg['duration']['value'] // 60  # Convert to minutes
        duration_in_traffic = leg.get('duration_in_traffic', {}).get('value', duration * 60) // 60
        
        delay = max(0, duration_in_traffic - duration)
        
        # Determine traffic density based on delay
        if delay < 5:
            density = 'light'
        elif delay < 15:
            density = 'moderate'
        elif delay < 30:
            density = 'heavy'
        else:
            density = 'severe'
        
        return TrafficData(
            current_delay=delay,
            traffic_density=density,
            alternative_routes=[],  # Will be populated by separate call
            estimated_duration=duration_in_traffic,
            distance=leg['distance']['value'] / 1000  # Convert to km
        )
    
    def _parse_alternative_routes(self, api_response: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Parse alternative routes from API response"""
        routes = []
        for route in api_response.get('routes', []):
            leg = route['legs'][0]
            duration = leg['duration']['value'] // 60
            distance = leg['distance']['value'] / 1000
            
            routes.append({
                'duration_minutes': duration,
                'distance_km': distance,
                'summary': route.get('summary', 'Alternative route'),
                'traffic_delay': leg.get('duration_in_traffic', {}).get('value', duration * 60) // 60 - duration
            })
        
        return routes
    
    def _get_mock_traffic_data(self) -> TrafficData:
        """Mock traffic data for testing"""
        return TrafficData(
            current_delay=8,
            traffic_density='moderate',
            alternative_routes=[],
            estimated_duration=25,
            distance=12.5
        )
    
    def _get_mock_alternative_routes(self) -> List[Dict[str, Any]]:
        """Mock alternative routes for testing"""
        return [
            {'duration_minutes': 23, 'distance_km': 11.8, 'summary': 'Via Main Street', 'traffic_delay': 3},
            {'duration_minutes': 28, 'distance_km': 14.2, 'summary': 'Via Highway bypass', 'traffic_delay': 1}
        ]
    
    def _get_mock_location_data(self) -> LocationData:
        """Mock location data for testing"""
        return LocationData(
            latitude=1.3521,
            longitude=103.8198,
            address="Singapore City Center",
            place_id="mock_place_id"
        )


class WeatherAPI:
    """Weather API integration for delivery impact predictions"""
    
    def __init__(self, api_key: str = None):
        self.api_key = api_key or os.getenv('OPENWEATHER_API_KEY')
        self.base_url = "http://api.openweathermap.org/data/2.5"
        
        if not self.api_key:
            logger.warning("Weather API key not provided. Using mock data.")
            self.use_mock = True
        else:
            self.use_mock = False
    
    async def get_current_weather(self, location: LocationData) -> WeatherData:
        """Get current weather data for a location"""
        if self.use_mock:
            return self._get_mock_weather_data()
        
        try:
            weather_url = f"{self.base_url}/weather"
            params = {
                'lat': location.latitude,
                'lon': location.longitude,
                'appid': self.api_key,
                'units': 'metric'
            }
            
            async with aiohttp.ClientSession() as session:
                async with session.get(weather_url, params=params) as response:
                    if response.status == 200:
                        data = await response.json()
                        return self._parse_weather_data(data)
                    else:
                        logger.error(f"Weather API error: {response.status}")
                        return self._get_mock_weather_data()
        
        except Exception as e:
            logger.error(f"Error getting weather data: {str(e)}")
            return self._get_mock_weather_data()
    
    async def get_weather_forecast(self, location: LocationData, hours_ahead: int = 2) -> List[WeatherData]:
        """Get weather forecast for the next few hours"""
        if self.use_mock:
            return [self._get_mock_weather_data() for _ in range(hours_ahead)]
        
        try:
            forecast_url = f"{self.base_url}/forecast"
            params = {
                'lat': location.latitude,
                'lon': location.longitude,
                'appid': self.api_key,
                'units': 'metric',
                'cnt': hours_ahead  # Number of forecast points
            }
            
            async with aiohttp.ClientSession() as session:
                async with session.get(forecast_url, params=params) as response:
                    if response.status == 200:
                        data = await response.json()
                        return [self._parse_weather_data(item) for item in data['list'][:hours_ahead]]
                    else:
                        return [self._get_mock_weather_data() for _ in range(hours_ahead)]
        
        except Exception as e:
            logger.error(f"Error getting weather forecast: {str(e)}")
            return [self._get_mock_weather_data() for _ in range(hours_ahead)]
    
    async def predict_weather_impact(self, location: LocationData) -> Dict[str, Any]:
        """Predict weather impact on delivery operations"""
        weather = await self.get_current_weather(location)
        forecast = await self.get_weather_forecast(location, 3)
        
        # Calculate overall impact score
        current_impact = weather.weather_impact_score
        future_impact = max([w.weather_impact_score for w in forecast]) if forecast else current_impact
        
        impact_level = 'low'
        if current_impact > 0.7 or future_impact > 0.7:
            impact_level = 'severe'
        elif current_impact > 0.4 or future_impact > 0.4:
            impact_level = 'moderate'
        elif current_impact > 0.2 or future_impact > 0.2:
            impact_level = 'mild'
        
        return {
            'impact_level': impact_level,
            'current_conditions': weather.condition,
            'temperature': weather.temperature,
            'precipitation_risk': weather.precipitation_probability,
            'recommended_delay': self._calculate_weather_delay(weather),
            'special_handling_required': weather.temperature < 5 or weather.temperature > 35,
            'visibility_concerns': weather.visibility < 5.0
        }
    
    def _parse_weather_data(self, api_response: Dict[str, Any]) -> WeatherData:
        """Parse weather API response to WeatherData"""
        main = api_response.get('main', {})
        weather = api_response.get('weather', [{}])[0]
        wind = api_response.get('wind', {})
        
        temperature = main.get('temp', 25.0)
        condition = weather.get('main', 'Clear').lower()
        
        # Calculate impact score based on conditions
        impact_score = self._calculate_weather_impact_score(
            condition, 
            temperature, 
            wind.get('speed', 0),
            api_response.get('visibility', 10000) / 1000  # Convert to km
        )
        
        return WeatherData(
            temperature=temperature,
            condition=condition,
            precipitation_probability=api_response.get('pop', 0.0),  # Probability of precipitation
            wind_speed=wind.get('speed', 0) * 3.6,  # Convert m/s to km/h
            visibility=api_response.get('visibility', 10000) / 1000,  # Convert to km
            weather_impact_score=impact_score
        )
    
    def _calculate_weather_impact_score(self, condition: str, temperature: float, wind_speed: float, visibility: float) -> float:
        """Calculate weather impact score from 0 (no impact) to 1 (severe impact)"""
        impact = 0.0
        
        # Temperature impact
        if temperature < 0 or temperature > 40:
            impact += 0.4
        elif temperature < 5 or temperature > 35:
            impact += 0.2
        
        # Precipitation impact
        if condition in ['rain', 'thunderstorm', 'snow']:
            impact += 0.3
        elif condition in ['drizzle', 'mist']:
            impact += 0.1
        
        # Wind impact
        if wind_speed > 50:  # km/h
            impact += 0.2
        elif wind_speed > 30:
            impact += 0.1
        
        # Visibility impact
        if visibility < 1:
            impact += 0.3
        elif visibility < 5:
            impact += 0.1
        
        return min(1.0, impact)
    
    def _calculate_weather_delay(self, weather: WeatherData) -> int:
        """Calculate recommended delay in minutes based on weather"""
        if weather.weather_impact_score > 0.7:
            return 20  # Severe conditions
        elif weather.weather_impact_score > 0.4:
            return 10  # Moderate conditions
        elif weather.weather_impact_score > 0.2:
            return 5   # Mild conditions
        else:
            return 0   # No delay needed
    
    def _get_mock_weather_data(self) -> WeatherData:
        """Mock weather data for testing"""
        return WeatherData(
            temperature=28.0,
            condition='partly_cloudy',
            precipitation_probability=0.15,
            wind_speed=12.0,
            visibility=8.5,
            weather_impact_score=0.1
        )


class PredictiveAnalytics:
    """Combines Maps and Weather APIs for comprehensive delivery predictions"""
    
    def __init__(self, maps_api: GoogleMapsAPI = None, weather_api: WeatherAPI = None):
        self.maps_api = maps_api or GoogleMapsAPI()
        self.weather_api = weather_api or WeatherAPI()
    
    async def predict_delivery_delay(self, origin: LocationData, destination: LocationData) -> Dict[str, Any]:
        """Comprehensive delivery delay prediction using traffic and weather"""
        # Get traffic and weather data in parallel
        traffic_task = asyncio.create_task(self.maps_api.get_traffic_data(origin, destination))
        weather_task = asyncio.create_task(self.weather_api.predict_weather_impact(destination))
        
        traffic_data = await traffic_task
        weather_impact = await weather_task
        
        # Combine traffic and weather delays
        total_delay = traffic_data.current_delay
        weather_delay = self._calculate_weather_delay_adjustment(weather_impact)
        total_delay += weather_delay
        
        # Determine confidence level
        confidence = 0.85  # Base confidence
        if weather_impact['impact_level'] in ['moderate', 'severe']:
            confidence -= 0.15
        if traffic_data.traffic_density in ['heavy', 'severe']:
            confidence -= 0.1
        
        return {
            'total_predicted_delay': total_delay,
            'traffic_delay': traffic_data.current_delay,
            'weather_delay': weather_delay,
            'confidence_score': max(0.5, confidence),
            'traffic_condition': traffic_data.traffic_density,
            'weather_condition': weather_impact['current_conditions'],
            'recommendations': self._generate_delay_recommendations(traffic_data, weather_impact),
            'estimated_arrival': datetime.now() + timedelta(minutes=traffic_data.estimated_duration + weather_delay)
        }
    
    async def optimize_delivery_route(self, origin: LocationData, destination: LocationData) -> Dict[str, Any]:
        """Optimize delivery route considering traffic and weather"""
        # Get alternative routes and weather forecast
        routes_task = asyncio.create_task(self.maps_api.get_alternative_routes(origin, destination))
        weather_task = asyncio.create_task(self.weather_api.get_weather_forecast(destination, 2))
        
        alternative_routes = await routes_task
        weather_forecast = await weather_task
        
        # Score each route based on time, weather impact, and reliability
        route_scores = []
        for route in alternative_routes:
            weather_delay = sum([self._calculate_weather_delay_adjustment({'impact_level': 'mild'}) for _ in weather_forecast]) // len(weather_forecast) if weather_forecast else 0
            
            total_time = route['duration_minutes'] + route['traffic_delay'] + weather_delay
            score = self._calculate_route_score(total_time, route['traffic_delay'], weather_delay)
            
            route_scores.append({
                **route,
                'weather_adjusted_time': total_time,
                'route_score': score,
                'recommended': False
            })
        
        # Find best route
        if route_scores:
            best_route = max(route_scores, key=lambda x: x['route_score'])
            best_route['recommended'] = True
        
        return {
            'optimized_routes': sorted(route_scores, key=lambda x: x['route_score'], reverse=True),
            'weather_considerations': len(weather_forecast) > 0,
            'optimization_confidence': 0.8 if alternative_routes else 0.6
        }
    
    def _calculate_weather_delay_adjustment(self, weather_impact: Dict[str, Any]) -> int:
        """Calculate additional delay due to weather conditions"""
        impact_delays = {
            'low': 0,
            'mild': 3,
            'moderate': 8,
            'severe': 15
        }
        return impact_delays.get(weather_impact.get('impact_level', 'low'), 0)
    
    def _calculate_route_score(self, total_time: int, traffic_delay: int, weather_delay: int) -> float:
        """Calculate route score (higher is better)"""
        # Base score inversely related to time
        base_score = max(0, 100 - total_time)
        
        # Penalize high delays
        delay_penalty = (traffic_delay + weather_delay) * 2
        
        # Bonus for reliability (lower delays)
        reliability_bonus = max(0, 20 - (traffic_delay + weather_delay))
        
        return max(0, base_score - delay_penalty + reliability_bonus)
    
    def _generate_delay_recommendations(self, traffic_data: TrafficData, weather_impact: Dict[str, Any]) -> List[str]:
        """Generate actionable recommendations based on predicted delays"""
        recommendations = []
        
        if traffic_data.traffic_density in ['heavy', 'severe']:
            recommendations.append("Consider alternative routes to avoid heavy traffic")
            recommendations.append("Increase delivery time estimates by 15-25 minutes")
        
        if weather_impact['impact_level'] in ['moderate', 'severe']:
            recommendations.append("Use weather-appropriate packaging and insulation")
            recommendations.append("Consider delaying non-urgent deliveries")
        
        if weather_impact.get('special_handling_required'):
            recommendations.append("Use temperature-controlled delivery bags")
            recommendations.append("Prioritize time-sensitive food orders")
        
        if weather_impact.get('visibility_concerns'):
            recommendations.append("Enable enhanced GPS tracking for safety")
            recommendations.append("Provide extra navigation support to delivery agents")
        
        return recommendations