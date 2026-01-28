import hashlib
import requests
from datetime import datetime
from typing import Optional, Dict, Any


class FastprintAPIClient:
    """Client for communicating with Fastprint recruitment API."""
    
    BASE_URL = "https://recruitment.fastprint.co.id/tes/api_tes_programmer"
    
    def __init__(self):
        self.username = self._generate_username()
        self.password = self._generate_password()
    
    def _generate_username(self) -> str:
        """
        Generate username based on current server time.
        Format: tesprogrammer{DD}{MM}{YY}C17
        Example: tesprogrammer280126C17 for January 28, 2026
        """
        now = datetime.now()
        day = now.strftime("%d")
        month = now.strftime("%m")
        year = now.strftime("%y")
        return f"tesprogrammer{day}{month}{year}C17"
    
    def _generate_password(self) -> str:
        """
        Generate MD5 hashed password based on current date.
        Format: MD5(bisacoding-{day}-{month_with_zero}-{year})
        Example: MD5(bisacoding-28-01-26) for January 28, 2026
        Note: Month must have leading zero, day and year do not
        """
        now = datetime.now()
        day = now.day
        month = now.strftime("%m")  # Month with leading zero
        year = now.year % 100  # Last 2 digits of year
        
        password_plain = f"bisacoding-{day}-{month}-{year}"
        password_md5 = hashlib.md5(password_plain.encode()).hexdigest()
        
        return password_md5
    
    def fetch_data(self) -> Optional[Dict[str, Any]]:
        try:
            response = requests.post(
                self.BASE_URL,
                data={
                    'username': self.username,
                    'password': self.password
                },
                timeout=30
            )
            
            response.raise_for_status()
            return response.json()
            
        except requests.exceptions.RequestException as e:
            print(f"Error fetching data from API: {e}")
            return None
        except ValueError as e:
            print(f"Error parsing JSON response: {e}")
            return None
    
    def get_credentials(self) -> Dict[str, str]:
        return {
            'username': self.username,
            'password': self.password
        }
