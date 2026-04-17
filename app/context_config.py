"""
Agno Context Configuration
==========================

Configures context window management using Agno's native features
to handle large tool outputs and prevent exceeding token limits.
"""

from agno.utils.log import logger

# ---------------------------------------------------------------------------
# Context Window Configuration
# ---------------------------------------------------------------------------

# Conservative context window limits (leaving room for system prompts and responses)
# Model has 200K limit, we use 150K effective limit
MAX_CONTEXT_TOKENS = 150000
SYSTEM_PROMPT_TOKENS = 2000
RESPONSE_TOKENS = 30000
EFFECTIVE_CONTEXT_LIMIT = MAX_CONTEXT_TOKENS - SYSTEM_PROMPT_TOKENS - RESPONSE_TOKENS

# Knowledge base search limits
KB_SEARCH_LIMIT = 5  # Maximum number of KB results to return
KB_RESULT_TOKENS = 20000  # Maximum tokens per KB result

# Tool output limits
MAX_TOOL_OUTPUT_TOKENS = 10000  # Maximum tokens for single tool output


# ---------------------------------------------------------------------------
# Context Caching Configuration
# ---------------------------------------------------------------------------

# Enable context caching for static content (reduces token usage)
ENABLE_CONTEXT_CACHING = True

# Static content that should be cached (placed at start of system message)
STATIC_CONTEXT_PARTS = [
    "agent_description",
    "instructions",
    "tools_description",
]


# ---------------------------------------------------------------------------
# Chat History Configuration
# ---------------------------------------------------------------------------

# Limit chat history to prevent context bloat
MAX_HISTORY_RUNS = 5  # Maximum number of history runs to include
ENABLE_SESSION_SUMMARIES = True  # Enable session summaries to condense history


# ---------------------------------------------------------------------------
# Tool Call Filtering Configuration
# ---------------------------------------------------------------------------

# Filter tool calls from history to reduce context
FILTER_TOOL_CALLS_FROM_HISTORY = True

# Tool types to exclude from history (large outputs)
EXCLUDE_TOOL_TYPES = [
    "knowledge_search",
    "file_read_large",
    "code_generation",
]


# ---------------------------------------------------------------------------
# Context Management Functions
# ---------------------------------------------------------------------------

def configure_agent_context(
    agent,
    max_history_runs: int = MAX_HISTORY_RUNS,
    enable_summaries: bool = ENABLE_SESSION_SUMMARIES,
    enable_caching: bool = ENABLE_CONTEXT_CACHING
):
    """
    Configure context management for an agent using Agno's native features.
    
    Args:
        agent: The Agno agent to configure
        max_history_runs: Maximum number of history runs to include
        enable_summaries: Enable session summaries
        enable_caching: Enable context caching
    """
    # Configure chat history
    agent.read_chat_history = True
    agent.num_history_runs = max_history_runs
    agent.enable_session_summaries = enable_summaries
    
    # Configure context caching (if supported by model provider)
    if enable_caching:
        # Agno automatically places static content at start of system message
        # for caching. This includes agent description, instructions, etc.
        logger.info(f"Context caching enabled for agent: {agent.name}")
    
    logger.info(f"Configured context for agent {agent.name}: "
                f"history_runs={max_history_runs}, "
                f"summaries={enable_summaries}, "
                f"caching={enable_caching}")


def configure_team_context(
    team,
    max_history_runs: int = MAX_HISTORY_RUNS,
    enable_summaries: bool = ENABLE_SESSION_SUMMARIES
):
    """
    Configure context management for a team using Agno's native features.
    
    Args:
        team: The Agno team to configure
        max_history_runs: Maximum number of history runs to include
        enable_summaries: Enable session summaries
    """
    # Configure chat history
    team.read_chat_history = True
    team.num_history_runs = max_history_runs
    team.enable_session_summaries = enable_summaries
    
    logger.info(f"Configured context for team {team.name}: "
                f"history_runs={max_history_runs}, "
                f"summaries={enable_summaries}")


def get_context_limits() -> dict:
    """
    Get current context window limits.
    
    Returns:
        Dictionary with context limit configuration
    """
    return {
        "max_context_tokens": MAX_CONTEXT_TOKENS,
        "system_prompt_tokens": SYSTEM_PROMPT_TOKENS,
        "response_tokens": RESPONSE_TOKENS,
        "effective_context_limit": EFFECTIVE_CONTEXT_LIMIT,
        "kb_search_limit": KB_SEARCH_LIMIT,
        "kb_result_tokens": KB_RESULT_TOKENS,
        "max_tool_output_tokens": MAX_TOOL_OUTPUT_TOKENS,
        "max_history_runs": MAX_HISTORY_RUNS,
    }
