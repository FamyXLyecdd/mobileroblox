"""
Roblox Auto-Signup Script (Modernized 2026)
Playwright-based automation with free services only
"""
import asyncio
import sys
from pathlib import Path
from typing import Optional
from loguru import logger
from tqdm.rich import tqdm

from lib.models import Config, Account
from lib.browser import BrowserManager
from lib.captcha import NopeCHASolver
from lib.email_service import EmailService
from lib.roblox_api import RobloxAPI
from lib.username_gen import UsernameGenerator, StructuredUsernameGenerator, get_resource_path


# Configure logger
logger.remove()  # Remove default handler
logger.add(
    sys.stderr,
    format="<green>{time:HH:mm:ss}</green> | <level>{level: <8}</level> | <level>{message}</level>",
    level="INFO"
)


class RobloxAccountCreator:
    """Main account creation orchestrator"""
    
    def __init__(self, config: Config):
        self.config = config
        self.browser_mgr: Optional[BrowserManager] = None
        self.captcha_solver: Optional[NopeCHASolver] = None
        self.email_service: Optional[EmailService] = None
        self.roblox_api: Optional[RobloxAPI] = None
        self.accounts = []
    
    async def initialize(self) -> None:
        """Initialize all services"""
        logger.info("Initializing services...")
        
        # Initialize Roblox API
        self.roblox_api = RobloxAPI()
        
        # Initialize browser
        self.browser_mgr = BrowserManager(self.config.browser)
        await self.browser_mgr.initialize()
        
        # Install NopeCHA if API key provided
        if self.config.captcha.api_key:
            extension_path = get_resource_path("lib/NopeCHA")
            await self.browser_mgr.install_extension(extension_path)
            self.captcha_solver = NopeCHASolver(self.config.captcha)
            logger.success("NopeCHA extension installed")
        
        # Initialize email service
        self.email_service = EmailService(self.config.email)
        
        logger.success("All services initialized")
    
    async def generate_username(self) -> str:
        """Generate and validate username"""
        if self.config.username_format:
            # Use prefix format
            counter = 0
            while counter < 100:
                username = f"{self.config.username_format}_{counter}"
                is_valid = await self.roblox_api.validate_username(username)
                if is_valid:
                    return username
                counter += 1
            
            # Fallback to scrambled if all taken
            logger.warning(f"All usernames with prefix '{self.config.username_format}' taken, using random")
        
        # Generate random username
        if self.config.username_scrambled:
            generator = UsernameGenerator()
        else:
            generator = StructuredUsernameGenerator()
        
        for _ in range(100):
            username = generator.generate()
            is_valid = await self.roblox_api.validate_username(username)
            if is_valid:
                return username
        
        raise Exception("Failed to generate valid username after 100 attempts")
    
    async def create_account(self, index: int, total: int) -> Optional[Account]:
        """Create a single Roblox account"""
        progress = tqdm(total=100, desc=f"Account {index + 1}/{total}", leave=True)
        
        try:
            # Generate username
            progress.set_description(f"Generating username [{index + 1}/{total}]")
            progress.update(10)
            username = await self.generate_username()
            logger.info(f"Generated username: {username}")
            
            # Create email if verification enabled
            email, email_password, email_id = None, None, None
            if self.config.verification_enabled:
                progress.set_description(f"Creating email [{index + 1}/{total}]")
                progress.update(10)
                email, email_password, email_id = await self.email_service.create_email(self.config.password)
                logger.info(f"Created email: {email}")
            
            # Navigate to signup page
            progress.set_description(f"Loading signup page [{index + 1}/{total}]")
            progress.update(10)
            
            page = await self.browser_mgr.new_page()
            
            # Configure NopeCHA if available
            if self.captcha_solver:
                await self.captcha_solver.configure_extension(page, self.config.captcha.api_key)
            
            await page.goto("https://www.roblox.com/CreateAccount", wait_until="networkidle")
            
            # Accept cookies if popup appears
            try:
                await page.click('.cookie-btn.btn-primary-md', timeout=3000)
            except:
                pass
            
            # Fill signup form
            progress.set_description(f"Filling form [{index + 1}/{total}]")
            progress.update(15)
            
            from datetime import datetime
            current_month = datetime.now().strftime("%b")
            current_day = datetime.now().day
            current_year = datetime.now().year - 19
            
            await page.select_option("#MonthDropdown", current_month)
            await page.select_option("#DayDropdown", f"{current_day:02d}")
            await page.select_option("#YearDropdown", str(current_year))
            await page.fill("#signup-username", username)
            await page.fill("#signup-password", self.config.password)
            
            # Check gender checkbox if present
            try:
                await page.click('input[id="signup-checkbox"]', timeout=2000)
            except:
                pass
            
            await asyncio.sleep(1)
            
            # Submit form
            progress.set_description(f"Submitting signup [{index + 1}/{total}]")
            progress.update(10)
            
            await page.click('button[id="signup-button"]', timeout=10000)
            
            # Handle captcha if present
            await asyncio.sleep(3)
            if self.captcha_solver:
                progress.set_description(f"Solving captcha [{index + 1}/{total}]")
                await self.captcha_solver.solve_captcha(page)
            
            progress.update(15)
            
            # Wait for redirect to home
            try:
                await page.wait_for_url("**/home", timeout=30000)
            except:
                logger.warning("Did not redirect to home page, checking current URL...")
            
            progress.set_description(f"Account created [{index + 1}/{total}]")
            progress.update(10)
            
            # Email verification
            if self.config.verification_enabled and email:
                progress.set_description(f"Verifying email [{index + 1}/{total}]")
                
                try:
                    # Click verification modal button
                    await page.click('.btn-primary-md', timeout=5000)
                    await asyncio.sleep(1)
                    
                    # Check if email input is present
                    email_input = page.locator('input[type="email"]')
                    if await email_input.count() > 0:
                        await email_input.fill(email)
                        await page.click('text="Add Email"', timeout=5000)
                        await asyncio.sleep(2)
                        
                        # Wait for verification email
                        logger.info("Waiting for verification email...")
                        verification_link = await self.email_service.wait_for_verification_email()
                        
                        if verification_link:
                            await page.goto(verification_link)
                            await asyncio.sleep(3)
                            logger.success("Email verified!")
                except Exception as e:
                    logger.warning(f"Email verification failed: {e}")
                
                progress.update(10)
            
            # Customize avatar
            if self.config.customization_enabled:
                progress.set_description(f"Customizing avatar [{index + 1}/{total}]")
                await self.roblox_api.customize_avatar(page)
                progress.update(5)
            
            # Follow users
            if self.config.following_enabled and self.config.following_usernames:
                progress.set_description(f"Following users [{index + 1}/{total}]")
                for follow_user in self.config.following_usernames[:3]:  # Limit to 3
                    await self.roblox_api.follow_user(page, follow_user)
                progress.update(5)
            
            # Extract cookies
            progress.set_description(f"Saving account [{index + 1}/{total}]")
            cookies = await page.context.cookies()
            cookie_list = [{"name": c["name"], "value": c["value"]} for c in cookies]
            
            # Create account object
            account = Account(
                username=username,
                password=self.config.password,
                email=email,
                email_password=email_password,
                cookies=cookie_list,
                verified=self.config.verification_enabled,
                customized=self.config.customization_enabled
            )
            
            progress.update(max(0, 100 - progress.n))
            progress.set_description(f"Complete [{index + 1}/{total}]")
            progress.close()
            
            logger.success(f"Account #{index + 1} created: {username}")
            return account
            
        except Exception as e:
            logger.error(f"Failed to create account #{index + 1}: {e}")
            progress.close()
            return None
    
    async def save_accounts(self) -> None:
        """Save accounts to various formats"""
        if not self.accounts:
            logger.warning("No accounts to save")
            return
        
        logger.info("Saving accounts...")
        
        # TXT format
        if "txt" in self.config.export_formats:
            with open("accounts.txt", "a", encoding="utf-8") as f:
                for account in self.accounts:
                    f.write(
                        f"Username: {account.username}, "
                        f"Password: {account.password}, "
                        f"Email: {account.email or 'N/A'}, "
                        f"Email Password: {account.email_password or 'N/A'} "
                        f"(Created at {account.created_at.strftime('%Y-%m-%d %H:%M:%S')})\n"
                    )
            logger.success("Saved to accounts.txt")
        
        # JSON format
        if "json" in self.config.export_formats:
            import json
            accounts_data = [account.to_dict() for account in self.accounts]
            with open("accounts.json", "w", encoding="utf-8") as f:
                json.dump(accounts_data, f, indent=2, default=str)
            logger.success("Saved to accounts.json")
        
        # CSV format
        if "csv" in self.config.export_formats:
            import csv
            with open("accounts.csv", "w", newline='', encoding="utf-8") as f:
                writer = csv.writer(f)
                writer.writerow(["Username", "Password", "Email", "Email Password", "ROBLOSECURITY", "Created At"])
                for account in self.accounts:
                    writer.writerow([
                        account.username,
                        account.password,
                        account.email or "N/A",
                        account.email_password or "N/A",
                        account.get_roblosecurity() or "N/A",
                        account.created_at.isoformat()
                    ])
            logger.success("Saved to accounts.csv")
        
        # Roblox Account Manager format
        if self.config.roblox_account_manager:
            import pyperclip
            roblosecurity_cookies = []
            for account in self.accounts:
                cookie = account.get_roblosecurity()
                if cookie:
                    roblosecurity_cookies.append(cookie)
            
            if roblosecurity_cookies:
                cookies_text = "\n".join(roblosecurity_cookies)
                pyperclip.copy(cookies_text)
                logger.success("ROBLOSECURITY cookies copied to clipboard!")
                print("\n✅ Paste these cookies into Roblox Account Manager (Cookie import mode)")
    
    async def run(self) -> None:
        """Main execution loop"""
        try:
            await self.initialize()
            
            logger.info(f"Creating {self.config.count} account(s)...")
            
            for i in range(self.config.count):
                account = await self.create_account(i, self.config.count)
                
                if account:
                    self.accounts.append(account)
                
                # Rate limiting between accounts
                if i < self.config.count - 1:
                    await asyncio.sleep(self.config.rate_limit_delay)
            
            # Save all accounts
            await self.save_accounts()
            
            logger.info(f"\n{'=' * 50}")
            logger.info(f"✅ Successfully created {len(self.accounts)}/{self.config.count} accounts")
            logger.info(f"{'=' * 50}\n")
            
        finally:
            # Cleanup
            if self.browser_mgr:
                await self.browser_mgr.close()
            if self.roblox_api:
                await self.roblox_api.close()


async def main():
    """Main entry point"""
    logger.info("Roblox Auto-Signup (2026 - Modernized)")
    logger.info("=" * 50)
    
    try:
        # Load configuration
        config_path = Path("config.yaml")
        if config_path.exists():
            logger.info("Loading configuration from config.yaml...")
            config = Config.from_yaml(str(config_path))
        else:
            logger.warning("config.yaml not found, using default configuration")
            config = Config()
        
        # Create accounts
        creator = RobloxAccountCreator(config)
        await creator.run()
        
        logger.success("\nAll done! Check accounts.txt, accounts.json, and accounts.csv")
        
    except KeyboardInterrupt:
        logger.warning("\n\nInterrupted by user")
    except Exception as e:
        logger.error(f"\nFatal error: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    asyncio.run(main())
