import requests
from bs4 import BeautifulSoup
import json

def scrape_mit_tech_review():
    url = "https://www.technologyreview.com/topic/artificial-intelligence/"
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36"
    }
    
    try:
        response = requests.get(url, headers=headers)
        response.raise_for_status()
        
        soup = BeautifulSoup(response.text, 'html.parser')
        articles = []
        
        # Extract article information
        article_elements = soup.select('.feedItem__title')
        
        for article in article_elements[:10]:  # Get top 10 articles
            title_element = article.find('a')
            if title_element:
                title = title_element.text.strip()
                link = title_element.get('href')
                if link and not link.startswith('http'):
                    link = 'https://www.technologyreview.com' + link
                
                articles.append({
                    'title': title,
                    'link': link
                })
        
        return articles
    except Exception as e:
        return {"error": str(e)}

def scrape_venturebeat_ai():
    url = "https://venturebeat.com/category/ai/"
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36"
    }
    
    try:
        response = requests.get(url, headers=headers)
        response.raise_for_status()
        
        soup = BeautifulSoup(response.text, 'html.parser')
        articles = []
        
        # Extract article information
        article_elements = soup.select('article.ArticleListing')
        
        for article in article_elements[:10]:  # Get top 10 articles
            title_element = article.find('h2')
            if title_element and title_element.find('a'):
                title = title_element.find('a').text.strip()
                link = title_element.find('a').get('href')
                
                articles.append({
                    'title': title,
                    'link': link
                })
        
        return articles
    except Exception as e:
        return {"error": str(e)}

# Collect data from multiple sources
mit_articles = scrape_mit_tech_review()
venturebeat_articles = scrape_venturebeat_ai()

# Combine results
results = {
    "mit_tech_review": mit_articles,
    "venturebeat": venturebeat_articles
}

print(json.dumps(results, indent=2))