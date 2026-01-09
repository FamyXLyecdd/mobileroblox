"""Browser manager for Playwright automation with stealth features (2026)"""
import asyncio
import platform
from typing import Optional
from playwright.async_api import async_playwright, Browser, BrowserContext, Page, Playwright
from fake_useragent import UserAgent
from loguru import logger

from .models import BrowserConfig


class BrowserManager:
    """Manages Playwright browser instances with anti-detection features"""
    
    def __init__(self, config: BrowserConfig):
        self.config = config
        self.playwright: Optional[Playwright] = None
        self.browser: Optional[Browser] = None
        self.context: Optional[BrowserContext] = None
        self.ua = UserAgent()
        
    async def __aenter__(self):
        """Async context manager entry"""
        await self.initialize()
        return self
    
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        """Async context manager exit"""
        await self.close()
    
    async def initialize(self) -> None:
        """Initialize Playwright and browser"""
        logger.info("Initializing Playwright browser...")
        
        self.playwright = await async_playwright().start()
        
        # Launch options
        launch_args = [
            '--disable-blink-features=AutomationControlled',
            '--disable-features=IsolateOrigins,site-per-process',
            '--no-sandbox',
            '--disable-setuid-sandbox',
            '--disable-dev-shm-usage',
            '--disable-accelerated-2d-canvas',
            '--disable-gpu',
            '--window-size=1920,1080',
            '--lang=en-US,en',
        ]
        
        # For Termux/Android compatibility
        if platform.system() == 'Linux' and 'ANDROID_ROOT' in platform.os.environ:
            launch_args.extend([
                '--single-process',
                '--no-zygote',
            ])
            logger.info("Detected Termux/Android environment - using compatible launch args")
        
        self.browser = await self.playwright.chromium.launch(
            headless=self.config.headless,
            args=launch_args
        )
        
        # Create context with stealth settings
        context_options = await self._get_context_options()
        self.context = await self.browser.new_context(**context_options)
        
        # Apply stealth patches
        if self.config.stealth_mode:
            await self._apply_stealth_scripts(self.context)
        
        logger.success("Browser initialized successfully")
    
    async def _get_context_options(self) -> dict:
        """Get browser context options with anti-detection"""
        user_agent = self.ua.random if self.config.user_agent == "auto" else self.config.user_agent
        
        return {
            'viewport': {'width': 1920, 'height': 1080},
            'user_agent': user_agent,
            'locale': 'en-US',
            'timezone_id': 'America/New_York',
            'permissions': ['geolocation', 'notifications'],
            'color_scheme': 'dark',
            'extra_http_headers': {
                'Accept-Language': 'en-US,en;q=0.9',
                'Accept-Encoding': 'gzip, deflate, br',
                'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8',
                'Sec-Fetch-Site': 'none',
                'Sec-Fetch-Mode': 'navigate',
                'Sec-Fetch-User': '?1',
                'Sec-Fetch-Dest': 'document',
            }
        }
    
    async def _apply_stealth_scripts(self, context: BrowserContext) -> None:
        """Apply JavaScript patches to hide automation"""
        stealth_js = """
        // Override the navigator.webdriver property
        Object.defineProperty(navigator, 'webdriver', {
            get: () => undefined
        });
        
        // Mock plugins
        Object.defineProperty(navigator, 'plugins', {
            get: () => [1, 2, 3, 4, 5]
        });
        
        // Mock languages
        Object.defineProperty(navigator, 'languages', {
            get: () => ['en-US', 'en']
        });
        
        // Chrome runtime
        window.chrome = {
            runtime: {}
        };
        
        // Permissions
        const originalQuery = window.navigator.permissions.query;
        window.navigator.permissions.query = (parameters) => (
            parameters.name === 'notifications' ?
                Promise.resolve({ state: Notification.permission }) :
                originalQuery(parameters)
        );
        
        // Remove Playwright-specific properties
        delete navigator.__playwright;
        delete navigator.__pw_manual;
        delete navigator.__fxdriver_evaluated;
        delete navigator.__webdriver_evaluate;
        delete navigator.__selenium_evaluate;
        delete navigator.__fxdriver_unwrapped;
        delete navigator.__driver_unwrapped;
        delete navigator.__webdriver_unwrapped;
        delete navigator.__selenium_unwrapped;
        delete navigator.__driver_evaluate;
        delete navigator.__webdriver_script_fn;
        """
        
        await context.add_init_script(stealth_js)
        logger.debug("Applied stealth JavaScript patches")
    
    async def new_page(self) -> Page:
        """Create a new page in the current context"""
        if not self.context:
            raise RuntimeError("Browser context not initialized. Call initialize() first.")
        
        page = await self.context.new_page()
        
        # Additional page-level stealth
        await page.set_extra_http_headers({
            'Upgrade-Insecure-Requests': '1',
        })
        
        return page
    
    async def install_extension(self, extension_path: str) -> None:
        """Install a browser extension (e.g., NopeCHA)"""
        if self.context:
            # Close existing context
            await self.context.close()
        
        # Recreate context with extension
        context_options = await self._get_context_options()
        
        # Extensions only work in non-headless mode
        if self.config.headless:
            logger.warning("Extensions require non-headless mode. Switching to headless=False")
            await self.browser.close()
            
            self.browser = await self.playwright.chromium.launch(
                headless=False,
                args=[
                    f'--disable-extensions-except={extension_path}',
                    f'--load-extension={extension_path}',
                    '--disable-blink-features=AutomationControlled',
                ]
            )
        
        self.context = await self.browser.new_context(**context_options)
        
        if self.config.stealth_mode:
            await self._apply_stealth_scripts(self.context)
        
        logger.info(f"Installed extension from {extension_path}")
    
    async def close(self) -> None:
        """Close browser and cleanup"""
        if self.context:
            await self.context.close()
            logger.debug("Browser context closed")
        
        if self.browser:
            await self.browser.close()
            logger.debug("Browser closed")
        
        if self.playwright:
            await self.playwright.stop()
            logger.debug("Playwright stopped")
        
        logger.info("Browser manager closed successfully")


async def test_browser():
    """Test browser manager"""
    config = BrowserConfig(headless=False, stealth_mode=True)
    
    async with BrowserManager(config) as browser_mgr:
        page = await browser_mgr.new_page()
        await page.goto("https://bot.sannysoft.com/")
        await asyncio.sleep(10)


if __name__ == "__main__":
    asyncio.run(test_browser())
