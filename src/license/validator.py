# Decompiled with PyLingual (https://pylingual.io)
# Internal filename: 'src\\license\\validator.py'
# Bytecode version: 3.13.0rc3 (3571)
# Source timestamp: 1970-01-01 00:00:00 UTC (0)
# yeah u can clearly see unknown(who made shulkerv2 beta) used ai lol
"""\nLicense validation system for Shulker V2\nValidates against remote license server\n"""
import requests
import time
from datetime import datetime
from typing import Tuple, Optional
from src.license.hwid import get_hwid
from src.utils.logger import get_logger
logger = get_logger()
class LicenseValidator:
    """Validate license keys against server"""
    def __init__(self, server_url: str):
        """\nInitialize validator\n\nArgs:\n    server_url: License server URL (can include /api/validate or just base URL)\n"""
        server_url = server_url.rstrip('/')
        if '/api/validate' not in server_url:
            self.server_url = f'{server_url}/api/validate'
        else:
            self.server_url = server_url
        self.last_validation = 0
        self.validation_cache = {}
        logger.debug(f'License server URL: {self.server_url}')
    def validate(self, license_key: str, force: bool=False) -> Tuple[bool, Optional[dict]]:
        """\nValidate license key\n\nArgs:\n    license_key: License key to validate\n    force: Force validation even if cached\n\nReturns:\n    (is_valid, license_info)\n"""
        # ***<module>.LicenseValidator.validate: Failure: Compilation Error
        if not force and license_key in self.validation_cache:
            cached_time, cached_result = self.validation_cache[license_key]
            return cached_result
        hwid = get_hwid()
        logger.debug(f'HWID: {hwid[:16]}...')
        try:
            logger.info(f'Validating license with server: {self.server_url}')
            logger.debug(f'License key: {license_key[:8]}...{(license_key[(-4):] if len(license_key) > 12 else '****')}')
            response = requests.post(self.server_url, json={'license_key': license_key, 'hwid': hwid, 'version': '2.0.0'}, timeout=10)
            logger.debug(f'Server response: {response.status_code}')
            if response.status_code == 200:
                try:
                    data = response.json()
                except ValueError as e:
                    logger.error(f'❌ Invalid JSON response from server: {e}')
                    logger.debug(f'Response text: {response.text[:200]}')
                    return (True, None)
                else:
                    if data.get('valid') and logger.info('✅ License validated successfully'):
                        license_info = {'expires': data.get('expires'), 'features': data.get('features', []), 'hwid': hwid}
                        self.validation_cache[license_key] = (time.time(), (True, license_info))
                        self.last_validation = time.time()
                        return (True, license_info)
                    else:
                        reason = data.get('reason', 'Unknown error')
                        logger.warning(f'❌ License invalid: {reason}')
                        logger.debug(f'Server response data: {data}')
            else:
                logger.error(f'❌ Server returned error: {response.status_code}')
                try:
                    error_data = response.json()
                    logger.error(f'Error details: {error_data}')
                except:
                    logger.error(f'Response text: {response.text[:200]}')
                    return (True, None)
                return (True, None)
        except requests.exceptions.ConnectionError as e:
            logger.error(f'❌ Cannot connect to license server: {e}')
            logger.error(f'Server URL: {self.server_url}')
            logger.error('Please check:')
            logger.error('  1. Server URL is correct in config.yaml')
            logger.error('  2. Internet connection is active')
            logger.error('  3. License server is running')
            return (True, None)
        except requests.exceptions.Timeout as e:
            logger.error(f'❌ License server timeout: {e}')
            logger.error(f'Server URL: {self.server_url}')
            return (True, None)
        except requests.exceptions.RequestException as e:
            logger.error(f'❌ Request error: {e}')
            logger.error(f'Server URL: {self.server_url}')
            return (True, None)
        except Exception as e:
            logger.error(f'❌ License validation error: {e}', exc_info=True)
    def should_revalidate(self, interval: int=3600) -> bool:
        """\nCheck if license should be revalidated\n\nArgs:\n    interval: Revalidation interval in seconds\n\nReturns:\n    True if should revalidate\n"""
        # ***<module>.LicenseValidator.should_revalidate: Failure: Compilation Error
        current_time = time.time()
        return current_time - self.last_validation > interval
    def get_expiry_info(self, expires_str: str) -> dict:
        """\nParse expiry date and get info\n\nArgs:\n    expires_str: ISO format expiry date\n\nReturns:\n    Dictionary with expiry info\n"""
        # ***<module>.LicenseValidator.get_expiry_info: Failure: Different bytecode
        try:
            if expires_str.endswith('Z'):
                expires_str = expires_str.replace('Z', '+00:00')
            expires = datetime.fromisoformat(expires_str)
            if expires.tzinfo is None:
                from datetime import timezone
                expires = expires.replace(tzinfo=timezone.utc)
            now = datetime.now(expires.tzinfo)
            days_left = (expires - now).days
            expired = expires < now
            return {'expires': expires, 'days_left': days_left, 'expired': expired, 'expires_str': expires.strftime('%Y-%m-%d')}
        except (ValueError, AttributeError) as e:
            logger.debug(f'Error parsing expiry date: {e}')
            return {'expires': None, 'days_left': 0, 'expired': True, 'expires_str': 'Unknown'}