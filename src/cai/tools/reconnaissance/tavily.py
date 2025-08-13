import asyncio

"""
Tavily search utility for reconnaissance.

This module provides functions to search Tavily for information about various topics
using the Tavily API for web search and research.
"""
import os
import requests
from typing import Dict, List, Optional, Any
from dotenv import load_dotenv
from cai.sdk.agents import function_tool

# Load environment variables
load_dotenv()


@function_tool
def tavily_search(query: str, limit: int = 5) -> str:
    """
    Search Tavily for information based on the provided query.

    Args:
        query (str): The Tavily search query.
        limit (int): Maximum number of results to return. Default is 5.

    Returns:
        str: A formatted string containing the search results.
    """
    results = _perform_tavily_search(query, limit)
    
    if not results:
        return "No results found or search error occurred."
    
    formatted_results = ""
    for i, result in enumerate(results, 1):
        formatted_results += f"Result {i}:\n"
        formatted_results += f"Title: {result.get('title', 'N/A')}\n"
        formatted_results += f"URL: {result.get('url', 'N/A')}\n"
        formatted_results += f"Content: {result.get('content', 'N/A')}\n"
        formatted_results += f"Score: {result.get('score', 'N/A')}\n"
        formatted_results += f"Published Date: {result.get('published_date', 'N/A')}\n"
        formatted_results += "\n"
    
    return formatted_results


@function_tool
def tavily_search_with_images(query: str, limit: int = 3) -> str:
    """
    Search Tavily for information with images based on the provided query.

    Args:
        query (str): The Tavily search query.
        limit (int): Maximum number of results to return. Default is 3.

    Returns:
        str: A formatted string containing the search results with images.
    """
    results = _perform_tavily_search(query, limit, include_images=True)
    
    if not results:
        return "No results found or search error occurred."
    
    formatted_results = ""
    for i, result in enumerate(results, 1):
        formatted_results += f"Result {i}:\n"
        formatted_results += f"Title: {result.get('title', 'N/A')}\n"
        formatted_results += f"URL: {result.get('url', 'N/A')}\n"
        formatted_results += f"Content: {result.get('content', 'N/A')}\n"
        formatted_results += f"Score: {result.get('score', 'N/A')}\n"
        formatted_results += f"Published Date: {result.get('published_date', 'N/A')}\n"
        
        # Include images if available
        if 'images' in result and result['images']:
            formatted_results += f"Images: {', '.join(result['images'])}\n"
        
        formatted_results += "\n"
    
    return formatted_results


@function_tool
def tavily_news_search(query: str, limit: int = 5) -> str:
    """
    Search Tavily for news articles based on the provided query.

    Args:
        query (str): The Tavily news search query.
        limit (int): Maximum number of news results to return. Default is 5.

    Returns:
        str: A formatted string containing the news search results.
    """
    results = _perform_tavily_search(query, limit, search_depth="basic", topic="news")
    
    if not results:
        return "No news results found or search error occurred."
    
    formatted_results = f"News search results for: {query}\n\n"
    for i, result in enumerate(results, 1):
        formatted_results += f"News {i}:\n"
        formatted_results += f"Title: {result.get('title', 'N/A')}\n"
        formatted_results += f"URL: {result.get('url', 'N/A')}\n"
        formatted_results += f"Content: {result.get('content', 'N/A')}\n"
        formatted_results += f"Score: {result.get('score', 'N/A')}\n"
        formatted_results += f"Published Date: {result.get('published_date', 'N/A')}\n"
        formatted_results += "\n"
    
    return formatted_results


@function_tool
def tavily_research(query: str, limit: int = 10) -> str:
    """
    Perform deep research using Tavily with advanced search depth.

    Args:
        query (str): The research query.
        limit (int): Maximum number of results to return. Default is 10.

    Returns:
        str: A formatted string containing the research results.
    """
    results = _perform_tavily_search(query, limit, search_depth="advanced")
    
    if not results:
        return "No research results found or search error occurred."
    
    formatted_results = f"Research results for: {query}\n\n"
    for i, result in enumerate(results, 1):
        formatted_results += f"Research Result {i}:\n"
        formatted_results += f"Title: {result.get('title', 'N/A')}\n"
        formatted_results += f"URL: {result.get('url', 'N/A')}\n"
        formatted_results += f"Content: {result.get('content', 'N/A')}\n"
        formatted_results += f"Score: {result.get('score', 'N/A')}\n"
        formatted_results += f"Published Date: {result.get('published_date', 'N/A')}\n"
        
        # Include raw content if available
        if 'raw_content' in result:
            formatted_results += f"Raw Content Preview: {result['raw_content'][:200]}...\n"
        
        formatted_results += "\n"
    
    return formatted_results


def _perform_tavily_search(query: str, limit: int = 5, search_depth: str = "basic", 
                          topic: str = "general", include_images: bool = False) -> List[Dict[str, Any]]:
    """
    Helper function to perform Tavily searches.

    Args:
        query (str): The Tavily search query.
        limit (int): Maximum number of results to return.
        search_depth (str): Search depth - "basic" or "advanced".
        topic (str): Search topic - "general" or "news".
        include_images (bool): Whether to include images in results.

    Returns:
        List[Dict[str, Any]]: A list of dictionaries containing the search results.
    """
    try:
        # Get API key from environment variable
        api_key = os.getenv("TAVILY_KEY")
        if not api_key:
            return []

        # Tavily API endpoint
        url = "https://api.tavily.com/search"
        
        # Request payload
        payload = {
            "query": query,
            "search_depth": search_depth,
            "include_images": include_images,
            "include_answer": True,
            "include_raw_content": search_depth == "advanced",
            "max_results": limit,
            "include_domains": [],
            "exclude_domains": []
        }
        
        # Add topic-specific parameters
        if topic == "news":
            payload["topic"] = "news"
        
        # Make the API request
        headers = {
            "Content-Type": "application/json",
            "Authorization": f"Bearer {api_key}"
        }
        
        response = requests.post(url, json=payload, headers=headers, timeout=30)
        
        if response.status_code != 200:
            return []

        data = response.json()
        
        # Return results if available
        if "results" not in data:
            return []
            
        return data["results"][:limit]
    
    except Exception:
        return []


def _get_tavily_answer(query: str) -> Optional[str]:
    """
    Helper function to get a direct answer from Tavily.

    Args:
        query (str): The query to get an answer for.

    Returns:
        Optional[str]: The answer or None if no answer is available.
    """
    try:
        # Get API key from environment variable
        api_key = os.getenv("TAVILY_KEY")
        if not api_key:
            return None

        # Tavily API endpoint
        url = "https://api.tavily.com/search"
        
        # Request payload for answer extraction
        payload = {
            "query": query,
            "search_depth": "basic",
            "include_answer": True,
            "max_results": 1
        }
        
        headers = {
            "Content-Type": "application/json",
            "Authorization": f"Bearer {api_key}"
        }
        
        response = requests.post(url, json=payload, headers=headers, timeout=30)
        
        if response.status_code != 200:
            return None

        data = response.json()
        
        # Return answer if available
        return data.get("answer")
    
    except Exception:
        return None


@function_tool
def tavily_get_answer(query: str) -> str:
    """
    Get a direct answer from Tavily for a specific question.

    Args:
        query (str): The question to get an answer for.

    Returns:
        str: The answer or an error message.
    """
    answer = _get_tavily_answer(query)
    
    if not answer:
        return "No answer found or search error occurred."
    
    return f"Answer for '{query}':\n\n{answer}"


@function_tool
def tavily_domain_search(query: str, domains: List[str], limit: int = 5) -> str:
    """
    Search Tavily within specific domains.

    Args:
        query (str): The search query.
        domains (List[str]): List of domains to search within.
        limit (int): Maximum number of results to return. Default is 5.

    Returns:
        str: A formatted string containing the domain-specific search results.
    """
    try:
        # Get API key from environment variable
        api_key = os.getenv("TAVILY_KEY")
        if not api_key:
            return "API key not found."

        # Tavily API endpoint
        url = "https://api.tavily.com/search"
        
        # Request payload
        payload = {
            "query": query,
            "search_depth": "basic",
            "include_answer": False,
            "max_results": limit,
            "include_domains": domains,
            "exclude_domains": []
        }
        
        headers = {
            "Content-Type": "application/json",
            "Authorization": f"Bearer {api_key}"
        }
        
        response = requests.post(url, json=payload, headers=headers, timeout=30)
        
        if response.status_code != 200:
            return "Search error occurred."

        data = response.json()
        
        if "results" not in data or not data["results"]:
            return f"No results found for '{query}' in domains: {', '.join(domains)}"
        
        results = data["results"]
        
        formatted_results = f"Domain search results for '{query}' in {', '.join(domains)}:\n\n"
        for i, result in enumerate(results, 1):
            formatted_results += f"Result {i}:\n"
            formatted_results += f"Title: {result.get('title', 'N/A')}\n"
            formatted_results += f"URL: {result.get('url', 'N/A')}\n"
            formatted_results += f"Content: {result.get('content', 'N/A')}\n"
            formatted_results += f"Score: {result.get('score', 'N/A')}\n"
            formatted_results += "\n"
        
        return formatted_results
        
    except Exception as e:
        return f"Error performing domain search: {str(e)}"

# # Test functions
# async def test_tavily_search():
#     print("Testing tavily_search...")
#     result = tavily_search("python programming", limit=2)
#     print(result)
#     print("-" * 50)

# async def test_tavily_search_with_images():
#     print("Testing tavily_search_with_images...")
#     result = tavily_search_with_images("python logo", limit=2)
#     print(result)
#     print("-" * 50)

# async def test_tavily_news_search():
#     print("Testing tavily_news_search...")
#     result = tavily_news_search("AI news", limit=2)
#     print(result)
#     print("-" * 50)

# async def test_tavily_research():
#     print("Testing tavily_research...")
#     result = tavily_research("machine learning", limit=2)
#     print(result)
#     print("-" * 50)

# async def test_tavily_get_answer():
#     print("Testing tavily_get_answer...")
#     result = tavily_get_answer("What is Python?")
#     print(result)
#     print("-" * 50)

# async def test_tavily_domain_search():
#     print("Testing tavily_domain_search...")
#     result = tavily_domain_search("python tutorial", ["realpython.com", "docs.python.org"], limit=2)
#     print(result)
#     print("-" * 50)

# async def run_all_tests():
#     print("=" * 60)
#     print("Running Tavily Search Tests")
#     print("=" * 60)
#     await test_tavily_search()
#     await test_tavily_search_with_images()
#     await test_tavily_news_search()
#     await test_tavily_research()
#     await test_tavily_get_answer()
#     await test_tavily_domain_search()
#     print("All tests completed!")

# if __name__ == "__main__":
#     asyncio.run(run_all_tests())
