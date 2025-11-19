"""
Tavily Search & Content Extraction Tools for Advanced Reconnaissance.

This module provides powerful intelligence gathering capabilities using Tavily's API:
- tavily_search: Performs web searches with AI-powered relevance ranking and advanced filtering
- tavily_extract_content: Deep-dives into specific URLs for comprehensive content analysis
- tavily_crawl: Systematically explores websites starting from a base URL
- tavily_map: Creates detailed site maps by analyzing website structure

For maximum effectiveness, use tavily_search first to find relevant URLs, 
then use tavily_extract_content to get detailed information from the most promising sources.
"""
from dotenv import load_dotenv
import os
from typing import List, Optional, Literal
from cai.sdk.agents import function_tool
from tavily import TavilyClient

# Load environment variables
load_dotenv()

def _get_tavily_client() -> TavilyClient:
    """Get Tavily client with API key validation."""
    tavily_api_key = os.getenv("TAVILY_KEY")
    if not tavily_api_key:
        raise ValueError("TAVILY_KEY environment variable is not set.")
    return TavilyClient(api_key=tavily_api_key)


def _add_optional_params(params: dict, **kwargs) -> dict:
    """Add optional parameters to params dict if they are not None or empty."""
    for key, value in kwargs.items():
        if value is not None and value != [] and value != "":
            params[key] = value
    return params


@function_tool
def tavily_search(
    query: str,
    search_depth: Literal["basic", "advanced"] = "basic",
    topic: Literal["general", "news"] = "general",
    days: Optional[int] = None,
    time_range: Optional[Literal["day", "week", "month", "year", "d", "w", "m", "y"]] = None,
    max_results: int = 10,
    include_images: bool = False,
    include_image_descriptions: bool = False,
    include_raw_content: bool = False,
    include_domains: Optional[List[str]] = None,
    exclude_domains: Optional[List[str]] = None,
    country: Optional[str] = None,
    include_favicon: bool = False
) -> str:
    """
    A powerful web search tool that provides comprehensive, real-time results using Tavily's AI search engine.

    Args:
        query (str): Search query
        search_depth (str): The depth of the search - 'basic' or 'advanced' (default: 'basic')
        topic (str): The category of the search - 'general' or 'news' (default: 'general')
        days (int, optional): Number of days back from current date for search results (only for 'news' topic)
        time_range (str, optional): Time range for results - 'day', 'week', 'month', 'year' (or 'd', 'w', 'm', 'y')
        max_results (int): Maximum number of search results to return (5-20, default: 10)
        include_images (bool): Include a list of query-related images (default: False)
        include_image_descriptions (bool): Include images with descriptions (default: False)
        include_raw_content (bool): Include cleaned and parsed HTML content of each result (default: False)
        include_domains (List[str], optional): List of domains to specifically include in search
        exclude_domains (List[str], optional): List of domains to specifically exclude from search
        country (str, optional): Boost search results from a specific country (only for 'general' topic)
        include_favicon (bool): Include favicon URL for each result (default: False)

    Returns:
        str: Formatted search results with URLs, titles, summaries, and optional images
    """
    tavily_client = _get_tavily_client()

    # Build search parameters
    search_params = {
        "query": query,
        "search_depth": search_depth,
        "topic": topic,
        "max_results": min(max(max_results, 5), 20),
        "include_images": include_images or include_image_descriptions,
        "include_image_descriptions": include_image_descriptions,
        "include_raw_content": include_raw_content,
    }

    # Add optional parameters
    if days is not None and topic == "news":
        search_params["days"] = days
    
    _add_optional_params(
        search_params,
        time_range=time_range,
        include_domains=include_domains,
        exclude_domains=exclude_domains,
        include_favicon=include_favicon if include_favicon else None
    )
    
    if country and topic == "general":
        search_params["topic"] = "general"
        search_params["country"] = country.lower()

    response = tavily_client.search(**search_params)

    # Format results similar to index.ts
    output = []
    
    # Include answer if available
    if "answer" in response and response["answer"]:
        output.append(f"Answer: {response['answer']}")
        output.append("")
    
    # Format detailed search results
    output.append("Detailed Results:")
    for result in response["results"]:
        output.append(f"\nTitle: {result['title']}")
        output.append(f"URL: {result['url']}")
        output.append(f"Content: {result['content']}")
        
        if "score" in result:
            output.append(f"Score: {result['score']:.2f}")
        
        if include_raw_content and "raw_content" in result and result["raw_content"]:
            output.append(f"Raw Content: {result['raw_content']}")
        
        if include_favicon and "favicon" in result and result["favicon"]:
            output.append(f"Favicon: {result['favicon']}")
    
    # Add images section if available
    if include_images and "images" in response and response["images"]:
        output.append("\nImages:")
        for index, image in enumerate(response["images"], 1):
            if isinstance(image, str):
                output.append(f"\n[{index}] URL: {image}")
            elif isinstance(image, dict):
                output.append(f"\n[{index}] URL: {image.get('url', 'N/A')}")
                if "description" in image and image["description"]:
                    output.append(f"   Description: {image['description']}")
    
    return "\n".join(output)

@function_tool
def tavily_extract(
    urls: List[str],
    extract_depth: Literal["basic", "advanced"] = "basic",
    include_images: bool = False,
    format: Literal["markdown", "text"] = "markdown",
    include_favicon: bool = False
) -> str:
    """
    A powerful web content extraction tool that retrieves and processes raw content from specified URLs.

    Args:
        urls (List[str]): List of URLs to extract content from
        extract_depth (str): Depth of extraction - 'basic' or 'advanced' (default: 'basic')
        include_images (bool): Include list of images extracted from the URLs (default: False)
        format (str): Format of extracted content - 'markdown' or 'text' (default: 'markdown')
        include_favicon (bool): Include favicon URL for each result (default: False)

    Returns:
        str: Full content from the webpages in the specified format
    """
    tavily_client = _get_tavily_client()

    # Build extract parameters
    extract_params = {"urls": urls, "extract_depth": extract_depth}
    _add_optional_params(
        extract_params,
        include_images=include_images if include_images else None,
        format=format,
        include_favicon=include_favicon if include_favicon else None
    )

    response = tavily_client.extract(**extract_params)

    # Format results similar to index.ts
    output = []
    output.append("Detailed Results:")
    
    for result in response["results"]:
        output.append(f"\nURL: {result['url']}")
        
        if "raw_content" in result and result["raw_content"]:
            output.append(f"Content: {result['raw_content']}")
        
        if include_favicon and "favicon" in result and result["favicon"]:
            output.append(f"Favicon: {result['favicon']}")
        
        # Add images if available
        if include_images and "images" in result and result["images"]:
            output.append(f"\nImages ({len(result['images'])} found):")
            for img_idx, image_url in enumerate(result["images"][:20], 1):
                output.append(f"  [{img_idx}] {image_url}")
    
    return "\n".join(output)


@function_tool
def tavily_crawl(
    url: str,
    max_depth: int = 1,
    max_breadth: int = 20,
    limit: int = 50,
    instructions: Optional[str] = None,
    select_paths: Optional[List[str]] = None,
    select_domains: Optional[List[str]] = None,
    allow_external: bool = True,
    extract_depth: Literal["basic", "advanced"] = "basic",
    format: Literal["markdown", "text"] = "markdown",
    include_favicon: bool = False
) -> str:
    """
    A powerful web crawler that initiates a structured web crawl starting from a specified base URL.
    The crawler expands from that point like a graph, following internal links across pages.

    Args:
        url (str): The root URL to begin the crawl
        max_depth (int): Max depth of the crawl - how far from base URL to explore (default: 1, minimum: 1)
        max_breadth (int): Max number of links to follow per level/page (default: 20, minimum: 1)
        limit (int): Total number of links to process before stopping (default: 50, minimum: 1)
        instructions (str, optional): Natural language instructions specifying which types of pages to return
        select_paths (List[str], optional): Regex patterns to select URLs with specific path patterns (e.g., /docs/.*, /api/v1.*)
        select_domains (List[str], optional): Regex patterns to restrict crawling to specific domains/subdomains
        allow_external (bool): Whether to return external links in the final response (default: True)
        extract_depth (str): 'basic' or 'advanced' extraction (default: 'basic')
        format (str): Format of extracted content - 'markdown' or 'text' (default: 'markdown')
        include_favicon (bool): Include favicon URL for each result (default: False)

    Returns:
        str: Crawl results with URLs and extracted content from each page
    """
    tavily_client = _get_tavily_client()

    # Build crawl parameters
    crawl_params = {
        "url": url,
        "max_depth": max(max_depth, 1),
        "max_breadth": max(max_breadth, 1),
        "limit": max(limit, 1),
        "allow_external": allow_external,
        "extract_depth": extract_depth,
    }

    _add_optional_params(
        crawl_params,
        instructions=instructions,
        select_paths=select_paths,
        select_domains=select_domains,
        format=format,
        include_favicon=include_favicon if include_favicon else None
    )

    response = tavily_client.crawl(**crawl_params)

    # Format results similar to index.ts
    output = []
    output.append("Crawl Results:")
    output.append(f"Base URL: {response.get('base_url', url)}")
    
    output.append("\nCrawled Pages:")
    for index, page in enumerate(response.get("results", []), 1):
        output.append(f"\n[{index}] URL: {page.get('url', 'N/A')}")
        
        if "raw_content" in page and page["raw_content"]:
            # Truncate content if it's too long
            content_preview = page["raw_content"][:200] + "..." if len(page["raw_content"]) > 200 else page["raw_content"]
            output.append(f"Content: {content_preview}")
        
        if include_favicon and "favicon" in page and page["favicon"]:
            output.append(f"Favicon: {page['favicon']}")
    
    return "\n".join(output)


@function_tool
def tavily_map(
    url: str,
    max_depth: int = 1,
    max_breadth: int = 20,
    limit: int = 50,
    instructions: Optional[str] = None,
    select_paths: Optional[List[str]] = None,
    select_domains: Optional[List[str]] = None,
    allow_external: bool = True
) -> str:
    """
    A powerful web mapping tool that creates a structured map of website URLs.
    Perfect for site audits, content discovery, and understanding website architecture.

    Args:
        url (str): The root URL to begin the mapping
        max_depth (int): Max depth of the mapping - how far from base URL to explore (default: 1, minimum: 1)
        max_breadth (int): Max number of links to follow per level/page (default: 20, minimum: 1)
        limit (int): Total number of links to process before stopping (default: 50, minimum: 1)
        instructions (str, optional): Natural language instructions for the crawler
        select_paths (List[str], optional): Regex patterns to select URLs with specific path patterns (e.g., /docs/.*, /api/v1.*)
        select_domains (List[str], optional): Regex patterns to restrict crawling to specific domains/subdomains
        allow_external (bool): Whether to return external links in the final response (default: True)

    Returns:
        str: Site map with all discovered URLs organized by structure
    """
    tavily_client = _get_tavily_client()

    # Build map parameters
    map_params = {
        "url": url,
        "max_depth": max(max_depth, 1),
        "max_breadth": max(max_breadth, 1),
        "limit": max(limit, 1),
        "allow_external": allow_external,
    }

    _add_optional_params(
        map_params,
        instructions=instructions,
        select_paths=select_paths,
        select_domains=select_domains
    )

    response = tavily_client.map(**map_params)

    # Format results similar to index.ts
    output = []
    output.append("Site Map Results:")
    output.append(f"Base URL: {response.get('base_url', url)}")
    
    output.append("\nMapped Pages:")
    for index, page_url in enumerate(response.get("results", []), 1):
        output.append(f"\n[{index}] URL: {page_url}")
    
    return "\n".join(output)


# Test functions
if __name__ == "__main__":
    import sys
    
    def test_tavily_search():
        """Test tavily_search function"""
        print("=" * 80)
        print("Testing tavily_search...")
        print("=" * 80)
        
        result = tavily_search(
            query="Python programming tutorials",
            max_results=3,
            search_depth="basic"
        )
        print(result)
        print("\n")
    
    def test_tavily_extract():
        """Test tavily_extract function"""
        print("=" * 80)
        print("Testing tavily_extract...")
        print("=" * 80)
        
        result = tavily_extract(
            urls=["https://www.python.org/about/"],
            extract_depth="basic"
        )
        print(result)
        print("\n")
    
    def test_tavily_crawl():
        """Test tavily_crawl function"""
        print("=" * 80)
        print("Testing tavily_crawl...")
        print("=" * 80)
        
        result = tavily_crawl(
            url="https://www.python.org",
            max_depth=1,
            max_breadth=5,
            limit=10
        )
        print(result)
        print("\n")
    
    def test_tavily_map():
        """Test tavily_map function"""
        print("=" * 80)
        print("Testing tavily_map...")
        print("=" * 80)
        
        result = tavily_map(
            url="https://www.python.org",
            max_depth=1,
            max_breadth=5,
            limit=10
        )
        print(result)
        print("\n")
    
    # Run tests based on command line argument
    if len(sys.argv) > 1:
        test_name = sys.argv[1]
        if test_name == "search":
            test_tavily_search()
        elif test_name == "extract":
            test_tavily_extract()
        elif test_name == "crawl":
            test_tavily_crawl()
        elif test_name == "map":
            test_tavily_map()
        else:
            print(f"Unknown test: {test_name}")
            print("Available tests: search, extract, crawl, map")
    else:
        # Run all tests
        print("Running all tests...\n")
        try:
            test_tavily_search()
        except Exception as e:
            print(f"Error in test_tavily_search: {e}\n")
        
        try:
            test_tavily_extract()
        except Exception as e:
            print(f"Error in test_tavily_extract: {e}\n")
        
        try:
            test_tavily_crawl()
        except Exception as e:
            print(f"Error in test_tavily_crawl: {e}\n")
        
        try:
            test_tavily_map()
        except Exception as e:
            print(f"Error in test_tavily_map: {e}\n")
