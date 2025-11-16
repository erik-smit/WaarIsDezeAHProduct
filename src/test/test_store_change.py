"""
Test the store change functionality
"""
import sys
from pathlib import Path

# Add parent directory to path to import main
sys.path.insert(0, str(Path(__file__).parent.parent))

from main import AHProductChecker
import time

print("="*60)
print("Testing Store Change Flow")
print("="*60)

# Create checker
checker = AHProductChecker()

# Get current store
xpath_store_selector = '//*[@resource-id="shoppingIntentToolbar_text_title"]'
if checker.device.xpath(xpath_store_selector).exists:
    current_store = checker.device.xpath(xpath_store_selector).get().attrib.get('text', 'Unknown')
    print(f"\nCurrent store: {current_store}")
else:
    print("\nCannot determine current store")
    current_store = "Unknown"

# Test postcodes
test_postcodes = ["9711HX", "9712BA"]

for idx, postcode in enumerate(test_postcodes, 1):
    print(f"\n{'='*60}")
    print(f"Test {idx}/{len(test_postcodes)}: Changing to {postcode}")
    print(f"{'='*60}")

    # Navigate to store selection
    if not checker.navigate_to_store_selection():
        print(f"✗ Failed to navigate to store selection")
        break

    # Select store by postcode
    result = checker.select_store_by_postcode(postcode)

    if result:
        print(f"\n✓ Store selection returned success")

        # Verify store changed
        time.sleep(2)

        # Close any remaining modals
        checker.device.press("back")
        time.sleep(1)

        if checker.device.xpath(xpath_store_selector).exists:
            new_store = checker.device.xpath(xpath_store_selector).get().attrib.get('text', 'Unknown')
            print(f"\nStore after change: {new_store}")

            if postcode in new_store.replace(" ", ""):
                print(f"✓ SUCCESS! Store changed to postcode {postcode}")
            else:
                print(f"? Store might be: {new_store}")
        else:
            print("? Cannot verify store change")
    else:
        print(f"\n✗ Store selection failed for {postcode}")
        # Try to recover by going back
        checker.device.press("back")
        time.sleep(1)
        checker.device.press("back")
        time.sleep(1)

print(f"\n{'='*60}")
print("Test Complete")
print(f"{'='*60}")
