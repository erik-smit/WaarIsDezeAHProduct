"""
Albert Heijn Product Store Availability Checker
Automates checking if a product is available at different AH stores in your area.
"""

import uiautomator2 as u2
import time
import json
import csv
from datetime import datetime
from pathlib import Path


class AHProductChecker:
    """Automates checking product availability across Albert Heijn stores."""

    def __init__(self, device_serial=None):
        """Initialize the checker and connect to Android device."""
        print("Connecting to Android device...")
        if device_serial:
            self.device = u2.connect(device_serial)
        else:
            self.device = u2.connect()  # Connect to first available device

        print(f"Connected to: {self.device.info}")
        self.results = []

    def launch_app(self, package_name="com.icemobile.albertheijn"):
        """Launch the Albert Heijn app."""
        print(f"Launching {package_name}...")
        self.device.app_start(package_name)
        time.sleep(3)  # Wait for app to launch

    def navigate_to_store_selection(self):
        """Navigate to the store selection screen."""
        print("Navigating to store selection...")

        # Click on store selector button using XPath
        xpath_store_selector = '//*[@resource-id="shoppingIntentToolbar_text_title"]'
        if self.device.xpath(xpath_store_selector).exists:
            print("Found store selector button")
            self.device.xpath(xpath_store_selector).click()
            time.sleep(2)
        else:
            print("Error: Store selector button not found")
            return False

        return True

    def select_store_by_postcode(self, postcode):
        """Select a store by its postcode using the search field."""
        print(f"Selecting store with postcode: {postcode}")

        # Clean postcode (remove spaces, uppercase)
        postcode_clean = postcode.replace(" ", "").upper()

        print(f"Searching for: {postcode_clean}")

        # XPath selectors
        xpath_choose_another = '//*[@content-desc="Kies een andere winkel"]'
        xpath_search_field = '//*[@hint="Zoek op plaats of postcode"]'
        xpath_choose_store = '//*[@content-desc="Kies deze winkel"]'
        xpath_vervang = '//*[@content-desc="Vervang"]'

        # Click "Kies een andere winkel" (Choose another store)
        if self.device.xpath(xpath_choose_another).exists:
            print("Clicking 'Choose another store' button...")
            self.device.xpath(xpath_choose_another).click()
            time.sleep(2)
        else:
            print("Warning: 'Choose another store' button not found")

        # Click the search field and enter postcode
        print("Clicking search field...")
        if self.device.xpath(xpath_search_field).exists:
            self.device.xpath(xpath_search_field).click()
            time.sleep(1)

            print(f"Entering postcode: {postcode_clean}")
            self.device.xpath(xpath_search_field).set_text(postcode_clean)
            time.sleep(2)  # Wait for search results
        else:
            print("Error: Cannot find search field")
            return False

        # Click "Kies deze winkel" button
        print("Clicking 'Kies deze winkel' button...")
        if self.device.xpath(xpath_choose_store).exists:
            self.device.xpath(xpath_choose_store).click()
            time.sleep(2)
            print("Clicked 'Kies deze winkel'")
        else:
            print(f"Error: Store with postcode '{postcode}' not found in search results")
            # Close the store selection screen
            xpath_close = '//*[@content-desc="Sluiten"]'
            if self.device.xpath(xpath_close).exists:
                self.device.xpath(xpath_close).click()
            return False

        # Click "Vervang" button to confirm store change
        print("Waiting for confirmation modal...")
        time.sleep(1)

        if self.device.xpath(xpath_vervang).exists:
            print("Clicking 'Vervang' to confirm...")
            self.device.xpath(xpath_vervang).click()
            time.sleep(2)

            # Click "Verder winkelen" (Continue shopping) button
            xpath_continue = '//*[@text="Verder winkelen"]'
            if self.device.xpath(xpath_continue).exists:
                print("Clicking 'Verder winkelen'...")
                self.device.xpath(xpath_continue).click()
                time.sleep(2)

            return True
        else:
            # Check if store is already selected (no confirmation modal appears)
            xpath_close = '//*[@content-desc="Sluiten"]'
            if self.device.xpath(xpath_close).exists:
                print("Store already selected (no confirmation needed)")
                self.device.xpath(xpath_close).click()
                time.sleep(1)
                return True
            else:
                print("Warning: 'Vervang' button not found and cannot determine state!")
                return False

    def search_for_product(self, product_name):
        """Search for a product in the app."""
        print(f"Searching for product: {product_name}")

        # XPath for search bar
        xpath_search_bar = '//*[@text="Zoek een product"]'

        # Click on search bar
        if self.device.xpath(xpath_search_bar).exists:
            print("Found search bar")
            self.device.xpath(xpath_search_bar).click()
            time.sleep(2)
        else:
            print("Error: Search bar not found")
            return False

        # Enter search term
        if self.device(className="android.widget.EditText").exists:
            self.device(className="android.widget.EditText").set_text(product_name)
            time.sleep(1)
            self.device.press("enter")
            time.sleep(2)
            return True
        else:
            print("Error: Could not find search input field")
            return False

    def click_product_in_results(self, product_name):
        """Click on a product from search results."""
        print(f"Looking for product in results: {product_name}")

        # Use partial match to find product
        # Extract first few words for partial match
        search_terms = " ".join(product_name.split()[:3])
        xpath_product = f'//android.widget.TextView[contains(@text, "{search_terms}")]'

        if self.device.xpath(xpath_product).exists:
            print(f"Found product matching '{search_terms}'")
            self.device.xpath(xpath_product).click()
            time.sleep(2)
            return True
        else:
            print(f"Error: Product not found in search results")
            return False

    def check_product_availability(self):
        """Check if the product is available at the current store."""
        print("Checking product availability...")

        # XPath selectors for availability
        xpath_not_available = '//*[@text="Niet te koop in mijn winkel"]'
        xpath_available = '//*[@text="Te koop in mijn winkel"]'

        # Wait a moment for page to load
        time.sleep(1)

        if self.device.xpath(xpath_not_available).exists:
            print("Product not available at this store")
            return False, "Not available at this store"
        elif self.device.xpath(xpath_available).exists:
            print("Product available at this store")
            return True, "Available at this store"
        else:
            print("Warning: Could not determine availability")
            return None, "Unknown"

    def get_current_store_info(self):
        """Extract current store name and address from the app."""
        print("Getting store information...")

        store_name = "Unknown Store"
        store_address = "Unknown Address"

        # Try to extract store info from the store selector button
        if self.device(resourceId="shoppingIntentToolbar_text_title").exists:
            elem = self.device(resourceId="shoppingIntentToolbar_text_title")
            store_text = elem.info.get('text', '')
            if store_text:
                store_name = store_text
                store_address = store_text
                print(f"Found store: {store_name}")

        return {
            "name": store_name,
            "address": store_address
        }

    def check_stores(self, product_name, postcodes_to_check):
        """Check product availability across multiple stores by postcode."""
        print(f"\n{'='*60}")
        print(f"Checking product: {product_name}")
        print(f"Number of postcodes to check: {len(postcodes_to_check)}")
        print(f"Postcodes: {', '.join(postcodes_to_check)}")
        print(f"{'='*60}\n")

        self.launch_app()

        for idx, postcode in enumerate(postcodes_to_check, 1):
            print(f"\n[{idx}/{len(postcodes_to_check)}] Processing postcode: {postcode}")
            print("-" * 60)

            # Navigate to store selection
            self.navigate_to_store_selection()

            # Select the store by postcode
            if not self.select_store_by_postcode(postcode):
                print(f"Skipping postcode: {postcode}")
                # Go back to home to retry
                xpath_home = '//android.widget.TextView[@text="Home"]'
                if self.device.xpath(xpath_home).exists:
                    self.device.xpath(xpath_home).click()
                else:
                    self.device.press("back")
                time.sleep(1)
                continue

            # Get store info before searching (to capture which store we selected)
            store_info = self.get_current_store_info()

            # Search for product
            if not self.search_for_product(product_name):
                print(f"Failed to search for product at {postcode}")
                xpath_home = '//android.widget.TextView[@text="Home"]'
                if self.device.xpath(xpath_home).exists:
                    self.device.xpath(xpath_home).click()
                else:
                    self.device.press("back")
                time.sleep(1)
                continue

            # Click on product in search results
            if not self.click_product_in_results(product_name):
                print(f"Failed to find product in results at {postcode}")
                xpath_home = '//android.widget.TextView[@text="Home"]'
                if self.device.xpath(xpath_home).exists:
                    self.device.xpath(xpath_home).click()
                else:
                    self.device.press("back")
                    self.device.press("back")
                time.sleep(1)
                continue

            # Check availability
            available, status = self.check_product_availability()

            # Record result
            result = {
                "timestamp": datetime.now().isoformat(),
                "postcode": postcode,
                "store_name": store_info["name"],
                "store_address": store_info["address"],
                "product_name": product_name,
                "available": available,
                "status": status
            }

            self.results.append(result)

            print(f"Result: Available={available} ({status})")

            # Go back to home for next iteration
            xpath_home = '//android.widget.TextView[@text="Home"]'
            if self.device.xpath(xpath_home).exists:
                self.device.xpath(xpath_home).click()
                time.sleep(1)
            else:
                print("Warning: Home button not found, using back button")
                self.device.press("back")
                time.sleep(1)

        print(f"\n{'='*60}")
        print(f"Completed checking {len(self.results)} stores")
        print(f"{'='*60}\n")

    def save_results(self, format="csv"):
        """Save results to file."""
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")

        if format == "csv":
            filename = f"results_{timestamp}.csv"
            self._save_csv(filename)
        elif format == "json":
            filename = f"results_{timestamp}.json"
            self._save_json(filename)
        else:
            print(f"Unknown format: {format}")
            return

        print(f"\nResults saved to: {filename}")

    def _save_csv(self, filename):
        """Save results as CSV."""
        if not self.results:
            print("No results to save")
            return

        with open(filename, 'w', newline='', encoding='utf-8') as f:
            writer = csv.DictWriter(f, fieldnames=self.results[0].keys())
            writer.writeheader()
            writer.writerows(self.results)

    def _save_json(self, filename):
        """Save results as JSON."""
        with open(filename, 'w', encoding='utf-8') as f:
            json.dump(self.results, f, indent=2, ensure_ascii=False)

    def print_summary(self):
        """Print a summary of results."""
        if not self.results:
            print("No results to summarize")
            return

        print("\n" + "="*60)
        print("SUMMARY")
        print("="*60)

        available_count = sum(1 for r in self.results if r["available"])
        total_count = len(self.results)

        product_name = self.results[0]["product_name"] if self.results else "Unknown"
        print(f"\nProduct: {product_name}")
        print(f"Available at {available_count}/{total_count} stores\n")

        print("Available at:")
        for result in self.results:
            if result["available"]:
                postcode = result.get("postcode", "")
                store_name = result.get("store_name", "Unknown")
                print(f"  - {postcode}: {store_name} ({result['status']})")

        if available_count < total_count:
            print("\nNot available at:")
            for result in self.results:
                if not result["available"]:
                    postcode = result.get("postcode", "")
                    store_name = result.get("store_name", "Unknown")
                    print(f"  - {postcode}: {store_name} ({result['status']})")

        print()


def load_config(config_file="config.json"):
    """Load configuration from JSON file."""
    try:
        with open(config_file, 'r', encoding='utf-8') as f:
            return json.load(f)
    except FileNotFoundError:
        print(f"Config file '{config_file}' not found. Using defaults.")
        return None


def main():
    """Main entry point."""
    print("Albert Heijn Product Store Checker")
    print("="*60)

    # Load config
    config = load_config()

    if config:
        product_name = config.get("product_name", "")
        postcodes = config.get("postcodes", [])
        output_format = config.get("output_format", "csv")
        device_serial = config.get("device_serial", None)
    else:
        # Interactive mode
        product_name = input("\nEnter product name to search for: ")
        postcodes_input = input("Enter postcodes (comma-separated, e.g. 9712BA,9711HX): ")
        postcodes = [s.strip() for s in postcodes_input.split(",")]
        output_format = "csv"
        device_serial = None

    if not product_name or not postcodes:
        print("Error: Product name and postcodes are required")
        return

    # Create checker and run
    try:
        checker = AHProductChecker(device_serial)
        checker.check_stores(product_name, postcodes)
        checker.print_summary()
        # Optionally save results to file (commented out by default)
        # checker.save_results(format=output_format)
    except Exception as e:
        print(f"\nError occurred: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    main()
