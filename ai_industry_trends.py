import requests
from bs4 import BeautifulSoup
import json

def scrape_ai_trends():
    url = "https://www.forbes.com/sites/bernardmarr/2023/11/22/the-top-10-artificial-intelligence-trends-for-2024/"
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36"
    }
    
    try:
        response = requests.get(url, headers=headers)
        response.raise_for_status()
        
        soup = BeautifulSoup(response.text, 'html.parser')
        
        # Extract article title
        title = soup.find('h1').text.strip() if soup.find('h1') else "No title found"
        
        # Extract article content
        content_elements = soup.select('div.article-body p')
        content = [p.text.strip() for p in content_elements if p.text.strip()]
        
        # Look for trend headings (usually in strong or b tags)
        trend_elements = soup.select('div.article-body strong, div.article-body b')
        trends = [trend.text.strip() for trend in trend_elements if trend.text.strip()]
        
        # Filter out elements that don't look like trends
        trends = [t for t in trends if len(t) > 10 and 'trend' not in t.lower()]
        
        return {
            "title": title,
            "trends": trends[:10],  # Get top 10 trends
            "content_summary": " ".join(content[:5])  # Summarize first few paragraphs
        }
    except Exception as e:
        return {"error": str(e)}

# Get another source of AI trends
def scrape_stanford_ai_index():
    url = "https://aiindex.stanford.edu/report/"
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36"
    }
    
    try:
        response = requests.get(url, headers=headers)
        response.raise_for_status()
        
        soup = BeautifulSoup(response.text, 'html.parser')
        
        # Extract key findings
        findings = []
        finding_elements = soup.select('.key-finding-text')
        
        for element in finding_elements[:8]:  # Get top 8 findings
            findings.append(element.text.strip())
        
        return {
            "title": "Stanford AI Index Report",
            "key_findings": findings
        }
    except Exception as e:
        return {"error": str(e)}

# Collect data from multiple sources
forbes_trends = scrape_ai_trends()
stanford_ai = scrape_stanford_ai_index()

# Combine results
results = {
    "forbes_ai_trends": forbes_trends,
    "stanford_ai_index": stanford_ai
}

print(json.dumps(results, indent=2))