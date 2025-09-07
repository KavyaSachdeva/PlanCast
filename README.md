# 🚀 PlanCast - AI Calendar & Weather Assistant

PlanCast is a Python application that integrates calendar management and weather information through natural language processing. Built with LangChain and powered by local LLMs via Ollama, it provides an AI agent that can interact with Google Calendar and weather APIs.

## ✨ Features

### 📅 Calendar Management

- **View Events**: Check your calendar for today, tomorrow, or any specific date
- **Schedule Meetings**: Create calendar events with natural language
- **Availability Check**: See if you're free at specific times
- **Smart Duplicate Prevention**: Avoids creating duplicate events
- **Google Calendar Integration**: Full sync with your Google Calendar

### 🌤️ Weather Intelligence

- **Current Weather**: Get real-time weather for any location
- **Weather Forecasts**: Plan ahead with weather predictions
- **Event Weather Planning**: Check weather for specific events and dates
- **Outdoor Activity Planning**: Get weather insights for outdoor events

### 🤖 AI-Powered

- **Natural Language Processing**: Understand complex requests
- **Smart Time Parsing**: Handles "tomorrow at 2pm", "next Friday", etc.
- **Context Awareness**: Remembers conversation history
- **Local LLM Support**: Uses Ollama for local language model inference

## 🛠️ Tech Stack

- **AI Framework**: LangChain with ReAct agent pattern
- **LLM**: Ollama (Mistral, Llama2, CodeLlama, Phi2)
- **Calendar**: Google Calendar API
- **Weather**: WeatherAPI.com
- **Language**: Python 3.8+
- **Database**: SQLite (for simplicity)

## 📋 Prerequisites

1. **Python 3.8+**
2. **Ollama** - [Install Ollama](https://ollama.ai/)
3. **Google Calendar API** - [Google Cloud Console](https://console.cloud.google.com/)
4. **WeatherAPI.com Account** - [Get API Key](https://www.weatherapi.com/)

## 🚀 Installation & Setup

### 1. Clone the Repository

```bash
git clone https://github.com/KavyaSachdeva/PlanCast.git
cd PlanCast
```

### 2. Install Dependencies

```bash
# Create virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install requirements
pip install -r requirements.txt
```

### 3. Set Up Ollama

```bash
# Start Ollama service
ollama serve

# Pull a model (in another terminal)
ollama pull mistral
```

### 4. Configure Environment

```bash
# Copy environment template
cp env.example .env

# Edit .env with your API keys
nano .env
```

Required environment variables:

```env
# Local LLM Configuration
LLM_MODEL=mistral
LLM_TEMPERATURE=0.1
OLLAMA_BASE_URL=http://localhost:11434

# Google Calendar API
GOOGLE_CLIENT_ID=your_google_client_id_here
GOOGLE_CLIENT_SECRET=your_google_client_secret_here
GOOGLE_REDIRECT_URI=http://localhost:8080/auth/callback

# Weather API
OPENWEATHER_API_KEY=your_weather_api_key
```

### 5. Set Up Google Calendar API

1. Go to [Google Cloud Console](https://console.cloud.google.com/)
2. Create a new project or select existing one
3. Enable Google Calendar API
4. Create credentials (OAuth 2.0 Client ID)
5. Download `credentials.json` to project root
6. Add your Google Calendar API credentials to `.env`

### 6. Run PlanCast

```bash
# Test basic setup
python main.py

# Run interactive assistant
python run_plancast.py
```

## 💬 Usage

### Calendar Operations

```
🤖 You: What's on my calendar today?
🤖 PlanCast: Found 2 events for today:
- Team Meeting at 10:00 AM (Conference Room)
- Lunch with Sarah at 12:30 PM

🤖 You: Schedule a meeting with john@email.com tomorrow at 2pm
🤖 PlanCast: ✅ Event created: Meeting with john@email.com on 2024-01-15 14:00:00

🤖 You: Am I free on Friday at 3pm?
🤖 PlanCast: ✅ Friday is available for 3pm
```

### Weather Operations

```
🤖 You: What's the weather like in San Francisco?
🤖 PlanCast: Current weather in San Francisco: 18°C, Partly cloudy, Humidity: 65%, Wind: 12 km/h

🤖 You: Check weather for my picnic this Saturday in Central Park
🤖 PlanCast: Weather for 2024-01-20 in Central Park: 15°C, Sunny, 10% chance of rain, Humidity: 45%
```

### Multi-step Operations

```
🤖 You: Schedule a picnic this weekend if the weather is nice
🤖 PlanCast: Let me check the weather and your availability...

[Checks weather for weekend]
[Checks calendar availability]
[Creates event if conditions are good]
```

## 🏗️ Project Structure

```
PlanCast/
├── agent/
│   └── tools.py              # LangChain tools for calendar & weather
├── config/
│   └── settings.py           # Configuration management
├── services/
│   ├── calendar.py           # Google Calendar integration
│   ├── calendar_auth.py      # OAuth authentication
│   ├── weather.py            # Weather API integration
│   └── weather_weatherapi.py # WeatherAPI.com service
├── utils/
│   └── time_parser.py        # Smart time parsing
├── main.py                   # Basic setup test
├── run_plancast.py          # Interactive CLI application
├── agent_test.py            # Agent testing script
├── requirements.txt         # Python dependencies
├── env.example             # Environment template
└── README.md               # This file
```

## 🔧 Configuration

### LLM Models

The application supports multiple Ollama models:

- **Mistral** (recommended) - Fast and accurate
- **Llama2** - Good general performance
- **CodeLlama** - Better for complex reasoning
- **Phi2** - Lightweight option

Change model in `.env`:

```env
LLM_MODEL=mistral  # or llama2, codellama, phi2
```

### Temperature Settings

Control AI creativity vs consistency:

```env
LLM_TEMPERATURE=0.1  # Lower = more consistent, Higher = more creative
```

## 🧪 Testing

Test application components:

```bash
# Test basic setup
python main.py

# Test agent functionality
python agent_test.py

# Test specific tools
python -c "from agent.tools import PlanCastTools; tools = PlanCastTools(); print('Tools loaded successfully')"
```

## 🚨 Troubleshooting

### Common Issues

**Ollama Connection Error**

```bash
# Make sure Ollama is running
ollama serve

# Check if model is available
ollama list
```

**Google Calendar Authentication**

- Ensure `credentials.json` is in project root
- Check OAuth redirect URI matches your `.env` setting
- Delete `token.json` to re-authenticate

**Weather API Issues**

- Verify API key is correct
- Check API quota limits
- Ensure internet connection

**Import Errors**

```bash
# Reinstall dependencies
pip install -r requirements.txt --force-reinstall
```

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/your-feature`)
3. Commit your changes (`git commit -m 'Add your feature'`)
4. Push to the branch (`git push origin feature/your-feature`)
5. Open a Pull Request

## 📝 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🙏 Acknowledgments

- [LangChain](https://langchain.com/) - AI framework
- [Ollama](https://ollama.ai/) - Local LLM runtime
- [Google Calendar API](https://developers.google.com/calendar) - Calendar integration
- [WeatherAPI.com](https://www.weatherapi.com/) - Weather data

## 📞 Support

If you encounter any issues or have questions:

1. Check the [Troubleshooting](#-troubleshooting) section
2. Search existing [Issues](https://github.com/KavyaSachdeva/PlanCast/issues)
3. Create a new issue with detailed information

---

**Made with ❤️ by [Kavya Sachdeva](https://github.com/KavyaSachdeva)**
