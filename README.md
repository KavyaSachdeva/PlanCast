# 🚀 PlanCast - AI Calendar & Weather Assistant

PlanCast is a Python application that integrates calendar management and weather information through natural language processing. Built with LangChain and powered by local LLMs via Ollama, it provides an AI agent that can interact with Google Calendar and weather APIs.

## ✨ Features

- **Calendar Management**: View, create, and check availability via Google Calendar
- **Weather Integration**: Current weather and forecasts for any location
- **Natural Language**: AI agent understands complex requests like "schedule meeting tomorrow at 2pm"
- **Local LLM**: Powered by Ollama for privacy and offline capability

## 🛠️ Tech Stack

- **LangChain** + **Ollama** (Mistral/Llama2) + **Google Calendar API** + **WeatherAPI.com**

## 📋 Prerequisites

- Python 3.8+, Ollama, Google Calendar API, WeatherAPI.com key

## 🚀 Quick Start

```bash
# 1. Setup
git clone https://github.com/KavyaSachdeva/PlanCast.git
cd PlanCast
python -m venv venv && source venv/bin/activate
pip install -r requirements.txt

# 2. Setup Ollama
ollama serve
ollama pull mistral

# 3. Configure
cp env.example .env
# Edit .env with your Google Calendar and WeatherAPI keys
# Download credentials.json from Google Cloud Console

# 4. Run
python run_plancast.py
```

## 💬 Usage

```
🤖 You: What's on my calendar today?
🤖 PlanCast: Found 2 events for today: Team Meeting at 10:00 AM, Lunch at 12:30 PM

🤖 You: Schedule a meeting with john@email.com tomorrow at 2pm
🤖 PlanCast: ✅ Event created: Meeting with john@email.com on 2024-01-15 14:00:00

🤖 You: What's the weather like in San Francisco?
🤖 PlanCast: Current weather in San Francisco: 18°C, Partly cloudy, Humidity: 65%

🤖 You: Schedule a picnic this weekend if the weather is nice
🤖 PlanCast: [Checks weather and availability, creates event if conditions are good]
```

## 🔧 Configuration

```env
LLM_MODEL=mistral  # or llama2, codellama, phi2
LLM_TEMPERATURE=0.1
GOOGLE_CLIENT_ID=your_google_client_id_here
GOOGLE_CLIENT_SECRET=your_google_client_secret_here
OPENWEATHER_API_KEY=your_weather_api_key
```
