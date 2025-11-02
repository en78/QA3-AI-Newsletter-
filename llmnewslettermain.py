import feedparser
import ssl

# Fix for potential SSL/TLS issues when fetching certain RSS feeds on some systems.
# This makes the script more robust for various hosting environments.
if hasattr(ssl, '_create_unverified_context'):
    ssl._create_default_https_context = ssl._create_unverified_context

# --- Configuration ---
# You can change this to any RSS feed URL you want to use.
SAMPLE_RSS_URL = "http://feeds.bbci.co.uk/news/technology/rss.xml"
MAX_ARTICLES = 5

def fetch_and_print_rss_feed(rss_url, max_articles=MAX_ARTICLES):
    """
    Fetches and parses an RSS feed URL and prints the headlines and links.
    
    Args:
        rss_url (str): The URL of the RSS feed.
        max_articles (int): The maximum number of entries (articles) to process.
    """
    
    print(f"--- Fetching news from RSS Feed: {rss_url} ---")

    try:
        # Use feedparser to fetch and parse the RSS feed
        feed = feedparser.parse(rss_url)
        
        # Check for errors during parsing (e.g., malformed XML)
        if feed.bozo:
            print(f"Warning: RSS feed may be malformed. Error: {feed.bozo_exception}")
            
        
        if not feed.entries:
            print("No entries found in the RSS feed.")
            return

        # Get the main title of the feed
        feed_title = feed.feed.get('title', 'Unknown Source')
        print(f"Source: {feed_title}")
        print(f"Total entries found: {len(feed.entries)}")

        # Print the required output: headlines and article links
        articles_count = 0
        print("\n--- Latest Headlines ---")
        for entry in feed.entries:
            if articles_count >= max_articles:
                break
            
            # RSS entries typically contain 'title' and 'link' attributes
            title = entry.get('title', 'No Title Available')
            link = entry.get('link', 'No Link Available')
            published = entry.get('published', 'N/A')

            print(f"\n{articles_count + 1}. Headline: {title}")
            print(f"   Link:     {link}")
            print(f"   Published: {published}")
            
            articles_count += 1
            
        if articles_count < len(feed.entries):
             print(f"\n--- Output limited to first {MAX_ARTICLES} articles. ---")
             
    except Exception as e:
        print(f"An error occurred while processing the RSS feed: {e}")

# --- Example Usage ---
if __name__ == '__main__':
    # You can easily change this URL to any RSS feed you want to use.
    fetch_and_print_rss_feed(rss_url=SAMPLE_RSS_URL, max_articles=MAX_ARTICLES)
