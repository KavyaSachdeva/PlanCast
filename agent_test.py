#!/usr/bin/env python3
"""
Test LangChain with Ollama
Simple test to verify our LLM setup works
"""

import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()


def test_langchain_ollama():
    """Test LangChain with Ollama"""
    try:
        from langchain_ollama import OllamaLLM
        from langchain.schema import HumanMessage

        print("🧪 Testing LangChain with Ollama...")

        # Initialize Ollama LLM
        llm = OllamaLLM(
            model=os.getenv("LLM_MODEL", "mistral"),
            temperature=float(os.getenv("LLM_TEMPERATURE", "0.1"))
        )

        # Test simple completion
        test_prompt = "Hello! I'm testing PlanCast. Can you respond with 'PlanCast is working!'?"

        print(f"Testing with prompt: {test_prompt}")
        response = llm.invoke(test_prompt)

        print(f"✅ LLM Response: {response}")
        return True

    except Exception as e:
        print(f"❌ Error testing LangChain with Ollama: {e}")
        print("Make sure:")
        print("1. Ollama is running: ollama serve")
        print("2. A model is pulled: ollama pull mistral")
        print("3. All dependencies are installed: pip install -r requirements.txt")
        return False


def main():
    """Main test function"""
    print("🧪 PlanCast - LangChain Test")
    print("=" * 40)

    if test_langchain_ollama():
        print("\n✅ LangChain with Ollama is working!")
        print("Ready to build the full agent!")
    else:
        print("\n❌ Setup needs attention")


if __name__ == "__main__":
    main()
