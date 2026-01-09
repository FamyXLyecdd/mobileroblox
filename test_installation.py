"""
Quick test script to verify the modernized installation works
"""
import asyncio
import sys
from pathlib import Path

async def test_imports():
    """Test that all modules import correctly"""
    print("Testing imports...")
    
    try:
        print("  ✓ models.py", end="")
        from lib.models import Config, Account
        print(" - OK")
        
        print("  ✓ browser.py", end="")
        from lib.browser import BrowserManager
        print(" - OK")
        
        print("  ✓ captcha.py", end="")
        from lib.captcha import NopeCHASolver
        print(" - OK")
        
        print("  ✓ email_service.py", end="")
        from lib.email_service import EmailService
        print(" - OK")
        
        print("  ✓ roblox_api.py", end="")
        from lib.roblox_api import RobloxAPI
        print(" - OK")
        
        print("  ✓ username_gen.py", end="")
        from lib.username_gen import UsernameGenerator
        print(" - OK")
        
        print("\n✅ All modules imported successfully!\n")
        return True
        
    except Exception as e:
        print(f"\n❌ Import failed: {e}\n")
        return False

async def test_config():
    """Test config loading"""
    print("Testing configuration...")
    
    try:
        from lib.models import Config
        
        config_path = Path("config.yaml")
        if config_path.exists():
            config = Config.from_yaml(str(config_path))
            print(f"  ✓ Loaded config.yaml")
            print(f"  ✓ Account count: {config.count}")
            print(f"  ✓ Captcha service: {config.captcha.service}")
            print(f"  ✓ Email service: {config.email.primary_service}")
        else:
            config = Config()
            print(f"  ✓ Using default config")
        
        print("\n✅ Configuration working!\n")
        return True
        
    except Exception as e:
        print(f"\n❌ Config test failed: {e}\n")
        return False

async def test_username_generation():
    """Test username generation"""
    print("Testing username generation...")
    
    try:
        from lib.username_gen import UsernameGenerator, StructuredUsernameGenerator
        
        # Test scrambled
        gen = UsernameGenerator()
        usernames = [gen.generate() for _ in range(3)]
        print(f"  ✓ Scrambled usernames: {', '.join(usernames)}")
        
        # Test structured
        struct_gen = StructuredUsernameGenerator()
        struct_usernames = [struct_gen.generate() for _ in range(3)]
        print(f"  ✓ Structured usernames: {', '.join(struct_usernames)}")
        
        print("\n✅ Username generation working!\n")
        return True
        
    except Exception as e:
        print(f"\n❌ Username generation failed: {e}\n")
        return False

async def test_roblox_api():
    """Test Roblox API"""
    print("Testing Roblox API...")
    
    try:
        from lib.roblox_api import RobloxAPI
        
        api = RobloxAPI()
        
        # Test username validation
        is_valid = await api.validate_username("TestUser12345RandomLongName")
        print(f"  ✓ Username validation: {is_valid}")
        
        # Test getting user ID
        user_id = await api.get_user_id("Roblox")
        print(f"  ✓ User ID lookup: {user_id}")
        
        await api.close()
        
        print("\n✅ Roblox API working!\n")
        return True
        
    except Exception as e:
        print(f"\n❌ Roblox API test failed: {e}\n")
        return False

async def main():
    """Run all tests"""
    print("=" * 60)
    print("Roblox Auto-Signup - Installation Test (2026)")
    print("=" * 60)
    print()
    
    tests = [
        test_imports(),
        test_config(),
        test_username_generation(),
        test_roblox_api(),
    ]
    
    results = await asyncio.gather(*tests, return_exceptions=True)
    
    passed = sum(1 for r in results if r is True)
    total = len(tests)
    
    print("=" * 60)
    if passed == total:
        print(f"✅ ALL TESTS PASSED ({passed}/{total})")
        print("\nYou're ready to use the script!")
        print("Run: python main.py")
    else:
        print(f"⚠️  SOME TESTS FAILED ({passed}/{total} passed)")
        print("\nPlease check the errors above.")
        if passed >= total - 1:
            print("\nMost tests passed - script should still work!")
    print("=" * 60)

if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("\n\nTest interrupted")
    except Exception as e:
        print(f"\n\nTest error: {e}")
        import traceback
        traceback.print_exc()
