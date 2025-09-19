import asyncio

"""
Tavily Search & Content Extraction Tools for Advanced Reconnaissance.

This module provides powerful intelligence gathering capabilities using Tavily's API:
- tavily_search: Performs web searches with AI-powered relevance ranking
- tavily_extract_content: Deep-dives into specific URLs for comprehensive content analysis

For maximum effectiveness, use tavily_search first to find relevant URLs, 
then use tavily_extract_content to get detailed information from the most promising sources.
"""
from dotenv import load_dotenv
import os
from typing import List
from cai.sdk.agents import function_tool
from tavily import TavilyClient

# Load environment variables
load_dotenv()

@function_tool
def tavily_search(query: str, limit: int = 5, search_depth: bool = False) -> str:
    """
    Search the web using Tavily's AI-powered search engine.

    Args:
        query (str): Search query
        limit (int): Number of results (1-20, default: 5)
        search_depth (bool): Use advanced search for higher accuracy

    Returns:
        str: Search results with URLs, titles, and summaries
    """
    tavily_api_key = os.getenv("TAVILY_KEY")

    if not tavily_api_key:
        raise ValueError("TAVILY_KEY environment variable is not set.")

    tavily_client = TavilyClient(api_key=tavily_api_key)

    response = tavily_client.search(
        query=query,
        max_results=min(limit, 20),
        search_depth="advanced" if search_depth else "basic"
    )

    formatted_result = f"# 🔍 Search Results for: {query}\n\n"
    num_results = len(response['results'])

    for i, result in enumerate(response['results'], 1):
        formatted_result += f"## 📄 Result {i}/{num_results}\n\n"
        formatted_result += f"**🔗 URL:** {result['url']}\n\n"
        formatted_result += f"**📌 Title:** {result['title']}\n\n"
        formatted_result += f"**📝 Summary:**\n{result['content']}\n\n"
        formatted_result += "---\n\n"

    return formatted_result.strip()

@function_tool
def tavily_extract_detail_content_in_url(url: str, extract_depth: bool) -> str:
    """
    Extract complete content from a specific URL.

    Args:
        url (str): Target URL to extract content from
        extract_depth (bool): Use advanced extraction for more thorough results

    Returns:
        str: Full content from the webpage in markdown format
    """
    tavily_api_key = os.getenv("TAVILY_KEY")

    if not tavily_api_key:
        raise ValueError("TAVILY_KEY environment variable is not set.")

    tavily_client = TavilyClient(api_key=tavily_api_key)

    response = tavily_client.extract(
        urls=url,
        extract_depth="advanced" if extract_depth else "basic"
    )

    formatted_result = f"# 🎯 Deep Content Extraction Results\n\n"
    formatted_result += f"**📊 Total Sources:** {len(response['results'])}\n\n"

    for result in response['results']:
        formatted_result += f"**🔗 URL:** {result['url']}\n\n"
        formatted_result += f"### 📖 Full Content:\n\n"
        formatted_result += f"```\n{result['raw_content']}\n```\n\n"
        formatted_result += "---\n\n"

    formatted_result += f"✅ **Success!** Extracted complete content from **{len(response['results'])} source(s)**. This is the full, unfiltered information goldmine you need! 🏆\n"

    return formatted_result.strip()




