# PlanCast - AI Calendar & Weather Assistant

PlanCast is an intelligent AI assistant that helps you manage your calendar and get weather information using natural language.

## 🚀 Quick Start

### 1. Prerequisites

- Python 3.8+
- Ollama installed and running
- Google Calendar API credentials
- WeatherAPI.com API key

### 2. Setup

```bash
# Clone the repository
git clone <your-repo-url>
cd PlanCast

# Create virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Set up environment variables
cp env.example .env
# Edit .env with your API keys
```

### 3. Configure API Keys

Edit `.env` file with your credentials:

```env
# Google Calendar API
GOOGLE_CLIENT_ID=your_google_client_id
GOOGLE_CLIENT_SECRET=your_google_client_secret

# WeatherAPI.com
WEATHERAPI_API_KEY=your_weatherapi_key

# LLM Settings
LLM_MODEL=mistral
LLM_TEMPERATURE=0.1
```

### 4. Start Ollama

```bash
# Install Ollama (if not already installed)
# https://ollama.ai/

# Start Ollama
ollama serve

# Pull the Mistral model
ollama pull mistral
```

### 5. Run the App

```bash
# Run the interactive PlanCast app
python run_plancast.py
```

## 💬 Example Commands

Once the app is running, you can ask:

- **Calendar**: "What's on my calendar today?"
- **Scheduling**: "Schedule a meeting with john@email.com tomorrow at 2pm"
- **Weather**: "What's the weather like in San Francisco?"
- **Availability**: "Check if I'm free on Friday at 3pm"
- **Smart Planning**: "Schedule a picnic this weekend if the weather is nice"

## 🛠️ Features

- **Smart Time Parsing**: Understands natural language like "next Monday" or "3pm"
- **Calendar Integration**: Create, view, and manage Google Calendar events
- **Weather Intelligence**: Get current weather and forecasts
- **Availability Checking**: Check if time slots are free
- **Conversation Memory**: Remembers context across interactions

## 📁 Project Structure

```
PlanCast/
├── agent/              # LangChain agent and tools
├── services/           # Calendar and weather services
├── utils/              # Utilities like smart time parser
├── config/             # Configuration settings
├── run_plancast.py     # Main app runner
├── main.py             # Basic setup test
└── requirements.txt    # Python dependencies
```

## 🔧 Troubleshooting

### Ollama Issues

- Make sure Ollama is running: `ollama serve`
- Check if model is pulled: `ollama list`
- Pull model if needed: `ollama pull mistral`

### API Issues

- Verify Google Calendar API credentials in `.env`
- Check WeatherAPI.com API key
- Ensure `credentials.json` exists for Google Calendar

### Environment Issues

- Activate virtual environment: `source venv/bin/activate`
- Install dependencies: `pip install -r requirements.txt`

## 🤝 Contributing

Feel free to submit issues and enhancement requests!

## 📄 License

This project is open source and available under the MIT License.
