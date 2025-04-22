#!/opt/homebrew/bin/uv run --script
# /// script
# requires-python = ">=3.13"
# dependencies = [
#     "typer",
#     "requests",
#     "urllib3",
# ]
# ///

import csv
import json
import logging
import os
import random
import subprocess
import time
from pathlib import Path
from typing import Dict, List, Optional, Tuple, Union

import requests
import typer
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry

# Set up logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s",
    handlers=[logging.StreamHandler()]
)
logger = logging.getLogger(__name__)

# Create the Typer app
app = typer.Typer(help="SNAPR API Query Tool")

# Constants
DEFAULT_OUTPUT_PATH = Path("./output")
DEFAULT_START_ACN = "Z1865690"
MAX_RETRIES = 3
BASE_URL = "https://snapr-service.bis.gov/api/workItems/stela"
TOKEN_URL = "https://bisexternal.ciamlogin.com/16a0fd8f-4db1-4496-8036-56968f632d98/oauth2/v2.0/token"
SAVE_POINT_FILE = Path("./snapr_save_point.json")
CONFIG_FILE = Path("./snapr_config.json")

# User agents for rotation
USER_AGENTS = [
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/134.0.0.0 Safari/537.36",
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/134.0.0.0 Safari/537.36",
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/17.0 Safari/605.1.15",
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:124.0) Gecko/20100101 Firefox/124.0",
]

# Headers for the request
def get_headers(token: str, user_id: str = "199785") -> Dict[str, str]:
    """Generate headers with a random user agent for the request."""
    return {
        "accept": "*/*",
        "accept-language": "en-US,en;q=0.9",
        "authorization": f"Bearer {token}",
        "origin": "https://snapr.bis.gov",
        "referer": "https://snapr.bis.gov/",
        "sec-ch-ua": '"Chromium";v="134", "Not:A-Brand";v="24", "Google Chrome";v="134"',
        "sec-ch-ua-mobile": "?0",
        "sec-ch-ua-platform": '"macOS"',
        "sec-fetch-dest": "empty",
        "sec-fetch-mode": "cors",
        "sec-fetch-site": "same-site",
        "user-agent": random.choice(USER_AGENTS),
        "x-user": user_id,
    }

def create_session() -> requests.Session:
    """Create a session with retry capabilities."""
    session = requests.Session()
    
    # Configure retry strategy
    retry_strategy = Retry(
        total=MAX_RETRIES,
        backoff_factor=1,
        status_forcelist=[429, 500, 502, 503, 504],
        allowed_methods=["GET"]
    )
    
    adapter = HTTPAdapter(max_retries=retry_strategy)
    session.mount("http://", adapter)
    session.mount("https://", adapter)
    
    return session

def load_config() -> Dict:
    """
    Load the configuration from a file.
    
    Returns:
        The configuration as a dictionary
    """
    # Default configuration
    default_config = {
        "curl_command": [
            'curl',
            'https://bisexternal.ciamlogin.com/16a0fd8f-4db1-4496-8036-56968f632d98/oauth2/v2.0/token',
            '-H', 'Accept: */*',
            '-H', 'Accept-Language: en-US,en;q=0.9,zh-CN;q=0.8,zh;q=0.7',
            '-H', 'Connection: keep-alive',
            '-H', 'Origin: https://snapr.bis.gov',
            '-H', 'Referer: https://snapr.bis.gov/',
            '-H', 'Sec-Fetch-Dest: empty',
            '-H', 'Sec-Fetch-Mode: cors',
            '-H', 'Sec-Fetch-Site: cross-site',
            '-H', 'User-Agent: Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/134.0.0.0 Safari/537.36',
            '-H', 'content-type: application/x-www-form-urlencoded;charset=utf-8',
            '-H', 'sec-ch-ua: "Chromium";v="134", "Not:A-Brand";v="24", "Google Chrome";v="134"',
            '-H', 'sec-ch-ua-mobile: ?0',
            '-H', 'sec-ch-ua-platform: "macOS"',
            '--data-raw', 'client_id=e9265e96-d5f2-4d09-96c7-855b114bb0b2&redirect_uri=https%3A%2F%2Fsnapr.bis.gov%2F&scope=api%3A%2F%2F98ff0f31-bee6-4d95-a402-cf5feadfa973%2Fsnapr.exporter%20openid%20profile%20offline_access&code=1.AbgAj_2gFrFNlkSANlaWj2MtmJZeJuny1QlNlseFWxFLsLK4AAC4AA.AgABBAIAAABVrSpeuWamRam2jAF1XRQEAwDs_wUA9P8CfTF-2VsbMA4ENoNVL2tjY74SI7ArFJHtbAhqe-8vRPPy0W-bgpF-YXhmomO7haAxY-OPzYD9KyWbGtW1W3i_gDV-NX3mK3fgAEwtOKc0lGtFcUxMnQlEwfSe0DXogfCWG0fFOvGZ2WHhY9Uzk3ut4k7UJ1KJ3YLrgsSXYZJ5ZuwByxeuUjbkLdoluRJS1sWoJL-6tbIdv8xLbTXbFByKvo7RX5u6fUesUvk_BU2xP86zJRrmh_S0i46p606Qzgtc1pupOIeV4TfFXgjHlrYdG56URexmTzC9qFDUqg1TBdxLmduZr8ua63i-O4xHmI87ajMnRHK0n-DtI-S6rFWM7lbHhqE3yxU8xa7w1nijGUAiUDGvOHj2TLwHeBQDNKevCfNV4SnDpZs4fni_Z8zs3Y79aEOvtUTxKLUd1iqHZVkasAJ8cdLitlawVvrmRLepO_zKG7j7ip02eJKe2gX2y5BxO3eRBT30s_0CvY1uBoG22vJ0-QzaDYJIuVtPnqIJNYmv75hyDA1uzsLQwUIEgvVjcDBKwVoYGa9abnG0lgiaUfiFvuXGfjCW3kf1UsAyfcMu2c7osiCDDJg9vVX4YLT4SwsmGk3JZPMrNHwG5Icyv6XGLPdAu47cWeadog0u0KsnOMmUDTzga9XJzs4G5RK4kqZUcWDwDGskNgk1RD1fuA2ZVJBYCXTG12sErT-ibddQGqWMmfr-UqPnHyWPbORrjsn2zca5QVuvpYTivwuYqL9PrC2ka5H8R8tA2ZDYDV1qo5p7RW8iQ7vEyXkkS6ylRlYIhUCLwF1qlPitk8Qcie1ju2FHZcuhVEqPjft2S-bYQDDBdyvdK5HfzBxI7pJgiEs3JW7LrIXOCwhWsPASVI19tUPQMzoaHE8elM5Um8gvHfquBVgNFVo6_DeBYCoqaF6-77w&x-client-SKU=msal.js.browser&x-client-VER=3.21.0&x-ms-lib-capability=retry-after, h429&x-client-current-telemetry=5|865,0,,,|@azure/msal-react,2.0.22&x-client-last-telemetry=5|0|||0,0&code_verifier=VyXVu9AjSVz6FRFrLGt-xRO6kmu86YF1ixDcPaAOkaE&grant_type=authorization_code&client_info=1&client-request-id=01964901-65a3-7a3e-b141-a963db662301&X-AnchorMailbox=Oid%3A7c078b24-1a8f-476a-a3ba-da7af15939dc%4016a0fd8f-4db1-4496-8036-56968f632d98'
        ]
    }
    
    if not CONFIG_FILE.exists():
        # Create the config file with default values
        try:
            with open(CONFIG_FILE, 'w') as f:
                json.dump(default_config, f, indent=2)
            logger.info(f"Created default configuration file at {CONFIG_FILE}")
        except Exception as e:
            logger.error(f"Failed to create configuration file: {e}")
        return default_config
    
    try:
        with open(CONFIG_FILE, 'r') as f:
            config = json.load(f)
        logger.info(f"Loaded configuration from {CONFIG_FILE}")
        return config
    except Exception as e:
        logger.error(f"Failed to load configuration: {e}")
        return default_config

def save_config(config: Dict) -> None:
    """
    Save the configuration to a file.
    
    Args:
        config: The configuration to save
    """
    try:
        with open(CONFIG_FILE, 'w') as f:
            json.dump(config, f, indent=2)
        logger.info(f"Saved configuration to {CONFIG_FILE}")
    except Exception as e:
        logger.error(f"Failed to save configuration: {e}")

def get_token_from_curl() -> Dict:
    """
    Get a new token using the curl command from the configuration.
    
    Returns:
        The token response as a dictionary
    """
    logger.info("Requesting new access token...")
    
    # Load the curl command from the configuration
    config = load_config()
    curl_command = config.get("curl_command", [])
    
    # Log the curl command for debugging
    logger.info(f"Using curl command with {len(curl_command)} parts")
    logger.info(f"First few parts: {curl_command[:3]}")
    logger.info(f"Last few parts: {curl_command[-2:] if len(curl_command) >= 2 else curl_command}")
    
    # Check if the curl command is valid
    if not curl_command or len(curl_command) < 2:
        logger.error("Invalid curl command. Please update the curl command using the update-curl command.")
        return None
    
    try:
        # Fix malformed refresh token in the curl command before executing
        fixed_curl_command = []
        for part in curl_command:
            if isinstance(part, str) and '--data-raw' in part and 'refresh_token=' in part:
                logger.info("Checking for malformed refresh token in curl command...")
                import re
                # Extract the refresh token parameter
                refresh_token_match = re.search(r'refresh_token=([^&]+)', part)
                if refresh_token_match:
                    old_refresh_token = refresh_token_match.group(1)
                    logger.debug(f"Found refresh token: {old_refresh_token[:10]}...")
                    
                    # Check if it's a JSON string or contains a JSON object
                    if (old_refresh_token.startswith('{') and old_refresh_token.endswith('}')) or '"refresh_token":' in old_refresh_token:
                        logger.info("Found malformed refresh token in config (JSON object)")
                        try:
                            # Try to find and extract the refresh_token value from the string
                            token_match = re.search(r'"refresh_token":"([^"]+)"', old_refresh_token)
                            if token_match:
                                actual_token = token_match.group(1)
                                logger.info(f"Extracted actual refresh token: {actual_token[:10]}...")
                                # Replace the JSON string with just the refresh token
                                fixed_part = part.replace(f"refresh_token={old_refresh_token}", f"refresh_token={actual_token}")
                                fixed_curl_command.append(fixed_part)
                                # Update the config for future use
                                config["curl_command"] = curl_command.copy()
                                for i, cmd_part in enumerate(config["curl_command"]):
                                    if isinstance(cmd_part, str) and '--data-raw' in cmd_part and 'refresh_token=' in cmd_part:
                                        config["curl_command"][i] = fixed_part
                                save_config(config)
                                logger.info("Updated config with fixed refresh token")
                                continue
                            else:
                                logger.warning("Could not extract refresh token from JSON string")
                        except Exception as e:
                            logger.warning(f"Error fixing refresh token: {e}")
            # If no special handling needed or if handling failed, use the original part
            fixed_curl_command.append(part)
        
        # Execute the fixed curl command and capture the output
        logger.info("Executing curl command...")
        result = subprocess.run(fixed_curl_command, capture_output=True, text=True)
        
        if result.returncode != 0:
            logger.error(f"Failed to get token: {result.stderr}")
            return None
        
        # Log the output for debugging
        logger.info(f"Curl command output length: {len(result.stdout)}")
        logger.info(f"Curl command output preview: {result.stdout[:100]}...")
        
        # Parse the JSON response
        try:
            token_data = json.loads(result.stdout)
            logger.info(f"Successfully parsed JSON response with keys: {token_data.keys()}")
            
            # Update the config with the new refresh token if available
            if 'refresh_token' in token_data:
                # Get the current curl command
                current_curl = config.get("curl_command", [])
                
                # Update the refresh token in the curl command
                for i, part in enumerate(current_curl):
                    if isinstance(part, str) and '--data-raw' in part and 'refresh_token=' in part:
                        # Extract the refresh token parameter
                        import re
                        refresh_token_match = re.search(r'refresh_token=([^&]+)', part)
                        if refresh_token_match:
                            old_refresh_token = refresh_token_match.group(1)
                            # Replace the old token with the new one
                            logger.info("Updating refresh token in config with new token")
                            new_part = part.replace(f"refresh_token={old_refresh_token}", f"refresh_token={token_data['refresh_token']}")
                            current_curl[i] = new_part
                            # Update the config
                            config["curl_command"] = current_curl
                            save_config(config)
                            logger.info("Updated config with new refresh token")
            
            return token_data
        except json.JSONDecodeError as e:
            logger.error(f"Failed to parse JSON response: {e}")
            logger.error(f"Response: {result.stdout}")
            return None
    except Exception as e:
        logger.error(f"Error getting token: {e}")
        return None

def query_acn(session: requests.Session, acn: str, token: str) -> Dict:
    """
    Query the SNAPR API for a specific ACN.
    
    Args:
        session: The requests session
        acn: The ACN to query
        token: The authentication token
        
    Returns:
        The JSON response as a dictionary or an empty dictionary with just the ACN if an error occurs
    """
    url = f"{BASE_URL}/{acn}"
    
    try:
        # Add jitter to delay between requests (anti-crawling)
        delay = random.uniform(0.1, 0.7)
        time.sleep(delay)
        
        # Rotate user agent and get headers
        headers = get_headers(token)
        
        # Make the request
        response = session.get(url, headers=headers, timeout=10)
        
        # Check for 404 error
        if response.status_code == 404:
            logger.info(f"ACN {acn} not found (404)")
            return None
        
        # Check for 401 error (unauthorized)
        if response.status_code == 401:
            logger.warning(f"Unauthorized (401) for ACN {acn} - token may have expired")
            return {"acn": acn, "error": {"status": 401, "message": "Unauthorized"}}
        
        # Raise an exception for other error codes
        response.raise_for_status()
        
        # Parse the JSON response
        data = response.json()
        logger.info(f"Successfully queried ACN {acn}")
        return data
        
    except requests.exceptions.HTTPError as e:
        if e.response.status_code == 404:
            return None
        if e.response.status_code == 401:
            logger.warning(f"Unauthorized (401) for ACN {acn} - token may have expired")
            return {"acn": acn, "error": {"status": 401, "message": "Unauthorized"}}
        logger.error(f"HTTP error occurred for ACN {acn}: {e}")
        # Return empty data with just the ACN for non-404 errors after retries
        return {"acn": acn}
    except requests.exceptions.RequestException as e:
        logger.error(f"Request error occurred for ACN {acn}: {e}")
        return {"acn": acn}
    except json.JSONDecodeError as e:
        logger.error(f"JSON decode error occurred for ACN {acn}: {e}")
        return {"acn": acn}
    except Exception as e:
        logger.error(f"Unexpected error occurred for ACN {acn}: {e}")
        return {"acn": acn}

def decrement_acn(acn: str) -> str:
    """
    Decrement the ACN number.
    
    Args:
        acn: The ACN to decrement (format: Z#######)
        
    Returns:
        The decremented ACN
    """
    prefix = acn[0]  # Should be 'Z'
    number = int(acn[1:])
    return f"{prefix}{number - 1}"

def save_state(current_acn: str, output_path: Path, count: int) -> None:
    """
    Save the current state to a file.
    
    Args:
        current_acn: The current ACN
        output_path: The output path for the CSV file
        count: The number of records processed so far
    """
    save_data = {
        "current_acn": current_acn,
        "output_path": str(output_path),
        "count": count,
        "timestamp": time.time()
    }
    
    try:
        with open(SAVE_POINT_FILE, 'w') as f:
            json.dump(save_data, f)
        logger.info(f"Saved state to {SAVE_POINT_FILE}")
    except Exception as e:
        logger.error(f"Failed to save state: {e}")

def load_state() -> Optional[Dict]:
    """
    Load the saved state from a file.
    
    Returns:
        The saved state as a dictionary or None if no state is found
    """
    if not SAVE_POINT_FILE.exists():
        return None
    
    try:
        with open(SAVE_POINT_FILE, 'r') as f:
            state = json.load(f)
        logger.info(f"Loaded state from {SAVE_POINT_FILE}")
        return state
    except Exception as e:
        logger.error(f"Failed to load state: {e}")
        return None

def save_to_csv(results: List[Dict], output_path: Path) -> None:
    """
    Save the results to a CSV file.
    If the file exists, append to it instead of overwriting.
    
    Args:
        results: The list of results to save
        output_path: The path to save the CSV file
    """
    if not results:
        logger.warning("No results to save")
        return
    
    try:
        # Create the directory if it doesn't exist
        output_path.parent.mkdir(parents=True, exist_ok=True)
        
        # Get the keys from all results
        keys = set()
        for result in results:
            keys.update(result.keys())
        
        # Sort the keys for consistent output
        sorted_keys = sorted(keys)
        
        # Check if the file exists
        file_exists = output_path.exists()
        logger.info(f"Output file {output_path} exists: {file_exists}")
        
        if file_exists:
            # Read existing data to get headers
            existing_headers = []
            try:
                with open(output_path, 'r', newline='') as f:
                    reader = csv.DictReader(f)
                    existing_headers = reader.fieldnames or []
                logger.info(f"Existing file has {len(existing_headers)} columns")
                
                # Merge headers
                for header in existing_headers:
                    if header not in sorted_keys:
                        sorted_keys.append(header)
                
                # Check if the file ends with a newline
                with open(output_path, 'r') as f:
                    f.seek(0, 2)  # Go to the end of the file
                    if f.tell() > 0:  # If file is not empty
                        f.seek(f.tell() - 1, 0)  # Go to the last character
                        last_char = f.read(1)
                        needs_newline = last_char != '\n'
                
                # Append the results to the CSV file
                with open(output_path, 'a', newline='') as f:
                    # Add a newline if needed to prevent data corruption
                    if needs_newline:
                        f.write('\n')
                    writer = csv.DictWriter(f, fieldnames=sorted_keys)
                    writer.writerows(results)
                
                logger.info(f"Appended {len(results)} results to existing file {output_path}")
                return
            except Exception as e:
                logger.error(f"Error reading or appending to existing file: {e}")
                # If there's an error, fall back to overwriting
                logger.warning("Falling back to creating a new file")
                file_exists = False
        
        # If file doesn't exist or we had an error, create a new file
        with open(output_path, 'w', newline='') as f:
            writer = csv.DictWriter(f, fieldnames=sorted_keys)
            writer.writeheader()
            writer.writerows(results)
        
        logger.info(f"Created new file with {len(results)} results at {output_path}")
    except Exception as e:
        logger.error(f"Failed to save results to CSV: {e}")

@app.command("update-curl")
def update_curl(
    curl_command: str = typer.Argument(..., help="The curl command to use for token refresh"),
):
    """
    Update the curl command used for token refresh.
    
    The curl command should be a complete curl command that can be used to get a new token.
    Example:
        ./query.py update-curl "curl 'https://bisexternal.ciamlogin.com/16a0fd8f-4db1-4496-8036-56968f632d98/oauth2/v2.0/token' -H 'Accept: */*' ... --data-raw '...'"
    """
    logger.info("Updating curl command...")
    
    # Set debug logging temporarily to see what's happening
    original_level = logger.level
    logger.setLevel(logging.DEBUG)
    
    # Remove backslashes used for line continuation
    curl_command = curl_command.replace("\\\n", " ")
    logger.debug(f"Command after removing line continuations: {curl_command[:50]}...")
    
    # Check if the command starts with curl
    if not curl_command.strip().startswith("curl"):
        logger.error("The command must start with 'curl'")
        raise typer.BadParameter("The command must start with 'curl'")
    
    # Use shlex to properly parse the command with quotes
    try:
        import shlex
        parts = shlex.split(curl_command)
        logger.debug(f"Parsed {len(parts)} parts using shlex")
        logger.debug(f"First few parts: {parts[:3]}")
        logger.debug(f"Last few parts: {parts[-2:] if len(parts) >= 2 else parts}")
    except Exception as e:
        logger.error(f"Error parsing command with shlex: {e}")
        
        # Fall back to manual parsing if shlex fails
        logger.debug("Falling back to manual parsing...")
        parts = []
        current_part = ""
        in_quotes = False
        quote_char = None
        
        for char in curl_command:
            if char in ['"', "'"]:
                if not in_quotes:
                    in_quotes = True
                    quote_char = char
                elif char == quote_char:
                    in_quotes = False
                    quote_char = None
            
            if char.isspace() and not in_quotes:
                if current_part:
                    parts.append(current_part)
                    current_part = ""
            else:
                current_part += char
        
        if current_part:
            parts.append(current_part)
        
        logger.debug(f"Parsed {len(parts)} parts manually")
        
        # Remove any quotes from the beginning and end of each part
        for i in range(len(parts)):
            if parts[i].startswith('"') and parts[i].endswith('"'):
                parts[i] = parts[i][1:-1]
            elif parts[i].startswith("'") and parts[i].endswith("'"):
                parts[i] = parts[i][1:-1]
    
    # Load the current configuration
    config = load_config()
    
    # Update the curl command
    config["curl_command"] = parts
    
    # Save the configuration
    save_config(config)
    
    # Test the curl command to make sure it works
    logger.debug("Testing the curl command...")
    try:
        result = subprocess.run(parts, capture_output=True, text=True)
        if result.returncode == 0:
            logger.info("Curl command test successful")
            try:
                token_data = json.loads(result.stdout)
                logger.info(f"Successfully parsed JSON response with keys: {token_data.keys()}")
                if "access_token" in token_data:
                    logger.info("Access token found in response")
                else:
                    logger.warning("No access token found in response")
            except json.JSONDecodeError:
                logger.warning("Could not parse JSON response from curl command test")
        else:
            logger.warning(f"Curl command test failed with return code {result.returncode}")
            logger.warning(f"Error: {result.stderr}")
    except Exception as e:
        logger.warning(f"Error testing curl command: {e}")
    
    # Restore original logging level
    logger.setLevel(original_level)
    
    logger.info(f"Curl command updated successfully with {len(parts)} parts")
    logger.info("You can now run the query command to use the updated curl command")

@app.command("uu")
def update_refresh_token(
    refresh_token: str = typer.Argument(..., help="The refresh token to use for token refresh"),
):
    """
    Update the curl command to use a refresh token.
    
    This command creates a curl command specifically for using a refresh token.
    Example:
        ./query.py update-refresh-token "your-refresh-token-here"
    """
    logger.info("Updating curl command to use refresh token...")
    
    # Set debug logging temporarily to see what's happening
    original_level = logger.level
    logger.setLevel(logging.DEBUG)
    
    # Create the curl command for refresh token
    curl_command = [
        'curl',
        'https://bisexternal.ciamlogin.com/16a0fd8f-4db1-4496-8036-56968f632d98/oauth2/v2.0/token',
        '-H', 'Accept: */*',
        '-H', 'Accept-Language: en-US,en;q=0.9,zh-CN;q=0.8,zh;q=0.7',
        '-H', 'Connection: keep-alive',
        '-H', 'Origin: https://snapr.bis.gov',
        '-H', 'Referer: https://snapr.bis.gov/',
        '-H', 'Sec-Fetch-Dest: empty',
        '-H', 'Sec-Fetch-Mode: cors',
        '-H', 'Sec-Fetch-Site: cross-site',
        '-H', 'User-Agent: Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/134.0.0.0 Safari/537.36',
        '-H', 'content-type: application/x-www-form-urlencoded;charset=utf-8',
        '-H', 'sec-ch-ua: "Chromium";v="134", "Not:A-Brand";v="24", "Google Chrome";v="134"',
        '-H', 'sec-ch-ua-mobile: ?0',
        '-H', 'sec-ch-ua-platform: "macOS"',
        '--data-raw', f'client_id=e9265e96-d5f2-4d09-96c7-855b114bb0b2&scope=api%3A%2F%2F98ff0f31-bee6-4d95-a402-cf5feadfa973%2Fsnapr.exporter%20openid%20profile%20offline_access&grant_type=refresh_token&client_info=1&x-client-SKU=msal.js.browser&x-client-VER=3.21.0&x-ms-lib-capability=retry-after, h429&x-client-current-telemetry=5|61,0,,,|@azure/msal-react,2.0.22&x-client-last-telemetry=5|0|||0,0&client-request-id=01964962-054d-7fe7-b1a1-5415227ca603&refresh_token={refresh_token}'
    ]
    
    logger.debug(f"Created curl command with {len(curl_command)} parts")
    logger.debug(f"First few parts: {curl_command[:3]}")
    logger.debug(f"Last few parts: {curl_command[-2:] if len(curl_command) >= 2 else curl_command}")
    
    # Load the current configuration
    config = load_config()
    
    # Update the curl command
    config["curl_command"] = curl_command
    
    # Save the configuration
    save_config(config)
    
    # Test the curl command to make sure it works
    logger.debug("Testing the curl command with refresh token...")
    try:
        result = subprocess.run(curl_command, capture_output=True, text=True)
        if result.returncode == 0:
            logger.info("Curl command test successful")
            try:
                token_data = json.loads(result.stdout)
                logger.info(f"Successfully parsed JSON response with keys: {token_data.keys()}")
                if "access_token" in token_data:
                    logger.info("Access token found in response")
                else:
                    logger.warning("No access token found in response")
            except json.JSONDecodeError:
                logger.warning("Could not parse JSON response from curl command test")
                logger.warning(f"Response: {result.stdout[:100]}...")
        else:
            logger.warning(f"Curl command test failed with return code {result.returncode}")
            logger.warning(f"Error: {result.stderr}")
    except Exception as e:
        logger.warning(f"Error testing curl command: {e}")
    
    # Restore original logging level
    logger.setLevel(original_level)
    
    logger.info("Curl command updated successfully to use refresh token")
    logger.info("You can now run the query command to use the updated curl command")

@app.command("fix-config")
def fix_config(
    debug: bool = typer.Option(False, "--debug", "-d", help="Enable debug logging"),
):
    """
    Fix issues with the configuration file.
    
    This command checks the configuration file for common issues and fixes them.
    Example:
        ./query.py fix-config
    """
    # Set debug logging if requested
    if debug:
        logger.setLevel(logging.DEBUG)
        logger.debug("Debug logging enabled")
    
    logger.info("Checking configuration file...")
    
    # Load the configuration
    config = load_config()
    
    # Check if the curl command exists
    if not config.get("curl_command"):
        logger.error("No curl command found in configuration")
        return
    
    # Check if the curl command is valid
    curl_command = config.get("curl_command", [])
    if not curl_command or len(curl_command) < 2:
        logger.error("Invalid curl command in configuration")
        return
    
    # Check for malformed refresh token
    fixed = False
    for i, part in enumerate(curl_command):
        if isinstance(part, str) and '--data-raw' in part and 'refresh_token=' in part:
            # Extract the refresh token parameter
            import re
            refresh_token_match = re.search(r'refresh_token=([^&]+)', part)
            if refresh_token_match:
                old_refresh_token = refresh_token_match.group(1)
                # Check if it's a JSON string
                if old_refresh_token.startswith('{') and old_refresh_token.endswith('}'):
                    logger.info("Found malformed refresh token in config")
                    try:
                        # Try to parse the JSON
                        import json
                        token_data = json.loads(old_refresh_token)
                        if 'refresh_token' in token_data:
                            # Replace the JSON string with just the refresh token
                            new_part = part.replace(f"refresh_token={old_refresh_token}", f"refresh_token={token_data['refresh_token']}")
                            curl_command[i] = new_part
                            fixed = True
                            logger.info("Fixed malformed refresh token in config")
                        else:
                            logger.warning("JSON does not contain a refresh_token field")
                    except json.JSONDecodeError:
                        logger.warning("Failed to parse refresh token as JSON")
    
    if fixed:
        # Update the config
        config["curl_command"] = curl_command
        save_config(config)
        logger.info("Updated config with fixed refresh token")
    else:
        logger.info("No issues found in configuration")
    
    # Test the curl command
    logger.info("Testing curl command...")
    try:
        result = subprocess.run(curl_command, capture_output=True, text=True)
        if result.returncode == 0:
            logger.info("Curl command test successful")
            try:
                token_data = json.loads(result.stdout)
                logger.info(f"Successfully parsed JSON response with keys: {token_data.keys()}")
                if "access_token" in token_data:
                    logger.info("Access token found in response")
                else:
                    logger.warning("No access token found in response")
            except json.JSONDecodeError:
                logger.warning("Could not parse JSON response from curl command test")
        else:
            logger.warning(f"Curl command test failed with return code {result.returncode}")
            logger.warning(f"Error: {result.stderr}")
    except Exception as e:
        logger.warning(f"Error testing curl command: {e}")
    
    logger.info("Configuration check complete")

@app.command()
def query(
    start_acn: str = typer.Option(DEFAULT_START_ACN, "--start-acn", "-s", help="The ACN to start querying from"),
    output_path: Path = typer.Option(DEFAULT_OUTPUT_PATH, "--output", "-o", help="The path to save the CSV file"),
    token: str = typer.Option(None, "--token", "-t", help="The authentication token for the SNAPR API (optional)"),
    limit: int = typer.Option(None, "--limit", "-l", help="Limit the number of ACNs to query (optional)"),
    resume: bool = typer.Option(False, "--resume", "-r", help="Resume from the last save point"),
    debug: bool = typer.Option(False, "--debug", "-d", help="Enable debug logging"),
):
    """
    Query the SNAPR API for work items and save the results to a CSV file.
    
    The script will start from the specified ACN and work backwards until a 404 error is encountered.
    If resume is True, it will resume from the last save point.
    
    Examples:
        ./query.py                                # Run with default settings
        ./query.py --start-acn Z1865690           # Start from a specific ACN
        ./query.py --resume                       # Resume from the last save point
        ./query.py --limit 100                    # Limit to 100 records
        ./query.py --debug                        # Enable debug logging
    """
    # Set debug logging if requested
    if debug:
        logger.setLevel(logging.DEBUG)
        logger.debug("Debug logging enabled")
    # Check if we should resume from a save point
    if resume:
        state = load_state()
        if state:
            current_acn = state["current_acn"]
            output_path = Path(state["output_path"])
            start_count = state.get("count", 0)
            logger.info(f"Resuming from ACN {current_acn}")
            logger.info(f"Output path: {output_path}")
            logger.info(f"Already processed {start_count} records")
        else:
            logger.warning("No save point found, starting fresh")
            current_acn = start_acn
            start_count = 0
            logger.info(f"Starting query from ACN {start_acn}")
            logger.info(f"Output path: {output_path}")
    else:
        current_acn = start_acn
        start_count = 0
        logger.info(f"Starting query from ACN {start_acn}")
        logger.info(f"Output path: {output_path}")
    
    # Create a session
    session = create_session()
    
    # Initialize variables
    results = []
    count = start_count
    
    # Add .csv extension if not present
    if not str(output_path).endswith('.csv'):
        output_path = Path(f"{output_path}.csv")
    
    # Get token if not provided
    if not token:
        logger.info("No token provided, attempting to get one using the stored curl command")
        # Check if we have a curl command in the configuration
        config = load_config()
        if not config.get("curl_command"):
            logger.error("No curl command found in configuration. Please update the curl command using the update-curl command.")
            logger.error("Example: ./query.py update-curl \"curl 'https://bisexternal.ciamlogin.com/...' ...\"")
            return
        
        token_data = get_token_from_curl()
        if not token_data:
            logger.error("Failed to get token. Exiting.")
            logger.error("Please update the curl command using the update-curl command.")
            return
        
        logger.debug(f"Token data keys: {token_data.keys()}")
        token = token_data.get("access_token")
        if not token:
            logger.error("No access token found in response. Exiting.")
            logger.error("Response: " + json.dumps(token_data)[:100] + "...")
            return
        
        logger.info("Successfully obtained token")
    
    try:
        while True:
            # Check if we've reached the limit
            if limit is not None and count >= limit:
                logger.info(f"Reached limit of {limit} queries")
                break
            
            # Query the ACN
            data = query_acn(session, current_acn, token)
            
            # Handle 401 error (unauthorized) - token might have expired
            if isinstance(data, dict) and data.get("acn") == current_acn and "error" in data and data["error"].get("status") == 401:
                logger.warning("Token expired (401 Unauthorized). Attempting to refresh...")
                
                # Check if we have a curl command in the configuration
                config = load_config()
                if not config.get("curl_command"):
                    logger.error("No curl command found in configuration. Please update the curl command using the update-curl command.")
                    logger.error("Example: ./query.py update-curl \"curl 'https://bisexternal.ciamlogin.com/...' ...\"")
                    save_state(current_acn, output_path, count)
                    break
                
                token_data = get_token_from_curl()
                if not token_data:
                    logger.error("Failed to refresh token. Saving state and exiting.")
                    logger.error("Please update the curl command using the update-curl command.")
                    save_state(current_acn, output_path, count)
                    break
                
                logger.debug(f"Token refresh data keys: {token_data.keys()}")
                token = token_data.get("access_token")
                if not token:
                    logger.error("No access token found in response. Saving state and exiting.")
                    logger.error("Response: " + json.dumps(token_data)[:100] + "...")
                    save_state(current_acn, output_path, count)
                    break
                
                logger.info("Token refreshed. Retrying query...")
                data = query_acn(session, current_acn, token)
            
            # If we get a 404, break the loop
            if data is None:
                logger.info(f"No more data found after ACN {current_acn}")
                break
            
            # Add the data to the results
            results.append(data)
            count += 1
            
            # Log progress every 10 records
            if count % 10 == 0:
                logger.info(f"Processed {count} records")
                # Save state periodically
                save_state(current_acn, output_path, count)
            
            # Decrement the ACN
            current_acn = decrement_acn(current_acn)
            
    except KeyboardInterrupt:
        logger.info("Query interrupted by user")
        save_state(current_acn, output_path, count)
    except Exception as e:
        logger.error(f"Error occurred: {e}")
        save_state(current_acn, output_path, count)
    finally:
        # Save the results to a CSV file
        save_to_csv(results, output_path)
        logger.info(f"Query complete. Processed {count} records.")

if __name__ == "__main__":
    app()
