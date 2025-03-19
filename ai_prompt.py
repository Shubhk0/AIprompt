#!/usr/bin/env python3
import argparse
import json
import os
import requests
import sys
import getpass
from typing import Dict, Any, Optional

# Default configuration
DEFAULT_CONFIG = {
    "openai": {
        "api_key": "",
        "default_model": "gpt-3.5-turbo"
    },
    "openrouter": {
        "api_key": "",
        "default_model": "google/gemini-2.0-pro-exp-02-05:free"
    },
    "anthropic": {
        "api_key": "",
        "default_model": "claude-3-opus-20240229"
    },
    "default_provider": "openrouter"
}

CONFIG_PATH = os.path.expanduser("~/.ai_prompt_config.json")

def load_config() -> Dict[str, Any]:
    """Load configuration from file or create default if not exists."""
    if os.path.exists(CONFIG_PATH):
        with open(CONFIG_PATH, 'r') as f:
            return json.load(f)
    else:
        # Create default config file
        with open(CONFIG_PATH, 'w') as f:
            json.dump(DEFAULT_CONFIG, f, indent=2)
        print(f"Created default configuration at {CONFIG_PATH}")
        return DEFAULT_CONFIG

def save_config(config: Dict[str, Any]) -> None:
    """Save configuration to file."""
    with open(CONFIG_PATH, 'w') as f:
        json.dump(config, f, indent=2)

def setup_config() -> None:
    """Interactive configuration setup."""
    config = load_config()
    
    print("AI Prompt Configuration Setup")
    print("============================")
    
        
    # API key setup
    print("\nAPI Key Configuration")
    print("======================")
    providers = [p for p in DEFAULT_CONFIG if p != 'default_provider']
    keys = load_keys()
    
    for provider in providers:
        if not keys[provider]:
            api_key = getpass.getpass(f"Enter {provider} API key: ")
            keys[provider] = api_key
    
    with open(os.path.expanduser("~/.ai_prompt_keys.json"), 'w') as f:
        json.dump(keys, f)
    
    # Model configuration
    print("\nModel Configuration")
    print("====================")
    config["openai"]["default_model"] = input(f"Default OpenAI Model [{config['openai']['default_model']}]: ") or config["openai"]["default_model"]
    config["openrouter"]["default_model"] = input(f"Default OpenRouter Model [{config['openrouter']['default_model']}]: ") or config["openrouter"]["default_model"]
    config["anthropic"]["default_model"] = input(f"Default Anthropic Model [{config['anthropic']['default_model']}]: ") or config["anthropic"]["default_model"]
    
    # Default provider
    print("\nDefault Provider:")
    default_provider = input(f"Default Provider (openai/openrouter/anthropic) [{config['default_provider']}]: ") or config['default_provider']
    if default_provider in ["openai", "openrouter", "anthropic"]:
        config["default_provider"] = default_provider
    else:
        print(f"Invalid provider '{default_provider}'. Using '{config['default_provider']}' as default.")
    
    save_config(config)
    print(f"\nConfiguration saved to {CONFIG_PATH}")

def query_openai(prompt: str, model: str, api_key: str) -> Optional[str]:
    """Query OpenAI API with the given prompt."""
    headers = {
        "Content-Type": "application/json",
        "Authorization": f"Bearer {api_key}"
    }
    
    data = {
        "model": model,
        "messages": [{"role": "user", "content": prompt}],
        "temperature": 0.7
    }
    
    response = None
    try:
        response = requests.post(
            "https://api.openai.com/v1/chat/completions",
            headers=headers,
            json=data
        )
        response.raise_for_status()
        return response.json()["choices"][0]["message"]["content"]
    except Exception as e:
        print(f"Error querying OpenAI: {e}")
        if response and hasattr(response, 'text'):
            print(f"Response: {response.text}")
        return None

def query_openrouter(prompt: str, model: str, api_key: str) -> Optional[str]:
    """Query OpenRouter API with the given prompt."""
    headers = {
        "Content-Type": "application/json",
        "Authorization": f"Bearer {api_key}",
        "HTTP-Referer": "https://github.com/terminal-ai-prompt",  # Replace with your actual site
        "X-Title": "Terminal AI Prompt"
    }
    
    data = {
        "model": model,
        "messages": [{"role": "user", "content": prompt}],
        "temperature": 0.7
    }
    
    try:
        response = requests.post(
            "https://openrouter.ai/api/v1/chat/completions",
            headers=headers,
            json=data
        )
        response.raise_for_status()
        return response.json()["choices"][0]["message"]["content"]
    except Exception as e:
        print(f"Error querying OpenRouter: {e}")
        if hasattr(response, 'text'):
            print(f"Response: {response.text}")
        return None

def query_anthropic(prompt: str, model: str, api_key: str) -> Optional[str]:
    """Query Anthropic API with the given prompt."""
    headers = {
        "Content-Type": "application/json",
        "x-api-key": api_key,
        "anthropic-version": "2023-06-01"
    }
    
    data = {
        "model": model,
        "messages": [{"role": "user", "content": prompt}],
        "max_tokens": 4000,
        "temperature": 0.7
    }
    
    try:
        response = requests.post(
            "https://api.anthropic.com/v1/messages",
            headers=headers,
            json=data
        )
        response.raise_for_status()
        return response.json()["content"][0]["text"]
    except Exception as e:
        print(f"Error querying Anthropic: {e}")
        if hasattr(response, 'text'):
            print(f"Response: {response.text}")
        return None

def list_models(provider: str, api_key: str) -> None:
    """List available models for the given provider."""
    if provider == "openai":
        url = "https://api.openai.com/v1/models"
        headers = {"Authorization": f"Bearer {api_key}"}
    elif provider == "openrouter":
        url = "https://openrouter.ai/api/v1/models"
        headers = {"Authorization": f"Bearer {api_key}"}
    elif provider == "anthropic":
        # Anthropic doesn't have a models endpoint, so we'll just list the known models
        print("\nAvailable Anthropic models:")
        for model in ["claude-3-opus-20240229", "claude-3-sonnet-20240229", "claude-3-haiku-20240307"]:
            print(f"  - {model}")
        return
    else:
        print(f"Unknown provider: {provider}")
        return
    
    try:
        response = requests.get(url, headers=headers)
        response.raise_for_status()
        models = response.json()
        
        if provider == "openai":
            # Filter to chat models
            chat_models = [model["id"] for model in models["data"] if "gpt" in model["id"].lower()]
            print(f"\nAvailable OpenAI models:")
            for model in sorted(chat_models):
                print(f"  - {model}")
        else:
            # OpenRouter format is different
            print(f"\nAvailable OpenRouter models:")
            for model in models["data"]:
                print(f"  - {model['id']} ({model['name']})")
    except Exception as e:
        print(f"Error listing models: {e}")
        if hasattr(response, 'text'):
            print(f"Response: {response.text}")

def main(args=None):
    config = load_config()
    
    parser = argparse.ArgumentParser(description="Query AI models from the terminal")
    parser.add_argument('-m', '--model', 
                    help='Model to use (defaults to provider\'s configured default)',
                    default=None)
    parser.add_argument("prompt", nargs="?", help="The prompt to send to the AI model")

    parser.add_argument("-p", "--provider", choices=["openai", "openrouter", "anthropic"], 
                        help="Specify the provider (openai, openrouter, or anthropic)")
    parser.add_argument("--setup", action="store_true", help="Run the configuration setup")
    parser.add_argument("--list-models", action="store_true", help="List available models")
    parser.add_argument("-f", "--file", help="Read prompt from file")
    
    args = parser.parse_args(args)
    
    if args.setup:
        setup_config()
        return
    
    # Determine provider
    provider = args.provider or config["default_provider"]
    if provider not in ["openai", "openrouter", "anthropic"]:
        print(f"Unknown provider: {provider}")
        return
    
    # Load API keys
    keys = load_keys()
    
    # Check if API key is configured
    if not keys[provider]:
        print(f"No API key configured for {provider}. Run with --setup to configure.")
        sys.exit(1)
    
    # List models if requested
    if args.list_models:
        list_models(provider, config[provider]["api_key"])
        return
    
    # Get prompt from arguments, file, or stdin
    prompt = None
    if args.prompt:
        prompt = args.prompt
    elif args.file:
        try:
            with open(args.file, 'r') as f:
                prompt = f.read()
        except Exception as e:
            print(f"Error reading file: {e}")
            return
    elif not sys.stdin.isatty():
        prompt = sys.stdin.read()
    
    if not prompt:
        parser.print_help()
        return
    
    # Determine model
    model = args.model or config[provider]["default_model"]
    
    # Query the appropriate API
    if provider == "openai":
        response = query_openai(prompt, model, keys["openai"])
    elif provider == "openrouter":
        response = query_openrouter(prompt, model, keys["openrouter"])
    else:  # anthropic
        response = query_anthropic(prompt, model, keys["anthropic"])
    
    if response:
        print(response)

def load_keys() -> dict:
    """Load API keys from JSON file"""
    key_file = os.path.expanduser("~/.ai_prompt_keys.json")
    try:
        with open(key_file, 'r') as f:
            return json.load(f)
    except (FileNotFoundError, json.JSONDecodeError):
        return {"openai": "", "openrouter": "", "anthropic": ""}

if __name__ == "__main__":
    main()