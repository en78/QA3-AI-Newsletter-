import feedparser
import ssl
import requests
from bs4 import BeautifulSoup
from openai import OpenAI

# Fix for potential SSL/TLS issues when fetching certain RSS feeds on some systems.
if hasattr(ssl, '_create_unverified_context'):
    ssl._create_default_https_context = ssl._create_unverified_context

# --- Configuration ---
# 1. RSS Feed URL (Topic of Interest)
SAMPLE_RSS_URL = "http://feeds.bbci.co.uk/news/technology/rss.xml"
MAX_ARTICLES_TO_PROCESS = 3 # Limiting to 3 as requested for testing

# 2. OpenAI Configuration
# IMPORTANT: Replace 'YOUR_OPENAI_API_KEY' with your actual key.
OPENAI_API_KEY = "apikeyhere"

# --- Content Fetching & Scraping ---

def fetch_article_content(url):
    """
    Fetches the HTML content of an article URL and attempts to extract
    the main body text using basic heuristics.
    
    NOTE: Web scraping is complex. This is a simple implementation 
    and may fail on complex websites.
    """
    try:
        # Use a common User-Agent to prevent some websites from blocking the request
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
        }
        response = requests.get(url, headers=headers, timeout=10)
        response.raise_for_status()
        
        soup = BeautifulSoup(response.content, 'html.parser')
        
        # Simple heuristic: try to find a container that holds the main article body.
        # This checks common tags/classes used for article content.
        article_text = ""
        
        # Check for common containers first (article tag, div with specific roles/classes)
        main_content = soup.find(['article', 'main'], class_=['story-body__inner', 'article-body', 'entry-content', 'td-post-content', 'post-content'])
        
        if main_content:
            # If a main container is found, get all paragraph text within it
            paragraphs = main_content.find_all('p')
            article_text = "\n".join([p.get_text() for p in paragraphs])
        else:
            # Fallback: get text from all paragraphs on the page (less reliable)
            paragraphs = soup.find_all('p')
            article_text = "\n".join([p.get_text() for p in paragraphs])
            
        return article_text.strip()
        
    except requests.exceptions.RequestException as e:
        print(f"   [Error Scraping] Failed to fetch article URL: {e}")
        return ""
    except Exception as e:
        print(f"   [Error Scraping] An unexpected error occurred: {e}")
        return ""

# --- LLM Summarization ---

def summarize_text(article_text, model="gpt-4.1-mini"):
    """
    Uses the OpenAI API to generate a concise, email-friendly summary.
    """
    if OPENAI_API_KEY == "YOUR_OPENAI_API_KEY":
        return "ERROR: Please provide your OpenAI API Key in the script configuration."

    if not article_text:
        return "No article content to summarize."

    # Initialize the OpenAI client
    client = OpenAI(api_key=OPENAI_API_KEY)

    system_prompt = (
        "You are an expert content curator for an email newsletter. "
        "Your task is to take the provided article text and create a concise, "
        "one-paragraph summary (maximum 100 words) suitable for a busy, professional audience. "
        "Focus only on the key takeaways and main impact."
    )

    try:
        # Call the OpenAI API
        response = client.chat.completions.create(
            model=model,
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": f"Summarize this article: {article_text}"}
            ],
            temperature=0.3, # Lower temperature for factual summarization
        )
        
        # Extract the summary text
        summary = response.choices[0].message.content
        return summary
    
    except Exception as e:
        return f"An OpenAI API error occurred: {e}"

# --- Main Logic ---

def generate_newsletter_draft(rss_url, max_articles=MAX_ARTICLES_TO_PROCESS):
    """
    Fetches, scrapes, and summarizes articles from an RSS feed.
    """
    print(f"--- 1. Fetching Feed: {rss_url} ---")

    # Fetch and parse the RSS feed
    feed = feedparser.parse(rss_url)
    
    if feed.bozo:
        print(f"Warning: RSS feed may be malformed. Error: {feed.bozo_exception}")
        
    if not feed.entries:
        print("No entries found in the RSS feed.")
        return

    feed_title = feed.feed.get('title', 'Unknown Source')
    print(f"Source: {feed_title}. Total entries found: {len(feed.entries)}")
    
    articles_data = []

    print("\n--- 2. Processing and Summarizing Articles ---")
    
    # Iterate for the requested number of articles
    for i, entry in enumerate(feed.entries):
        if i >= max_articles:
            break
        
        title = entry.get('title', 'No Title Available')
        link = entry.get('link', 'No Link Available')
        
        print(f"\n[{i + 1}/{max_articles}] Article: '{title}'")
        
        # A. Scrape Article Content
        print("   Scraping article content...")
        article_content = fetch_article_content(link)
        
        if len(article_content) < 50: # Check if content is too short to summarize
            print("   Warning: Article content is too short or scraping failed. Skipping summary.")
            summary = "SUMMARY FAILED (Insufficient content)"
        else:
            # B. Summarize Content with LLM
            print("   Generating summary with OpenAI...")
            summary = summarize_text(article_content)
        
        # C. Store and Print Results
        articles_data.append({
            'title': title,
            'link': link,
            'summary': summary
        })
        
        print("\n--- Summary Output ---")
        print(f"TITLE: {title}")
        print(f"SUMMARY:\n{summary}")
        print("-" * 50)


# --- Example Usage ---
if __name__ == '__main__':
    generate_newsletter_draft(rss_url=SAMPLE_RSS_URL)
