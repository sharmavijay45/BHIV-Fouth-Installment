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
    """Determine if Vaani should be used for the given agent and input."""
    try:
        logger.info(f"Checking if Vaani should be used for agent {agent_id}, operation: {operation}")
        vaani_config = get_agent_vaani_config(agent_id)
        if not vaani_config or not vaani_config.get("enabled"):
            logger.info(f"Vaani not enabled for agent {agent_id}")
            return False
        
        # Check for language triggers
        if operation in ["translate", "language"] or operation is None:
            logger.info(f"Checking for language triggers in input text")
            if any(lang in input_text.lower() for lang in ["hindi", "sanskrit", "marathi", "हिंदी", "संस्कृत", "मराठी"]):
                logger.info(f"Language trigger found! Vaani will be used for translation")
                return True
        
        # Check for content generation triggers
        if operation in ["generate", "content"] or operation is None:
            logger.info(f"Checking for content generation triggers in input text")
            if any(word in input_text.lower() for word in ["generate", "create", "write", "content"]):
                logger.info(f"Content generation trigger found! Vaani will be used for content creation")
                return True
        
        # Check for voice triggers
        if operation in ["voice", "audio"] or operation is None:
            logger.info(f"Checking for voice triggers in input text")
            if any(word in input_text.lower() for word in ["voice", "audio", "speak", "tts"]):
                logger.info(f"Voice trigger found! Vaani will be used for voice generation")
                return True
        
        logger.info(f"No triggers found for Vaani usage in agent {agent_id}")
        return False
        
    except Exception as e:
        logger.error(f"Failed to determine Vaani usage for agent {agent_id}: {str(e)}")
        return False

def enhanced_agent_response(agent_id: str, input_text: str, base_response: str) -> Dict[str, Any]:
    """Generate enhanced response for an agent using Vaani capabilities."""
    enhanced_result = {
        "original_response": base_response,
        "enhanced_features": {},
        "vaani_used": False
    }
    
    try:
        logger.info(f"Starting enhanced response generation for agent {agent_id}")
        vaani_config = get_agent_vaani_config(agent_id)
        if not vaani_config or not vaani_config.get("enabled"):
            logger.info(f"Vaani integration disabled for agent {agent_id}")
            return enhanced_result
        
        logger.info(f"Vaani integration enabled for agent {agent_id}. Processing enhancements...")
        enhanced_result["vaani_used"] = True
        
        # Auto-translation if enabled
        if vaani_config.get("auto_translate"):
            logger.info(f"Auto-translation enabled for agent {agent_id}. Checking preferred languages...")
            preferred_languages = vaani_config.get("preferred_languages", ["en"])
            logger.info(f"Preferred languages: {preferred_languages}")
            for lang in preferred_languages:
                if lang != "en":  # Don't translate to English if already in English
                    logger.info(f"Attempting translation to {lang} for agent {agent_id}")
                    translated_response = auto_translate_for_agent(agent_id, base_response, lang)
                    if translated_response != base_response:
                        logger.info(f"Translation successful! Adding {lang} translation to enhanced response")
                        enhanced_result["enhanced_features"]["translation"] = {
                            "translated_text": translated_response,
                            "target_language": lang,
                            "original_text": base_response
                        }
                        break
                    else:
                        logger.info(f"Translation to {lang} failed or returned same text for agent {agent_id}")
        else:
            logger.info(f"Auto-translation disabled for agent {agent_id}")
        
        # Content generation if enabled
        if should_use_vaani(agent_id, input_text, "generate"):
            logger.info(f"Content generation triggered for agent {agent_id}")
            content_type = vaani_config.get("content_type", "tweet")  # FIXED: Changed from "informative" to "tweet"
            logger.info(f"Using content type: {content_type}")
            generated_content = generate_content_for_agent(agent_id, input_text, content_type)
            if generated_content:
                logger.info(f"Content generation successful! Adding generated content to enhanced response")
                enhanced_result["enhanced_features"]["content_generation"] = {
                    "generated_text": generated_content,
                    "prompt": input_text,
                    "content_type": content_type
                }
            else:
                logger.warning(f"Content generation failed for agent {agent_id}")
        else:
            logger.info(f"Content generation not triggered for agent {agent_id}")
        
        # Voice generation if enabled
        if vaani_config.get("voice_generation") and should_use_vaani(agent_id, input_text, "voice"):
            logger.info(f"Voice generation enabled and triggered for agent {agent_id}")
            preferred_languages = vaani_config.get("preferred_languages", ["en"])
            logger.info(f"Using language {preferred_languages[0]} for voice generation")
            voice_result = generate_voice_for_agent(agent_id, base_response, preferred_languages[0])
            if voice_result:
                logger.info(f"Voice generation successful! Adding voice result to enhanced response")
                enhanced_result["enhanced_features"]["voice_generation"] = voice_result
            else:
                logger.warning(f"Voice generation failed for agent {agent_id}")
        else:
            logger.info(f"Voice generation not enabled or not triggered for agent {agent_id}")
        
        feature_count = len(enhanced_result['enhanced_features'])
        logger.info(f"Enhanced response generation completed for agent {agent_id} with {feature_count} features")
        if feature_count > 0:
            logger.info(f"Features added: {list(enhanced_result['enhanced_features'].keys())}")
        
    except Exception as e:
        logger.error(f"Enhanced response generation failed for agent {agent_id}: {str(e)}")
        enhanced_result["error"] = str(e)
    
    return enhanced_result

# Initialize Vaani integration on module load
try:
    # Initialize with default configuration
    vaani_integration.authenticate()
    logger.info("Vaani integration initialized successfully with default configuration")
except Exception as e:
    logger.warning(f"Vaani integration initialization failed: {str(e)}")