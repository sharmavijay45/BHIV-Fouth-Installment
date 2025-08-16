# Vaani Sentinel X Integration with BHIV Core

This guide explains how to use the Vaani Sentinel X integration that's now built into your existing BHIV Core system.

## 🚀 What's New

Your existing agents now automatically use Vaani capabilities when appropriate:
- **Auto-translation** to Hindi, Sanskrit, Marathi, and other languages
- **Content generation** for social media platforms
- **Voice generation** with language-specific voice tags
- **Platform optimization** for different social media channels

## 🔧 Configuration

The integration is configured in `config/agent_configs.json`. Each agent has a `vaani_integration` section:

```json
{
  "vedas_agent": {
    "vaani_integration": {
      "enabled": true,
      "auto_translate": true,
      "preferred_languages": ["en", "hi", "sa"],
      "content_type": "devotional",
      "voice_generation": true,
      "tone": "devotional"
    }
  }
}
```

## 📡 API Endpoints

### Agent Endpoints (Enhanced)
Your existing endpoints now return enhanced responses with Vaani features:

- `POST /ask-vedas` - Spiritual wisdom with auto-translation
- `POST /edumentor` - Educational content with multi-language support
- `POST /wellness` - Wellness advice with voice generation

### Direct Vaani Endpoints
- `POST /vaani/content/create` - Create content directly
- `POST /vaani/content/translate` - Translate existing content
- `POST /vaani/content/platform` - Generate platform-specific content
- `POST /vaani/voice/generate` - Generate voice content
- `GET /vaani/health` - Check Vaani system status
- `GET /vaani/agent-config/{agent_id}` - View agent Vaani settings

## 🎯 How It Works

### Automatic Detection
Agents automatically detect when to use Vaani based on:

1. **Language Triggers**: Words like "Hindi", "Sanskrit", "हिंदी", "संस्कृत"
2. **Content Triggers**: Words like "generate", "create", "write", "content"
3. **Voice Triggers**: Words like "voice", "audio", "speak", "tts"

### Response Enhancement
When Vaani is used, responses include:

```json
{
  "response": "Original response text",
  "vaani_used": true,
  "vaani_enhancements": {
    "translation": {
      "translated_text": "Translated content",
      "target_language": "hi",
      "original_text": "Original content"
    },
    "content_generation": {
      "generated_text": "Generated content",
      "prompt": "Original query",
      "content_type": "devotional"
    },
    "voice_generation": {
      "content_id": "voice_content_id",
      "voice_script": "Voice generation result",
      "language": "hi"
    }
  }
}
```

## 🧪 Testing

Run the test script to verify integration:

```bash
python test_vaani_integration_simple.py
```

This will test:
- Vaani API connectivity
- Agent responses with Vaani features
- Direct Vaani endpoints
- Agent configurations

## 💡 Usage Examples

### 1. Automatic Translation
```bash
curl -X POST "http://localhost:8001/ask-vedas" \
  -H "Content-Type: application/json" \
  -d '{"query": "Tell me about peace in Hindi", "user_id": "user123"}'
```

### 2. Content Generation
```bash
curl -X POST "http://localhost:8001/edumentor" \
  -H "Content-Type: application/json" \
  -d '{"query": "Generate content about meditation", "user_id": "user123"}'
```

### 3. Direct Vaani Usage
```bash
# Create content
curl -X POST "http://localhost:8001/vaani/content/create" \
  -H "Content-Type: application/json" \
  -d '{"text": "Peace and harmony", "content_type": "devotional", "language": "en"}'

# Translate content
curl -X POST "http://localhost:8001/vaani/content/translate" \
  -H "Content-Type: application/json" \
  -d '{"content_id": "content_id_here", "target_languages": ["hi"], "tone": "devotional"}'
```

## 🔍 Monitoring

### Health Check
```bash
curl "http://localhost:8001/vaani/health"
```

### Agent Configurations
```bash
curl "http://localhost:8001/vaani/agent-config/vedas_agent"
```

## 🛠️ Troubleshooting

### Common Issues

1. **Authentication Failed**
   - Check Vaani API credentials
   - Verify network connectivity to Vaani servers

2. **No Vaani Features**
   - Ensure agent has `vaani_integration.enabled: true`
   - Check if input triggers Vaani usage
   - Verify Vaani API health

3. **Translation Not Working**
   - Check if target language is in `preferred_languages`
   - Verify Vaani translation service availability

### Debug Mode
Enable detailed logging by setting log level to DEBUG in your logger configuration.

## 🌟 Features by Agent

| Agent | Languages | Content Type | Voice | Special Features |
|-------|-----------|--------------|-------|------------------|
| vedas_agent | en, hi, sa | devotional | ✅ | Sanskrit support |
| edumentor_agent | en, hi, mr | educational | ✅ | Learning content |
| wellness_agent | en, hi | wellness | ✅ | Calming tone |
| text_agent | en, hi, sa, mr | general | ✅ | Multi-language |
| knowledge_agent | en, hi, sa | informative | ❌ | Search-focused |

## 🔮 Future Enhancements

- **Real-time Translation**: Live translation during conversations
- **Voice Commands**: Voice input for agent interactions
- **Platform Analytics**: Track content performance across platforms
- **Custom Voice Models**: Train agent-specific voice profiles

## 📚 Additional Resources

- [Vaani Sentinel X Documentation](https://vaani-sentinel-gs6x.onrender.com/docs)
- [BHIV Core Documentation](./docs/)
- [Agent Configuration Guide](./config/)

---

**Note**: Vaani integration is automatically enabled for all configured agents. No additional setup required beyond the configuration file.
