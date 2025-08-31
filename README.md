# Tagalog Translation Script

**Version:** 1.0.0  
**Last Updated:** 2024-12-19

A command-line tool for translating English text to Tagalog (Filipino) using OpenAI's Responses API. This script provides accurate, context-aware translations while preserving names, URLs, code blocks, and custom terminology.

## Overview

This script uses OpenAI's GPT-4.1-mini model with optimized settings for faithful Tagalog translation. It automatically chunks large texts into manageable segments (up to 4,000 words per request) and rejoins the outputs seamlessly.

### Key Features

- **Accurate Translation**: Uses temperature=0.2 for consistent, faithful translations
- **Smart Chunking**: Automatically splits large texts while preserving paragraph structure
- **Term Preservation**: Maintains names, URLs, code blocks, numbers, and custom glossary terms
- **Flexible Input/Output**: Read from files or stdin, write to files or stdout
- **Formal/Informal Tones**: Choose between formal and natural Tagalog styles
- **Custom Glossary**: Define terms that should remain untranslated

## Critical Configurations

### OpenAI API Key Setup

**⚠️ SECURITY WARNING**: Never hard-code your API key into the script. Always use environment variables.

#### Temporary Setup (per shell session)

**macOS / Linux (bash/zsh):**
```bash
export OPENAI_API_KEY='your-actual-api-key-here'
```

**Windows PowerShell:**
```powershell
$env:OPENAI_API_KEY = 'your-actual-api-key-here'
```

#### Persistent Setup

**macOS / Linux:**
Add to your shell profile (`~/.zshrc`, `~/.bashrc`, etc.):
```bash
export OPENAI_API_KEY='your-actual-api-key-here'
```

**Windows:**
Add to your PowerShell profile or use System Environment Variables.

### Required Dependencies

```bash
pip install --upgrade openai
```

## Installation & Setup

### 1. Save the Script

Ensure `translate_to_tagalog.py` is in your working directory.

### 2. Install Dependencies

```bash
pip install --upgrade openai
```

### 3. Set Your API Key

Choose your operating system and set the environment variable:

**macOS / Linux:**
```bash
export OPENAI_API_KEY='key-here'
```

**Windows PowerShell:**
```powershell
$env:OPENAI_API_KEY = 'key-here'
```

## Usage Examples

### Basic Translation

**Translate a file:**
```bash
python translate_to_tagalog.py -i input.txt -o output.tl.txt
```

**Translate from stdin:**
```bash
echo "Your English text here..." | python translate_to_tagalog.py
```

### Advanced Options

**Formal translation with custom glossary:**
```bash
python translate_to_tagalog.py -i input.txt -o output.tl.txt --formal --glossary "Blue Butterfly,Dragon,Jeet Kune Do,Microsoft"
```

**Custom model and chunk size:**
```bash
python translate_to_tagalog.py -i input.txt --model gpt-4 --max-words 2000
```

### Command Line Options

| Option | Description | Default |
|--------|-------------|---------|
| `-i, --input` | Input file path (omit for stdin) | stdin |
| `-o, --output` | Output file path (omit for stdout) | stdout |
| `--model` | OpenAI model to use | gpt-4.1-mini |
| `--formal` | Use formal Tagalog tone | False |
| `--glossary` | Comma-separated terms to preserve | "" |
| `--max-words` | Maximum words per chunk | 4000 |

## Technical Details

### Translation Process

1. **Text Chunking**: Splits input into paragraphs, then into word-limited chunks
2. **System Instruction**: Builds context-aware translation instructions
3. **API Call**: Uses OpenAI Responses API with temperature=0.2
4. **Output Assembly**: Rejoins translated chunks with proper formatting

### Model Configuration

```python
DEFAULT_MODEL = "gpt-4.1-mini"   # Quality/cost balanced
MAX_WORDS_PER_CHUNK = 4000       # Optimal chunk size
TEMPERATURE = 0.2                # Low temperature for consistency
```

### Translation Guidelines

The script instructs the AI to:
- Use natural or formal Tagalog based on the `--formal` flag
- Preserve names, technical terms, code blocks, numbers, and URLs
- Maintain proper Filipino grammar and prepositions
- Avoid literal translations when idiomatic equivalents exist
- Preserve custom glossary terms exactly as specified

## Security Best Practices

### API Key Protection

1. **Never commit keys to Git**: Use `.gitignore` to exclude files containing keys
2. **Use environment variables**: Always set keys via `OPENAI_API_KEY`
3. **Rotate keys regularly**: Change your API key if it ever gets exposed
4. **Clear shell history**: If you pasted the key directly:
   ```bash
   # Linux/macOS
   history -d
   
   # Windows PowerShell
   Remove-Item (Get-PSReadLineOption).HistorySavePath
   ```

### Alternative Setup Methods

**Using .env file:**
```bash
# Install python-dotenv
pip install python-dotenv

# Create .env file
echo "OPENAI_API_KEY=your-key-here" > .env

# Load in script (modify script to include):
from dotenv import load_dotenv
load_dotenv()
```

**Using a wrapper script:**
```bash
#!/bin/bash
# translate.sh
export OPENAI_API_KEY='your-key-here'
python translate_to_tagalog.py "$@"
```

## Error Handling

The script includes comprehensive error handling for:
- Missing API key
- Invalid file paths
- Empty input text
- API connection issues
- Missing dependencies

## Performance Considerations

- **Chunking**: Large texts are automatically split to stay within API limits
- **Rate Limiting**: Consider API rate limits for very large documents
- **Cost Optimization**: Uses gpt-4.1-mini by default; adjust model as needed
- **Memory Usage**: Processes text in chunks to minimize memory footprint

## Troubleshooting

### Common Issues

**"OPENAI_API_KEY is not set"**
- Verify the environment variable is set: `echo $OPENAI_API_KEY`
- Restart your terminal after setting the variable

**"Please install the official OpenAI Python SDK"**
- Run: `pip install --upgrade openai`

**Translation quality issues**
- Try the `--formal` flag for more precise translations
- Add problematic terms to the `--glossary` parameter
- Consider using a larger model with `--model gpt-4`

### Debug Mode

For troubleshooting, you can modify the script to add debug output:
```python
# Add to translate_chunk function
print(f"Translating chunk {idx}/{len(chunks)} ({word_count(chunk)} words)", file=sys.stderr)
```

## Cross-References

- [OpenAI API Documentation](https://platform.openai.com/docs/api-reference/responses)
- [OpenAI Python SDK](https://github.com/openai/openai-python)
- [Tagalog Language Resources](https://en.wikipedia.org/wiki/Tagalog_language)

## Conclusion

This script provides a robust, secure, and user-friendly way to translate English text to Tagalog using OpenAI's advanced language models. By following the security best practices and using the provided examples, you can safely and effectively translate documents while maintaining accuracy and preserving important terminology.

For questions or issues, ensure you have the latest version of the script and the OpenAI Python SDK installed.
