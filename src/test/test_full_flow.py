"""
Test the complete end-to-end flow: store change, product search, and availability check
"""
import sys
from pathlib import Path

# Add parent directory to path to import main
sys.path.insert(0, str(Path(__file__).parent.parent))

from main import AHProductChecker
import time

print("="*60)
print("Testing Complete End-to-End Flow")
print("="*60)

# Configuration
product_name = "Crosta Mollica Garlic & mozzarella flatbread"
test_postcodes = ["9711HX", "9712BA", "9721CX"]  # Test with 3 postcodes

# Create checker
checker = AHProductChecker()

# Get current store
xpath_store_selector = '//*[@resource-id="shoppingIntentToolbar_text_title"]'
if checker.device.xpath(xpath_store_selector).exists:
    initial_store = checker.device.xpath(xpath_store_selector).get().attrib.get('text', 'Unknown')
    print(f"\nInitial store: {initial_store}")
else:
    print("\nCannot determine current store")
    initial_store = "Unknown"

print(f"\nProduct to check: {product_name}")
print(f"Postcodes to test: {', '.join(test_postcodes)}")

# Run the check
for idx, postcode in enumerate(test_postcodes, 1):
    print(f"\n{'='*60}")
    print(f"Test {idx}/{len(test_postcodes)}: Checking at postcode {postcode}")
    print(f"{'='*60}")

    # Navigate to store selection
    print("\n1. Navigating to store selection...")
    if not checker.navigate_to_store_selection():
        print(f"✗ Failed to navigate to store selection")
        break

    # Select store by postcode
    print(f"\n2. Selecting store with postcode {postcode}...")
    xpath_home = '//android.widget.TextView[@text="Home"]'
    if not checker.select_store_by_postcode(postcode):
        print(f"✗ Failed to select store for {postcode}")
        if checker.device.xpath(xpath_home).exists:
            checker.device.xpath(xpath_home).click()
        else:
            checker.device.press("back")
        time.sleep(1)
        continue

    # Verify store changed
    time.sleep(1)
    if checker.device.xpath(xpath_store_selector).exists:
        current_store = checker.device.xpath(xpath_store_selector).get().attrib.get('text', 'Unknown')
        print(f"   Current store: {current_store}")

    # Get store info
    print("\n3. Getting store information...")
    store_info = checker.get_current_store_info()
    print(f"   Store: {store_info['name']}")

    # Search for product
    print(f"\n4. Searching for product...")
    if not checker.search_for_product(product_name):
        print(f"✗ Failed to search for product")
        if checker.device.xpath(xpath_home).exists:
            checker.device.xpath(xpath_home).click()
        else:
            checker.device.press("back")
        time.sleep(1)
        continue

    # Click on product in results
    print(f"\n5. Clicking on product in search results...")
    if not checker.click_product_in_results(product_name):
        print(f"✗ Failed to find/click product in results")
        if checker.device.xpath(xpath_home).exists:
            checker.device.xpath(xpath_home).click()
        else:
            checker.device.press("back")
        time.sleep(1)
        continue

    # Check availability
    print(f"\n6. Checking product availability...")
    available, status = checker.check_product_availability()

    print(f"\n{'─'*60}")
    print(f"RESULT for {postcode}:")
    print(f"  Store: {store_info['name']}")
    print(f"  Product: {product_name}")
    print(f"  Available: {available}")
    print(f"  Status: {status}")
    print(f"{'─'*60}")

    # Record result
    result = {
        "postcode": postcode,
        "store_name": store_info["name"],
        "available": available,
        "status": status
    }
    checker.results.append(result)

    # Go back to home for next iteration
    print(f"\n7. Returning to home screen...")
    xpath_home = '//android.widget.TextView[@text="Home"]'
    if checker.device.xpath(xpath_home).exists:
        checker.device.xpath(xpath_home).click()
        time.sleep(1)
    else:
        print("   Warning: Home button not found, using back")
        checker.device.press("back")
        time.sleep(1)

# Print summary
print(f"\n{'='*60}")
print("SUMMARY")
print(f"{'='*60}")
print(f"\nProduct: {product_name}")
print(f"Stores checked: {len(checker.results)}\n")

for result in checker.results:
    status_symbol = "✓" if result["available"] else "✗"
    print(f"{status_symbol} {result['postcode']}: {result['status']}")

print(f"\n{'='*60}")
print("Test Complete")
print(f"{'='*60}")
