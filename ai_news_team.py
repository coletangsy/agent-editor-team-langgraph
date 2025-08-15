from typing import TypedDict, List, Annotated
from langchain_core.messages import HumanMessage, AIMessage
from langgraph.graph import StateGraph
from langgraph.graph.message import add_messages
from datetime import datetime, timedelta
import logging
import os 

# Initialize logger
logger = logging.getLogger(__name__)

class EditorState(TypedDict):
    """State definition for the editor team workflow.
    
    Attributes:
        messages: List of chat messages in the conversation
        research: Processed research content from researcher agent
        draft: Formatted draft from writer agent
        final_content: Polished output from editor agent
        research_metrics: Performance metrics from research phase
        writing_metrics: Performance metrics from writing phase
        editing_metrics: Performance metrics from editing phase
        raw_articles: Original articles before processing
    """
    messages: Annotated[List[HumanMessage | AIMessage], add_messages]
    research: str
    draft: str
    final_content: str
    research_metrics: dict
    writing_metrics: dict
    editing_metrics: dict
    raw_articles: list

def create_agents(feed_reader, research_llm, writing_llm, editing_llm):
    """Factory function to create all agents with their dependencies.
    
    Args:
        feed_reader: Configured RSS feed reader instance
        research_llm: LLM instance for research agent
        writing_llm: LLM instance for writer agent
        editing_llm: LLM instance for editor agent
    
    Returns:
        Tuple of three agent functions: (research_agent, writer_agent, editor_agent)
    """
    
    # Create agent functions
    def research_agent(state: EditorState):
        """Agent responsible for identifying AI breakthroughs from news feeds.
        
        Processes raw articles to find significant AI developments, filtering out non-AI content.
        Logs processing metrics and preserves original articles for reference.
        
        Args:
            state: Current workflow state containing messages
            
        Returns:
            Dictionary with:
            - research: Formatted research findings
            - raw_articles: Original articles before processing
            - research_metrics: Processing time and article counts
        """
        # Get raw articles from trusted sources
        logger.info("🕵️ Research Agent started - Fetching articles from configured feeds")
        raw_articles = feed_reader.fetch_weekly_feeds()
        logger.info(f"📰 Found {len(raw_articles)} raw articles from sources")
        
        research_prompt = f"""
            Analyze these recent tech articles and identify ONLY AI breakthroughs:
            
            Articles: {raw_articles}
            
            Required Output Format for each valid AI breakthrough:
            
            ### [Breakthrough Title]
            - **Source Publication**: [Publication Name]
            - **Article Title**: [Exact Article Title]
            - **Published**: [YYYY-MM-DD]
            - **URL**: [Article Link]
            - **Technical Novelty**: 
            [1-2 sentences explaining the technical innovation]
            - **Significance**: 
            [1 sentence on why this matters to developers/researchers]
            - **Ethical Considerations**: 
            [If any, otherwise state "None identified"]

            Strict Filtering Criteria:
            1. MUST be about AI models, algorithms, or products
            2. MUST include verifiable technical details
            3. MUST come from our trusted sources
            4. REJECT completely if:
            - About non-AI technology
            - Just company announcements without technical depth
            - Opinion pieces without research backing

            Sort by:
            - Publication date (newest first)
            - Technical significance (most innovative first)
            """
        
        start_time = datetime.now()
        research = research_llm.invoke(research_prompt)
        processing_time = (datetime.now() - start_time).total_seconds()
        
        logger.info(f"🔍 Research completed in {processing_time:.2f}s")
        logger.debug(f"Research findings:\n{research.content[:500]}...")  # Truncate long output
        
        return {
            "research": research.content,
            "raw_articles": raw_articles,
            "research_metrics": {
                "articles_processed": len(raw_articles),
                "processing_time": processing_time
            }
        }

    def writer_agent(state: EditorState):
        """Agent that transforms technical research into accessible content.
        
        Converts research findings into developer/executive-friendly format while
        maintaining technical accuracy. Tracks content length changes.
        
        Args:
            state: Current workflow state containing research content
            
        Returns:
            Dictionary with:
            - draft: Formatted content draft
            - writing_metrics: Processing stats and content lengths
        """
        logger.info("✍️ Writer Agent started - Transforming research into digest")
        logger.debug(f"Working with research:\n{state['research'][:300]}...")
        
        writer_prompt = f"""
            Transform this AI research into developer/executive-friendly content:
            
            Research: {state['research']}
            
            Guidelines:
            1. Maintain technical accuracy
            2. Explain concepts clearly
            3. Highlight business implications
            4. Keep summaries concise (1-2 paragraphs per item)
            5. Use engaging but professional tone
            
            Output format for each item:
            ### [Simplified Title]
            [Clear explanation with technical depth]
            [Business/development impact]
            """
        
        start_time = datetime.now()
        draft = writing_llm.invoke(writer_prompt)
        processing_time = (datetime.now() - start_time).total_seconds()
        
        logger.info(f"📝 Writing completed in {processing_time:.2f}s")
        logger.debug(f"Draft content:\n{draft.content[:500]}...")
        
        return {
            "draft": draft.content,
            "writing_metrics": {
                "input_length": len(state['research']),
                "output_length": len(draft.content),
                "processing_time": processing_time
            }
        }


    def editor_agent(state: EditorState):
        """Agent that formats content into final digest structure.
        
        Enforces consistent output format, validates required elements,
        and ensures professional tone. Tracks structural validation.
        
        Args:
            state: Current workflow state containing content draft
            
        Returns:
            Dictionary with:
            - final_content: Polished digest output
            - editing_metrics: Processing stats and validation results
        """
        logger.info("✂️ Editor Agent started - Formatting final digest")
        
        # Get current week dates
        today = datetime.now().date()
        week_start = today - timedelta(days=today.weekday())
        week_end = week_start + timedelta(days=6)
        week_range = f"{week_start.strftime('%Y-%m-%d')} to {week_end.strftime('%Y-%m-%d')}"
        
        editor_prompt = f"""
            Create a clean weekly AI digest using ONLY this template. Output NOTHING else - no commentary, notes, or explanations:

            ## Weekly AI News Digest

            **📅 Week of:** {week_range}
            **🌐 Sources:** [Comma-separated sources]

            ### 🔥 Top Story of the Week
            **Title:** [Title]
            *(Source: [Name])*
            **Published:** [YYYY-MM-DD]
            **Summary:** [200-300 words]
            **Why It Matters:** [100-150 words]

            ### 📰 This Week's Highlights
            1. **Title:** [Title]
            *(Source: [Name])*
            **Published:** [YYYY-MM-DD]
            - **Key Point:** [200 chars]

            2. **Title:** [Title] 
            *(Source: [Name])*
            **Published:** [YYYY-MM-DD]
            - **Key Point:** [200 chars]

            3. **Title:** [Title]
            *(Source: [Name])*
            **Published:** [YYYY-MM-DD] 
            - **Key Point:** [200 chars]

            ### 💡 Quick Bites
            - [Source: Title (YYYY-MM-DD)]
            - [Source: Title (YYYY-MM-DD)]

            Input Content:
            {state['draft']}
            """

        start_time = datetime.now()
        edited = editing_llm.invoke(editor_prompt)
        processing_time = (datetime.now() - start_time).total_seconds()
        logger.info(f"✅ Editing completed in {processing_time:.2f}s")
        logger.debug(f"Final structure validation:\n{edited.content[:500]}...")
            
        return {
            "final_content": edited.content,
            "editing_metrics": {
                "processing_time": processing_time,
                "week_range": week_range,
                "dates_included": edited.content.count("Published:"),
                "structure_valid": all(
                    x in edited.content 
                    for x in ["### 🔥 Top Story", "### 📰 This Week's Highlights", "### 💡 Quick Bites"]
                )
            }
        }

    return research_agent, writer_agent, editor_agent


def build_workflow(*agents):
    """Constructs and compiles the LangGraph workflow.
    
    Connects the agent nodes in sequence: researcher → writer → editor.
    Sets entry point and compiles the executable graph.
    
    Args:
        *agents: Three agent functions in order (research, writer, editor)
        
    Returns:
        Compiled LangGraph workflow that can be invoked
    """
    workflow = StateGraph(EditorState)
    
    # Add nodes
    for name, agent in zip(["researcher", "writer", "editor"], agents):
        workflow.add_node(name, agent)
    
    # Define edges
    workflow.add_edge("researcher", "writer")
    workflow.add_edge("writer", "editor")
    
    workflow.set_entry_point("researcher")
    return workflow.compile()