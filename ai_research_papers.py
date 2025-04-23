import requests
from bs4 import BeautifulSoup
import json

def scrape_arxiv_ai_papers():
    url = "https://arxiv.org/list/cs.AI/recent"
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36"
    }
    
    try:
        response = requests.get(url, headers=headers)
        response.raise_for_status()
        
        soup = BeautifulSoup(response.text, 'html.parser')
        papers = []
        
        # Find the dl elements containing papers
        dl_elements = soup.find_all('dl')
        
        for dl in dl_elements:
            # Find all dt elements (contain dates and links)
            dt_elements = dl.find_all('dt')
            # Find all dd elements (contain abstracts)
            dd_elements = dl.find_all('dd')
            
            # Process each paper
            for i in range(min(10, len(dt_elements))):  # Get top 10 papers
                dt = dt_elements[i]
                dd = dd_elements[i]
                
                # Extract paper ID and link
                paper_id_element = dt.find('a', {'title': 'Abstract'})
                if paper_id_element:
                    paper_id = paper_id_element.text.strip()
                    paper_link = "https://arxiv.org" + paper_id_element['href']
                
                    # Extract title
                    title_element = dd.find('div', {'class': 'list-title'})
                    title = title_element.text.replace('Title:', '').strip() if title_element else "No title found"
                    
                    # Extract authors
                    authors_element = dd.find('div', {'class': 'list-authors'})
                    authors = authors_element.text.replace('Authors:', '').strip() if authors_element else "No authors found"
                    
                    # Extract abstract
                    abstract_element = dd.find('p', {'class': 'mathjax'})
                    abstract = abstract_element.text.strip() if abstract_element else "No abstract found"
                    
                    papers.append({
                        'paper_id': paper_id,
                        'title': title,
                        'authors': authors,
                        'link': paper_link,
                        'abstract': abstract[:200] + "..." if len(abstract) > 200 else abstract  # Truncate long abstracts
                    })
        
        return papers
    except Exception as e:
        return {"error": str(e)}

# Get recent AI research papers from arXiv
papers = scrape_arxiv_ai_papers()

# Output results
print(json.dumps(papers, indent=2))