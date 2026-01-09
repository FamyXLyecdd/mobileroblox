"""NopeCHA captcha solver with configurable delays for improved accuracy (2026)"""
import asyncio
from typing import Optional
from playwright.async_api import Page, Frame
from loguru import logger
from tenacity import retry, stop_after_attempt, wait_exponential

from .models import CaptchaConfig


class NopeCHASolver:
    """NopeCHA captcha solver with accuracy-focused delays"""
    
    def __init__(self, config: CaptchaConfig):
        self.config = config
        self.extension_configured = False
    
    async def configure_extension(self, page: Page, api_key: str) -> None:
        """Configure NopeCHA extension with API key"""
        try:
            logger.info(f"Configuring NopeCHA with API key...")
            await page.goto(f"https://nopecha.com/setup#{api_key}")
            await asyncio.sleep(2)
            self.extension_configured = True
            logger.success("NopeCHA configured successfully")
        except Exception as e:
            logger.error(f"Failed to configure NopeCHA: {e}")
            raise
    
    async def detect_captcha(self, page: Page, timeout: int = 5) -> Optional[Frame]:
        """Detect if captcha is present on page"""
        try:
            # Check for FunCaptcha (Arkose Labs) iframe
            captcha_frame = page.frame(url=lambda url: "arkose" in url.lower())
            if captcha_frame:
                logger.warning("FunCaptcha detected")
                return captcha_frame
            
            # Check for specific iframe ID
            captcha_frame = page.frame_locator('xpath=//*[@id="arkose-iframe"]')
            if await captcha_frame.locator('body').count() > 0:
                logger.warning("FunCaptcha iframe detected")
                return captcha_frame
            
            return None
        except Exception as e:
            logger.debug(f"No captcha detected: {e}")
            return None
    
    @retry(
        stop=stop_after_attempt(5),
        wait=wait_exponential(multiplier=1, min=4, max=10),
        reraise=True
    )
    async def solve_captcha(self, page: Page) -> bool:
        """
        Solve captcha with configurable delays for better accuracy
        
        Returns:
            True if solved successfully, False otherwise
        """
        if not self.extension_configured:
            logger.error("NopeCHA not configured. Call configure_extension() first")
            return False
        
        try:
            # Wait before solving (let page fully load)
            logger.info(f"Waiting {self.config.delays['before_solve']}s before solving...")
            await asyncio.sleep(self.config.delays['before_solve'])
            
            # Detect captcha
            captcha_frame = await self.detect_captcha(page)
            if not captcha_frame:
                logger.info("No captcha detected")
                return True
            
            logger.info("Captcha detected - waiting for NopeCHA to solve...")
            
            # Wait for NopeCHA to solve (max timeout)
            start_time = asyncio.get_event_loop().time()
            solved = False
            
            while (asyncio.get_event_loop().time() - start_time) < self.config.timeout:
                # Check if captcha is gone
                current_captcha = await self.detect_captcha(page, timeout=2)
                if not current_captcha:
                    solved = True
                    break
                
                # Check if URL changed (successful submission)
                if "/home" in page.url or page.url != page.url:
                    solved = True
                    break
                
                await asyncio.sleep(2)
            
            if not solved:
                logger.error("Captcha solving timed out")
                return False
            
            # Wait after solving (let submission complete)
            logger.info(f"Captcha solved! Waiting {self.config.delays['after_solve']}s...")
            await asyncio.sleep(self.config.delays['after_solve'])
            
            logger.success("Captcha solved successfully")
            return True
            
        except Exception as e:
            logger.error(f"Error solving captcha: {e}")
            
            if self.config.auto_retry_on_fail:
                logger.info(f"Retrying in {self.config.delays['between_retries']}s...")
                await asyncio.sleep(self.config.delays['between_retries'])
            
            return False
    
    async def wait_and_check_captcha(self, page: Page, action_func, max_retries: Optional[int] = None) -> bool:
        """
        Perform an action and handle captcha if it appears
        
        Args:
            page: Playwright page object
            action_func: Async function that triggers potential captcha
            max_retries: Override default max_retries
            
        Returns:
            True if action succeeded (with or without captcha), False otherwise
        """
        retries = max_retries or self.config.max_retries
        
        for attempt in range(retries):
            try:
                # Perform the action
                await action_func()
                
                # Check for captcha
                await asyncio.sleep(2)
                captcha = await self.detect_captcha(page)
                
                if captcha:
                    logger.warning(f"Captcha appeared after action (attempt {attempt + 1}/{retries})")
                    success = await self.solve_captcha(page)
                    
                    if success:
                        return True
                    else:
                        if attempt < retries - 1:
                            logger.info(f"Retrying action in {self.config.delays['between_retries']}s...")
                            await asyncio.sleep(self.config.delays['between_retries'])
                        continue
                else:
                    # No captcha, success
                    logger.success("Action completed without captcha")
                    return True
                    
            except Exception as e:
                logger.error(f"Error in action (attempt {attempt + 1}/{retries}): {e}")
                if attempt < retries - 1:
                    await asyncio.sleep(self.config.delays['between_retries'])
                continue
        
        logger.error(f"Failed after {retries} attempts")
        return False


async def test_captcha_solver():
    """Test captcha solver"""
    from .browser import BrowserManager
    from .models import BrowserConfig
    
    config = CaptchaConfig(
        api_key="YOUR_API_KEY_HERE",
        delays={
            "before_solve": 3,
            "after_solve": 5,
            "between_retries": 10
        }
    )
    
    browser_config = BrowserConfig(headless=False, stealth_mode=True)
    
    async with BrowserManager(browser_config) as browser_mgr:
        # Install NopeCHA extension
        await browser_mgr.install_extension("./lib/NopeCHA")
        
        page = await browser_mgr.new_page()
        
        solver = NopeCHASolver(config)
        await solver.configure_extension(page, config.api_key)
        
        # Navigate to a page with captcha (Roblox signup)
        await page.goto("https://www.roblox.com/CreateAccount")
        
        # Test solving
        success = await solver.solve_captcha(page)
        logger.info(f"Captcha solve result: {success}")


if __name__ == "__main__":
    asyncio.run(test_captcha_solver())
