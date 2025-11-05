import feedparser
import ssl
import requests
import random
import smtplib
from bs4 import BeautifulSoup
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from openai import OpenAI

# --- CONFIGURATION ---
# Your OpenAI API Key
OPENAI_API_KEY = "your open ai api key here"

# Email Settings (Gmail SMTP)
SMTP_SERVER = "smtp.gmail.com"
SMTP_PORT = 587
SENDER_EMAIL = "Sender email"
SENDER_PASSWORD = "16 digit app password to sender email here"  # App password, not your main Gmail password
RECIPIENT_EMAIL = "recipient email"

TECH_FEEDS = [
    "http://feeds.bbci.co.uk/news/technology/rss.xml",
    "https://www.wired.com/feed/rss",
    "https://techcrunch.com/feed/",
    "https://www.theverge.com/rss/index.xml"
]
# --- Handles SSL Certificate Errors
if hasattr(ssl, '_create_unverified_context'):
    ssl._create_default_https_context = ssl._create_unverified_context


# --- ARTICLE FETCHING ---

def fetch_article_content(url):
    try:
        headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64)'}
        response = requests.get(url, headers=headers, timeout=10)
        response.raise_for_status()
        soup = BeautifulSoup(response.content, 'html.parser')

        main_content = soup.find(['article', 'main'], class_=[
            'story-body__inner', 'article-body', 'entry-content',
            'td-post-content', 'post-content'
        ])

        if main_content:
            paragraphs = main_content.find_all('p')
        else:
            paragraphs = soup.find_all('p')

        text = "\n".join(p.get_text() for p in paragraphs)
        return text.strip()
    except Exception as e:
        print(f"[Error Scraping] {e}")
        return ""


# --- SUMMARIZATION ---

def summarize_text(article_text, model="gpt-4.1-mini"):
    if not article_text:
        return "No content available to summarize."

    client = OpenAI(api_key=OPENAI_API_KEY)

    system_prompt = (
        "You are an expert tech journalist writing a short AI-powered newsletter. "
        "Summarize the article in under 100 words, keeping it professional and insightful. "
        "Focus on key developments, impacts, and why it matters."
    )

    try:
        response = client.chat.completions.create(
            model=model,
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": article_text}
            ],
            temperature=0.4,
        )
        return response.choices[0].message.content.strip()
    except Exception as e:
        return f"OpenAI API error: {e}"


# --- EMAIL BUILDING AND SENDING (HTML VERSION) ---
# Defining Email Sending Function w/ necessary pieces
def send_email(subject, summary, title, link, to_email):
    try:
        # Build HTML and plain text versions
        html_body = f"""
        <html>
            <body style="font-family: Arial, sans-serif; color: #222; background-color: #f9f9f9; padding: 20px;">
                <div style="max-width: 600px; margin: auto; background-color: #fff; border-radius: 10px; box-shadow: 0 2px 8px rgba(0,0,0,0.1); padding: 30px;">
                    <h2 style="color: #2b6cb0;">📰 AI Tech Newsletter</h2>
                    <h3 style="color: #1a202c;">{title}</h3>
                    <p style="font-size: 16px; line-height: 1.5;">{summary}</p>
                    <div style="text-align: center; margin-top: 25px;">
                        <a href="{link}" target="_blank"
                           style="background-color: #2b6cb0; color: #fff; text-decoration: none; padding: 12px 25px; border-radius: 6px; font-weight: bold;">
                           Read Full Article
                        </a>
                    </div>
                    <hr style="margin-top: 30px; border: none; border-top: 1px solid #ddd;">
                    <p style="font-size: 12px; color: #555; text-align: center;">
                        Sent by your AI Tech Newsletter<br>
                        <em>Each run brings you a fresh tech story.</em>
                    </p>
                </div>
            </body>
        </html>
        """

        plain_text = f"""
        AI Tech Newsletter

        {title}
        {summary}

        Read more: {link}

        — AI Tech Newsletter 
        """

        # Prepare message
        msg = MIMEMultipart("alternative")
        msg["From"] = SENDER_EMAIL
        msg["To"] = to_email
        msg["Subject"] = subject

        # Attach both plain and HTML versions
        msg.attach(MIMEText(plain_text, "plain"))
        msg.attach(MIMEText(html_body, "html"))

        # Send email
        with smtplib.SMTP(SMTP_SERVER, SMTP_PORT) as server:
            server.starttls()
            server.login(SENDER_EMAIL, SENDER_PASSWORD)
            server.send_message(msg)

        print(f"[Email Sent] Message successfully delivered to {to_email} ✅")

    except Exception as e:
        print(f"[Email Error] {e}")


# --- MAIN LOGIC ---

def generate_and_email_newsletter():
    rss_url = random.choice(TECH_FEEDS)
    print(f"--- Fetching from RSS Feed: {rss_url} ---")

    feed = feedparser.parse(rss_url)
    if not feed.entries:
        print("No entries found.")
        return

    entry = random.choice(feed.entries)
    title = entry.get('title', 'No Title')
    link = entry.get('link', '')
    print(f"Selected Article: {title}")

    content = fetch_article_content(link)
    if len(content) < 50:
        print("Article content too short. Skipping.")
        return

    summary = summarize_text(content)

    subject = f"AI Tech Brief: {title}"
    send_email(subject, summary, title, link, RECIPIENT_EMAIL)


# --- RUN ---
if __name__ == "__main__":
    generate_and_email_newsletter()
