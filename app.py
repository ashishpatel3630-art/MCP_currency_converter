import os
import json

import pandas as pd
import streamlit as st

from google import genai

from weather_tools import (
    get_current_weather,
    get_weather_forecast,
    compare_weather,
)


# ============================================================
# PAGE CONFIG
# ============================================================

st.set_page_config(
    page_title="Weather AI",
    page_icon="🌦️",
    layout="wide",
    initial_sidebar_state="expanded",
)


# ============================================================
# CUSTOM CSS
# ============================================================

st.markdown(
    """
    <style>

    .stApp {
        background:
            radial-gradient(
                circle at 15% 10%,
                rgba(59, 130, 246, 0.10),
                transparent 30%
            ),
            radial-gradient(
                circle at 85% 20%,
                rgba(14, 165, 233, 0.08),
                transparent 30%
            ),
            #070b12;

        color: #f8fafc;
    }

    .block-container {
        max-width: 1400px;
        padding-top: 2rem;
        padding-bottom: 4rem;
    }

    .hero {
        padding: 2rem 0 1rem 0;
    }

    .hero-title {
        font-size: 3rem;
        font-weight: 800;
        letter-spacing: -0.05em;
        margin-bottom: 0.4rem;

        background:
            linear-gradient(
                90deg,
                #ffffff,
                #93c5fd,
                #67e8f9
            );

        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
    }

    .hero-subtitle {
        color: #94a3b8;
        font-size: 1.05rem;
        max-width: 700px;
    }

    .weather-card {
        background:
            linear-gradient(
                135deg,
                rgba(30, 41, 59, 0.92),
                rgba(15, 23, 42, 0.94)
            );

        border: 1px solid
            rgba(148, 163, 184, 0.15);

        border-radius: 24px;

        padding: 28px;

        box-shadow:
            0 25px 80px
            rgba(0, 0, 0, 0.35);

        margin-bottom: 1.5rem;
    }

    .weather-city {
        font-size: 1.4rem;
        font-weight: 700;
        color: #f8fafc;
    }

    .weather-condition {
        color: #94a3b8;
        margin-top: 4px;
    }

    .temperature {
        font-size: 5rem;
        line-height: 1;
        font-weight: 800;
        letter-spacing: -0.06em;
    }

    .temp-unit {
        font-size: 1.5rem;
        color: #94a3b8;
        vertical-align: top;
    }

    .metric-card {
        background:
            rgba(15, 23, 42, 0.75);

        border: 1px solid
            rgba(148, 163, 184, 0.12);

        border-radius: 18px;

        padding: 20px;

        min-height: 115px;
    }

    .metric-label {
        color: #94a3b8;
        font-size: 0.85rem;
        margin-bottom: 8px;
    }

    .metric-value {
        color: #f8fafc;
        font-size: 1.45rem;
        font-weight: 700;
    }

    .section-title {
        font-size: 1.45rem;
        font-weight: 750;
        margin-top: 2rem;
        margin-bottom: 1rem;
        color: #f8fafc;
    }

    .forecast-card {
        background:
            rgba(15, 23, 42, 0.72);

        border: 1px solid
            rgba(148, 163, 184, 0.12);

        border-radius: 18px;

        padding: 18px;

        text-align: center;

        min-height: 220px;
    }

    .forecast-date {
        color: #cbd5e1;
        font-weight: 600;
    }

    .forecast-icon {
        font-size: 2rem;
        margin: 12px 0;
    }

    .forecast-temp {
        font-size: 1.2rem;
        font-weight: 700;
    }

    .forecast-rain {
        color: #60a5fa;
        font-size: 0.85rem;
        margin-top: 8px;
    }

    .ai-box {
        background:
            linear-gradient(
                135deg,
                rgba(30, 64, 175, 0.15),
                rgba(8, 145, 178, 0.10)
            );

        border: 1px solid
            rgba(96, 165, 250, 0.18);

        border-radius: 22px;

        padding: 24px;

        margin-top: 1rem;
    }

    [data-testid="stSidebar"] {
        background: #080d16;

        border-right: 1px solid
            rgba(148, 163, 184, 0.10);
    }

    .stButton > button {
        border-radius: 12px;

        border: 1px solid
            rgba(148, 163, 184, 0.18);

        background: #111827;

        color: white;

        font-weight: 600;

        min-height: 44px;

        transition: 0.2s ease;
    }

    .stButton > button:hover {
        border-color: #60a5fa;

        background: #172033;

        transform: translateY(-1px);
    }

    .stTextInput input,
    .stNumberInput input {
        border-radius: 12px !important;
    }

    [data-testid="stChatMessage"] {
        border-radius: 18px;

        border: 1px solid
            rgba(148, 163, 184, 0.10);

        margin-bottom: 10px;
    }

    .footer {
        text-align: center;

        color: #64748b;

        padding: 3rem 0 1rem 0;

        font-size: 0.85rem;
    }

    </style>
    """,
    unsafe_allow_html=True,
)


# ============================================================
# GEMINI
# ============================================================

@st.cache_resource
def get_gemini_client():

    api_key = os.getenv(
        "GEMINI_API_KEY"
    )

    if not api_key:
        return None

    return genai.Client(
        api_key=api_key
    )


gemini_client = get_gemini_client()


# ============================================================
# WEATHER EMOJI
# ============================================================

def weather_emoji(condition):

    condition = condition.lower()

    if "thunder" in condition:
        return "⛈️"

    if "snow" in condition:
        return "❄️"

    if "freezing" in condition:
        return "🧊"

    if "rain" in condition:
        return "🌧️"

    if "drizzle" in condition:
        return "🌦️"

    if "fog" in condition:
        return "🌫️"

    if "cloud" in condition:
        return "☁️"

    if "overcast" in condition:
        return "☁️"

    if "clear" in condition:
        return "☀️"

    return "🌤️"


# ============================================================
# GEMINI WEATHER ASSISTANT
# ============================================================

def ask_gemini_about_weather(
    user_question,
    weather_data,
):

    if gemini_client is None:

        return (
            "⚠️ Gemini API key is not configured.\n\n"
            "Set `GEMINI_API_KEY` in your environment "
            "and restart Streamlit."
        )

    prompt = f"""
You are Weather AI, a professional weather assistant.

Use ONLY the weather data supplied below.

Do not invent temperature, rainfall,
humidity, wind, forecast or weather conditions.

WEATHER DATA:

{json.dumps(
    weather_data,
    indent=2
)}

USER QUESTION:

{user_question}

Rules:

1. Give a concise answer.
2. Use the supplied weather data.
3. If the user asks about clothing, walking,
   travel, umbrella, outdoor sports or activities,
   give practical advice based on the data.
4. If precipitation probability is high,
   mention it when relevant.
5. If weather information is not available
   in the supplied data, clearly say that it
   is not available.
"""

    try:

        response = (
            gemini_client
            .models
            .generate_content(
                model="gemini-3.5-flash",
                contents=prompt,
            )
        )

        return response.text

    except Exception as e:

        return (
            f"Gemini request failed: {e}"
        )


# ============================================================
# SESSION STATE
# ============================================================

if "weather" not in st.session_state:
    st.session_state.weather = None

if "forecast" not in st.session_state:
    st.session_state.forecast = None

if "city" not in st.session_state:
    st.session_state.city = "Bhopal"

if "messages" not in st.session_state:
    st.session_state.messages = []


# ============================================================
# SIDEBAR
# ============================================================

with st.sidebar:

    st.markdown(
        """
        <h2>🌦️ Weather AI</h2>

        <p style="color:#94a3b8;">
        AI-powered weather intelligence
        </p>
        """,
        unsafe_allow_html=True,
    )

    st.divider()

    city = st.text_input(
        "📍 Location",
        value=st.session_state.city,
        placeholder="Enter city...",
    )

    days = st.slider(
        "Forecast days",
        min_value=1,
        max_value=7,
        value=5,
    )

    st.divider()

    if st.button(
        "🔄 Refresh Weather",
        use_container_width=True,
    ):

        if not city.strip():

            st.error(
                "Please enter a city."
            )

        else:

            try:

                with st.spinner(
                    "Updating weather..."
                ):

                    st.session_state.weather = (
                        get_current_weather(
                            city
                        )
                    )

                    st.session_state.forecast = (
                        get_weather_forecast(
                            city,
                            days,
                        )
                    )

                    st.session_state.city = (
                        city
                    )

                st.success(
                    "Weather updated."
                )

            except Exception as e:

                st.error(
                    f"Unable to load weather: {e}"
                )

    st.divider()

    st.caption(
        "Powered by Open-Meteo + Gemini"
    )


# ============================================================
# HEADER
# ============================================================

st.markdown(
    """
    <div class="hero">

        <div class="hero-title">
            Weather Intelligence
        </div>

        <div class="hero-subtitle">
            Real-time weather, forecasts and
            AI-powered recommendations in one
            intelligent dashboard.
        </div>

    </div>
    """,
    unsafe_allow_html=True,
)


# ============================================================
# INITIAL LOAD
# ============================================================

if st.session_state.weather is None:

    try:

        with st.spinner(
            "Loading weather..."
        ):

            st.session_state.weather = (
                get_current_weather(
                    st.session_state.city
                )
            )

            st.session_state.forecast = (
                get_weather_forecast(
                    st.session_state.city,
                    days,
                )
            )

    except Exception as e:

        st.error(
            f"Could not load weather: {e}"
        )

        st.stop()


weather = st.session_state.weather

forecast_data = st.session_state.forecast


# ============================================================
# CURRENT WEATHER
# ============================================================

st.markdown(
    '<div class="section-title">'
    'Current Conditions'
    '</div>',
    unsafe_allow_html=True,
)

st.markdown(
    f"""
    <div class="weather-card">

        <div class="weather-city">
            📍 {weather["city"]},
            {weather["country"]}
        </div>

        <div class="weather-condition">
            {weather["condition"]}
            · WMO {weather["weather_code"]}
        </div>

        <br>

        <div class="temperature">
            {weather["temperature_c"]:.1f}
            <span class="temp-unit">°C</span>
        </div>

        <div style="color:#94a3b8;margin-top:10px;">
            Feels like
            {weather["feels_like_c"]:.1f}°C
        </div>

    </div>
    """,
    unsafe_allow_html=True,
)


# ============================================================
# METRICS
# ============================================================

cols = st.columns(4)

metrics = [

    (
        "💧 Humidity",
        f'{weather["humidity_percent"]}%'
    ),

    (
        "💨 Wind",
        f'{weather["wind_speed_kmh"]:.1f} km/h'
    ),

    (
        "🌧️ Precipitation",
        f'{weather["precipitation_mm"]:.2f} mm'
    ),

    (
        "☁️ Cloud Cover",
        f'{weather["cloud_cover_percent"]}%'
    ),
]


for col, (label, value) in zip(
    cols,
    metrics,
):

    with col:

        st.markdown(
            f"""
            <div class="metric-card">

                <div class="metric-label">
                    {label}
                </div>

                <div class="metric-value">
                    {value}
                </div>

            </div>
            """,
            unsafe_allow_html=True,
        )


# ============================================================
# EXTRA CURRENT INFORMATION
# ============================================================

st.markdown(
    '<div class="section-title">'
    'Weather Details'
    '</div>',
    unsafe_allow_html=True,
)

details_col1, details_col2, details_col3 = (
    st.columns(3)
)


with details_col1:

    st.metric(
        "Wind Direction",
        f'{weather["wind_direction_deg"]}°',
    )


with details_col2:

    st.metric(
        "Wind Gusts",
        f'{weather["wind_gusts_kmh"]:.1f} km/h',
    )


with details_col3:

    st.metric(
        "Local Time",
        weather["time"].replace(
            "T",
            " "
        ),
    )


# ============================================================
# FORECAST
# ============================================================

st.markdown(
    '<div class="section-title">'
    'Forecast'
    '</div>',
    unsafe_allow_html=True,
)

forecast = forecast_data["forecast"]

forecast_cols = st.columns(
    len(forecast)
)


for col, day in zip(
    forecast_cols,
    forecast,
):

    with col:

        emoji = weather_emoji(
            day["condition"]
        )

        st.markdown(
            f"""
            <div class="forecast-card">

                <div class="forecast-date">
                    {day["date"]}
                </div>

                <div class="forecast-icon">
                    {emoji}
                </div>

                <div>
                    {day["condition"]}
                </div>

                <br>

                <div class="forecast-temp">
                    {day["max_temperature_c"]:.1f}°
                    /
                    {day["min_temperature_c"]:.1f}°
                </div>

                <div class="forecast-rain">
                    🌧️
                    {day["rain_probability_percent"]}%
                    precipitation
                </div>

                <div style="
                    color:#64748b;
                    font-size:0.8rem;
                    margin-top:8px;
                ">
                    {day["precipitation_mm"]:.1f} mm
                    expected
                </div>

            </div>
            """,
            unsafe_allow_html=True,
        )


# ============================================================
# TEMPERATURE CHART
# ============================================================

st.markdown(
    '<div class="section-title">'
    'Temperature Trend'
    '</div>',
    unsafe_allow_html=True,
)

chart_df = pd.DataFrame(
    forecast
)

chart_df = chart_df.set_index(
    "date"
)[
    [
        "max_temperature_c",
        "min_temperature_c",
    ]
]

chart_df.columns = [
    "Maximum °C",
    "Minimum °C",
]

st.line_chart(
    chart_df,
    width="stretch",
)


# ============================================================
# AI ASSISTANT
# ============================================================

st.markdown(
    '<div class="section-title">'
    '🤖 AI Weather Assistant'
    '</div>',
    unsafe_allow_html=True,
)

st.markdown(
    """
    <div class="ai-box">

        <b>Ask Weather AI</b>

        <br><br>

        • Should I carry an umbrella today?<br>
        • Is this good weather for a morning walk?<br>
        • What should I wear tomorrow?<br>
        • Is tomorrow good for outdoor cricket?<br>
        • Should I plan a trip this weekend?<br>

    </div>
    """,
    unsafe_allow_html=True,
)


# Display previous messages

for message in st.session_state.messages:

    with st.chat_message(
        message["role"]
    ):

        st.markdown(
            message["content"]
        )


user_question = st.chat_input(
    "Ask anything about the weather..."
)


if user_question:

    st.session_state.messages.append(
        {
            "role": "user",
            "content": user_question,
        }
    )

    with st.chat_message("user"):

        st.markdown(
            user_question
        )

    with st.chat_message("assistant"):

        with st.spinner(
            "Analyzing weather..."
        ):

            combined_weather = {

                "current": weather,

                "forecast": forecast,
            }

            answer = (
                ask_gemini_about_weather(
                    user_question,
                    combined_weather,
                )
            )

            st.markdown(
                answer
            )

    st.session_state.messages.append(
        {
            "role": "assistant",
            "content": answer,
        }
    )


# ============================================================
# CITY COMPARISON
# ============================================================

st.markdown(
    '<div class="section-title">'
    '🏙️ Compare Cities'
    '</div>',
    unsafe_allow_html=True,
)

compare_col1, compare_col2 = (
    st.columns(2)
)


with compare_col1:

    city1 = st.text_input(
        "First city",
        "Bhopal",
        key="compare_city_1",
    )


with compare_col2:

    city2 = st.text_input(
        "Second city",
        "Delhi",
        key="compare_city_2",
    )


if st.button(
    "Compare Weather",
    use_container_width=True,
):

    if (
        not city1.strip()
        or not city2.strip()
    ):

        st.error(
            "Please enter both cities."
        )

    else:

        try:

            with st.spinner(
                "Comparing..."
            ):

                comparison = (
                    compare_weather(
                        city1,
                        city2,
                    )
                )

            c1, c2 = st.columns(2)


            with c1:

                w1 = comparison["city1"]

                st.markdown(
                    f"""
                    <div class="weather-card">

                        <div class="weather-city">
                            📍 {w1["city"]}
                        </div>

                        <div class="weather-condition">
                            {w1["condition"]}
                        </div>

                        <br>

                        <div class="temperature">
                            {w1["temperature_c"]:.1f}°
                        </div>

                        <br>

                        💧 Humidity:
                        {w1["humidity_percent"]}%<br>

                        💨 Wind:
                        {w1["wind_speed_kmh"]:.1f} km/h<br>

                        🌧️ Rain:
                        {w1["precipitation_mm"]:.2f} mm

                    </div>
                    """,
                    unsafe_allow_html=True,
                )


            with c2:

                w2 = comparison["city2"]

                st.markdown(
                    f"""
                    <div class="weather-card">

                        <div class="weather-city">
                            📍 {w2["city"]}
                        </div>

                        <div class="weather-condition">
                            {w2["condition"]}
                        </div>

                        <br>

                        <div class="temperature">
                            {w2["temperature_c"]:.1f}°
                        </div>

                        <br>

                        💧 Humidity:
                        {w2["humidity_percent"]}%<br>

                        💨 Wind:
                        {w2["wind_speed_kmh"]:.1f} km/h<br>

                        🌧️ Rain:
                        {w2["precipitation_mm"]:.2f} mm

                    </div>
                    """,
                    unsafe_allow_html=True,
                )

        except Exception as e:

            st.error(
                f"Comparison failed: {e}"
            )


# ============================================================
# FOOTER
# ============================================================

st.markdown(
    """
    <div class="footer">

        Weather AI · Open-Meteo + Gemini

        <br><br>

        Built with Streamlit

    </div>
    """,
    unsafe_allow_html=True,
)