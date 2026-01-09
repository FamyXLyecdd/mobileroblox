"""Roblox API interactions (2026)"""
import asyncio
import re
from typing import Optional, List, Tuple
from datetime import datetime
import httpx
from playwright.async_api import Page
from loguru import logger

from .models import Account


class RobloxAPI:
    """Handles all Roblox API interactions"""
    
    def __init__(self):
        self.client = httpx.AsyncClient(timeout=10)
        self.csrf_token: Optional[str] = None
    
    async def get_csrf_token(self) -> str:
        """Get X-CSRF-TOKEN for API requests"""
        try:
            response = await self.client.post(
                "https://auth.roblox.com/v2/login",
                headers={"User-Agent": "Mozilla/5.0"}
            )
            token = response.headers.get("x-csrf-token")
            self.csrf_token = token
            return token
        except Exception as e:
            logger.error(f"Failed to get CSRF token: {e}")
            return ""
    
    async def validate_username(self, username: str) -> bool:
        """Check if username is available"""
        try:
            response = await self.client.get(
                f"https://auth.roblox.com/v2/usernames/validate"
                f"?request.username={username}&request.birthday=04%2F15%2F02&request.context=Signup"
            )
            
            data = response.json()
            is_valid = data.get("code") == 0
            
            if is_valid:
                logger.debug(f"Username '{username}' is available")
            else:
                logger.debug(f"Username '{username}' is taken: {data.get('message')}")
            
            return is_valid
            
        except Exception as e:
            logger.error(f"Error validating username: {e}")
            return False
    
    async def validate_password(self, username: str, password: str) -> Tuple[bool, str]:
        """Validate password complexity"""
        try:
            if not self.csrf_token:
                await self.get_csrf_token()
            
            data = {"username": username, "password": password}
            headers = {
                "accept": "application/json",
                "content-type": "application/json;charset=UTF-8",
                "x-csrf-token": self.csrf_token,
                "user-agent": "Mozilla/5.0"
            }
            
            response = await self.client.post(
                "https://auth.roblox.com/v2/passwords/validate",
                json=data,
                headers=headers
            )
            
            result = response.json()
            is_valid = result.get("code") == 0
            message = result.get("message", "") if not is_valid else "Password is valid"
            
            return is_valid, message
            
        except Exception as e:
            logger.error(f"Error validating password: {e}")
            return False, str(e)
    
    async def get_user_id(self, username: str) -> Optional[int]:
        """Get user ID from username"""
        try:
            response = await self.client.post(
                "https://users.roblox.com/v1/usernames/users",
                json={"usernames": [username]}
            )
            
            data = response.json()
            users = data.get("data", [])
            
            if users:
                user_id = users[0].get("id")
                logger.debug(f"User ID for '{username}': {user_id}")
                return user_id
            
            return None
            
        except Exception as e:
            logger.error(f"Error getting user ID: {e}")
            return None
    
    async def follow_user(self, page: Page, username: str) -> bool:
        """Follow a user via UI interaction"""
        try:
            user_id = await self.get_user_id(username)
            if not user_id:
                logger.warning(f"User '{username}' not found")
                return False
            
            url = f"https://www.roblox.com/users/{user_id}/profile"
            await page.goto(url, wait_until="networkidle")
            await asyncio.sleep(2)
            
            # Click dropdown menu
            try:
                await page.click(
                    'button[data-testid="user-profile-more-button"]',
                    timeout=5000
                )
                await asyncio.sleep(0.5)
                
                # Click follow button
                await page.click(
                    '//button[@id="follow-button"]',
                    timeout=5000
                )
                
                logger.success(f"Successfully followed user '{username}'")
                return True
                
            except Exception as e:
                logger.warning(f"Could not find follow button for '{username}': {e}")
                return False
                
        except Exception as e:
            logger.error(f"Error following user '{username}': {e}")
            return False
    
    async def customize_avatar(self, page: Page) -> bool:
        """Randomize avatar appearance"""
        try:
            logger.info("Customizing avatar...")
            
            # Navigate to avatar page
            await page.goto("https://www.roblox.com/my/avatar", wait_until="networkidle")
            await asyncio.sleep(2)
            
            # Listen for inventory API call
            async with page.expect_response("**/avatar-inventory**") as response_info:
                await page.wait_for_load_state("networkidle")
            
            response = await response_info.value
            inventory = await response.json()
            
            # Group items by type
            items_by_type = {}
            for item in inventory.get('avatarInventoryItems', []):
                if 'itemCategory' in item and 'itemSubType' in item['itemCategory']:
                    item_type = item["itemCategory"]["itemSubType"]
                    if item_type not in items_by_type:
                        items_by_type[item_type] = []
                    items_by_type[item_type].append(item)
            
            # Select random item from each category
            import random
            selected_items = []
            for item_type, items in items_by_type.items():
                if items:
                    selected = random.choice(items)
                    selected_items.append(selected)
            
            # Click on selected items
            for item in selected_items[:5]:  # Limit to 5 items to avoid timeout
                try:
                    item_name = item.get("itemName", "")
                    if item_name:
                        # Find and click item by data attribute
                        await page.click(f'a[data-item-name="{item_name}"]', timeout=3000)
                        await asyncio.sleep(0.5)
                except Exception as e:
                    logger.debug(f"Could not equip item: {e}")
                    continue
            
            # Randomize body type
            try:
                body_value = random.choice([i for i in range(0, 101, 5)])
                await page.evaluate(f"""
                    const slider = document.querySelector('input[aria-label="Body Type Scale"]');
                    if (slider) {{
                        slider.value = {body_value};
                        slider.dispatchEvent(new Event('input', {{ bubbles: true }}));
                        slider.dispatchEvent(new Event('change', {{ bubbles: true }}));
                    }}
                """)
                await asyncio.sleep(1)
            except Exception as e:
                logger.debug(f"Could not adjust body type: {e}")
            
            logger.success("Avatar customized successfully")
            return True
            
        except Exception as e:
            logger.error(f"Error customizing avatar: {e}")
            return False
    
    async def close(self):
        """Close HTTP client"""
        await self.client.aclose()


async def test_roblox_api():
    """Test Roblox API"""
    api = RobloxAPI()
    
    # Test username validation
    is_valid = await api.validate_username("TestUser12345")
    logger.info(f"Username valid: {is_valid}")
    
    # Test password validation
    is_valid, msg = await api.validate_password("TestUser", "Qing762.chy")
    logger.info(f"Password valid: {is_valid} - {msg}")
    
    # Test get user ID
    user_id = await api.get_user_id("Roblox")
    logger.info(f"User ID: {user_id}")
    
    await api.close()


if __name__ == "__main__":
    asyncio.run(test_roblox_api())
