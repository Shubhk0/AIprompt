#!/bin/bash

# Check if jq is installed
if ! command -v jq &> /dev/null; then
    echo "Error: jq is required. Please install jq first."
    echo "On macOS: brew install jq"
    echo "On Linux: sudo apt-get install jq"
    exit 1
fi

KEY_FILE="$HOME/.ai_prompt_keys.json"
CONFIG_FILE="$HOME/.ai_prompt_config.json"

# Initialize existing values
if [ -f "$KEY_FILE" ]; then
    existing=$(jq -c . "$KEY_FILE")
    openai_key=$(jq -r .openai <<< "$existing")
    openrouter_key=$(jq -r .openrouter <<< "$existing")
    anthropic_key=$(jq -r .anthropic <<< "$existing")
else
    openai_key=""
    openrouter_key=""
    anthropic_key=""
fi

# Function to ask yes/no question
ask_yes_no() {
    while true; do
        read -p "$1 (y/n): " yn
        case $yn in
            [Yy]* ) return 0;;  # Yes
            [Nn]* ) return 1;;  # No
            * ) echo "Please answer y or n.";;  # Invalid input
        esac
    done
}

# Collect API keys securely
echo "API Key Setup:"

# OpenAI API Key
if [ -n "$openai_key" ]; then
    echo "OpenAI API Key: [Already configured]" 
    if ask_yes_no "Do you want to update your OpenAI API Key?"; then
        read -p "Enter your OpenAI API Key: " -s new_openai
        [ -n "$new_openai" ] && openai_key="$new_openai"
        echo
    fi
else
    if ask_yes_no "Do you have an OpenAI API Key?"; then
        read -p "Enter your OpenAI API Key: " -s new_openai
        [ -n "$new_openai" ] && openai_key="$new_openai"
        echo
    fi
fi

# OpenRouter API Key
if [ -n "$openrouter_key" ]; then
    echo "OpenRouter API Key: [Already configured]" 
    if ask_yes_no "Do you want to update your OpenRouter API Key?"; then
        read -p "Enter your OpenRouter API Key: " -s new_openrouter
        [ -n "$new_openrouter" ] && openrouter_key="$new_openrouter"
        echo
    fi
else
    if ask_yes_no "Do you have an OpenRouter API Key?"; then
        read -p "Enter your OpenRouter API Key: " -s new_openrouter
        [ -n "$new_openrouter" ] && openrouter_key="$new_openrouter"
        echo
    fi
fi

# Anthropic API Key
if [ -n "$anthropic_key" ]; then
    echo "Anthropic API Key: [Already configured]" 
    if ask_yes_no "Do you want to update your Anthropic API Key?"; then
        read -p "Enter your Anthropic API Key: " -s new_anthropic
        [ -n "$new_anthropic" ] && anthropic_key="$new_anthropic"
        echo
    fi
else
    if ask_yes_no "Do you have an Anthropic API Key?"; then
        read -p "Enter your Anthropic API Key: " -s new_anthropic
        [ -n "$new_anthropic" ] && anthropic_key="$new_anthropic"
        echo
    fi
fi

# Create JSON structure for API keys
jq -n --arg o "$openai_key" \
    --arg or "$openrouter_key" \
    --arg a "$anthropic_key" \
    '{openai: $o, openrouter: $or, anthropic: $a}' > "$KEY_FILE"

echo "API keys updated successfully in $KEY_FILE"

# Setup configuration file if it doesn't exist or update it
if [ -f "$CONFIG_FILE" ]; then
    config=$(jq -c . "$CONFIG_FILE")
    openai_model=$(jq -r '.openai.default_model // "gpt-3.5-turbo"' <<< "$config")
    openrouter_model=$(jq -r '.openrouter.default_model // "google/gemini-2.0-pro-exp-02-05:free"' <<< "$config")
    anthropic_model=$(jq -r '.anthropic.default_model // "claude-3-opus-20240229"' <<< "$config")
    default_provider=$(jq -r '.default_provider // "openrouter"' <<< "$config")
else
    # Default values
    openai_model="gpt-3.5-turbo"
    openrouter_model="google/gemini-2.0-pro-exp-02-05:free"
    anthropic_model="claude-3-opus-20240229"
    default_provider="openrouter"
fi

# Ask for model configuration
echo -e "\nModel Configuration"
echo "==================="

read -p "Default OpenAI Model [$openai_model]: " new_openai_model
openai_model=${new_openai_model:-$openai_model}

read -p "Default OpenRouter Model [$openrouter_model]: " new_openrouter_model
openrouter_model=${new_openrouter_model:-$openrouter_model}

read -p "Default Anthropic Model [$anthropic_model]: " new_anthropic_model
anthropic_model=${new_anthropic_model:-$anthropic_model}

# Ask for default provider
echo -e "\nDefault Provider:"
read -p "Default Provider (openai/openrouter/anthropic) [$default_provider]: " new_default_provider
if [[ -n "$new_default_provider" ]]; then
    if [[ "$new_default_provider" =~ ^(openai|openrouter|anthropic)$ ]]; then
        default_provider="$new_default_provider"
    else
        echo "Invalid provider '$new_default_provider'. Using '$default_provider' as default."
    fi
fi

# Create JSON structure for config
jq -n \
    --arg openai_model "$openai_model" \
    --arg openrouter_model "$openrouter_model" \
    --arg anthropic_model "$anthropic_model" \
    --arg default_provider "$default_provider" \
    '{
        "openai": {
            "api_key": "",
            "default_model": $openai_model
        },
        "openrouter": {
            "api_key": "",
            "default_model": $openrouter_model
        },
        "anthropic": {
            "api_key": "",
            "default_model": $anthropic_model
        },
        "default_provider": $default_provider
    }' > "$CONFIG_FILE"

echo "Configuration saved to $CONFIG_FILE"
echo -e "\nSetup complete! You can now use ai_prompt.py directly."