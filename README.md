# Roblox Auto-Signup (2026 - Modernized Edition)

A modern, fully automated Roblox account creation tool using **Playwright** for browser automation. **100% FREE** services only, with advanced anti-detection features.

## ✨ What's New in 2026 Edition

- **Playwright Migration**: Modern, reliable browser automation (industry standard in 2026)
- **Async/Await Throughout**: Fast, efficient Python async patterns
- **Modular Architecture**: Clean, maintainable code structure
- **NopeCHA Delays**: Improved captcha accuracy with configurable delays
- **3 Free Email Services**: Automatic fallback between Mail.tm, Temp-Mail, Guerrilla Mail
- **Termux Compatible**: Works on Android cloud phones (rooted)
- **Type-Safe**: Full type hints with Pydantic models
- **Config File**: YAML configuration instead of interactive prompts
- **Modern Logging**: Beautiful colored logs with loguru

## 🚀 Features

✅ **Free Services Only**
- NopeCHA captcha solver (200 free solves/day)
- 3 free email providers with automatic fallback
- No paid services required

✅ **Advanced Features**
- Email verification
- Avatar randomization
- Follow users automatically
- Multiple export formats (TXT, JSON, CSV, Roblox Account Manager)
- Proxy support with health checking
- Stealth mode (anti-detection)

✅ **Modern UX**
- Progress bars with rich output
- Beautiful colored logs
- Resume failed batches
- Rate limiting protection

## 📦 Installation

### Windows

```bash
# Clone repository
git clone https://github.com/qing762/roblox-auto-signup.git
cd roblox-auto-signup

# Install Python dependencies
python -m pip install -r requirements.txt

# Install Playwright browsers
python -m playwright install chromium
```

### Termux/Android (Cloud Phone)

```bash
# Install system dependencies
pkg install python nodejs rust binutils clang
pkg upgrade

# Clone repository
git clone https://github.com/qing762/roblox-auto-signup.git
cd roblox-auto-signup

# Install Python dependencies
pip install --upgrade pip setuptools wheel
pip install -r requirements.txt

# Install Playwright browsers (~300MB download)
playwright install chromium
```

## ⚙️ Configuration

Edit `config.yaml` to customize settings:

```yaml
# Account Settings
account:
  password: "YourPasswordHere"  # Change this!
  count: 5  # Number of accounts to create
  verification_enabled: true
  customization_enabled: true

# Captcha Settings (NopeCHA - FREE)
captcha:
  api_key: "YOUR_NOPECHA_API_KEY"  # Get from https://nopecha.com/manage
  delays:
    before_solve: 3  # Slower = more accurate
    after_solve: 5
    between_retries: 10

# Username Settings
username:
  format: ""  # Leave empty for random, or use "player" for player_0, player_1, etc.
  scrambled: true  # true = random (Qek7wola), false = structured (JumpingBlueCat42)

# Following (Optional)
following:
  enabled: false
  usernames:
    - "Roblox"
    - "Builderman"
```

## 🎯 Usage

```bash
# Run with config file
python main.py

# That's it! Check these files for results:
# - accounts.txt
# - accounts.json
# - accounts.csv
# - ROBLOSECURITY cookies (copied to clipboard)
```

## 📊 Output Formats

### accounts.txt
```
Username: Player123, Password: *****, Email: test@mail.tm, Email Password: ***** (Created at 2026-01-09 12:54:00)
```

### accounts.json
```json
[
  {
    "username": "Player123",
    "password": "YourPassword",
    "email": "test@mail.tm",
    "email_password": "YourPassword",
    "cookies": [...],
    "created_at": "2026-01-09T12:54:00",
    "verified": true,
    "customized": true
  }
]
```

### accounts.csv
```csv
Username,Password,Email,Email Password,ROBLOSECURITY,Created At
Player123,YourPassword,test@mail.tm,YourPassword,_|WARNING:-DO-NOT-SHARE...,2026-01-09T12:54:00
```

### Roblox Account Manager
Cookies automatically copied to clipboard! Paste into RAM using "Cookie(s)" import mode.

## 🔒 NopeCHA Setup (FREE)

1. Go to https://nopecha.com/manage
2. Create a free account
3. Copy your API key
4. Paste it in `config.yaml` under `captcha.api_key`
5. You get **200 free captcha solves per day**!

### Accuracy Tips
The script uses slower delays for better accuracy:
- **Before solving**: 3 seconds (lets page load fully)
- **After solving**: 5 seconds (ensures submission)
- **Between retries**: 10 seconds (avoids rate limits)

Total time per captcha: ~18 seconds (vs ~5s = more accurate!)

## 🛡️ Privacy & Ethics

- **100% Free**: No paid services required
- **Anonymous**: Uses temporary email addresses
- **Ethical**: Respects Roblox's rate limits
- **Open Source**: All code is visible and auditable

⚠️ **Use responsibly**. This tool is for educational purposes. Creating excessive accounts may violate Roblox's Terms of Service.

## 🐛 Troubleshooting

### "pip: command not found"
Use `python -m pip` instead of `pip`

### "Playwright browsers not found"
Run: `python -m playwright install chromium`

### "NopeCHA not working"
1. Check your API key in `config.yaml`
2. Verify you haven't exceeded 200 free solves/day
3. Try increasing delays in config

### Termux Issues
Make sure you installed all system dependencies:
```bash
pkg install python nodejs rust binutils clang
```

## 📝 Changelog (2026 Edition)

**Major Changes:**
- ✅ Migrated from DrissionPage to Playwright
- ✅ Full async/await implementation
- ✅ Modular architecture (7 new modules)
- ✅ YAML configuration system
- ✅ NopeCHA delay improvements for accuracy
- ✅ 3 free email services with fallback
- ✅ Termux/Android compatibility
- ✅ Type hints throughout
- ✅ Modern logging with loguru

## 🤝 Contributing

Contributions welcome! Please:
1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Submit a pull request

## 📜 License

GNU General Public License v3.0 - see [LICENSE](LICENSE)

## 🙏 Credits

- Original script: [qing762](https://github.com/qing762)
- Username generator: [mrsobakin/pungen](https://github.com/mrsobakin/pungen)
- 2026 modernization: Updated with latest best practices

## 💬 Support

- **Discord**: [Join Server](https://qing762.is-a.dev/discord)
- **Issues**: [GitHub Issues](https://github.com/qing762/roblox-auto-signup/issues)

---

**⭐ If this helped you, please star the repository!**
