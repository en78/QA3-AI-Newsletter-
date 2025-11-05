# 📰 AI News Summarizer and Emailer

## 🚀 Project Goal

This script automates the delivery of a personalized, AI-generated news digest. It fetches tech articles, uses the OpenAI API to create brief summaries, and emails the results securely.

## ✨ Key Features

* **RSS Feed Integration:** Pulls news links and titles from a randomized list of major tech publications (BBC, Wired, TechCrunch, The Verge).
* **Intelligent Web Scraping:** Uses the `BeautifulSoup` library with targeted CSS class detection to reliably extract only the main article text, avoiding boilerplate and ads.
* **AI Summarization:** Utilizes the **OpenAI API** (specifically a cost-effective model like `gpt-4.1-mini`) to generate professional, constraint-based summaries (under 100 words).
* **Secure Email Delivery:** Sends the newsletter using **Gmail's SMTP** server, ensuring security with **TLS encryption** and an **App Password**.
* **Dual-Format Email:** Sends the message using the `MIMEMultipart("alternative")` format, ensuring high-quality HTML rendering with a reliable plain-text fallback.

## 🛠️ Setup Guide

### 1. Prerequisites

Before running the script, ensure you have the following:

1.  **Python 3.x** installed.
2.  An **OpenAI API Key** for the summarization service.
3.  A **Gmail App Password** for secure login to the SMTP server. You must enable **2-Factor Authentication** on your Google account to generate this.

### 2. Install Dependencies

Open your terminal or command prompt and run this single command to install all necessary Python libraries:

```bash
pip install feedparser requests beautifulsoup4 openai