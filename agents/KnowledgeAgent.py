from utils.file_based_retriever import file_retriever
from utils.logger import get_logger
import uuid
from datetime import datetime
from reinforcement.rl_context import RLContext
from reinforcement.reward_functions import get_reward_from_output
from typing import Dict, Any

# Try to import VedabaseRetriever, but don't fail if not available
try:
    from vedabase_retriever import VedabaseRetriever
    QDRANT_AVAILABLE = True
except ImportError as e:
    logger = get_logger(__name__)
    logger.warning(f"VedabaseRetriever not available: {e}")
    VedabaseRetriever = None
    QDRANT_AVAILABLE = False

# Try to import NAS retriever for enhanced knowledge retrieval
try:
    from example.nas_retriever import NASKnowledgeRetriever
    NAS_RETRIEVER_AVAILABLE = True
except ImportError as e:
    logger = get_logger(__name__)
    logger.warning(f"NAS retriever not available: {e}")
    NASKnowledgeRetriever = None
    NAS_RETRIEVER_AVAILABLE = False

logger = get_logger(__name__)

class KnowledgeAgent:
    def __init__(self):
        # Always try file-based retriever first since it's more reliable
        self.file_retriever_available = True

        # Try NAS+Qdrant retriever first (most advanced)
        if NAS_RETRIEVER_AVAILABLE and NASKnowledgeRetriever:
            try:
                self.nas_retriever = NASKnowledgeRetriever("vedas", qdrant_url="localhost:6333")
                self.nas_available = True
                logger.info("KnowledgeAgent initialized with NAS+Qdrant support")
            except Exception as e:
                logger.info(f"NAS retriever not available: {str(e)}")
                self.nas_retriever = None
                self.nas_available = False
        else:
            self.nas_retriever = None
            self.nas_available = False

        # Try Qdrant-based retriever as secondary option
        if QDRANT_AVAILABLE and VedabaseRetriever:
            try:
                self.retriever = VedabaseRetriever()
                self.qdrant_available = True
                logger.info("KnowledgeAgent initialized with Qdrant support")
            except Exception as e:
                logger.info(f"Qdrant not available, using file-based retriever only: {str(e)}")
                self.retriever = None
                self.qdrant_available = False
        else:
            logger.info("VedabaseRetriever not available, using file-based retriever only")
            self.retriever = None
            self.qdrant_available = False

        self.rl_context = RLContext()

    def query(self, query_text: str, filters: dict = None, task_id: str = None) -> dict:
        task_id = task_id or str(uuid.uuid4())

        print(f"🧠 [KNOWLEDGE AGENT] Starting knowledge retrieval...")
        print(f"🔍 [SEARCH QUERY] '{query_text}'")
        if filters:
            print(f"🎯 [FILTERS] {filters}")

        # Always try file-based retriever first (more reliable)
        if self.file_retriever_available:
            print(f"📚 [FILE RETRIEVER] Searching knowledge base...")
            logger.info(f"KnowledgeAgent query {task_id}: Using file-based retriever (primary)")
            try:
                file_results = file_retriever.search(query_text, limit=5)
                if file_results:
                    print(f"✅ [FOUND] {len(file_results)} relevant chunks in knowledge base")
                    # Format results for consistency
                    formatted_results = [result['text'] for result in file_results]
                    sources = [result['source'] for result in file_results]

                    return {
                        "query_id": task_id,
                        "query": query_text,
                        "response": formatted_results,
                        "sources": sources,
                        "timestamp": datetime.now().isoformat(),
                        "endpoint": "knowledge",
                        "status": 200,
                        "metadata": {
                            "tags": ["semantic_search", "file_based"],
                            "retriever": "file_based",
                            "total_results": len(file_results)
                        }
                    }
                else:
                    # No results found, return empty for LLM fallback
                    return {
                        "query_id": task_id,
                        "query": query_text,
                        "response": [],
                        "sources": [],
                        "timestamp": datetime.now().isoformat(),
                        "endpoint": "knowledge",
                        "status": 200,
                        "metadata": {"tags": ["semantic_search", "vedabase"], "fallback_mode": True}
                    }
            except Exception as e:
                logger.error(f"File-based retriever failed: {str(e)}")
                return {
                    "query_id": task_id,
                    "query": query_text,
                    "response": [],
                    "sources": [],
                    "timestamp": datetime.now().isoformat(),
                    "endpoint": "knowledge",
                    "status": 200,
                    "metadata": {"tags": ["semantic_search", "vedabase"], "fallback_mode": True}
                }

        try:
            results = self.retriever.get_relevant_docs(query_text, filters)
            response = {
                "query_id": task_id,
                "query": query_text,
                "response": results,
                "sources": [],
                "timestamp": datetime.now().isoformat(),
                "endpoint": "knowledge",
                "status": 200,
                "metadata": {"tags": ["semantic_search", "vedabase"]}
            }
            reward = get_reward_from_output(response, task_id)
            self.rl_context.log_action(
                task_id=task_id,
                agent="knowledge_agent",
                model="none",
                action="query_vedabase",
                metadata={"query": query_text, "filters": filters}
            )
            logger.info(f"KnowledgeAgent query {task_id}: {len(results) if isinstance(results, list) else 1} results")
            return response
        except Exception as e:
            logger.error(f"KnowledgeAgent query {task_id} failed: {str(e)}")
            return {
                "query_id": task_id,
                "query": query_text,
                "response": [],
                "sources": [],
                "timestamp": datetime.now().isoformat(),
                "endpoint": "knowledge",
                "status": 200,
                "metadata": {"tags": ["semantic_search", "vedabase"], "fallback_mode": True},
                "error": str(e)
            }

    def enhance_with_llm(self, query: str, knowledge_context: str) -> str:
        """Enhanced response using local processing (no external API calls)."""
        try:
            print(f"🎨 [LOCAL ENHANCEMENT] Processing knowledge without external APIs...")
            # Simple enhancement without external API calls
            if knowledge_context.strip():
                enhanced = f"Based on the available knowledge:\n\n{knowledge_context}\n\nThis information addresses your query about: {query}"
                print(f"✨ [ENHANCED] Response formatted and ready")
                return enhanced
            else:
                print(f"❌ [NO KNOWLEDGE] No relevant information found")
                return f"I don't have specific information about '{query}' in the knowledge base."

        except Exception as e:
            logger.error(f"LLM enhancement failed: {str(e)}")
            return knowledge_context if knowledge_context.strip() else "Unable to process your query at this time."

    def run(self, input_path: str, live_feed: str = "", model: str = "knowledge_agent", input_type: str = "text", task_id: str = None) -> Dict[str, Any]:
        """Main entry point for agent execution - compatible with existing agent interface."""
        task_id = task_id or str(uuid.uuid4())
        logger.info(f"KnowledgeAgent processing task {task_id}, query: {input_path}")

        # Use input_path as the query text
        query_result = self.query(input_path, task_id=task_id)

        # Format response to match expected agent output format
        if query_result["status"] == 200 and query_result.get("response"):
            # Combine knowledge base results
            if isinstance(query_result["response"], list) and query_result["response"]:
                combined_text = "\n\n".join(query_result["response"][:3])
            else:
                combined_text = str(query_result["response"])

            # Enhance with LLM for better formatting and context
            enhanced_response = self.enhance_with_llm(input_path, combined_text)

            return {
                "response": enhanced_response,
                "query_id": task_id,
                "query": input_path,
                "sources": query_result.get("sources", []),
                "metadata": query_result.get("metadata", {}),
                "timestamp": query_result["timestamp"],
                "status": 200,
                "model": model,
                "knowledge_base_results": len(query_result.get("response", [])) if isinstance(query_result.get("response"), list) else 1,
                "endpoint": "knowledge_agent"
            }
        else:
            # Fallback to LLM only if no knowledge base results
            try:
                fallback_response = self.enhance_with_llm(input_path, "No specific knowledge found in database.")
                return {
                    "response": fallback_response,
                    "query_id": task_id,
                    "query": input_path,
                    "sources": [],
                    "metadata": {},
                    "timestamp": datetime.now().isoformat(),
                    "status": 200,
                    "model": model,
                    "knowledge_base_results": 0,
                    "fallback": True,
                    "endpoint": "knowledge_agent"
                }
            except Exception:
                return {
                    "response": "I couldn't find relevant information in the knowledge base for your query.",
                    "query_id": task_id,
                    "query": input_path,
                    "sources": [],
                    "metadata": {},
                    "timestamp": datetime.now().isoformat(),
                    "status": 404,
                    "model": model,
                    "error": query_result.get("error", "No results found"),
                    "endpoint": "knowledge_agent"
                }