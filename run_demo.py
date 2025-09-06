#!/usr/bin/env python3
"""
Script for quick RAG demo launch
"""
import os
import sys
import subprocess

def check_requirements():
    """Check installed dependencies"""
    try:
        import flask
        import chromadb
        import sentence_transformers
        import bs4
        print("✅ All dependencies installed")
        return True
    except ImportError as e:
        print(f"❌ Missing dependency: {e}")
        print("Install dependencies: pip install -r requirements.txt")
        return False

def check_env_file():
    """Check for .env file"""
    if not os.path.exists('.env'):
        print("⚠️  .env file not found")
        print("Copy .env.example to .env and configure API keys")
        return False
    print("✅ .env file found")
    return True

def main():
    """Main function"""
    print("🚀 Starting RAG Demo")
    print("=" * 50)
    
    # Check dependencies
    if not check_requirements():
        return 1
    
    # Check .env file
    env_ok = check_env_file()
    if not env_ok:
        print("\nFor full functionality, configure the .env file")
        print("The system will run in limited mode")
    
    print("\n🌐 Starting web server...")
    print("Open browser: http://localhost:5000")
    print("To stop press Ctrl+C")
    print("=" * 50)
    
    try:
        # Run the Flask application
        sys.path.append('src')
        from web.app import app
        # Use debug=False for a more production-like start, or keep True for development
        app.run(host='0.0.0.0', port=5000, debug=True) 
    except KeyboardInterrupt:
        print("\n👋 Server stopped")
        return 0
    except Exception as e:
        print(f"❌ Startup error: {e}")
        return 1

if __name__ == "__main__":
    sys.exit(main())
    
