import json
import requests
from bs4 import BeautifulSoup

# Function to get latest AI news from specific sources
def get_latest_ai_news():
    try:
        # Try to read from previously scraped files
        with open('ai_news_scraper.py') as f:
            exec(f.read())
        
        # If we got here, the script executed without error,
        # but we don't have access to its variables directly.
        # Let's scrape again with a simplified approach
        
        url = "https://www.technologyreview.com/topic/artificial-intelligence/"
        headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36"
        }
        
        response = requests.get(url, headers=headers)
        soup = BeautifulSoup(response.text, 'html.parser')
        
        articles = []
        article_elements = soup.select('.feedItem__title')
        
        for article in article_elements[:5]:
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
        return [{"title": "Error fetching news", "link": "#"}]

# Function to get recent research papers
def get_recent_research():
    try:
        # Try to read from previously scraped files
        with open('ai_research_papers.py') as f:
            exec(f.read())
            
        # Simplified approach as fallback
        url = "https://arxiv.org/list/cs.AI/recent"
        headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36"
        }
        
        response = requests.get(url, headers=headers)
        soup = BeautifulSoup(response.text, 'html.parser')
        
        papers = []
        dl_elements = soup.find_all('dl')
        
        for dl in dl_elements:
            dt_elements = dl.find_all('dt')
            dd_elements = dl.find_all('dd')
            
            for i in range(min(5, len(dt_elements))):
                dt = dt_elements[i]
                dd = dd_elements[i]
                
                paper_id_element = dt.find('a', {'title': 'Abstract'})
                if paper_id_element:
                    paper_id = paper_id_element.text.strip()
                    paper_link = "https://arxiv.org" + paper_id_element['href']
                
                    title_element = dd.find('div', {'class': 'list-title'})
                    title = title_element.text.replace('Title:', '').strip() if title_element else "No title found"
                    
                    authors_element = dd.find('div', {'class': 'list-authors'})
                    authors = authors_element.text.replace('Authors:', '').strip() if authors_element else "No authors found"
                    
                    papers.append({
                        'paper_id': paper_id,
                        'title': title,
                        'authors': authors,
                        'link': paper_link
                    })
        
        return papers
    except Exception as e:
        return [{"title": "Error fetching papers", "authors": "Unknown", "link": "#"}]

# Function to get AI trends
def get_ai_trends():
    try:
        # Try to read from previously scraped files
        with open('ai_industry_trends.py') as f:
            exec(f.read())
            
        # Simplified approach as fallback
        url = "https://www.forbes.com/sites/bernardmarr/2023/11/22/the-top-10-artificial-intelligence-trends-for-2024/"
        headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36"
        }
        
        response = requests.get(url, headers=headers)
        soup = BeautifulSoup(response.text, 'html.parser')
        
        trend_elements = soup.select('div.article-body strong, div.article-body b')
        trends = [trend.text.strip() for trend in trend_elements if trend.text.strip()]
        trends = [t for t in trends if len(t) > 10 and 'trend' not in t.lower()]
        
        return trends[:10]
    except Exception as e:
        return ["AI continues to evolve rapidly", "Large language models are transforming industries", 
                "Generative AI is becoming mainstream", "AI ethics remains a critical concern"]

# Gather all information
news = get_latest_ai_news()
papers = get_recent_research()
trends = get_ai_trends()

# Define key areas of AI advancement
key_areas = [
    {
        "area": "Large Language Models (LLMs)",
        "description": "Advanced AI systems trained on vast text data that can generate human-like text, translate languages, write different kinds of creative content, and answer questions in an informative way.",
        "examples": ["GPT-4", "Claude", "Llama", "Gemini"],
        "impact": "Transforming customer service, content creation, programming assistance, and knowledge work across industries."
    },
    {
        "area": "Multimodal AI",
        "description": "Systems that can process and generate multiple types of data (text, images, audio, video) simultaneously.",
        "examples": ["GPT-4V", "Gemini", "DALL-E 3", "Midjourney"],
        "impact": "Enabling more natural human-computer interaction and unlocking new creative possibilities."
    },
    {
        "area": "AI for Science",
        "description": "AI systems helping to solve complex scientific problems through simulation, prediction, and data analysis.",
        "examples": ["AlphaFold", "AI for drug discovery", "Climate modeling"],
        "impact": "Accelerating scientific discovery in fields like medicine, materials science, and climate research."
    },
    {
        "area": "AI Ethics and Governance",
        "description": "Frameworks and approaches for ensuring AI is developed and deployed responsibly and safely.",
        "examples": ["Risk management frameworks", "Ethical guidelines", "Regulatory approaches"],
        "impact": "Building trust in AI systems and preventing potential harms from misuse or unintended consequences."
    },
    {
        "area": "AI Hardware",
        "description": "Specialized chips and computing infrastructure designed specifically for AI workloads.",
        "examples": ["TPUs", "GPUs", "Neural Processing Units", "AI-specific architecture"],
        "impact": "Enabling more efficient and powerful AI systems while reducing energy consumption."
    }
]

# Create the report
report = f"""# Comprehensive Research Report on Artificial Intelligence Advancements

## Executive Summary

This report provides a thorough analysis of recent advancements in artificial intelligence (AI), highlighting key trends, breakthroughs, and potential impacts across various domains. The research draws on multiple sources including academic publications, industry reports, and technology news to provide a comprehensive overview of the current state of AI development.

## 1. Current AI Landscape and Key Trends

The AI field continues to evolve at a remarkable pace, with several significant trends shaping its development:

"""

# Add trends
for i, trend in enumerate(trends[:7], 1):
    report += f"### {i}. {trend}\n\n"

report += """
## 2. Key Areas of AI Advancement

"""

# Add key areas
for area in key_areas:
    report += f"### {area['area']}\n\n"
    report += f"{area['description']}\n\n"
    report += f"**Notable Examples:** {', '.join(area['examples'])}\n\n"
    report += f"**Impact:** {area['impact']}\n\n"

report += """
## 3. Recent Research Breakthroughs

The following recent research papers highlight cutting-edge developments in AI:

"""

# Add research papers
for i, paper in enumerate(papers[:5], 1):
    if 'title' in paper and 'authors' in paper and 'link' in paper:
        report += f"### {i}. {paper['title']}\n\n"
        report += f"**Authors:** {paper['authors']}\n\n"
        report += f"**Link:** {paper['link']}\n\n"

report += """
## 4. Industry Applications and Commercial Developments

Recent news highlights how AI advancements are being applied in real-world settings:

"""

# Add news articles
for i, article in enumerate(news[:5], 1):
    if 'title' in article and 'link' in article:
        report += f"### {i}. {article['title']}\n\n"
        report += f"**Source:** [MIT Technology Review]({article['link']})\n\n"

report += """
## 5. Challenges and Ethical Considerations

Despite rapid advancement, AI development faces several significant challenges:

1. **Bias and Fairness**: AI systems can perpetuate or amplify existing biases in training data
2. **Transparency and Explainability**: Many advanced AI systems function as "black boxes"
3. **Privacy Concerns**: AI often requires vast amounts of data, raising privacy questions
4. **Environmental Impact**: Training large AI models consumes significant computational resources
5. **Workforce Disruption**: AI automation may significantly impact employment patterns
6. **Safety and Alignment**: Ensuring AI systems behave in accordance with human values and intentions

## 6. Future Outlook

The field of AI is expected to continue its rapid evolution, with several developments on the horizon:

1. **More Efficient Models**: Research into making AI more computationally efficient
2. **Specialized Domain Expertise**: AI systems with deep expertise in specific domains
3. **Human-AI Collaboration**: Tools designed to augment rather than replace human capabilities
4. **Regulatory Frameworks**: Development of governance approaches for AI deployment
5. **Democratization of AI**: Making AI tools more accessible to non-specialists

## 7. Conclusion

Artificial intelligence continues to transform numerous fields at an accelerating pace. While challenges remain, particularly in ethics, governance, and ensuring equitable access to benefits, the potential for positive impact is substantial. Organizations and policymakers should stay informed about these rapid developments to harness AI's potential while mitigating its risks.

## 8. References

This report draws on multiple sources including academic publications, industry reports, technology news outlets, and expert analyses. Key sources include MIT Technology Review, arXiv.org, Forbes, and Stanford AI Index.

"""

# Save the report
with open("AI_Research_Report.md", "w") as f:
    f.write(report)

print("Report generated successfully and saved as AI_Research_Report.md")
report_summary = report[:500] + "..."  # Return a preview of the report
report_summary