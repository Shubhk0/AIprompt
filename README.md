# Terminal AI Prompt Tool

A command-line utility for interacting with various AI models directly from your terminal. This tool supports multiple AI providers including OpenAI, OpenRouter, and Anthropic.

## Features

- Query AI models from your terminal with simple commands
- Support for multiple AI providers:
  - OpenAI (GPT models)
  - OpenRouter (access to multiple AI models through one API)
  - Anthropic (Claude models)
- Read prompts from command line arguments, files, or standard input
- Configure default models for each provider
- List available models for each provider
- Secure API key management

## Installation

### Prerequisites

- Python 3.6 or higher
- Required Python packages: `requests`
- For the setup script: `jq` command-line tool

### Setup

1. Clone this repository or download the script files
2. Install required dependencies:

```bash
pip install requests
```

3. Make the scripts executable:

```bash
chmod +x ai_prompt.py setup_api_keys.sh
```

4. Run the setup script to configure your API keys and default models:

```bash
./setup_api_keys.sh
```

Alternatively, you can run the Python setup directly:

```bash
python ai_prompt.py --setup
```

## Configuration

The tool stores configuration in two files in your home directory:

- `~/.ai_prompt_config.json` - Stores default models and provider settings
- `~/.ai_prompt_keys.json` - Securely stores your API keys

You can edit these files manually or use the setup commands to configure them.

### Default Configuration

By default, the tool uses:
- OpenRouter as the default provider
- Default models:
  - OpenAI: `gpt-3.5-turbo`
  - OpenRouter: `google/gemini-2.0-pro-exp-02-05:free`
  - Anthropic: `claude-3-opus-20240229`

## Usage

### Basic Usage

Query an AI model with a prompt:

```bash
./ai_prompt.py "What is the capital of France?"
```

### Specifying a Provider

```bash
./ai_prompt.py -p openai "Explain quantum computing in simple terms"
```

Available providers: `openai`, `openrouter`, `anthropic`

### Specifying a Model

```bash
./ai_prompt.py -m gpt-4 "Write a short story about a robot"
```

### Reading Prompt from a File

```bash
./ai_prompt.py -f prompt.txt
```

### Reading Prompt from Standard Input

```bash
cat prompt.txt | ./ai_prompt.py
```

### Listing Available Models

```bash
./ai_prompt.py --list-models
```

To list models for a specific provider:

```bash
./ai_prompt.py -p openai --list-models
```

### Running Setup

```bash
./ai_prompt.py --setup
```

## Command-Line Options

```
-m, --model MODEL       Model to use (defaults to provider's configured default)
-p, --provider {openai,openrouter,anthropic}
                        Specify the provider
--setup                 Run the configuration setup
--list-models           List available models
-f, --file FILE         Read prompt from file
```

## API Keys

You'll need API keys from the providers you want to use:

- OpenAI: https://platform.openai.com/api-keys
- OpenRouter: https://openrouter.ai/keys
- Anthropic: https://console.anthropic.com/keys

## Examples

### Using OpenAI with GPT-4

```bash
./ai_prompt.py -p openai -m gpt-4 "Write a Python function to calculate Fibonacci numbers"
```

### Using Anthropic with Claude

```bash
./ai_prompt.py -p anthropic "Explain the difference between REST and GraphQL"
```

### Using OpenRouter with a specific model

```bash
./ai_prompt.py -p openrouter -m anthropic/claude-3-opus-20240229 "Suggest five book recommendations"
```

## Troubleshooting

### API Key Issues

If you encounter authentication errors, ensure your API keys are correctly configured:

```bash
./ai_prompt.py --setup
```

### Model Availability

If a specified model is unavailable, use the `--list-models` option to see available models for your provider.

### Rate Limiting

If you encounter rate limit errors, wait a few minutes before trying again or switch to a different provider.

## License

This project is open source and available under the MIT License.