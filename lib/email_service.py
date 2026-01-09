"""Free email service providers for account verification (2026)"""
import asyncio
import re
from abc import ABC, abstractmethod
from typing import Optional, List, Tuple
from datetime import datetime
import httpx
from pymailtm import MailTm, Account
from loguru import logger
from tenacity import retry, stop_after_attempt, wait_fixed

from .models import EmailConfig


class EmailProvider(ABC):
    """Abstract base class for email providers"""
    
    @abstractmethod
    async def create_account(self, password: str) -> Tuple[str, str, str]:
        """
        Create email account
        
        Returns:
            (email_address, email_password, account_id)
        """
        pass
    
    @abstractmethod
    async def get_messages(self, account_id: str, email: str, password: str) -> List:
        """Get messages from inbox"""
        pass
    
    @abstractmethod
    async def extract_verification_link(self, message) -> Optional[str]:
        """Extract Roblox verification link from email"""
        pass


class MailTmProvider(EmailProvider):
    """Mail.tm provider (FREE)"""
    
    def __init__(self):
        self.mailtm = MailTm()
    
    async def create_account(self, password: str) -> Tuple[str, str, str]:
        """Create Mail.tm account"""
        try:
            # Get available domains
            domains = self.mailtm._get_domains_list()
            if not domains:
                raise Exception("No Mail.tm domains available")
            
            # Generate random username
            from .lib import Main
            lib = Main()
            username = lib.generateUsername(scrambled=True).lower()
            address = f"{username}@{domains[0]}"
            
            # Create account via API
            async with httpx.AsyncClient() as client:
                response = await client.post(
                    "https://api.mail.tm/accounts",
                    json={"address": address, "password": password},
                    timeout=10
                )
                
                if response.status_code != 201:
                    raise Exception(f"Failed to create Mail.tm account: {response.text}")
                
                data = response.json()
                account_id = data.get("id")
                
                logger.success(f"Created Mail.tm account: {address}")
                return address, password, account_id
                
        except Exception as e:
            logger.error(f"Mail.tm account creation failed: {e}")
            raise
    
    async def get_messages(self, account_id: str, email: str, password: str) -> List:
        """Get messages from Mail.tm inbox"""
        try:
            # Get auth token
            async with httpx.AsyncClient() as client:
                token_response = await client.post(
                    "https://api.mail.tm/token",
                    json={"address": email, "password": password},
                    timeout=10
                )
                
                if token_response.status_code != 200:
                    raise Exception(f"Failed to get Mail.tm token: {token_response.text}")
                
                token = token_response.json().get("token")
                
                # Get messages
                messages_response = await client.get(
                    "https://api.mail.tm/messages",
                    headers={"Authorization": f"Bearer {token}"},
                    timeout=10
                )
                
                if messages_response.status_code != 200:
                    return []
                
                messages = messages_response.json().get("hydra:member", [])
                return messages
                
        except Exception as e:
            logger.debug(f"Error fetching Mail.tm messages: {e}")
            return []
    
    async def extract_verification_link(self, message) -> Optional[str]:
        """Extract verification link from Mail.tm message"""
        try:
            # Get message ID
            msg_id = message.get("id")
            
            # Fetch full message
            async with httpx.AsyncClient() as client:
                # Get token (simplified - should cache this)
                response = await client.get(
                    f"https://api.mail.tm/messages/{msg_id}",
                    timeout=10
                )
                
                if response.status_code != 200:
                    return None
                
                data = response.json()
                text = data.get("text", "") or data.get("html", [""])[0] if "html" in data else ""
                
                # Extract Roblox verification link
                match = re.search(
                    r'https://www\.roblox\.com/account/settings/verify-email\?ticket=[^\s)"]+',
                    text
                )
                
                if match:
                    return match.group(0)
                
                return None
                
        except Exception as e:
            logger.error(f"Error extracting verification link: {e}")
            return None


class TempMailProvider(EmailProvider):
    """Temp-Mail.org provider (FREE) - via unofficial API"""
    
    async def create_account(self, password: str) -> Tuple[str, str, str]:
        """Create Temp-Mail account"""
        try:
            async with httpx.AsyncClient() as client:
                # Get random email
                response = await client.get(
                    "https://www.1secmail.com/api/v1/?action=genRandomMailbox&count=1",
                    timeout=10
                )
                
                if response.status_code != 200:
                    raise Exception(f"Failed to create Temp-Mail account: {response.text}")
                
                email = response.json()[0]
                # Parse email for API calls
                login, domain = email.split("@")
                
                logger.success(f"Created Temp-Mail account: {email}")
                return email, password, f"{login}@{domain}"
                
        except Exception as e:
            logger.error(f"Temp-Mail account creation failed: {e}")
            raise
    
    async def get_messages(self, account_id: str, email: str, password: str) -> List:
        """Get messages from Temp-Mail inbox"""
        try:
            login, domain = email.split("@")
            
            async with httpx.AsyncClient() as client:
                response = await client.get(
                    f"https://www.1secmail.com/api/v1/?action=getMessages&login={login}&domain={domain}",
                    timeout=10
                )
                
                if response.status_code != 200:
                    return []
                
                messages = response.json()
                return messages
                
        except Exception as e:
            logger.debug(f"Error fetching Temp-Mail messages: {e}")
            return []
    
    async def extract_verification_link(self, message) -> Optional[str]:
        """Extract verification link from Temp-Mail message"""
        try:
            msg_id = message.get("id")
            email = message.get("to")
            login, domain = email.split("@")
            
            async with httpx.AsyncClient() as client:
                response = await client.get(
                    f"https://www.1secmail.com/api/v1/?action=readMessage&login={login}&domain={domain}&id={msg_id}",
                    timeout=10
                )
                
                if response.status_code != 200:
                    return None
                
                data = response.json()
                text = data.get("textBody", "") or data.get("htmlBody", "")
                
                # Extract verification link
                match = re.search(
                    r'https://www\.roblox\.com/account/settings/verify-email\?ticket=[^\s)"]+',
                    text
                )
                
                if match:
                    return match.group(0)
                
                return None
                
        except Exception as e:
            logger.error(f"Error extracting verification link: {e}")
            return None


class GuerrillaMailProvider(EmailProvider):
    """Guerrilla Mail provider (FREE)"""
    
    def __init__(self):
        self.session_id = None
        self.email = None
    
    async def create_account(self, password: str) -> Tuple[str, str, str]:
        """Create Guerrilla Mail account"""
        try:
            async with httpx.AsyncClient() as client:
                response = await client.get(
                    "https://api.guerrillamail.com/ajax.php?f=get_email_address",
                    timeout=10
                )
                
                if response.status_code != 200:
                    raise Exception(f"Failed to create Guerrilla Mail account: {response.text}")
                
                data = response.json()
                email = data.get("email_addr")
                sid_token = data.get("sid_token")
                
                self.session_id = sid_token
                self.email = email
                
                logger.success(f"Created Guerrilla Mail account: {email}")
                return email, password, sid_token
                
        except Exception as e:
            logger.error(f"Guerrilla Mail account creation failed: {e}")
            raise
    
    async def get_messages(self, account_id: str, email: str, password: str) -> List:
        """Get messages from Guerrilla Mail inbox"""
        try:
            async with httpx.AsyncClient() as client:
                response = await client.get(
                    f"https://api.guerrillamail.com/ajax.php?f=get_email_list&sid_token={account_id}",
                    timeout=10
                )
                
                if response.status_code != 200:
                    return []
                
                data = response.json()
                messages = data.get("list", [])
                return messages
                
        except Exception as e:
            logger.debug(f"Error fetching Guerrilla Mail messages: {e}")
            return []
    
    async def extract_verification_link(self, message) -> Optional[str]:
        """Extract verification link from Guerrilla Mail message"""
        try:
            mail_id = message.get("mail_id")
            
            async with httpx.AsyncClient() as client:
                response = await client.get(
                    f"https://api.guerrillamail.com/ajax.php?f=fetch_email&email_id={mail_id}&sid_token={self.session_id}",
                    timeout=10
                )
                
                if response.status_code != 200:
                    return None
                
                data = response.json()
                text = data.get("mail_body", "")
                
                # Extract verification link
                match = re.search(
                    r'https://www\.roblox\.com/account/settings/verify-email\?ticket=[^\s)"]+',
                    text
                )
                
                if match:
                    return match.group(0)
                
                return None
                
        except Exception as e:
            logger.error(f"Error extracting verification link: {e}")
            return None


class EmailService:
    """Email service manager with automatic fallback"""
    
    def __init__(self, config: EmailConfig):
        self.config = config
        self.providers = {
            "mailtm": MailTmProvider(),
            "tempmail": TempMailProvider(),
            "guerrillamail": GuerrillaMailProvider()
        }
        self.current_provider: Optional[EmailProvider] = None
        self.email: Optional[str] = None
        self.password: Optional[str] = None
        self.account_id: Optional[str] = None
    
    async def create_email(self, password: str) -> Tuple[str, str, str]:
        """Create email with automatic fallback"""
        # Try primary service
        services = [self.config.primary_service] + self.config.fallback_services
        
        for service_name in services:
            try:
                provider = self.providers.get(service_name)
                if not provider:
                    logger.warning(f"Unknown email service: {service_name}")
                    continue
                
                logger.info(f"Trying {service_name}...")
                email, pwd, account_id = await provider.create_account(password)
                
                self.current_provider = provider
                self.email = email
                self.password = pwd
                self.account_id = account_id
                
                logger.success(f"Email created with {service_name}: {email}")
                return email, pwd, account_id
                
            except Exception as e:
                logger.warning(f"{service_name} failed: {e}")
                continue
        
        raise Exception("All email services failed")
    
    @retry(stop=stop_after_attempt(30), wait=wait_fixed(5))
    async def wait_for_verification_email(self) -> Optional[str]:
        """Wait for verification email and extract link"""
        if not self.current_provider or not self.email:
            raise Exception("No active email account")
        
        try:
            # Get messages
            messages = await self.current_provider.get_messages(
                self.account_id,
                self.email,
                self.password
            )
            
            if not messages:
                logger.debug("No messages yet, waiting...")
                raise Exception("No messages")  # Trigger retry
            
            # Check each message for verification link
            for message in messages:
                link = await self.current_provider.extract_verification_link(message)
                if link:
                    logger.success(f"Found verification link: {link}")
                    return link
            
            logger.debug("Messages found but no verification link")
            raise Exception("No verification link")  # Trigger retry
            
        except Exception as e:
            logger.debug(f"Waiting for verification email: {e}")
            raise  # Trigger retry


async def test_email_service():
    """Test email service"""
    config = EmailConfig(
        primary_service="mailtm",
        fallback_services=["tempmail", "guerrillamail"]
    )
    
    service = EmailService(config)
    email, pwd, account_id = await service.create_email("TestPassword123")
    
    logger.info(f"Email created: {email}")
    logger.info(f"Account ID: {account_id}")


if __name__ == "__main__":
    asyncio.run(test_email_service())
