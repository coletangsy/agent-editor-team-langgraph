import os
import logging
from dotenv import load_dotenv
from langchain_deepseek import ChatDeepSeek
from util import load_feeds_from_file, RSSFeedReader, save_final_digest
from ai_news_team import create_agents, build_workflow
from datetime import datetime

def configure_environment():
    """Initialize the application environment configuration.
    
    Loads environment variables from .env file and sets up basic logging configuration.
    This should be called before any other application initialization.
    """
    load_dotenv()
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(levelname)s - %(message)s',
        handlers=[
            logging.FileHandler('editor_team.log'),
            logging.StreamHandler()
        ]
    )

def configure_logging():
    """Configure advanced logging with timestamped log files.
    
    Creates a dedicated log directory and configures logging with:
    - Timestamped log files (editor_team_YYYYMMDD_HHMMSS.log)
    - Both file and console output handlers
    - Consistent log formatting
    
    Returns:
        str: Path to the created log file
    """
    os.makedirs('log', exist_ok=True)
    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    log_file = f'log/editor_team_{timestamp}.log'
    
    # Clear any existing handlers
    logging.getLogger().handlers.clear()
    
    # Create formatter
    formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')
    
    # Create file handler
    file_handler = logging.FileHandler(log_file)
    file_handler.setFormatter(formatter)
    
    # Create console handler
    console_handler = logging.StreamHandler()
    console_handler.setFormatter(formatter)
    
    # Get root logger and configure
    logger = logging.getLogger()
    logger.setLevel(logging.INFO)
    logger.addHandler(file_handler)
    logger.addHandler(console_handler)
    
    return log_file

def initialize_llms():
    """Initialize and configure LLM instances for different roles.
    
    Creates three separate LLM instances with different temperature settings:
    - Research LLM (higher temperature for creative discovery)
    - Writing LLM (moderate temperature for balanced output)
    - Editing LLM (low temperature for precise edits)
    
    Returns:
        dict: Dictionary containing configured LLM instances with keys:
              'research', 'writing', 'editing'
    """
    return {
        'research': ChatDeepSeek(model="deepseek-chat", temperature=0.7),
        'writing': ChatDeepSeek(model="deepseek-chat", temperature=0.4), 
        'editing': ChatDeepSeek(model="deepseek-chat", temperature=0.2)
    }

def main():
    """Main entry point for the AI News Team workflow.
    
    Orchestrates the entire process:
    1. Initializes environment and logging
    2. Configures LLM instances
    3. Sets up feed reader
    4. Creates agent team
    5. Builds and executes workflow
    6. Saves final output
    
    Logs progress through each stage and handles the workflow execution.
    """
    # Initialization
    configure_environment()

    log_path = configure_logging()
    logger = logging.getLogger(__name__)
    logger.info(f"🚀 Starting AI News Team workflow - Logging to {log_path}")
    
    llms = initialize_llms()
    feed_reader = RSSFeedReader(load_feeds_from_file('feeds.txt'))
    
    # Create agent team
    research_agent, writer_agent, editor_agent = create_agents(
        feed_reader=feed_reader,
        research_llm=llms['research'],
        writing_llm=llms['writing'],
        editing_llm=llms['editing']
    )
    
    # Build and execute workflow
    app = build_workflow(research_agent, writer_agent, editor_agent)
    result = app.invoke({"messages": []})
    
    # Save output
    print(save_final_digest(result["final_content"]))

if __name__ == "__main__":
    main()