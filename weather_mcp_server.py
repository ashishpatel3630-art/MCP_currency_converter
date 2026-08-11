
import httpx

from mcp.server import MCPServer


mcp = MCPServer(
    "Weather MCP Server"
)


def get_coordinates(city: str):

    url = (
        "https://geocoding-api.open-meteo.com/v1/search"
    )

    params = {
        "name": city,
        "count": 1,
        "language": "en",
        "format": "json"
    }

    response = httpx.get(
        url,
        params=params,
        timeout=10
    )

    response.raise_for_status()

    data = response.json()

    if not data.get("results"):
        raise ValueError(
            f"City '{city}' not found."
        )

    location = data["results"][0]

    return {
        "name": location["name"],
        "latitude": location["latitude"],
        "longitude": location["longitude"],
        "country": location.get("country"),
        "timezone": location.get("timezone")
    }


def weather_code_to_text(code: int):

    codes = {

        0: "Clear sky",

        1: "Mainly clear",
        2: "Partly cloudy",
        3: "Overcast",

        45: "Fog",
        48: "Depositing rime fog",

        51: "Light drizzle",
        53: "Moderate drizzle",
        55: "Dense drizzle",

        61: "Slight rain",
        63: "Moderate rain",
        65: "Heavy rain",

        71: "Slight snow",
        73: "Moderate snow",
        75: "Heavy snow",

        80: "Slight rain showers",
        81: "Moderate rain showers",
        82: "Violent rain showers",

        95: "Thunderstorm",

        96: "Thunderstorm with slight hail",
        99: "Thunderstorm with heavy hail"
    }

    return codes.get(
        code,
        "Unknown"
    )


@mcp.tool()
def get_current_weather(
    city: str
) -> dict:
    """
    Get the current weather for a city.
    """

    location = get_coordinates(city)

    url = (
        "https://api.open-meteo.com/v1/forecast"
    )

    params = {

        "latitude": location["latitude"],

        "longitude": location["longitude"],

        "current": (
            "temperature_2m,"
            "relative_humidity_2m,"
            "apparent_temperature,"
            "precipitation,"
            "weather_code,"
            "wind_speed_10m"
        ),

        "timezone": "auto"
    }

    response = httpx.get(
        url,
        params=params,
        timeout=10
    )

    response.raise_for_status()

    data = response.json()

    current = data["current"]

    return {

        "city": location["name"],

        "country": location["country"],

        "condition": weather_code_to_text(
            current["weather_code"]
        ),

        "temperature_c":
            current["temperature_2m"],

        "feels_like_c":
            current["apparent_temperature"],

        "humidity_percent":
            current["relative_humidity_2m"],

        "precipitation_mm":
            current["precipitation"],

        "wind_speed_kmh":
            current["wind_speed_10m"],

        "time":
            current["time"],

        "timezone":
            data["timezone"]
    }


@mcp.tool()
def get_weather_forecast(
    city: str,
    days: int = 3
) -> dict:
    """
    Get the weather forecast for a city.
    """

    if days < 1:
        days = 1

    if days > 7:
        days = 7

    location = get_coordinates(city)

    url = (
        "https://api.open-meteo.com/v1/forecast"
    )

    params = {

        "latitude": location["latitude"],

        "longitude": location["longitude"],

        "daily": (
            "weather_code,"
            "temperature_2m_max,"
            "temperature_2m_min,"
            "precipitation_probability_max,"
            "precipitation_sum,"
            "wind_speed_10m_max"
        ),

        "forecast_days": days,

        "timezone": "auto"
    }

    response = httpx.get(
        url,
        params=params,
        timeout=10
    )

    response.raise_for_status()

    data = response.json()

    daily = data["daily"]

    forecast = []

    for i in range(len(daily["time"])):

        forecast.append({

            "date": daily["time"][i],

            "condition": weather_code_to_text(
                daily["weather_code"][i]
            ),

            "max_temperature_c":
                daily["temperature_2m_max"][i],

            "min_temperature_c":
                daily["temperature_2m_min"][i],

            "rain_probability_percent":
                daily[
                    "precipitation_probability_max"
                ][i],

            "precipitation_mm":
                daily["precipitation_sum"][i],

            "max_wind_speed_kmh":
                daily["wind_speed_10m_max"][i]
        })

    return {

        "city": location["name"],

        "country": location["country"],

        "timezone": data["timezone"],

        "forecast": forecast
    }


@mcp.tool()
def compare_weather(
    city1: str,
    city2: str
) -> dict:
    """
    Compare current weather between two cities.
    """

    weather1 = get_current_weather(city1)

    weather2 = get_current_weather(city2)

    return {
        "city1": weather1,
        "city2": weather2
    }


if __name__ == "__main__":
    mcp.run()
