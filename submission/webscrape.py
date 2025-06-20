import requests
from bs4 import BeautifulSoup
import pandas as pd
from concurrent.futures import ThreadPoolExecutor, as_completed
from urllib.parse import urlparse

def create_headers():
    return {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36"
    }

def scrape_article(link):
    base_url = "https://r.jina.ai/"
    jina_headers = {"Accept": "text/event-stream"}
    url = base_url + link
    try:
        response = requests.get(url, headers=jina_headers)
        response.raise_for_status()
        return response.text
    except requests.exceptions.RequestException as e:
        print(f"Error fetching {url}: {e}")
        return None

def scrape_google_news(search_query, no_articles=10, scraped_urls=None):
    if scraped_urls is None:
        scraped_urls = set()
    
    query = search_query.replace(' ', '+')
    url = f"https://www.google.com/search?q={query}&tbm=nws"
    headers = create_headers()
    
    articles = []
    page_counter = 1
    consecutive_empty_pages = 0
    max_empty_pages = 3
    max_pages = 20
    
    while len(articles) < no_articles and consecutive_empty_pages < max_empty_pages and page_counter <= max_pages:
        response = requests.get(url, headers=headers)
        soup = BeautifulSoup(response.text, "html.parser")
        article_links = soup.find_all('a', class_='WlydOe')
        
        if not article_links:
            consecutive_empty_pages += 1
            print(f"No articles found on page {page_counter}. Empty pages: {consecutive_empty_pages}")
        else:
            consecutive_empty_pages = 0
        
        new_articles_found = False
        for item in article_links:
            if len(articles) >= no_articles:
                break
            link = item['href']
            
            parsed_url = urlparse(link)
            if 'gcaptain.com' in parsed_url.netloc or 'maritime-executive.com' in parsed_url.netloc:
                print(f"Skipping {parsed_url.netloc} link: {link}")
                continue
            
            if link in scraped_urls:
                print(f"Skipping duplicate article: {link}")
                continue
            
            content = scrape_article(link)
            if content:
                articles.append({
                    'search_query': search_query,
                    'link': link,
                    'content': content
                })
                scraped_urls.add(link)
                new_articles_found = True
                print(f"Scraped: {len(articles)}")
        
        if not new_articles_found:
            consecutive_empty_pages += 1
            print(f"No new articles found on page {page_counter}. Empty pages: {consecutive_empty_pages}")
        
        page_counter += 1
        next_page = soup.find('a', attrs={'aria-label': f"Page {page_counter}"})
        if next_page and 'href' in next_page.attrs:
            url = "https://www.google.com" + next_page['href']
        else:
            break
    
    if len(articles) < no_articles:
        print(f"Warning: Only found {len(articles)} unique articles out of {no_articles} requested.")
    
    return pd.DataFrame(articles)

def scrape_gcaptain(search_query, no_articles=10, scraped_urls=None):
    if scraped_urls is None:
        scraped_urls = set()
    
    query = search_query.replace(' ', '+')
    url = f"https://gcaptain.com/?s={query}"
    headers = create_headers()
    
    articles = []
    page_counter = 1
    consecutive_empty_pages = 0
    max_empty_pages = 3
    max_pages = 20
    
    while len(articles) < no_articles and consecutive_empty_pages < max_empty_pages and page_counter <= max_pages:
        response = requests.get(url, headers=headers)
        soup = BeautifulSoup(response.text, "html.parser")
        article_links = soup.find_all('a', class_='headline')
        
        if not article_links:
            consecutive_empty_pages += 1
            print(f"No articles found on page {page_counter}. Empty pages: {consecutive_empty_pages}")
        else:
            consecutive_empty_pages = 0
        
        new_articles_found = False
        for item in article_links:
            if len(articles) >= no_articles:
                break
            link = item['href']
            
            if link in scraped_urls:
                print(f"Skipping duplicate article: {link}")
                continue
            
            content = scrape_article(link)
            if content:
                articles.append({
                    'search_query': search_query,
                    'link': link,
                    'content': content
                })
                scraped_urls.add(link)
                new_articles_found = True
                print(f"Scraped: {len(articles)}")
        
        if not new_articles_found:
            consecutive_empty_pages += 1
            print(f"No new articles found on page {page_counter}. Empty pages: {consecutive_empty_pages}")
        
        page_counter += 1
        url = f"https://gcaptain.com/page/{page_counter}/?s={query}"
    
    if len(articles) < no_articles:
        print(f"Warning: Only found {len(articles)} unique articles out of {no_articles} requested.")
    
    return pd.DataFrame(articles)

def scrape_maritime_executive(search_query, no_articles=10, scraped_urls=None):
    if scraped_urls is None:
        scraped_urls = set()
    
    query = search_query.replace(' ', '+')
    url = f"https://www.maritime-executive.com/search?key={query}"
    headers = create_headers()
    
    articles = []
    page_counter = 1
    consecutive_empty_pages = 0
    max_empty_pages = 3
    max_pages = 20
    
    while len(articles) < no_articles and consecutive_empty_pages < max_empty_pages and page_counter <= max_pages:
        response = requests.get(url, headers=headers)
        soup = BeautifulSoup(response.text, "html.parser")
        article_links = soup.find_all('button', class_='search_article_link')
        
        if not article_links:
            consecutive_empty_pages += 1
            print(f"No articles found on page {page_counter}. Empty pages: {consecutive_empty_pages}")
        else:
            consecutive_empty_pages = 0
        
        new_articles_found = False
        for item in article_links:
            if len(articles) >= no_articles:
                break
            link = item.find('a')['href']
            
            if link in scraped_urls:
                print(f"Skipping duplicate article: {link}")
                continue
            
            content = scrape_article(link)
            if content:
                articles.append({
                    'search_query': search_query,
                    'link': link,
                    'content': content
                })
                scraped_urls.add(link)
                new_articles_found = True
                print(f"Scraped: {len(articles)}")
        
        if not new_articles_found:
            consecutive_empty_pages += 1
            print(f"No new articles found on page {page_counter}. Empty pages: {consecutive_empty_pages}")
        
        page_counter += 1
        url = f"https://www.maritime-executive.com/search?key={query}&amp;page={page_counter}"
    
    if len(articles) < no_articles:
        print(f"Warning: Only found {len(articles)} unique articles out of {no_articles} requested.")
    
    return pd.DataFrame(articles)

def jina_search(query, no_articles=1, scraped_urls=None):
    if scraped_urls is None:
        scraped_urls = set()
    
    try:
        jina_headers = {"Accept": "text/event-stream"}
        url = f"https://s.jina.ai/{query}/"
        
        if url in scraped_urls:
            print(f"Skipping duplicate Jina search: {url}")
            return pd.DataFrame()
        
        ws_response = requests.get(url, headers=jina_headers)
        ws_response.raise_for_status()
        
        scraped_urls.add(url)
        return pd.DataFrame({'search_query': query, 'link': url, 'content': ws_response.text}, index=[0])
    except requests.exceptions.RequestException as e:
        print(f"Error fetching from Jina AI for query '{query}': {e}")
        return pd.DataFrame()

def scrape_all_sources(query, no_articles=100, scraped_urls=None):
    if scraped_urls is None:
        scraped_urls = set()
    
    sources = [
        (scrape_google_news, "Google News"),
        (scrape_gcaptain, "GCaptain"),
        (scrape_maritime_executive, "Maritime Executive"),
        (jina_search, "Jina AI")
    ]
    
    results = []
    with ThreadPoolExecutor(max_workers=len(sources)) as executor:
        future_to_source = {executor.submit(func, query, no_articles, scraped_urls): name for func, name in sources}
        for future in as_completed(future_to_source):
            source_name = future_to_source[future]
            try:
                df = future.result()
                results.append(df)
                print(f"Completed scraping from {source_name}")
            except Exception as exc:
                print(f"{source_name} generated an exception: {exc}")
    
    return pd.concat(results, ignore_index=True)

def main():
    queries = [
        "Vessel delay","Vessel accidents","martime piracy","terrorism risk","port congestion","important route congestion","port criminal activites",
        "cargo damage and loss","inland transportation risks","maritime environmental impacts and pollution",
        "natural extreme events and extreme weather maritime","cargo and ship detainment","maritime unstable regulatory and political environment","Maritime port incident response strategies",
        "Best practices in port accident mitigation","Port risk management and incident prevention","Recent port disruptions and recovery strategies","Mitigation strategies for oil spills at ports",
        "Response to hazardous material spills in maritime ports","Fire safety protocols in maritime ports", "Cybersecurity threats and response in maritime logistics","Port infrastructure resilience during natural disasters",
        "Structural failure prevention strategies in ports","Resilient port design to mitigate environmental incidents","Use of AI in maritime incident prevention and response",
        "Port automation technologies for incident mitigation","Predictive maintenance in port operations to avoid incidents","Global policies on maritime incident response",
        "Port authority protocols for incident mitigation","Impact of international maritime regulations on port safety",
            ]
    
    all_results = []
    scraped_urls = set()
    for query in queries:
        print(f"Processing query: {query}")
        results = scrape_all_sources(query, scraped_urls=scraped_urls)
        all_results.append(results)
        print(f"Completed processing for: {query}")
    
    final_df = pd.concat(all_results, ignore_index=True)
    final_df.to_csv("maritime_data.csv", index=False)
    print("Data saved to maritime_data.csv")
    print(f"Total unique articles scraped: {len(scraped_urls)}")

if __name__ == "__main__":
    main()
    
    
   
