"""
Tools for the LangGraph agent.
Updated to use FileManager and new Vue-based editor.
"""
import logging
from langchain.tools import tool
from llm_new.actor_agent import generate_action_llm
from llm_new.editor_agent import generate_vue_page, generate_vue_component
from llm_new.clarifier_agent import generate_clarification_llm
from llm_new.file_manager import FileManager
from llm_new.session_manager import SessionManager

logger = logging.getLogger(__name__)

# Global instances (will be initialized by server)
file_manager: FileManager = None
session_manager: SessionManager = None


def initialize_tools(fm: FileManager, sm: SessionManager):
    """Initialize tools with FileManager and SessionManager instances"""
    global file_manager, session_manager
    file_manager = fm
    session_manager = sm
    logger.info("[Tools] Initialized with FileManager and SessionManager")


@tool
async def edit_tool(intent: str, context: str, session_id: str = None) -> str:
    """
    Create or edit website pages/components using Vue files.
    
    Args:
        intent: User's editing request
        context: Additional context
        session_id: Session identifier (required)
    
    Returns:
        Success message with file path
    """
    logger.info(f"[EDIT_TOOL] Called with intent: {intent[:100]}...")
    logger.info(f"[EDIT_TOOL] Session ID: {session_id}")
    
    if not session_id:
        logger.error("[EDIT_TOOL] No session_id provided")
        return "Error: Session ID required for editing"
    
    if not file_manager:
        logger.error("[EDIT_TOOL] FileManager not initialized")
        return "Error: FileManager not initialized"
    
    try:
        # Classify the intent - is it creating a new page, editing existing, or creating component?
        classification = await classify_edit_intent(intent, session_id)
        
        if classification["action"] == "CREATE_PAGE":
            # Generate new page
            page_name = classification["target"]
            existing_pages = await file_manager.list_pages(session_id)
            
            logger.info(f"[EDIT_TOOL] Creating new page: {page_name}")
            
            vue_code = await generate_vue_page(
                page_name=page_name,
                intent=intent,
                context=context,
                existing_pages=existing_pages
            )
            
            await file_manager.create_new_page(session_id, page_name, vue_code)
            
            result = f"Successfully created page: {page_name}"
            logger.info(f"[EDIT_TOOL] {result}")
            return result
            
        elif classification["action"] == "EDIT_PAGE":
            # Edit existing page
            page_name = classification["target"]
            existing_pages = await file_manager.list_pages(session_id)
            
            logger.info(f"[EDIT_TOOL] Editing existing page: {page_name}")
            
            vue_code = await generate_vue_page(
                page_name=page_name,
                intent=intent,
                context=context,
                existing_pages=existing_pages
            )
            
            await file_manager.write_view(session_id, page_name, vue_code)
            
            result = f"Successfully updated page: {page_name}"
            logger.info(f"[EDIT_TOOL] {result}")
            return result
            
        elif classification["action"] == "CREATE_COMPONENT":
            # Create reusable component
            component_name = classification["target"]
            
            logger.info(f"[EDIT_TOOL] Creating component: {component_name}")
            
            vue_code = await generate_vue_component(
                component_name=component_name,
                intent=intent,
                context=context
            )
            
            await file_manager.write_component(session_id, component_name, vue_code)
            
            result = f"Successfully created component: {component_name}"
            logger.info(f"[EDIT_TOOL] {result}")
            return result
            
        else:
            logger.warning(f"[EDIT_TOOL] Unknown action: {classification['action']}")
            return "Error: Could not determine editing action"
            
    except Exception as e:
        logger.error(f"[EDIT_TOOL] Error: {e}")
        import traceback
        traceback.print_exc()
        return f"Error during editing: {str(e)}"


async def classify_edit_intent(intent: str, session_id: str) -> dict:
    """
    Classify what type of editing action is needed.
    
    Returns:
        dict with "action" (CREATE_PAGE, EDIT_PAGE, CREATE_COMPONENT) and "target" (name)
    """
    # Simple classification logic (can be enhanced with LLM later)
    intent_lower = intent.lower()
    
    # Get existing pages
    existing_pages = await file_manager.list_pages(session_id) if file_manager else []
    
    # Check for page creation keywords
    if any(kw in intent_lower for kw in ["create", "add", "new"]) and any(kw in intent_lower for kw in ["page", "screen", "view"]):
        # Extract page name (simplified)
        for word in ["about", "contact", "pricing", "features", "home", "blog", "team", "services"]:
            if word in intent_lower:
                return {"action": "CREATE_PAGE", "target": word.capitalize()}
        
        return {"action": "CREATE_PAGE", "target": "NewPage"}
    
    # Check for component creation
    if any(kw in intent_lower for kw in ["component", "button", "card", "modal", "widget"]):
        # Extract component name
        for word in ["button", "card", "modal", "navbar", "footer", "input", "form"]:
            if word in intent_lower:
                return {"action": "CREATE_COMPONENT", "target": word.capitalize()}
        
        return {"action": "CREATE_COMPONENT", "target": "Component"}
    
    # Check for editing existing pages
    for page_name in existing_pages:
        if page_name.lower() in intent_lower:
            return {"action": "EDIT_PAGE", "target": page_name}
    
    # Default: assume editing main page
    if existing_pages:
        return {"action": "EDIT_PAGE", "target": existing_pages[0]}
    
    return {"action": "CREATE_PAGE", "target": "Home"}


@tool
async def action_tool(intent: str, context: str) -> str:
    """
    Generate UI action (navigate, click, etc.) using actor agent
    
    Args:
        intent: User's action request
        context: Additional context
    
    Returns:
        Action JSON payload
    """
    logger.info(f"[ACTION_TOOL] Called with intent: {intent[:100]}...")
    
    try:
        result = await generate_action_llm(intent)
        logger.info(f"[ACTION_TOOL] Generated action")
        logger.info(f"[ACTION_TOOL] Output length: {len(result)}")
        return result
    except Exception as e:
        logger.error(f"[ACTION_TOOL] Error: {e}")
        return f"Error generating action: {str(e)}"


@tool
async def clarify_tool(intent: str, context: str) -> str:
    """
    Generate clarification question for ambiguous user request
    
    Args:
        intent: User's request
        context: Additional context
    
    Returns:
        Clarification question
    """
    logger.info(f"[CLARIFY_TOOL] Called with intent: {intent[:100]}...")
    
    try:
        result = await generate_clarification_llm(intent)
        logger.info(f"[CLARIFY_TOOL] Generated clarification")
        logger.info(f"[CLARIFY_TOOL] Output: {result[:100]}...")
        return result
    except Exception as e:
        logger.error(f"[CLARIFY_TOOL] Error: {e}")
        return f"Error generating clarification: {str(e)}"


# Tool mapping
TOOL_MAP = {
    "edit_tool": edit_tool,
    "action_tool": action_tool,
    "clarify_tool": clarify_tool
}
