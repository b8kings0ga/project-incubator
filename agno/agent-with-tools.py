# /// script
# requires-python = ">=3.13"
# dependencies = [
#     "agno",
#     "litellm",
#     "requests",
#     "pillow", # Optional, for image processing
#     "playwright", # For browser automation
#     "wikipedia",
# ]
# ///
"""🗽 Agent with Tools - Your AI News Buddy that can search the web and add images to notebooks

This example shows how to create an AI news reporter agent that can search the web
for real-time news, download relevant images, and create rich notebooks with both text and images.
The agent combines web searching capabilities with engaging storytelling to deliver news in an
entertaining way, enhanced with visual content.

Run `uv add --script openai requests pillow agno playwright` to install dependencies.
"""

from textwrap import dedent
import time
import random
import logging
import os
from pathlib import Path
from typing import Any, Dict, List, Optional, Union, Callable

from agno.agent import Agent
from agno.models.litellm import LiteLLM
from agno.tools.shell import ShellTools
from agno.tools.file import FileTools
from agno.tools.calculator import CalculatorTools
from agno.tools.thinking import ThinkingTools
from agno.tools.python import PythonTools
from agno.tools.webbrowser import WebBrowserTools
from agno.tools.website import WebsiteTools





import os
import requests
import time
import json
from pathlib import Path
from typing import Optional, Dict, Any, List, Union

# Create directories for notebooks and images
os.makedirs("./notebooks", exist_ok=True)
os.makedirs("./images", exist_ok=True)

# Create images directory

# Function to download images from URLs
def download_image(image_url, filename=None):
    """
    Download an image from a URL and save it to the images directory.
    
    Args:
        image_url: The URL of the image to download
        filename: Optional filename to use (if not provided, will be derived from the URL)
        
    Returns:
        A string containing the path to the downloaded image
    """
    try:
        # Make a request to get the image
        response = requests.get(image_url, stream=True)
        response.raise_for_status()
        
        # Determine the filename if not provided
        if not filename:
            # Extract filename from URL or use a default name with timestamp
            url_path = Path(image_url.split('?')[0])
            filename = url_path.name or f"image_{int(time.time())}.jpg"
        
        # Ensure the filename has an extension
        if not Path(filename).suffix:
            # Try to determine the content type
            content_type = response.headers.get('Content-Type', '')
            if 'jpeg' in content_type or 'jpg' in content_type:
                filename += '.jpg'
            elif 'png' in content_type:
                filename += '.png'
            elif 'gif' in content_type:
                filename += '.gif'
            elif 'webp' in content_type:
                filename += '.webp'
            else:
                filename += '.jpg'  # Default to jpg
        
        # Save the image to the images directory
        image_path = Path("./images") / filename
        with open(image_path, 'wb') as f:
            for chunk in response.iter_content(chunk_size=8192):
                f.write(chunk)
        
        return f"Image downloaded successfully to {image_path}"
    except Exception as e:
        return f"Error downloading image: {str(e)}"

class RetryLiteLLM:
    """
    A wrapper for LiteLLM that adds retry capability on exceptions.
    This class maintains the same API as the original LiteLLM class.
    """
    
    def __init__(
        self,
        id: str,
        api_key: Optional[str] = None,
        api_base: Optional[str] = None,
        provider: Optional[str] = None,
        max_retries: int = 3,
        initial_retry_delay: float = 1.0,
        max_retry_delay: float = 60.0,
        backoff_factor: float = 2.0,
        jitter: bool = True,
        retry_exceptions: Optional[List[type]] = None,
        **kwargs
    ):
        """
        Initialize RetryLiteLLM with the same parameters as LiteLLM plus retry configuration.
        
        Args:
            id: The model ID
            api_key: API key for the LLM provider
            api_base: Base URL for the API
            provider: Provider name
            max_retries: Maximum number of retry attempts
            initial_retry_delay: Initial delay between retries in seconds
            max_retry_delay: Maximum delay between retries in seconds
            backoff_factor: Factor by which the delay increases with each retry
            jitter: Whether to add randomness to the retry delay
            retry_exceptions: List of exception types to retry on (defaults to Exception)
            **kwargs: Additional arguments to pass to LiteLLM
        """
        # Initialize the underlying LiteLLM instance
        self.llm = LiteLLM(
            id=id,
            api_key=api_key,
            api_base=api_base,
            provider=provider,
            **kwargs
        )
        
        # Retry configuration
        self.max_retries = max_retries
        self.initial_retry_delay = initial_retry_delay
        self.max_retry_delay = max_retry_delay
        self.backoff_factor = backoff_factor
        self.jitter = jitter
        self.retry_exceptions = retry_exceptions or [Exception]
        
        # Set up logging
        self.logger = logging.getLogger("RetryLiteLLM")
    
    def _calculate_retry_delay(self, attempt: int) -> float:
        """Calculate the delay before the next retry attempt with exponential backoff."""
        delay = min(
            self.max_retry_delay,
            self.initial_retry_delay * (self.backoff_factor ** attempt)
        )
        
        if self.jitter:
            # Add jitter (random value between 0 and delay/2)
            delay = delay + (random.random() * delay / 2)
            
        return delay
    
    def _retry_operation(self, operation: Callable, *args, **kwargs) -> Any:
        """
        Execute an operation with retry logic.
        
        Args:
            operation: The function to execute
            *args: Arguments to pass to the operation
            **kwargs: Keyword arguments to pass to the operation
            
        Returns:
            The result of the operation
            
        Raises:
            The last exception encountered after all retries are exhausted
        """
        last_exception = None
        
        for attempt in range(self.max_retries + 1):  # +1 for the initial attempt
            try:
                return operation(*args, **kwargs)
            except tuple(self.retry_exceptions) as e:
                last_exception = e
                
                if attempt < self.max_retries:
                    delay = self._calculate_retry_delay(attempt)
                    self.logger.warning(
                        f"Attempt {attempt + 1}/{self.max_retries + 1} failed with error: {str(e)}. "
                        f"Retrying in {delay:.2f} seconds..."
                    )
                    time.sleep(delay)
                else:
                    self.logger.error(
                        f"All {self.max_retries + 1} attempts failed. Last error: {str(e)}"
                    )
        
        # If we get here, all retries have been exhausted
        raise last_exception
    
    # Delegate all methods to the underlying LiteLLM instance with retry logic
    
    def __getattr__(self, name: str) -> Any:
        """
        Delegate attribute access to the underlying LiteLLM instance.
        This allows for accessing any attributes or methods of the original LiteLLM class.
        """
        attr = getattr(self.llm, name)
        
        # If the attribute is callable (a method), wrap it with retry logic
        if callable(attr):
            def wrapped_method(*args, **kwargs):
                #print(f"Calling method: {name} with args: {args} and kwargs: {kwargs}")
                return self._retry_operation(attr, *args, **kwargs)
            return wrapped_method
        
        # Otherwise, return the attribute directly
        return attr



# Get OpenAI API key and base URL from environment variables
openai_api_key = os.getenv("OPENAI_API_KEY", "")
openai_api_base = os.getenv("OPENAI_API_BASE", "")

# Use RetryLiteLLM instead of LiteLLM
llm = RetryLiteLLM(
    id="openai/claude-3-7-sonnet",
    #provider="",
    # name="Claude 3.7 Sonnet",
    api_key=openai_api_key,
    api_base=openai_api_base,
    max_retries=3,  # Retry up to 3 times
    initial_retry_delay=1.0,  # Start with a 1-second delay
    backoff_factor=2.0,  # Double the delay with each retry
    jitter=True,  # Add randomness to the delay
    retry_exceptions=[Exception],  # Retry on all exceptions
)

# Create a News Reporter Agent with a fun personality
agent = Agent(
    model=llm,
    instructions=dedent("""\
        You are an enthusiastic news reporter with a flair for storytelling! 🗽
        Think of yourself as a mix between a witty comedian and a sharp journalist.

        Follow these guidelines for every report:
        1. Start with an attention-grabbing headline using relevant emoji
        2. Use the search tool to find current, accurate information
        3. Present news with authentic NYC enthusiasm and local flavor
        4. Structure your reports in clear sections:
            - Catchy headline
            - Brief summary of the news
            - Key details and quotes
            - Local impact or context
        5. Keep responses concise but informative (2-3 paragraphs max)
        6. Include NYC-style commentary and local references
        7. End with a signature sign-off phrase

        Sign-off examples:
        - 'Back to you in the studio, folks!'
        - 'Reporting live from the city that never sleeps!'
        - 'This is [Your Name], live from the heart of Manhattan!'

        Remember: Always verify facts through web searches and maintain that authentic NYC energy!
        
        You have access to a variety of powerful tools:
        
        1. Python Tools:
           - Execute Python code
           - Perform data analysis and computations
           - Create and manipulate Python objects
           
        2. Web Browser Tools:
           - Browse websites and extract information
           - Search the web for relevant content
           - Download images and other resources
           
        3. Website Tools:
           - Analyze website content
           - Extract information from web pages
           - Process HTML and web data
           
        4. Shell Tools:
           - Execute shell commands
           
        5. File Management:
           - For saving and organizing information
           
        6. Computational Tools:
           - Calculator for performing mathematical operations
           
        7. Thinking Tools:
           - For structured reasoning and problem-solving
        
        When creating content:
        - Use multiple tools to gather comprehensive information
        - Verify facts through different sources
        - Perform calculations when needed
        - Think through complex problems step by step
        - Save your findings in well-organized notebooks
        
        Your goal is to create engaging, informative content by leveraging all available tools!\
    """),
    tools=[
        PythonTools(),
        WebBrowserTools(),
        WebsiteTools(),
        ShellTools(),
        FileTools(base_dir=Path("./notebooks"), save_files=True, read_files=True, list_files=True),
        CalculatorTools(enable_all=True),
        ThinkingTools()
    ],
    show_tool_calls=True,
    markdown=True,
    retries=10,
    delay_between_retries=5,
    telemetry=False,
)

response = """
I need a comprehensive research report on artificial intelligence advancements. Please:

1. Use Web Browser tools to search for the latest AI research and breakthroughs
2. Use Website tools to extract information from research papers and tech blogs
3. Use Python to organize and process the collected information
4. Create a summary of key AI trends and developments
5. Save your findings in a well-organized notebook with explanations and references

Use all the available tools to create a thorough and insightful report.
"""

# Example usage
agent.print_response(
    response, stream=False
)

# More example prompts to try:
"""
Try these research queries:
1. "Research the latest developments in quantum computing"
2. "Analyze the impact of social media on mental health"
3. "Investigate sustainable agriculture practices around the world"
4. "Explore the history and evolution of electric vehicles"
5. "Research the applications of machine learning in healthcare"
"""
