import hashlib
import requests
import logging
from datetime import datetime
from typing import Optional, Dict, Any

logger = logging.getLogger('products')


class FastprintAPIClient:
    """Client for communicating with Fastprint recruitment API."""
    
    BASE_URL = "https://recruitment.fastprint.co.id/tes/api_tes_programmer"
    
    def __init__(self):
        self.username = self._generate_username()
        self.password = self._generate_password()
    
    def _generate_username(self) -> str:
        now = datetime.now()
        return f"tesprogrammer{now:%d%m%y}C{now.hour:02d}"
    
    def _generate_password(self) -> str:
        now = datetime.now()
        password_plain = f"bisacoding-{now.day}-{now:%m}-{now.year % 100}"
        return hashlib.md5(password_plain.encode()).hexdigest()
    
    def fetch_data(self) -> Optional[Dict[str, Any]]:
        """Fetch data from external API."""
        logger.info(f"Fetching data from API with username: {self.username}")
        
        try:
            response = requests.post(
                self.BASE_URL,
                data={'username': self.username, 'password': self.password},
                timeout=30
            )
            response.raise_for_status()
            data = response.json()
            
            logger.info(f"Successfully fetched data from API. Status code: {response.status_code}")
            return data
            
        except requests.exceptions.Timeout:
            logger.error("API request timed out after 30 seconds")
            return None
        except requests.exceptions.RequestException as e:
            logger.error(f"API request failed: {e}")
            return None
        except ValueError as e:
            logger.error(f"Failed to parse JSON response: {e}")
            return None
    
    def get_credentials(self) -> Dict[str, str]:
        return {'username': self.username, 'password': self.password}
