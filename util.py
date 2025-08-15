from typing import List, Dict
import requests
from requests.adapters import HTTPAdapter, Retry
from datetime import datetime, timedelta
import feedparser
import os

def load_feeds_from_file(file_path: str) -> Dict[str, str]:
    """Load RSS feed URLs from a configuration file.
    
    Args:
        file_path: Path to the feed configuration file
        
    Returns:
        Dictionary mapping feed names to their URLs
        
    Raises:
        ValueError: If the configuration file is not found
    """
    try:
        with open(file_path, 'r') as file:
            return {
                name.strip(): url.strip()
                for line in file
                if (stripped_line := line.strip()) and not stripped_line.startswith('#')
                for name, url in [stripped_line.split(':', 1)]
            }
    except FileNotFoundError:
        raise ValueError(f"Feed config file not found: {file_path}")

def save_final_digest(content: str) -> str:
    """Save digest content to a markdown file with naming format AI-Digest-YYYYMMDD.md.
    
    Args:
        content: Formatted markdown content
        
    Returns:
        str: Status message with file path or error
    """
    try:
        # Create output directory if it doesn't exist
        os.makedirs('digests', exist_ok=True)
        
        # Generate filename
        today = datetime.now().strftime('%Y%m%d')
        week_start = (datetime.now() - timedelta(days=7)).strftime('%Y%m%d')
        filename = f"digests/AI-Weekly-Digest-{week_start}-to-{today}.md"
        
        # Save content to file
        with open(filename, 'w', encoding='utf-8') as f:
            f.write(content)
        
        return f"✅ Successfully saved digest to {filename}"
    
    except Exception as e:
        return f"❌ Failed to save digest: {str(e)}"

class RSSFeedReader:
    """Reader for fetching and processing RSS feeds."""
    
    def __init__(self, feed_urls: Dict[str, str]):
        """Initialize the RSS feed reader.
        
        Args:
            feed_urls: Dictionary mapping feed names to URLs
        """
        self.feed_urls = feed_urls
        self.fetch_todays_feeds = self.fetch_weekly_feeds  # Backward compatibility
        self.session = requests.Session()
        retries = Retry(total=3, backoff_factor=1)
        self.session.mount('http://', HTTPAdapter(max_retries=retries))
        self.session.mount('https://', HTTPAdapter(max_retries=retries))

    def fetch_weekly_feeds(self) -> List[Dict]:
        """Fetch articles from the past week (last 7 days) from all configured RSS feeds.
        
        Returns:
            List of dictionaries containing article information
        """
        today = datetime.now().date()
        week_ago = today - timedelta(days=7)
        articles = []
        
        for source, url in self.feed_urls.items():
            try:
                feed = feedparser.parse(url)
                for entry in feed.entries:
                    if not hasattr(entry, 'published_parsed'):
                        continue
                    pub_date = datetime(*entry.published_parsed[:6]).date()
                    if week_ago <= pub_date < today:
                        articles.append({
                            'source': source,
                            'title': entry.get('title', 'No title'),
                            'link': entry.get('link', '#'),
                            'summary': entry.get('summary', ''),
                            'published': pub_date
                        })
            except Exception as e:
                print(f"Error processing {source} feed: {str(e)}")
        
        # Sort articles by date (newest first)
        articles.sort(key=lambda x: x['published'], reverse=True)
        return articles