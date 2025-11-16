# AH Product Store Checker

Automates checking if a product is available at different Albert Heijn stores using Android UI automation.

## Prerequisites

- Android device with Albert Heijn app installed
- USB debugging enabled on your device
- Python 3.13+ with uv
- ADB (Android Debug Bridge) installed

## Setup

1. **Install ADB** (if not already installed)
   ```bash
   # Windows (with Chocolatey)
   choco install adb

   # macOS
   brew install android-platform-tools

   # Linux
   sudo apt install adb
   ```

2. **Connect your Android device**
   ```bash
   adb devices  # Verify connection
   ```

3. **Install uiautomator2 on device**
   ```bash
   uv run python -m uiautomator2 init
   ```

4. **Configure your search**

   Copy and edit the config file:
   ```bash
   cp config.example.json config.json
   ```

   Edit `config.json` with your product name and postcodes:
   ```json
   {
     "product_name": "Your product name",
     "postcodes": ["9712BA", "9711HX", "9712HA"]
   }
   ```

## Usage

```bash
uv run src/main.py
```

The script will check each store and print a summary of where the product is available.

## Output

```
SUMMARY
Product: Crosta Mollica Garlic & mozzarella flatbread
Stores checked: 5

✓ 9712BA: Available at this store
✗ 9711HX: Not available at this store
...
```

## Troubleshooting

- **Device not found**: Run `adb devices` to verify connection
- **App crashes**: Reinstall uiautomator2 with `uv run python -m uiautomator2 init --reinstall`

## Disclaimer

For personal use only. Use responsibly and comply with the Albert Heijn app's terms of service.
