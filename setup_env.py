import os

def setup_environment():
    """
    Helper script to set up the .env file with Google API key
    """
    print("Setting up your environment for JD Parser...")
    print("\n1. Go to: https://aistudio.google.com/app/apikey")
    print("2. Sign in with your Google account")
    print("3. Click 'Create API key'")
    print("4. Copy the generated API key")
    print("\n" + "="*50)
    
    api_key = input("Paste your Google API key here: ").strip()
    
    if not api_key:
        print("No API key provided. Exiting...")
        return
    
    # Create .env file
    env_content = f"GOOGLE_API_KEY={api_key}\n"
    
    try:
        with open('.env', 'w') as f:
            f.write(env_content)
        print("\n✅ .env file created successfully!")
        print("You can now run: python jd_parser.py")
    except Exception as e:
        print(f"❌ Error creating .env file: {e}")

if __name__ == "__main__":
    setup_environment() 