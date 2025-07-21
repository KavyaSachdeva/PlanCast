#!/usr/bin/env python3
"""
PlanCast App Runner
Interactive CLI to use the PlanCast AI agent
"""

import os
from dotenv import load_dotenv
from langchain_ollama import OllamaLLM
from langchain.memory import ConversationBufferMemory
from langchain.agents import AgentExecutor, create_react_agent
from langchain.prompts import PromptTemplate
from agent.tools import PlanCastTools

# Load environment variables
load_dotenv()


def create_plancast_agent():
    """Create and configure the PlanCast agent"""
    try:
        # Initialize LLM
        llm = OllamaLLM(
            model=os.getenv("LLM_MODEL", "mistral"),
            temperature=float(os.getenv("LLM_TEMPERATURE", "0.1"))
        )
        
        # Initialize tools
        tools = PlanCastTools(llm).get_tools()
        
        # Create memory
        memory = ConversationBufferMemory(
            memory_key="chat_history",
            return_messages=True
        )
        
        # Create prompt template for the agent
        prompt = PromptTemplate.from_template("""You are PlanCast, an AI assistant that helps with calendar management and weather information.

You have access to the following tools:
{tools}

Use the following format:

Question: the input question you must answer
Thought: you should always think about what to do
Action: the action to take, should be one of [{tool_names}]
Action Input: the input to the action
Observation: the result of the action
... (this Thought/Action/Action Input/Observation can repeat N times)
Thought: I now know the final answer
Final Answer: the final answer to the original input question

Begin!

Previous conversation history:
{chat_history}

Question: {input}
Thought: {agent_scratchpad}""")
        
        # Create agent
        agent = create_react_agent(
            llm=llm,
            tools=tools,
            prompt=prompt
        )
        
        # Create agent executor
        agent_executor = AgentExecutor(
            agent=agent,
            tools=tools,
            memory=memory,
            verbose=True,
            max_iterations=2,
            handle_parsing_errors=True,
            max_execution_time=30
        )
        
        return agent_executor
        
    except Exception as e:
        print(f"❌ Error creating agent: {e}")
        return None


def run_interactive():
    """Run interactive PlanCast session"""
    print("🚀 PlanCast - AI Calendar & Weather Assistant")
    print("=" * 50)
    print("Type 'quit' or 'exit' to end the session")
    print("Type 'help' for example commands")
    print()
    
    # Create agent
    agent = create_plancast_agent()
    if not agent:
        print("❌ Failed to create agent. Please check your setup.")
        return
    
    print("✅ Agent ready! Ask me anything about your calendar or weather.")
    print("💡 Tip: Be specific with meeting details to avoid duplicates")
    print()
    
    # Example commands
    examples = [
        "What's on my calendar today?",
        "Schedule a meeting with john@email.com tomorrow at 2pm",
        "What's the weather like in San Francisco?",
        "Check if I'm free on Friday at 3pm",
        "Schedule a picnic this weekend if the weather is nice"
    ]
    
    while True:
        try:
            # Get user input
            user_input = input("🤖 You: ").strip()
            
            if user_input.lower() in ['quit', 'exit', 'bye']:
                print("👋 Goodbye! Thanks for using PlanCast!")
                break
            elif user_input.lower() == 'help':
                print("\n📋 Example commands:")
                for example in examples:
                    print(f"  • {example}")
                print("\n💡 Tips to avoid duplicates:")
                print("  • Be specific: 'Schedule meeting with john@email.com tomorrow 2pm'")
                print("  • Include all details in one request")
                print("  • Wait for confirmation before asking again")
                print()
                continue
            elif not user_input:
                continue
            
            # Get agent response
            print("🤖 PlanCast: ", end="", flush=True)
            response = agent.invoke({"input": user_input})
            
            print(response["output"])
            print()
            
        except KeyboardInterrupt:
            print("\n👋 Goodbye! Thanks for using PlanCast!")
            break
        except Exception as e:
            print(f"❌ Error: {e}")
            print("Please try again or type 'help' for examples.")


def main():
    """Main function"""
    # Check if Ollama is running
    try:
        import requests
        response = requests.get("http://localhost:11434/api/tags")
        if response.status_code != 200:
            print("❌ Ollama is not running!")
            print("Please start Ollama: ollama serve")
            return
    except Exception:
        print("❌ Cannot connect to Ollama!")
        print("Please make sure Ollama is installed and running:")
        print("1. Install Ollama: https://ollama.ai/")
        print("2. Start Ollama: ollama serve")
        print("3. Pull a model: ollama pull mistral")
        return
    
    # Check environment variables
    required_vars = ["GOOGLE_CLIENT_ID", "GOOGLE_CLIENT_SECRET", "WEATHERAPI_API_KEY"]
    missing_vars = [var for var in required_vars if not os.getenv(var)]
    
    if missing_vars:
        print("⚠️  Missing environment variables:")
        for var in missing_vars:
            print(f"  - {var}")
        print("\nPlease create a .env file from env.example and fill in your API keys.")
        return
    
    # Run interactive session
    run_interactive()


if __name__ == "__main__":
    main()
