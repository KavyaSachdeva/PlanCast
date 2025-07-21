#!/usr/bin/env python3
"""
PlanCast - AI Calendar and Weather Assistant
Main entry point for the application
"""

import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()


def test_ollama_connection():
    """Test if Ollama is running and accessible"""
    try:
        import requests
        response = requests.get("http://localhost:11434/api/tags")
        if response.status_code == 200:
            print("✅ Ollama is running!")
            models = response.json().get("models", [])
            if models:
                print(
                    f"Available models: {[model['name'] for model in models]}")
            else:
                print("No models found. Please run: ollama pull mistral")
            return True
        else:
            print("❌ Ollama is not responding properly")
            return False
    except Exception as e:
        print(f"❌ Cannot connect to Ollama: {e}")
        print("Please make sure Ollama is installed and running:")
        print("1. Install Ollama: https://ollama.ai/")
        print("2. Start Ollama: ollama serve")
        print("3. Pull a model: ollama pull mistral")
        return False


def main():
    """Main function to test basic setup"""
    print("🚀 PlanCast - AI Calendar and Weather Assistant")
    print("=" * 50)

    # Test Ollama connection
    if not test_ollama_connection():
        return

    print("\n✅ Basic setup looks good!")
    print("Next steps:")
    print("1. Set up Google Calendar API credentials")
    print("2. Get WeatherAPI.com API key")
    print("3. Create .env file from env.example")
    print("4. Run: python agent_test.py")


if __name__ == "__main__":
    main()
