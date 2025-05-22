#!/usr/bin/env python3
"""
Setup script for FinanceGPT
Helps install dependencies and configure the environment.
"""

import subprocess
import sys
import os
from pathlib import Path

def install_requirements():
    """Install Python requirements."""
    print("📦 Installing Python dependencies...")
    try:
        subprocess.check_call([sys.executable, "-m", "pip", "install", "-r", "requirements.txt"])
        print("✅ Dependencies installed successfully!")
        return True
    except subprocess.CalledProcessError:
        print("❌ Failed to install dependencies")
        return False

def check_ollama():
    """Check if Ollama is available."""
    print("\n🤖 Checking Ollama availability...")
    try:
        result = subprocess.run(["ollama", "--version"], capture_output=True, text=True)
        if result.returncode == 0:
            print("✅ Ollama is installed")
            return True
        else:
            print("❌ Ollama not found")
            return False
    except FileNotFoundError:
        print("❌ Ollama not found")
        return False

def show_ollama_setup():
    """Show Ollama setup instructions."""
    print("""
🤖 Ollama Setup Instructions:

1. Install Ollama:
   - Visit: https://ollama.ai
   - Download and install for your system

2. Start Ollama (in terminal):
   ollama serve

3. Install a model (in another terminal):
   ollama pull llama3.2:3b
   
   Alternative models:
   - llama3.2:1b (smaller, faster)
   - phi3:mini (Microsoft's efficient model)
   - mistral:7b (good balance)

4. Verify installation:
   ollama list
""")

def run_demo():
    """Run the demo script."""
    print("\n🎬 Running demo...")
    try:
        subprocess.check_call([sys.executable, "demo.py"])
        return True
    except subprocess.CalledProcessError:
        print("❌ Demo failed")
        return False

def main():
    """Main setup process."""
    print("🏦 FinanceGPT Setup")
    print("=" * 50)
    
    # Check if we're in the right directory
    if not Path("requirements.txt").exists():
        print("❌ Please run this script from the FinanceGPT directory")
        sys.exit(1)
    
    # Install dependencies
    if not install_requirements():
        print("❌ Setup failed")
        sys.exit(1)
    
    # Check Ollama
    ollama_available = check_ollama()
    if not ollama_available:
        show_ollama_setup()
    
    # Offer to run demo
    response = input("\n🎬 Would you like to run the demo? (y/n): ").lower()
    if response in ['y', 'yes']:
        if run_demo():
            print("✅ Demo completed successfully!")
        else:
            print("❌ Demo encountered issues")
    
    print(f"""
🎉 Setup Complete!

Next steps:
1. Run the main application:
   python main.py

2. Or analyze your own CSV:
   python main.py --file your_spending.csv

3. For enhanced AI insights:
   {'✅ Ollama is ready!' if ollama_available else '⚠️  Install Ollama (see instructions above)'}

Happy budgeting! 💰
""")

if __name__ == "__main__":
    main() 