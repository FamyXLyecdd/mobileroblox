"""Data models for Roblox auto-signup script (2026)"""
from dataclasses import dataclass, field
from typing import Optional, List, Dict
from datetime import datetime


@dataclass
class Account:
    """Represents a created Roblox account"""
    username: str
    password: str
    email: Optional[str] = None
    email_password: Optional[str] = None
    cookies: List[Dict[str, str]] = field(default_factory=list)
    created_at: datetime = field(default_factory=datetime.now)
    verified: bool = False
    customized: bool = False
    
    def get_roblosecurity(self) -> Optional[str]:
        """Extract .ROBLOSECURITY cookie value"""
        for cookie in self.cookies:
            if cookie.get("name") == ".ROBLOSECURITY":
                return cookie.get("value")
        return None
    
    def to_dict(self) -> dict:
        """Convert to dictionary for JSON export"""
        return {
            "username": self.username,
            "password": self.password,
            "email": self.email,
            "email_password": self.email_password,
            "cookies": self.cookies,
            "created_at": self.created_at.isoformat(),
            "verified": self.verified,
            "customized": self.customized
        }


@dataclass
class CaptchaConfig:
    """Captcha service configuration"""
    service: str = "nopecha"
    api_key: str = ""
    delays: Dict[str, int] = field(default_factory=lambda: {
        "before_solve": 3,
        "after_solve": 5,
        "between_retries": 10
    })
    timeout: int = 300
    max_retries: int = 5
    auto_retry_on_fail: bool = True


@dataclass
class EmailConfig:
    """Email service configuration"""
    primary_service: str = "mailtm"
    fallback_services: List[str] = field(default_factory=lambda: ["tempmail", "guerrillamail"])
    verification_timeout: int = 60
    max_retries: int = 5
    check_interval: int = 5


@dataclass
class ProxyConfig:
    """Proxy configuration"""
    enabled: bool = False
    rotation: bool = True
    list: List[str] = field(default_factory=list)


@dataclass
class BrowserConfig:
    """Browser configuration"""
    headless: bool = False
    stealth_mode: bool = True
    user_agent: str = "auto"


@dataclass
class Config:
    """Main configuration object"""
    # Account settings
    password: str = "Qing762.chy"
    count: int = 1
    verification_enabled: bool = True
    customization_enabled: bool = True
    
    # Username settings
    username_format: str = ""
    username_scrambled: bool = True
    
    # Following settings
    following_enabled: bool = False
    following_usernames: List[str] = field(default_factory=list)
    
    # Export settings
    export_formats: List[str] = field(default_factory=lambda: ["txt", "json", "csv"])
    roblox_account_manager: bool = True
    
    # Advanced settings
    analytics: bool = True
    parallel_execution: bool = False
    max_parallel: int = 3
    rate_limit_delay: int = 5
    
    # Component configs
    captcha: CaptchaConfig = field(default_factory=CaptchaConfig)
    email: EmailConfig = field(default_factory=EmailConfig)
    proxy: ProxyConfig = field(default_factory=ProxyConfig)
    browser: BrowserConfig = field(default_factory=BrowserConfig)
    
    @classmethod
    def from_yaml(cls, yaml_path: str) -> 'Config':
        """Load configuration from YAML file"""
        import yaml
        
        with open(yaml_path, 'r', encoding='utf-8') as f:
            data = yaml.safe_load(f)
        
        return cls(
            password=data.get('account', {}).get('password', 'Qing762.chy'),
            count=data.get('account', {}).get('count', 1),
            verification_enabled=data.get('account', {}).get('verification_enabled', True),
            customization_enabled=data.get('account', {}).get('customization_enabled', True),
            username_format=data.get('username', {}).get('format', ''),
            username_scrambled=data.get('username', {}).get('scrambled', True),
            following_enabled=data.get('following', {}).get('enabled', False),
            following_usernames=data.get('following', {}).get('usernames', []),
            export_formats=data.get('export', {}).get('formats', ['txt', 'json', 'csv']),
            roblox_account_manager=data.get('export', {}).get('roblox_account_manager', True),
            analytics=data.get('advanced', {}).get('analytics', True),
            parallel_execution=data.get('advanced', {}).get('parallel_execution', False),
            max_parallel=data.get('advanced', {}).get('max_parallel', 3),
            rate_limit_delay=data.get('advanced', {}).get('rate_limit_delay', 5),
            captcha=CaptchaConfig(
                service=data.get('captcha', {}).get('service', 'nopecha'),
                api_key=data.get('captcha', {}).get('api_key', ''),
                delays=data.get('captcha', {}).get('delays', {}),
                timeout=data.get('captcha', {}).get('timeout', 300),
                max_retries=data.get('captcha', {}).get('max_retries', 5),
                auto_retry_on_fail=data.get('captcha', {}).get('auto_retry_on_fail', True)
            ),
            email=EmailConfig(
                primary_service=data.get('email', {}).get('primary_service', 'mailtm'),
                fallback_services=data.get('email', {}).get('fallback_services', []),
                verification_timeout=data.get('email', {}).get('verification_timeout', 60),
                max_retries=data.get('email', {}).get('max_retries', 5),
                check_interval=data.get('email', {}).get('check_interval', 5)
            ),
            proxy=ProxyConfig(
                enabled=data.get('proxy', {}).get('enabled', False),
                rotation=data.get('proxy', {}).get('rotation', True),
                list=data.get('proxy', {}).get('list', [])
            ),
            browser=BrowserConfig(
                headless=data.get('browser', {}).get('headless', False),
                stealth_mode=data.get('browser', {}).get('stealth_mode', True),
                user_agent=data.get('browser', {}).get('user_agent', 'auto')
            )
        )
