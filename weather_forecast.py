import requests
from datetime import datetime
import json
import os
from colorama import init, Fore, Style

class WeatherForecast:
    def __init__(self, api_key):
        self.api_key = api_key
        self.base_url = "http://api.openweathermap.org/data/2.5"
        self.units = "metric"  # Para obtener temperaturas en Celsius
        self.ciudades_favoritas = self.cargar_ciudades_favoritas()

    def cargar_ciudades_favoritas(self):
        """Carga las ciudades favoritas desde un archivo JSON"""
        try:
            if os.path.exists('ciudades_favoritas.json'):
                with open('ciudades_favoritas.json', 'r') as f:
                    return json.load(f)
            return []
        except:
            return []

    def guardar_ciudades_favoritas(self):
        """Guarda las ciudades favoritas en un archivo JSON"""
        with open('ciudades_favoritas.json', 'w') as f:
            json.dump(self.ciudades_favoritas, f)

    def agregar_ciudad_favorita(self, ciudad):
        """Agrega una ciudad a las favoritas"""
        if ciudad not in self.ciudades_favoritas:
            self.ciudades_favoritas.append(ciudad)
            self.guardar_ciudades_favoritas()
            return True
        return False

    def get_current_weather(self, city):
        """Obtiene el clima actual de una ciudad"""
        url = f"{self.base_url}/weather"
        params = {
            "q": city,
            "appid": self.api_key,
            "units": self.units,
            "lang": "es"  # Para obtener descripciones en español
        }

        try:
            response = requests.get(url, params=params)
            response.raise_for_status()
            data = response.json()

            # Extraer información relevante
            weather_data = {
                "ciudad": data["name"],
                "temperatura": data["main"]["temp"],
                "sensacion_termica": data["main"]["feels_like"],
                "humedad": data["main"]["humidity"],
                "descripcion": data["weather"][0]["description"],
                "viento": data["wind"]["speed"],
                "presion": data["main"]["pressure"],
                "icono": data["weather"][0]["icon"],
                "amanecer": datetime.fromtimestamp(data["sys"]["sunrise"]).strftime("%H:%M"),
                "atardecer": datetime.fromtimestamp(data["sys"]["sunset"]).strftime("%H:%M"),
                "visibilidad": data.get("visibility", "No disponible") / 1000 if "visibility" in data else "No disponible"
            }
            return weather_data
        except requests.exceptions.RequestException as e:
            print(f"{Fore.RED}Error al obtener el clima actual: {e}{Style.RESET_ALL}")
            return None

    def get_weekly_forecast(self, city):
        """Obtiene el pronóstico semanal de una ciudad"""
        url = f"{self.base_url}/forecast"
        params = {
            "q": city,
            "appid": self.api_key,
            "units": self.units,
            "lang": "es"
        }

        try:
            response = requests.get(url, params=params)
            response.raise_for_status()
            data = response.json()

            # Agrupar pronósticos por día
            daily_forecasts = {}
            for forecast in data["list"]:
                date = datetime.fromtimestamp(forecast["dt"]).strftime("%Y-%m-%d")
                if date not in daily_forecasts:
                    daily_forecasts[date] = {
                        "temperaturas": [],
                        "descripciones": [],
                        "humedad": [],
                        "viento": [],
                        "precipitacion": []
                    }
                
                daily_forecasts[date]["temperaturas"].append(forecast["main"]["temp"])
                daily_forecasts[date]["descripciones"].append(forecast["weather"][0]["description"])
                daily_forecasts[date]["humedad"].append(forecast["main"]["humidity"])
                daily_forecasts[date]["viento"].append(forecast["wind"]["speed"])
                daily_forecasts[date]["precipitacion"].append(forecast.get("rain", {}).get("3h", 0))

            # Calcular promedios diarios
            for date in daily_forecasts:
                temps = daily_forecasts[date]["temperaturas"]
                daily_forecasts[date]["temp_min"] = min(temps)
                daily_forecasts[date]["temp_max"] = max(temps)
                daily_forecasts[date]["temp_promedio"] = sum(temps) / len(temps)
                daily_forecasts[date]["descripcion"] = max(set(daily_forecasts[date]["descripciones"]), 
                                                         key=daily_forecasts[date]["descripciones"].count)
                daily_forecasts[date]["humedad_promedio"] = sum(daily_forecasts[date]["humedad"]) / len(daily_forecasts[date]["humedad"])
                daily_forecasts[date]["viento_promedio"] = sum(daily_forecasts[date]["viento"]) / len(daily_forecasts[date]["viento"])
                daily_forecasts[date]["precipitacion_total"] = sum(daily_forecasts[date]["precipitacion"])

            return daily_forecasts
        except requests.exceptions.RequestException as e:
            print(f"{Fore.RED}Error al obtener el pronóstico semanal: {e}{Style.RESET_ALL}")
            return None

    def display_current_weather(self, weather_data):
        """Muestra el clima actual de forma formateada"""
        if not weather_data:
            return

        print(f"\n{Fore.CYAN}🌤️ Clima Actual en {weather_data['ciudad']}{Style.RESET_ALL}")
        print(f"{Fore.YELLOW}Temperatura: {weather_data['temperatura']}°C{Style.RESET_ALL}")
        print(f"Sensación térmica: {weather_data['sensacion_termica']}°C")
        print(f"Descripción: {weather_data['descripcion'].capitalize()}")
        print(f"Humedad: {weather_data['humedad']}%")
        print(f"Viento: {weather_data['viento']} m/s")
        print(f"Presión: {weather_data['presion']} hPa")
        print(f"Visibilidad: {weather_data['visibilidad']} km")
        print(f"Amanecer: {weather_data['amanecer']}")
        print(f"Atardecer: {weather_data['atardecer']}")

    def display_weekly_forecast(self, forecasts):
        """Muestra el pronóstico semanal de forma formateada"""
        if not forecasts:
            return

        print(f"\n{Fore.CYAN}📅 Pronóstico Semanal{Style.RESET_ALL}")
        for date, forecast in forecasts.items():
            print(f"\n{Fore.GREEN}{datetime.strptime(date, '%Y-%m-%d').strftime('%A %d/%m')}:{Style.RESET_ALL}")
            print(f"  Temperatura: {forecast['temp_min']:.1f}°C - {forecast['temp_max']:.1f}°C")
            print(f"  Promedio: {forecast['temp_promedio']:.1f}°C")
            print(f"  Descripción: {forecast['descripcion'].capitalize()}")
            print(f"  Humedad promedio: {forecast['humedad_promedio']:.1f}%")
            print(f"  Viento promedio: {forecast['viento_promedio']:.1f} m/s")
            if forecast['precipitacion_total'] > 0:
                print(f"  Precipitación esperada: {forecast['precipitacion_total']:.1f} mm")

def main():
    init()  # Inicializa colorama
    print(f"{Fore.CYAN}🌍 Consulta del Clima{Style.RESET_ALL}")
    
    # API key de OpenWeatherMap
    api_key = "ba0fdf698e00b9a333e10d595727cef4"
    weather = WeatherForecast(api_key)

    while True:
        print(f"\n{Fore.CYAN}Menú Principal:{Style.RESET_ALL}")
        print("1. Ver clima actual")
        print("2. Ver pronóstico semanal")
        print("3. Agregar ciudad a favoritos")
        print("4. Ver ciudades favoritas")
        print("5. Salir")
        
        opcion = input("\nSelecciona una opción (1-5): ")
        
        if opcion == "5":
            break
        
        if opcion == "4":
            if weather.ciudades_favoritas:
                print(f"\n{Fore.YELLOW}Ciudades favoritas:{Style.RESET_ALL}")
                for i, ciudad in enumerate(weather.ciudades_favoritas, 1):
                    print(f"{i}. {ciudad}")
            else:
                print(f"{Fore.YELLOW}No hay ciudades favoritas guardadas.{Style.RESET_ALL}")
            continue

        if opcion == "3":
            ciudad = input("Ingresa el nombre de la ciudad a agregar a favoritos: ")
            if weather.agregar_ciudad_favorita(ciudad):
                print(f"{Fore.GREEN}✅ Ciudad agregada a favoritos!{Style.RESET_ALL}")
            else:
                print(f"{Fore.YELLOW}La ciudad ya está en favoritos.{Style.RESET_ALL}")
            continue

        if opcion in ["1", "2"]:
            if weather.ciudades_favoritas:
                print("\nCiudades favoritas:")
                for i, ciudad in enumerate(weather.ciudades_favoritas, 1):
                    print(f"{i}. {ciudad}")
                print("0. Ingresar nueva ciudad")
                
                ciudad_opcion = input("\nSelecciona una ciudad (número) o 0 para nueva: ")
                if ciudad_opcion == "0":
                    ciudad = input("Ingresa el nombre de la ciudad: ")
                else:
                    try:
                        index = int(ciudad_opcion) - 1
                        if 0 <= index < len(weather.ciudades_favoritas):
                            ciudad = weather.ciudades_favoritas[index]
                        else:
                            print(f"{Fore.RED}Opción inválida.{Style.RESET_ALL}")
                            continue
                    except ValueError:
                        print(f"{Fore.RED}Opción inválida.{Style.RESET_ALL}")
                        continue
            else:
                ciudad = input("Ingresa el nombre de la ciudad: ")
            
            if opcion == "1":
                current_weather = weather.get_current_weather(ciudad)
                weather.display_current_weather(current_weather)
            elif opcion == "2":
                weekly_forecast = weather.get_weekly_forecast(ciudad)
                weather.display_weekly_forecast(weekly_forecast)
        else:
            print(f"{Fore.RED}Opción no válida. Intenta de nuevo.{Style.RESET_ALL}")

if __name__ == "__main__":
    main() 