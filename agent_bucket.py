import logging
import requests
import json
from typing import Dict, Any, List, Optional
from utils.logger import get_logger
import os

logger = get_logger(__name__)

def store_agent_data(data: dict):
    """JSON structure for agents."""
    logger.info(f"Storing agent data: {data}")
    return data

# Vaani Sentinel X Integration Functions
class VaaniIntegration:
    """Vaani Sentinel X integration for BHIV Core agents."""
    
    def __init__(self, agent_id: str = None):
        self.agent_id = agent_id
        self.base_url = None
        self.username = None
        self.password = None
        self.timeout = 30
        self.max_retries = 3
        self.session = requests.Session()
        self.access_token = None
        
        # Load configuration from agent config if agent_id is provided
        if agent_id:
            self.load_agent_config(agent_id)
        else:
            # Default configuration from environment variables
            self.base_url = os.getenv("VAANI_BASE_URL", "https://vaani-sentinel-gs6x.onrender.com")
            self.username = os.getenv("VAANI_USERNAME", "admin")
            self.password = os.getenv("VAANI_PASSWORD", "secret")
            self.timeout = int(os.getenv("VAANI_REQUEST_TIMEOUT", "30"))
            self.max_retries = int(os.getenv("VAANI_MAX_RETRIES", "3"))
    
    def load_agent_config(self, agent_id: str):
        """Load Vaani configuration from agent configs."""
        try:
            with open("config/agent_configs.json", "r") as f:
                agent_configs = json.load(f)
            
            agent_config = agent_configs.get(agent_id)
            if agent_config and "vaani_integration" in agent_config:
                vaani_config = agent_config["vaani_integration"]
                env_config = vaani_config.get("environment_config", {})
                
                # Load values from environment variables
                self.base_url = os.getenv(env_config.get("base_url", "VAANI_BASE_URL"), 
                                        "https://vaani-sentinel-gs6x.onrender.com")
                self.username = os.getenv(env_config.get("username", "VAANI_USERNAME"), "admin")
                self.password = os.getenv(env_config.get("password", "VAANI_PASSWORD"), "secret")
                self.timeout = int(os.getenv(env_config.get("timeout", "VAANI_REQUEST_TIMEOUT"), "30"))
                self.max_retries = int(os.getenv(env_config.get("max_retries", "VAANI_MAX_RETRIES"), "3"))
                
                logger.info(f"Loaded Vaani config for agent {agent_id}: {self.base_url}")
            else:
                logger.warning(f"No Vaani config found for agent {agent_id}, using defaults")
                self._load_default_config()
                
        except Exception as e:
            logger.error(f"Failed to load agent config for {agent_id}: {str(e)}")
            self._load_default_config()
    
    def _load_default_config(self):
        """Load default configuration from environment variables."""
        self.base_url = os.getenv("VAANI_BASE_URL", "https://vaani-sentinel-gs6x.onrender.com")
        self.username = os.getenv("VAANI_USERNAME", "admin")
        self.password = os.getenv("VAANI_PASSWORD", "secret")
        self.timeout = int(os.getenv("VAANI_REQUEST_TIMEOUT", "30"))
        self.max_retries = int(os.getenv("VAANI_MAX_RETRIES", "3"))
        
    def authenticate(self, username: str = None, password: str = None) -> bool:
        """Authenticate with Vaani API."""
        try:
            # Use provided credentials or loaded ones
            auth_username = username or self.username
            auth_password = password or self.password
            
            if not auth_username or not auth_password:
                logger.error("No username or password available for Vaani authentication")
                return False
            
            auth_data = {"username": auth_username, "password": auth_password}
            response = self.session.post(
                f"{self.base_url}/api/v1/auth/login",
                json=auth_data,
                timeout=self.timeout
            )
            response.raise_for_status()
            
            auth_response = response.json()
            self.access_token = auth_response.get("access_token")
            
            if self.access_token:
                self.session.headers.update({
                    'Authorization': f'Bearer {self.access_token}'
                })
                logger.info(f"Vaani authentication successful for agent {self.agent_id or 'default'}")
                return True
            return False
            
        except Exception as e:
            logger.error(f"Vaani authentication failed for agent {self.agent_id or 'default'}: {str(e)}")
            return False
    
    def create_content(self, text: str, content_type: str = "tweet", 
                      language: str = "en", metadata: Dict[str, Any] = None) -> Optional[Dict[str, Any]]:
        """Create content using Vaani."""
        if not self.access_token:
            logger.error("Not authenticated with Vaani")
            return None
            
        try:
            payload = {
                "text": str(text),  # Ensure text is string
                "content_type": str(content_type),  # Ensure content_type is string
                "language": str(language)  # Ensure language is string
            }
            if metadata:
                # Ensure all metadata values are strings
                payload["metadata"] = {str(k): str(v) for k, v in metadata.items()}
                
            # Log the payload as JSON string to verify format
            payload_json = json.dumps(payload, ensure_ascii=False)
            logger.info(f"Creating content with payload JSON: {payload_json}")
                
            response = self.session.post(
                f"{self.base_url}/api/v1/content/create",
                json=payload,
                timeout=30
            )
            response.raise_for_status()
            return response.json()
            
        except Exception as e:
            logger.error(f"Content creation failed: {str(e)}")
            return None
    
    def translate_content(self, content_id: str, target_languages: List[str], 
                        tone: str = "casual") -> Optional[Dict[str, Any]]:
        """Translate content to specified languages using platform content generation."""
        if not self.access_token:
            logger.error("Not authenticated with Vaani")
            return None
            
        try:
            logger.info(f"Attempting to translate content {content_id} to languages: {target_languages}")
            
            # Use platform content generation for translation with target language
            payload = {
                "content_id": str(content_id),  # Ensure content_id is string
                "platforms": ["twitter"],  # Use a default platform for translation
                "tone": str(tone),  # Ensure tone is string
                "language": str(target_languages[0] if target_languages else "en")  # Ensure language is string
            }
            
            # Log the payload as JSON string to verify format
            payload_json = json.dumps(payload, ensure_ascii=False)
            logger.info(f"Using platform content generation for translation with payload JSON: {payload_json}")
            
            response = self.session.post(
                f"{self.base_url}/api/v1/agents/generate-content",  # FIXED: Correct working endpoint
                json=payload,
                timeout=30
            )
            response.raise_for_status()
            
            result = response.json()
            logger.info(f"Translation response received: {result}")
            
            # Extract translated text from the platform content response
            if result and "generated_content" in result:
                generated_content = result["generated_content"]
                if "twitter" in generated_content:
                    translated_text = generated_content["twitter"]
                    logger.info(f"Successfully extracted translated text: {translated_text[:100]}...")
                    
                    # Return in the expected format for the calling function
                    return {
                        "translations": {
                            target_languages[0]: {
                                "text": translated_text,
                                "language": target_languages[0]
                            }
                        }
                    }
            
            logger.warning(f"Translation response format unexpected: {result}")
            return None
            
        except Exception as e:
            logger.error(f"Translation failed: {str(e)}")
            return None
    
    def generate_platform_content(self, content_id: str, platforms: List[str], 
                                tone: str = "casual", language: str = "en") -> Optional[Dict[str, Any]]:
        """Generate platform-specific content."""
        if not self.access_token:
            logger.error("Not authenticated with Vaani")
            return None
            
        try:
            logger.info(f"Generating platform content for content_id: {content_id}, platforms: {platforms}")
            payload = {
                "content_id": str(content_id),  # Ensure content_id is string
                "platforms": [str(p) for p in platforms],  # Ensure all platforms are strings
                "tone": str(tone),  # Ensure tone is string
                "language": str(language)  # Ensure language is string
            }
            
            # Log the payload as JSON string to verify format
            payload_json = json.dumps(payload, ensure_ascii=False)
            logger.info(f"Platform content generation payload JSON: {payload_json}")
            
            response = self.session.post(
                f"{self.base_url}/api/v1/agents/generate-content",  # FIXED: Correct working endpoint
                json=payload,
                timeout=30
            )
            response.raise_for_status()
            
            result = response.json()
            logger.info(f"Platform content generation successful for content_id: {content_id}")
            return result
            
        except Exception as e:
            logger.error(f"Platform content generation failed: {str(e)}")
            return None
    
    def generate_voice_content(self, content_id: str, language: str = "en",
                             tone: str = "casual", voice_tag: str = None) -> Optional[Dict[str, Any]]:
        """Generate voice content."""
        if not self.access_token:
            logger.error("Not authenticated with Vaani")
            return None
            
        try:
            logger.info(f"Generating voice content for content_id: {content_id}, language: {language}")
            payload = {
                "content_id": str(content_id),  # Ensure content_id is string
                "language": str(language),  # Ensure language is string
                "tone": str(tone)  # Ensure tone is string
            }
            if voice_tag:
                payload["voice_tag"] = str(voice_tag)  # Ensure voice_tag is string
                
            # Log the payload as JSON string to verify format
            payload_json = json.dumps(payload, ensure_ascii=False)
            logger.info(f"Voice generation payload JSON: {payload_json}")
            
            response = self.session.post(
                f"{self.base_url}/api/v1/agents/generate-voice",  # FIXED: Correct working endpoint
                json=payload,
                timeout=30
            )
            response.raise_for_status()
            
            result = response.json()
            logger.info(f"Voice generation successful for content_id: {content_id}")
            return result
            
        except Exception as e:
            logger.error(f"Voice generation failed: {str(e)}")
            return None
    
    def health_check(self) -> bool:
        """Check Vaani API health."""
        try:
            response = self.session.get(f"{self.base_url}/health", timeout=10)
            return response.status_code == 200
        except Exception as e:
            logger.error(f"Vaani health check failed: {str(e)}")
            return False
    
    def close(self):
        """Close session."""
        if self.session:
            self.session.close()

    def detect_language(self, content: str) -> Optional[Dict[str, Any]]:
        """Detect the language of given text using Vaani's language detection API."""
        if not self.access_token:
            logger.error("Not authenticated with Vaani")
            return None
            
        try:
            logger.info(f"Detecting language for content: {content[:100]}...")
            payload = {"content": str(content)}
            
            response = self.session.post(
                f"{self.base_url}/api/v1/multilingual/detect-language",
                json=payload,
                timeout=30
            )
            response.raise_for_status()
            
            result = response.json()
            logger.info(f"Language detection successful: {result}")
            return result
            
        except Exception as e:
            logger.error(f"Language detection failed: {str(e)}")
            return None
    
    def analyze_content_security(self, content_id: str) -> Optional[Dict[str, Any]]:
        """Analyze content for security risks using Vaani's security API."""
        if not self.access_token:
            logger.error("Not authenticated with Vaani")
            return None
            
        try:
            logger.info(f"Analyzing content security for content_id: {content_id}")
            payload = {"content_id": str(content_id)}
            
            response = self.session.post(
                f"{self.base_url}/api/v1/security/analyze-content",
                json=payload,
                timeout=30
            )
            response.raise_for_status()
            
            result = response.json()
            logger.info(f"Security analysis successful: {result}")
            return result
            
        except Exception as e:
            logger.error(f"Security analysis failed: {str(e)}")
            return None
    
    def generate_engagement_metrics(self, post_id: str, platform: str, content_type: str, 
                                  language: str, posting_time: str = None) -> Optional[Dict[str, Any]]:
        """Generate engagement metrics for a post using Vaani's analytics API."""
        if not self.access_token:
            logger.error("Not authenticated with Vaani")
            return None
            
        try:
            logger.info(f"Generating engagement metrics for post: {post_id}")
            payload = {
                "post_id": str(post_id),
                "platform": str(platform),
                "content_type": str(content_type),
                "language": str(language)
            }
            
            if posting_time:
                payload["posting_time"] = str(posting_time)
            
            response = self.session.post(
                f"{self.base_url}/api/v1/analytics/generate-engagement",
                json=payload,
                timeout=30
            )
            response.raise_for_status()
            
            result = response.json()
            logger.info(f"Engagement metrics generation successful: {result}")
            return result
            
        except Exception as e:
            logger.error(f"Engagement metrics generation failed: {str(e)}")
            return None
    
    def get_performance_insights(self, days: int = 7) -> Optional[Dict[str, Any]]:
        """Get performance insights for specified time period using Vaani's analytics API."""
        if not self.access_token:
            logger.error("Not authenticated with Vaani")
            return None
            
        try:
            logger.info(f"Getting performance insights for {days} days")
            
            response = self.session.get(
                f"{self.base_url}/api/v1/analytics/performance-insights?days={days}",
                timeout=30
            )
            response.raise_for_status()
            
            result = response.json()
            logger.info(f"Performance insights retrieval successful: {result}")
            return result
            
        except Exception as e:
            logger.error(f"Performance insights retrieval failed: {str(e)}")
            return None
    
    def get_supported_platforms(self) -> Optional[Dict[str, Any]]:
        """Get list of all supported social media platforms using Vaani's agents API."""
        if not self.access_token:
            logger.error("Not authenticated with Vaani")
            return None
            
        try:
            logger.info("Getting supported platforms from Vaani")
            
            response = self.session.get(
                f"{self.base_url}/api/v1/agents/platforms",
                timeout=30
            )
            response.raise_for_status()
            
            result = response.json()
            logger.info(f"Supported platforms retrieval successful: {result}")
            return result
            
        except Exception as e:
            logger.error(f"Supported platforms retrieval failed: {str(e)}")
            return None
    
    def get_supported_tones(self) -> Optional[Dict[str, Any]]:
        """Get list of all supported content tones using Vaani's agents API."""
        if not self.access_token:
            logger.error("Not authenticated with Vaani")
            return None
            
        try:
            logger.info("Getting supported tones from Vaani")
            
            response = self.session.get(
                f"{self.base_url}/api/v1/agents/tones",
                timeout=30
            )
            response.raise_for_status()
            
            result = response.json()
            logger.info(f"Supported tones retrieval successful: {result}")
            return result
            
        except Exception as e:
            logger.error(f"Supported tones retrieval failed: {str(e)}")
            return None
    
    def get_supported_languages(self) -> Optional[Dict[str, Any]]:
        """Get list of all supported languages using Vaani's agents API."""
        if not self.access_token:
            logger.error("Not authenticated with Vaani")
            return None
            
        try:
            logger.info("Getting supported languages from Vaani")
            
            response = self.session.get(
                f"{self.base_url}/api/v1/agents/languages",
                timeout=30
            )
            response.raise_for_status()
            
            result = response.json()
            logger.info(f"Supported languages retrieval successful: {result}")
            return result
            
        except Exception as e:
            logger.error(f"Supported languages retrieval failed: {str(e)}")
            return None
    
    def batch_generate_content(self, content_ids: List[str], platforms: List[str], 
                              tone: str = "uplifting", language: str = "en") -> Optional[Dict[str, Any]]:
        """Generate content for multiple items at once using Vaani's batch API."""
        if not self.access_token:
            logger.error("Not authenticated with Vaani")
            return None
            
        try:
            logger.info(f"Batch generating content for {len(content_ids)} items")
            payload = {
                "content_ids": [str(cid) for cid in content_ids],
                "platforms": [str(p) for p in platforms],
                "tone": str(tone),
                "language": str(language)
            }
            
            response = self.session.post(
                f"{self.base_url}/api/v1/agents/batch-generate",
                json=payload,
                timeout=60  # Longer timeout for batch operations
            )
            response.raise_for_status()
            
            result = response.json()
            logger.info(f"Batch content generation successful for {len(content_ids)} items")
            return result
            
        except Exception as e:
            logger.error(f"Batch content generation failed: {str(e)}")
            return None
    
    def batch_translate_content(self, content_ids: List[str], target_languages: List[str]) -> Optional[Dict[str, Any]]:
        """Translate multiple content items at once using Vaani's multilingual API."""
        if not self.access_token:
            logger.error("Not authenticated with Vaani")
            return None
            
        try:
            logger.info(f"Batch translating {len(content_ids)} items to {len(target_languages)} languages")
            payload = {
                "content_ids": [str(cid) for cid in content_ids],
                "target_languages": [str(lang) for lang in target_languages]
            }
            
            response = self.session.post(
                f"{self.base_url}/api/v1/multilingual/batch-translate",
                json=payload,
                timeout=60  # Longer timeout for batch operations
            )
            response.raise_for_status()
            
            result = response.json()
            logger.info(f"Batch translation successful for {len(content_ids)} items")
            return result
            
        except Exception as e:
            logger.error(f"Batch translation failed: {str(e)}")
            return None

# Global Vaani instance (default configuration)
vaani_integration = VaaniIntegration()

def get_vaani_integration(agent_id: str = None) -> VaaniIntegration:
    """Get Vaani integration instance for a specific agent or default."""
    if agent_id:
        return VaaniIntegration(agent_id)
    return vaani_integration

def auto_translate_for_agent(agent_id: str, text: str, target_language: str) -> str:
    """Automatically translate text for a specific agent using Vaani."""
    try:
        logger.info(f"Starting auto-translation for agent {agent_id} to {target_language}")
        vaani = VaaniIntegration(agent_id)
        if not vaani.access_token:
            if not vaani.authenticate():
                logger.warning(f"Vaani authentication failed for agent {agent_id}")
                return text
        
        # Create content first - FIXED: Changed "response" to "tweet"
        logger.info(f"Creating content for translation with type 'tweet'")
        content_result = vaani.create_content(
            text, "tweet", "en", {"agent_id": agent_id}
        )
        
        if not content_result:
            logger.error(f"Content creation failed for translation in agent {agent_id}")
            return text
            
        content_id = content_result.get("content_id")
        if not content_id:
            logger.error(f"No content_id received for translation in agent {agent_id}")
            return text
            
        logger.info(f"Content created successfully for translation. Content ID: {content_id}")
        logger.info(f"Now proceeding to translate content to {target_language}")
        
        # Translate content using the CORRECT endpoint
        translation_result = vaani.translate_content(
            content_id, [target_language], "uplifting"  # FIXED: Changed from "informative" to "uplifting"
        )
        
        if translation_result and "translations" in translation_result:
            for lang, content in translation_result["translations"].items():
                if lang == target_language:
                    translated_text = content.get("text", text)
                    logger.info(f"Translation successful! Text translated to {target_language} for agent {agent_id}")
                    return translated_text
        
        logger.warning(f"Translation failed or no translations received for agent {agent_id}")
        return text
        
    except Exception as e:
        logger.error(f"Auto-translation failed for agent {agent_id}: {str(e)}")
        return text

def generate_content_for_agent(agent_id: str, prompt: str, content_type: str = "tweet") -> Optional[str]:
    """Generate content for a specific agent using Vaani."""
    try:
        logger.info(f"Starting content generation for agent {agent_id} with type '{content_type}'")
        vaani = VaaniIntegration(agent_id)
        if not vaani.access_token:
            if not vaani.authenticate():
                logger.warning(f"Vaani authentication failed for agent {agent_id}")
                return None
        
        # Step 1: Create content to get content_id
        logger.info(f"Step 1: Creating initial content to get content_id")
        content_result = vaani.create_content(
            prompt, content_type, "en", {"agent_id": agent_id}
        )
        
        if not content_result or "content_id" not in content_result:
            logger.error(f"Content creation failed or no content_id received for agent {agent_id}")
            return None
            
        content_id = content_result["content_id"]
        logger.info(f"Content created successfully! Content ID: {content_id}")
        
        # Step 2: Generate platform-specific content using the content_id
        logger.info(f"Step 2: Now generating platform-specific content using content_id: {content_id}")
        agent_config = get_agent_vaani_config(agent_id)
        platforms = agent_config.get("supported_platforms", ["twitter"])
        logger.info(f"Target platforms: {platforms}")
        
        platform_result = vaani.generate_platform_content(
            content_id, platforms, "uplifting", "en"  # FIXED: Changed from "informative" to "uplifting"
        )
        
        if platform_result and "generated_content" in platform_result:
            # Return the first available platform content
            generated_content = platform_result["generated_content"]
            first_platform = list(generated_content.keys())[0]
            logger.info(f"Platform content generated successfully! Using {first_platform} content")
            return generated_content[first_platform]
        
        logger.warning(f"Platform content generation failed for agent {agent_id}")
        return None
        
    except Exception as e:
        logger.error(f"Content generation failed for agent {agent_id}: {str(e)}")
        return None

def generate_voice_for_agent(agent_id: str, text: str, language: str = "en") -> Optional[Dict[str, Any]]:
    """Generate voice content for a specific agent using Vaani."""
    try:
        logger.info(f"Starting voice generation for agent {agent_id} in {language}")
        vaani = VaaniIntegration(agent_id)
        if not vaani.access_token:
            if not vaani.authenticate():
                logger.warning(f"Vaani authentication failed for agent {agent_id}")
                return None
        
        # Create content first - FIXED: Changed "voice" to "tweet"
        logger.info(f"Creating content for voice generation with type 'tweet'")
        content_result = vaani.create_content(
            text, "tweet", language, {"agent_id": agent_id}
        )
        
        if not content_result:
            logger.error(f"Content creation failed for voice generation in agent {agent_id}")
            return None
            
        content_id = content_result.get("content_id")
        if not content_id:
            logger.error(f"No content_id received for voice generation in agent {agent_id}")
            return None
            
        logger.info(f"Content created successfully for voice generation. Content ID: {content_id}")
        logger.info(f"Now proceeding to generate voice content")
        
        # Generate voice using the CORRECT endpoint
        voice_result = vaani.generate_voice_content(
            content_id, language, "uplifting"  # FIXED: Changed from "informative" to "uplifting"
        )
        
        if voice_result:
            logger.info(f"Voice generation successful for agent {agent_id}")
            return voice_result
        
        logger.warning(f"Voice generation failed for agent {agent_id}")
        return None
        
    except Exception as e:
        logger.error(f"Voice generation failed for agent {agent_id}: {str(e)}")
        return None

def get_agent_vaani_config(agent_id: str) -> Optional[Dict[str, Any]]:
    """Get Vaani configuration for a specific agent."""
    try:
        # Load agent configs
        with open("config/agent_configs.json", "r") as f:
            agent_configs = json.load(f)
        
        agent_config = agent_configs.get(agent_id)
        if agent_config:
            return agent_config.get("vaani_integration")
        
        return None
        
    except Exception as e:
        logger.error(f"Failed to get Vaani config for agent {agent_id}: {str(e)}")
        return None

def should_use_vaani(agent_id: str, input_text: str, operation: str = None) -> bool:
    """Intelligently determine if and how Vaani should be used for the given agent and input."""
    try:
        logger.info(f"🔍 Intelligent Vaani detection for agent {agent_id}, operation: {operation}")
        vaani_config = get_agent_vaani_config(agent_id)
        if not vaani_config or not vaani_config.get("enabled"):
            logger.info(f"❌ Vaani not enabled for agent {agent_id}")
            return False
        
        input_lower = input_text.lower()
        
        # 🎯 PRIORITY 1: Direct Translation Requests (HIGHEST PRIORITY)
        if operation in ["translate", "language"] or operation is None:
            logger.info(f"🔍 Checking for translation triggers in input text")
            
            # Direct translation keywords
            translation_keywords = [
                "translate", "translation", "convert", "in hindi", "in sanskrit", "in marathi",
                "हिंदी में", "संस्कृत में", "मराठी में", "to hindi", "to sanskrit", "to marathi",
                "translate this", "convert to", "change language", "switch to"
            ]
            
            if any(keyword in input_lower for keyword in translation_keywords):
                logger.info(f"🎯 Translation request detected! Vaani will be used for direct translation")
                return True
        
        # 🎯 PRIORITY 2: Content Creation & Generation Requests
        if operation in ["generate", "content", "create"] or operation is None:
            logger.info(f"🔍 Checking for content creation triggers in input text")
            
            # Content creation keywords
            content_keywords = [
                "generate", "create", "write", "content", "post", "tweet", "instagram", "linkedin",
                "social media", "caption", "description", "bio", "story", "article", "blog",
                "inspirational", "motivational", "devotional", "educational", "informative"
            ]
            
            if any(keyword in input_lower for keyword in content_keywords):
                logger.info(f"🎯 Content creation request detected! Vaani will be used for content generation")
                return True
            
            # Platform-specific requests
            platform_keywords = {
                "twitter": ["tweet", "twitter post", "twitter content"],
                "instagram": ["instagram", "ig post", "instagram caption", "story"],
                "linkedin": ["linkedin", "professional post", "business content"],
                "facebook": ["facebook", "fb post", "status update"]
            }
            
            for platform, keywords in platform_keywords.items():
                if any(keyword in input_lower for keyword in keywords):
                    logger.info(f"🎯 {platform.title()} content request detected! Vaani will be used for platform-specific content")
                    return True
        
        # 🎯 PRIORITY 3: Voice & Audio Generation Requests
        if operation in ["voice", "audio", "speech"] or operation is None:
            logger.info(f"🔍 Checking for voice generation triggers in input text")
            
            voice_keywords = [
                "voice", "audio", "speak", "tts", "text to speech", "voice over", "narration",
                "podcast", "voice script", "audio content", "voice tag", "voice generation"
            ]
            
            if any(keyword in input_lower for keyword in voice_keywords):
                logger.info(f"🎯 Voice generation request detected! Vaani will be used for voice content")
                return True
        
        # 🎯 PRIORITY 4: Multilingual Processing Requests
        if operation in ["multilingual", "language_detection"] or operation is None:
            logger.info(f"🔍 Checking for multilingual processing triggers in input text")
            
            multilingual_keywords = [
                "detect language", "language detection", "what language", "which language",
                "multilingual", "multiple languages", "language processing", "auto detect"
            ]
            
            if any(keyword in input_lower for keyword in multilingual_keywords):
                logger.info(f"🎯 Multilingual processing request detected! Vaani will be used for language detection")
                return True
        
        # 🎯 PRIORITY 5: Analytics & Performance Requests
        if operation in ["analytics", "performance", "metrics"] or operation is None:
            logger.info(f"🔍 Checking for analytics triggers in input text")
            
            analytics_keywords = [
                "analytics", "performance", "metrics", "engagement", "views", "likes", "shares",
                "insights", "strategy", "trends", "comparison", "dashboard", "reports",
                "how well", "performance analysis", "engagement metrics"
            ]
            
            if any(keyword in input_lower for keyword in analytics_keywords):
                logger.info(f"🎯 Analytics request detected! Vaani will be used for performance insights")
                return True
        
        # 🎯 PRIORITY 6: Security & Content Analysis Requests
        if operation in ["security", "analysis", "safety"] or operation is None:
            logger.info(f"🔍 Checking for security triggers in input text")
            
            security_keywords = [
                "security", "safe", "appropriate", "inappropriate", "content analysis",
                "risk assessment", "security check", "content safety", "moderation",
                "encrypt", "secure", "protect", "safety check"
            ]
            
            if any(keyword in input_lower for keyword in security_keywords):
                logger.info(f"🎯 Security request detected! Vaani will be used for content safety analysis")
                return True
        
        # 🎯 PRIORITY 7: Batch Processing Requests
        if operation in ["batch", "bulk", "multiple"] or operation is None:
            logger.info(f"🔍 Checking for batch processing triggers in input text")
            
            batch_keywords = [
                "batch", "bulk", "multiple", "several", "many", "all", "process all",
                "generate multiple", "create several", "translate all", "batch process"
            ]
            
            if any(keyword in input_lower for keyword in batch_keywords):
                logger.info(f"🎯 Batch processing request detected! Vaani will be used for bulk operations")
                return True
        
        # 🎯 PRIORITY 8: Language-Specific Content Requests (Content + Language)
        if operation in ["language_content", "multilingual_content"] or operation is None:
            logger.info(f"🔍 Checking for language-specific content requests")
            
            # Check if this is a content request in a specific language
            language_indicators = ["hindi", "sanskrit", "marathi", "हिंदी", "संस्कृत", "मराठी"]
            content_indicators = ["what is", "explain", "tell me about", "describe", "how to", "guide", "tutorial"]
            
            has_language = any(lang in input_lower for lang in language_indicators)
            has_content_request = any(indicator in input_lower for indicator in content_indicators)
            
            if has_language and has_content_request:
                logger.info(f"🎯 Language-specific content request detected! Vaani will be used for content creation + translation")
                return True
            elif has_language and not has_content_request:
                logger.info(f"🎯 Language-only request detected! Vaani will be used for translation")
                return True
        
        # 🎯 PRIORITY 9: Tone & Style Requests
        if operation in ["tone", "style", "mood"] or operation is None:
            logger.info(f"🔍 Checking for tone/style triggers in input text")
            
            tone_keywords = [
                "tone", "style", "mood", "uplifting", "devotional", "casual", "formal", "neutral",
                "inspirational", "motivational", "professional", "friendly", "serious", "funny"
            ]
            
            if any(keyword in input_lower for keyword in tone_keywords):
                logger.info(f"🎯 Tone/style request detected! Vaani will be used for tone-specific content")
                return True
        
        # 🎯 PRIORITY 10: Platform Optimization Requests
        if operation in ["optimize", "platform_specific"] or operation is None:
            logger.info(f"🔍 Checking for platform optimization triggers in input text")
            
            optimize_keywords = [
                "optimize", "optimization", "platform specific", "best for", "tailored for",
                "twitter optimized", "instagram ready", "linkedin professional", "social media ready"
            ]
            
            if any(keyword in input_lower for keyword in optimize_keywords):
                logger.info(f"🎯 Platform optimization request detected! Vaani will be used for platform-specific content")
                return True
        
        logger.info(f"❌ No specific Vaani triggers found for agent {agent_id}")
        return False
        
    except Exception as e:
        logger.error(f"❌ Failed to determine Vaani usage for agent {agent_id}: {str(e)}")
        return False

def direct_translate_text(agent_id: str, text: str, target_language: str) -> Optional[str]:
    """Directly translate text using Vaani's translation capabilities."""
    try:
        logger.info(f"Starting direct translation for agent {agent_id} to {target_language}")
        vaani = VaaniIntegration(agent_id)
        if not vaani.access_token:
            if not vaani.authenticate():
                logger.warning(f"Vaani authentication failed for agent {agent_id}")
                return None
        
        # For direct translation, we'll use a simple approach
        # Create content in source language first
        logger.info(f"Creating content for direct translation")
        content_result = vaani.create_content(
            text, "tweet", "en", {"agent_id": agent_id, "translation_request": True}
        )
        
        if not content_result:
            logger.error(f"Content creation failed for direct translation in agent {agent_id}")
            return None
            
        content_id = content_result.get("content_id")
        if not content_id:
            logger.error(f"No content_id received for direct translation in agent {agent_id}")
            return None
            
        logger.info(f"Content created successfully for direct translation. Content ID: {content_id}")
        logger.info(f"Now proceeding to translate content to {target_language}")
        
        # Use platform content generation with target language for translation
        # This will generate content in the target language based on the source text
        translation_result = vaani.generate_platform_content(
            content_id, ["twitter"], "uplifting", target_language
        )
        
        if translation_result and "generated_content" in translation_result:
            generated_content = translation_result["generated_content"]
            if "twitter" in generated_content:
                translated_text = generated_content["twitter"]
                logger.info(f"Direct translation successful! Text translated to {target_language}")
                return translated_text
        
        logger.warning(f"Direct translation failed for agent {agent_id}")
        return None
        
    except Exception as e:
        logger.error(f"Direct translation failed for agent {agent_id}: {str(e)}")
        return None

def enhanced_agent_response(agent_id: str, input_text: str, base_response: str) -> Dict[str, Any]:
    """Generate intelligent enhanced response for an agent using Vaani capabilities."""
    enhanced_result = {
        "original_response": base_response,
        "enhanced_features": {},
        "vaani_used": False,
        "request_type": "unknown"
    }
    
    try:
        logger.info(f"🚀 Starting intelligent enhanced response generation for agent {agent_id}")
        vaani_config = get_agent_vaani_config(agent_id)
        if not vaani_config or not vaani_config.get("enabled"):
            logger.info(f"❌ Vaani integration disabled for agent {agent_id}")
            return enhanced_result
        
        logger.info(f"✅ Vaani integration enabled for agent {agent_id}. Processing intelligent enhancements...")
        enhanced_result["vaani_used"] = True
        
        input_lower = input_text.lower()
        
        # 🎯 INTELLIGENT REQUEST TYPE DETECTION
        request_type = "unknown"
        
        # 1. Translation Request Detection
        translation_keywords = [
            "translate", "translation", "convert", "in hindi", "in sanskrit", "in marathi",
            "हिंदी में", "संस्कृत में", "मराठी में", "to hindi", "to sanskrit", "to marathi",
            "translate this", "convert to", "change language", "switch to"
        ]
        
        if any(keyword in input_lower for keyword in translation_keywords):
            request_type = "translation"
            enhanced_result["request_type"] = "translation"
            logger.info(f"🎯 Translation request detected! Processing with Vaani translation")
        
        # 2. Content Creation Request Detection
        elif any(keyword in input_lower for keyword in ["generate", "create", "write", "content", "post", "tweet", "instagram", "linkedin"]):
            request_type = "content_creation"
            enhanced_result["request_type"] = "content_creation"
            logger.info(f"🎯 Content creation request detected! Processing with Vaani content generation")
        
        # 3. Voice Generation Request Detection
        elif any(keyword in input_lower for keyword in ["voice", "audio", "speak", "tts", "text to speech"]):
            request_type = "voice_generation"
            enhanced_result["request_type"] = "voice_generation"
            logger.info(f"🎯 Voice generation request detected! Processing with Vaani voice generation")
        
        # 4. Analytics Request Detection
        elif any(keyword in input_lower for keyword in ["analytics", "performance", "metrics", "engagement", "insights"]):
            request_type = "analytics"
            enhanced_result["request_type"] = "analytics"
            logger.info(f"🎯 Analytics request detected! Processing with Vaani analytics")
        
        # 5. Security Request Detection
        elif any(keyword in input_lower for keyword in ["security", "safe", "appropriate", "content analysis", "safety"]):
            request_type = "security"
            enhanced_result["request_type"] = "security"
            logger.info(f"🎯 Security request detected! Processing with Vaani security analysis")
        
        # 6. Multilingual Processing Request Detection
        elif any(keyword in input_lower for keyword in ["detect language", "language detection", "what language", "multilingual"]):
            request_type = "multilingual_processing"
            enhanced_result["request_type"] = "multilingual_processing"
            logger.info(f"🎯 Multilingual processing request detected! Processing with Vaani language detection")
        
        # 7. Batch Processing Request Detection
        elif any(keyword in input_lower for keyword in ["batch", "bulk", "multiple", "several", "process all"]):
            request_type = "batch_processing"
            enhanced_result["request_type"] = "batch_processing"
            logger.info(f"🎯 Batch processing request detected! Processing with Vaani batch operations")
        
        # 8. Platform Optimization Request Detection
        elif any(keyword in input_lower for keyword in ["optimize", "platform specific", "best for", "tailored for"]):
            request_type = "platform_optimization"
            enhanced_result["request_type"] = "platform_optimization"
            logger.info(f"🎯 Platform optimization request detected! Processing with Vaani platform-specific content")
        
        # 9. Tone/Style Request Detection
        elif any(keyword in input_lower for keyword in ["tone", "style", "mood", "uplifting", "devotional", "casual", "formal"]):
            request_type = "tone_style"
            enhanced_result["request_type"] = "tone_style"
            logger.info(f"🎯 Tone/style request detected! Processing with Vaani tone-specific content")
        
        # 10. Language-Specific Content Request Detection
        elif any(lang in input_lower for lang in ["hindi", "sanskrit", "marathi", "हिंदी", "संस्कृत", "मराठी"]):
            if any(indicator in input_lower for indicator in ["what is", "explain", "tell me about", "describe", "how to"]):
                request_type = "language_specific_content"
                enhanced_result["request_type"] = "language_specific_content"
                logger.info(f"🎯 Language-specific content request detected! Processing with Vaani content + translation")
            else:
                request_type = "translation"
                enhanced_result["request_type"] = "translation"
                logger.info(f"🎯 Language request detected! Processing with Vaani translation")
        
        else:
            request_type = "general_enhancement"
            enhanced_result["request_type"] = "general_enhancement"
            logger.info(f"🎯 General enhancement request detected! Processing with Vaani general features")
        
        # 🚀 PROCESSING BASED ON DETECTED REQUEST TYPE
        
        # 1. TRANSLATION PROCESSING
        if request_type == "translation":
            logger.info(f"🔄 Processing translation request for agent {agent_id}")
            if vaani_config.get("auto_translate"):
                preferred_languages = vaani_config.get("preferred_languages", ["hi"])
                logger.info(f"🌍 Preferred languages for translation: {preferred_languages}")
                
                for lang in preferred_languages:
                    if lang != "en":
                        logger.info(f"🔄 Attempting translation to {lang}")
                        translated_response = direct_translate_text(agent_id, base_response, lang)
                        
                        if translated_response and translated_response != base_response:
                            logger.info(f"✅ Translation successful! Adding {lang} translation")
                            enhanced_result["enhanced_features"]["translation"] = {
                                "translated_text": translated_response,
                                "target_language": lang,
                                "original_text": base_response,
                                "translation_type": "direct",
                                "request_type": "translation"
                            }
                            break
                        else:
                            logger.warning(f"❌ Translation to {lang} failed for agent {agent_id}")
        
        # 2. CONTENT CREATION PROCESSING
        elif request_type == "content_creation":
            logger.info(f"📝 Processing content creation request for agent {agent_id}")
            if should_use_vaani(agent_id, input_text, "generate"):
                content_type = vaani_config.get("content_type", "tweet")
                logger.info(f"📝 Using content type: {content_type}")
                
                generated_content = generate_content_for_agent(agent_id, input_text, content_type)
                if generated_content:
                    logger.info(f"✅ Content generation successful!")
                    enhanced_result["enhanced_features"]["content_generation"] = {
                        "generated_text": generated_content,
                        "prompt": input_text,
                        "content_type": content_type,
                        "request_type": "content_creation"
                    }
                else:
                    logger.warning(f"❌ Content generation failed for agent {agent_id}")
        
        # 3. VOICE GENERATION PROCESSING
        elif request_type == "voice_generation":
            logger.info(f"🎵 Processing voice generation request for agent {agent_id}")
            if vaani_config.get("voice_generation"):
                preferred_languages = vaani_config.get("preferred_languages", ["en"])
                logger.info(f"🎵 Using language {preferred_languages[0]} for voice generation")
                
                voice_result = generate_voice_for_agent(agent_id, base_response, preferred_languages[0])
                if voice_result:
                    logger.info(f"✅ Voice generation successful!")
                    enhanced_result["enhanced_features"]["voice_generation"] = {
                        **voice_result,
                        "request_type": "voice_generation"
                    }
                else:
                    logger.warning(f"❌ Voice generation failed for agent {agent_id}")
        
        # 4. MULTILINGUAL PROCESSING
        elif request_type == "multilingual_processing":
            logger.info(f"🌍 Processing multilingual request for agent {agent_id}")
            # This would use Vaani's language detection API
            # For now, we'll use translation as a fallback
            if vaani_config.get("auto_translate"):
                preferred_languages = vaani_config.get("preferred_languages", ["hi", "sa", "mr"])
                logger.info(f"🌍 Processing for multiple languages: {preferred_languages}")
                
                multilingual_results = {}
                for lang in preferred_languages:
                    if lang != "en":
                        translated_response = direct_translate_text(agent_id, base_response, lang)
                        if translated_response:
                            multilingual_results[lang] = translated_response
                
                if multilingual_results:
                    logger.info(f"✅ Multilingual processing successful!")
                    enhanced_result["enhanced_features"]["multilingual_processing"] = {
                        "translations": multilingual_results,
                        "request_type": "multilingual_processing"
                    }
        
        # 5. PLATFORM OPTIMIZATION
        elif request_type == "platform_optimization":
            logger.info(f"📱 Processing platform optimization request for agent {agent_id}")
            # Generate content optimized for different platforms
            platforms = vaani_config.get("supported_platforms", ["twitter", "instagram", "linkedin"])
            logger.info(f"📱 Optimizing for platforms: {platforms}")
            
            if should_use_vaani(agent_id, input_text, "generate"):
                content_type = vaani_config.get("content_type", "tweet")
                generated_content = generate_content_for_agent(agent_id, input_text, content_type)
                
                if generated_content:
                    logger.info(f"✅ Platform optimization successful!")
                    enhanced_result["enhanced_features"]["platform_optimization"] = {
                        "generated_content": generated_content,
                        "platforms": platforms,
                        "request_type": "platform_optimization"
                    }
        
        # 6. GENERAL ENHANCEMENT (Fallback)
        else:
            logger.info(f"🔄 Processing general enhancement for agent {agent_id}")
            
            # Auto-translation if enabled
            if vaani_config.get("auto_translate"):
                preferred_languages = vaani_config.get("preferred_languages", ["hi"])
                for lang in preferred_languages:
                    if lang != "en":
                        translated_response = auto_translate_for_agent(agent_id, base_response, lang)
                        if translated_response and translated_response != base_response:
                            enhanced_result["enhanced_features"]["translation"] = {
                                "translated_text": translated_response,
                                "target_language": lang,
                                "original_text": base_response,
                                "translation_type": "auto",
                                "request_type": "general_enhancement"
                            }
                            break
            
            # Content generation if enabled
            if should_use_vaani(agent_id, input_text, "generate"):
                content_type = vaani_config.get("content_type", "tweet")
                generated_content = generate_content_for_agent(agent_id, input_text, content_type)
                if generated_content:
                    enhanced_result["enhanced_features"]["content_generation"] = {
                        "generated_text": generated_content,
                        "prompt": input_text,
                        "content_type": content_type,
                        "request_type": "general_enhancement"
                    }
            
            # Voice generation if enabled
            if vaani_config.get("voice_generation") and should_use_vaani(agent_id, input_text, "voice"):
                preferred_languages = vaani_config.get("preferred_languages", ["en"])
                voice_result = generate_voice_for_agent(agent_id, base_response, preferred_languages[0])
                if voice_result:
                    enhanced_result["enhanced_features"]["voice_generation"] = {
                        **voice_result,
                        "request_type": "general_enhancement"
                    }
        
        # 📊 FINAL SUMMARY
        feature_count = len(enhanced_result['enhanced_features'])
        logger.info(f"🎉 Intelligent enhanced response generation completed for agent {agent_id}")
        logger.info(f"📊 Request type detected: {request_type}")
        logger.info(f"📊 Features added: {feature_count}")
        if feature_count > 0:
            logger.info(f"🎯 Features: {list(enhanced_result['enhanced_features'].keys())}")
        
    except Exception as e:
        logger.error(f"❌ Intelligent enhanced response generation failed for agent {agent_id}: {str(e)}")
        enhanced_result["error"] = str(e)
    
    return enhanced_result

# Initialize Vaani integration on module load
try:
    # Initialize with default configuration
    vaani_integration.authenticate()
    logger.info("Vaani integration initialized successfully with default configuration")
except Exception as e:
    logger.warning(f"Vaani integration initialization failed: {str(e)}")

def detect_language_for_agent(agent_id: str, text: str) -> Optional[Dict[str, Any]]:
    """Detect language for a specific agent using Vaani."""
    try:
        logger.info(f"🔍 Starting language detection for agent {agent_id}")
        vaani = VaaniIntegration(agent_id)
        if not vaani.access_token:
            if not vaani.authenticate():
                logger.warning(f"❌ Vaani authentication failed for agent {agent_id}")
                return None
        
        result = vaani.detect_language(text)
        if result:
            logger.info(f"✅ Language detection successful for agent {agent_id}")
            return result
        else:
            logger.warning(f"❌ Language detection failed for agent {agent_id}")
            return None
        
    except Exception as e:
        logger.error(f"❌ Language detection failed for agent {agent_id}: {str(e)}")
        return None

def analyze_security_for_agent(agent_id: str, content_id: str) -> Optional[Dict[str, Any]]:
    """Analyze content security for a specific agent using Vaani."""
    try:
        logger.info(f"🔒 Starting security analysis for agent {agent_id}, content_id: {content_id}")
        vaani = VaaniIntegration(agent_id)
        if not vaani.access_token:
            if not vaani.authenticate():
                logger.warning(f"❌ Vaani authentication failed for agent {agent_id}")
                return None
        
        result = vaani.analyze_content_security(content_id)
        if result:
            logger.info(f"✅ Security analysis successful for agent {agent_id}")
            return result
        else:
            logger.warning(f"❌ Security analysis failed for agent {agent_id}")
            return None
        
    except Exception as e:
        logger.error(f"❌ Security analysis failed for agent {agent_id}: {str(e)}")
        return None

def get_analytics_for_agent(agent_id: str, days: int = 7) -> Optional[Dict[str, Any]]:
    """Get performance insights for a specific agent using Vaani."""
    try:
        logger.info(f"📊 Starting analytics retrieval for agent {agent_id}, days: {days}")
        vaani = VaaniIntegration(agent_id)
        if not vaani.access_token:
            if not vaani.authenticate():
                logger.warning(f"❌ Vaani authentication failed for agent {agent_id}")
                return None
        
        result = vaani.get_performance_insights(days)
        if result:
            logger.info(f"✅ Analytics retrieval successful for agent {agent_id}")
            return result
        else:
            logger.warning(f"❌ Analytics retrieval failed for agent {agent_id}")
            return None
        
    except Exception as e:
        logger.error(f"❌ Analytics retrieval failed for agent {agent_id}: {str(e)}")
        return None

def get_vaani_capabilities_for_agent(agent_id: str) -> Optional[Dict[str, Any]]:
    """Get Vaani capabilities (platforms, tones, languages) for a specific agent."""
    try:
        logger.info(f"🔧 Getting Vaani capabilities for agent {agent_id}")
        vaani = VaaniIntegration(agent_id)
        if not vaani.access_token:
            if not vaani.authenticate():
                logger.warning(f"❌ Vaani authentication failed for agent {agent_id}")
                return None
        
        capabilities = {}
        
        # Get supported platforms
        platforms = vaani.get_supported_platforms()
        if platforms:
            capabilities["platforms"] = platforms
        
        # Get supported tones
        tones = vaani.get_supported_tones()
        if tones:
            capabilities["tones"] = tones
        
        # Get supported languages
        languages = vaani.get_supported_languages()
        if languages:
            capabilities["languages"] = languages
        
        if capabilities:
            logger.info(f"✅ Vaani capabilities retrieved successfully for agent {agent_id}")
            return capabilities
        else:
            logger.warning(f"❌ No Vaani capabilities retrieved for agent {agent_id}")
            return None
        
    except Exception as e:
        logger.error(f"❌ Failed to get Vaani capabilities for agent {agent_id}: {str(e)}")
        return None

def batch_process_for_agent(agent_id: str, content_ids: List[str], operation: str = "generate", 
                           platforms: List[str] = None, target_languages: List[str] = None,
                           tone: str = "uplifting", language: str = "en") -> Optional[Dict[str, Any]]:
    """Batch process content for a specific agent using Vaani."""
    try:
        logger.info(f"🔄 Starting batch processing for agent {agent_id}, operation: {operation}")
        vaani = VaaniIntegration(agent_id)
        if not vaani.access_token:
            if not vaani.authenticate():
                logger.warning(f"❌ Vaani authentication failed for agent {agent_id}")
                return None
        
        if operation == "generate":
            if not platforms:
                platforms = ["twitter"]  # Default platform
            result = vaani.batch_generate_content(content_ids, platforms, tone, language)
        elif operation == "translate":
            if not target_languages:
                target_languages = ["hi"]  # Default target language
            result = vaani.batch_translate_content(content_ids, target_languages)
        else:
            logger.error(f"❌ Unknown batch operation: {operation}")
            return None
        
        if result:
            logger.info(f"✅ Batch {operation} successful for agent {agent_id}")
            return result
        else:
            logger.warning(f"❌ Batch {operation} failed for agent {agent_id}")
            return None
        
    except Exception as e:
        logger.error(f"❌ Batch processing failed for agent {agent_id}: {str(e)}")
        return None