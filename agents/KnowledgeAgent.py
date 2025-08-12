from utils.file_based_retriever import file_retriever
from utils.logger import get_logger
import uuid
import os
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
    # Import via package path first, fallback to relative example path
    from example.nas_retriever import NASKnowledgeRetriever
    NAS_RETRIEVER_AVAILABLE = True
except Exception as e:
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

        # Try NAS+Qdrant retriever first (most advanced)
        if self.nas_available and self.nas_retriever:
            print(f"🚀 [NAS RETRIEVER] Searching NAS-based Qdrant knowledge base...")
            logger.info(f"KnowledgeAgent query {task_id}: Using NAS+Qdrant retriever (primary)")
            try:
                nas_results = self.nas_retriever.query(query_text, top_k=5)
                if nas_results:
                    print(f"✅ [FOUND] {len(nas_results)} relevant chunks in NAS knowledge base")
                    # Format results for consistency
                    formatted_results = [result['content'] for result in nas_results]
                    sources = [f"NAS-Qdrant:{result.get('document_id', 'unknown')}" for result in nas_results]

                    return {
                        "query_id": task_id,
                        "query": query_text,
                        "response": formatted_results,
                        "sources": sources,
                        "timestamp": datetime.now().isoformat(),
                        "endpoint": "knowledge",
                        "status": 200,
                        "metadata": {
                            "tags": ["semantic_search", "nas_qdrant"],
                            "retriever": "nas_qdrant",
                            "total_results": len(nas_results)
                        }
                    }
                else:
                    print(f"⚠️ [NO RESULTS] NAS retriever found no results, trying Qdrant...")
            except Exception as e:
                logger.error(f"NAS retriever failed: {str(e)}")
                print(f"❌ [NAS ERROR] {str(e)}, trying Qdrant...")

        # Try Qdrant-based retriever as secondary option
        if self.qdrant_available and self.retriever:
            print(f"🔍 [QDRANT RETRIEVER] Searching Qdrant knowledge base...")
            logger.info(f"KnowledgeAgent query {task_id}: Using Qdrant retriever (secondary)")
            try:
                results = self.retriever.get_relevant_docs(query_text, filters)
                if results:
                    print(f"✅ [FOUND] {len(results) if isinstance(results, list) else 1} results in Qdrant")
                    
                    # Format results for consistency - extract text content
                    if isinstance(results, list):
                        formatted_results = []
                        sources = []
                        for result in results:
                            if isinstance(result, dict):
                                text_content = result.get("text", str(result))
                                source = result.get("source", "unknown")
                                formatted_results.append(text_content)
                                sources.append(source)
                            else:
                                formatted_results.append(str(result))
                                sources.append("unknown")
                    else:
                        formatted_results = [str(results)]
                        sources = ["unknown"]
                    
                    response = {
                        "query_id": task_id,
                        "query": query_text,
                        "response": formatted_results,
                        "sources": sources,
                        "timestamp": datetime.now().isoformat(),
                        "endpoint": "knowledge",
                        "status": 200,
                        "metadata": {"tags": ["semantic_search", "qdrant"]}
                    }
                    reward = get_reward_from_output(response, task_id)
                    self.rl_context.log_action(
                        task_id=task_id,
                        agent="knowledge_agent",
                        model="none",
                        action="query_vedabase",
                        metadata={"query": query_text, "filters": filters}
                    )
                    logger.info(f"KnowledgeAgent query {task_id}: {len(formatted_results)} results")
                    return response
                else:
                    print(f"⚠️ [NO RESULTS] Qdrant found no results, trying file-based...")
            except Exception as e:
                logger.error(f"Qdrant retriever failed: {str(e)}")
                print(f"❌ [QDRANT ERROR] {str(e)}, trying file-based...")

        # Fallback to file-based retriever (least preferred)
        if self.file_retriever_available:
            print(f"📚 [FILE RETRIEVER] Searching file-based knowledge base (fallback)...")
            logger.info(f"KnowledgeAgent query {task_id}: Using file-based retriever (fallback)")
            try:
                file_results = file_retriever.search(query_text, limit=5)
                if file_results:
                    print(f"✅ [FOUND] {len(file_results)} relevant chunks in file-based knowledge base")
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
                        "metadata": {"tags": ["semantic_search", "file_based"], "fallback_mode": True}
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
                    "metadata": {"tags": ["semantic_search", "file_based"], "fallback_mode": True}
                }

        # Final fallback if no retrievers are available
        print(f"❌ [NO RETRIEVERS] No retrievers available, returning empty response")
        logger.warning(f"KnowledgeAgent query {task_id}: No retrievers available")
        return {
            "query_id": task_id,
            "query": query_text,
            "response": [],
            "sources": [],
            "timestamp": datetime.now().isoformat(),
            "endpoint": "knowledge",
            "status": 200,
            "metadata": {"tags": ["semantic_search", "no_retriever"], "fallback_mode": True}
        }


    def enhance_with_llm(self, query: str, knowledge_context: str) -> str:
        """Enhanced response using Ollama fallback if configured, else local formatting."""
        try:
            # Try Ollama when configured
            import requests
            ollama_url = os.getenv("OLLAMA_URL", "http://localhost:11434/api/generate")
            ollama_model = os.getenv("OLLAMA_MODEL", "llama3-8b-8192")
            if ollama_url and ollama_model:
                prompt = (
                    "You are a helpful assistant. Use the following knowledge context if available to answer the query.\n\n"
                    f"Query: {query}\n\n"
                    f"Knowledge Context:\n{knowledge_context}\n\n"
                    "If the context is empty or irrelevant, give a general helpful answer. Keep it clear and concise."
                )
                payload = {"model": ollama_model, "prompt": prompt, "stream": False}
                headers = {"Content-Type": "application/json"}
                r = requests.post(ollama_url, json=payload, headers=headers, timeout=int(os.getenv("OLLAMA_TIMEOUT", "60")))
                if r.status_code == 200:
                    data = r.json()
                    text = data.get("response") or data.get("message", {}).get("content")
                    if text:
                        return text.strip()

            # Fallback: local formatting and summarization
            if knowledge_context.strip():
                # Simple summarization: find sentences with the most query words
                query_words = set(query.lower().split())
                sentences = knowledge_context.split('.')
                sentence_scores = []
                for sentence in sentences:
                    if not sentence.strip():
                        continue
                    sentence_words = set(sentence.lower().split())
                    score = len(query_words.intersection(sentence_words))
                    sentence_scores.append((score, sentence))

                sentence_scores.sort(key=lambda x: x[0], reverse=True)

                # Return the top 3 sentences
                top_sentences = [s for score, s in sentence_scores[:3] if score > 0]

                if top_sentences:
                    return ". ".join(top_sentences).strip() + "."
                else:
                    # If no sentences have query words, return the first 3 sentences
                    return ". ".join(sentences[:3]).strip() + "."

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