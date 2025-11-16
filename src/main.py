"""
Albert Heijn Product Store Availability Checker
Automates checking if a product is available at different AH stores in your area.
"""

import uiautomator2 as u2
import time
import json
import csv
import logging
from datetime import datetime
from pathlib import Path

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    datefmt='%Y-%m-%d %H:%M:%S'
)
logger = logging.getLogger(__name__)


class AHProductChecker:
    """Automates checking product availability across Albert Heijn stores."""

    def __init__(self, device_serial=None):
        """Initialize the checker and connect to Android device."""
        logger.info("Connecting to Android device...")
        if device_serial:
            self.device = u2.connect(device_serial)
        else:
            self.device = u2.connect()  # Connect to first available device

        logger.info(f"Connected to: {self.device.info}")
        self.results = []

    def launch_app(self, package_name="com.icemobile.albertheijn"):
        """Launch the Albert Heijn app."""
        logger.info(f"Launching {package_name}...")
        self.device.app_start(package_name)
        time.sleep(3)  # Wait for app to launch

    def navigate_to_store_selection(self):
        """Navigate to the store selection screen."""
        logger.info("Navigating to store selection...")

        # Click on store selector button using XPath
        xpath_store_selector = '//*[@resource-id="shoppingIntentToolbar_text_title"]'
        try:
            logger.info("Clicking store selector button")
            self.device.xpath(xpath_store_selector).click()
            return True
        except Exception as e:
            logger.error(f"Store selector button not found: {e}")
            return False

    def select_store_by_postcode(self, postcode):
        """Select a store by its postcode using the search field."""
        logger.info(f"Selecting store with postcode: {postcode}")

        # Clean postcode (remove spaces, uppercase)
        postcode_clean = postcode.replace(" ", "").upper()

        logger.info(f"Searching for: {postcode_clean}")

        # XPath selectors
        xpath_choose_another = '//*[@content-desc="Kies een andere winkel"]'
        xpath_search_field = '//*[@hint="Zoek op plaats of postcode"]'
        xpath_choose_store = '//*[@content-desc="Kies deze winkel"]'
        xpath_vervang = '//*[@content-desc="Vervang"]'

        # Click "Kies een andere winkel" (Choose another store)
        try:
            logger.info("Clicking 'Choose another store' button...")
            self.device.xpath(xpath_choose_another).click()
        except Exception as e:
            logger.warning(f"'Choose another store' button not found: {e}")

        # Click the search field and enter postcode
        try:
            logger.info("Clicking search field...")
            self.device.xpath(xpath_search_field).click()
            logger.info(f"Entering postcode: {postcode_clean}")
            self.device.xpath(xpath_search_field).set_text(postcode_clean)
        except Exception as e:
            logger.error(f"Cannot find search field: {e}")
            return False

        # Click "Kies deze winkel" button
        try:
            logger.info("Clicking 'Kies deze winkel' button...")
            self.device.xpath(xpath_choose_store).click()
            logger.info("Clicked 'Kies deze winkel'")
        except Exception as e:
            logger.error(f"Store with postcode '{postcode}' not found: {e}")
            # Close the store selection screen
            try:
                xpath_close = '//*[@content-desc="Sluiten"]'
                self.device.xpath(xpath_close).click()
            except Exception as e2:
                logger.warning(f"Could not close modal: {e2}")
            return False

        # Click "Vervang" button to confirm store change
        try:
            logger.info("Clicking 'Vervang' to confirm...")
            self.device.xpath(xpath_vervang).click()

            # Click "Verder winkelen" (Continue shopping) button
            try:
                xpath_continue = '//*[@text="Verder winkelen"]'
                logger.info("Clicking 'Verder winkelen'...")
                self.device.xpath(xpath_continue).click()
            except Exception as e:
                logger.warning(f"'Verder winkelen' button not found: {e}")

            return True
        except Exception as e:
            # Check if store is already selected (no confirmation modal appears)
            try:
                xpath_close = '//*[@content-desc="Sluiten"]'
                logger.info("Store already selected (no confirmation needed)")
                self.device.xpath(xpath_close).click()
                return True
            except Exception as e2:
                logger.warning(f"'Vervang' button not found: {e}")
                return False

    def search_for_product(self, product_name):
        """Search for a product in the app."""
        logger.info(f"Searching for product: {product_name}")

        # XPath for search bar
        xpath_search_bar = '//*[@text="Zoek een product"]'

        # Click on search bar
        try:
            logger.info("Clicking search bar")
            self.device.xpath(xpath_search_bar).click()
        except Exception as e:
            logger.error(f"Search bar not found: {e}")
            return False

        # Enter search term
        try:
            self.device(className="android.widget.EditText").set_text(product_name)
            self.device.press("enter")
            return True
        except Exception as e:
            logger.error(f"Could not find search input field: {e}")
            return False

    def click_product_in_results(self, product_name):
        """Click on a product from search results."""
        logger.info(f"Looking for product in results: {product_name}")

        # Use partial match to find product
        # Extract first few words for partial match
        search_terms = " ".join(product_name.split()[:3])
        xpath_product = f'//android.widget.TextView[contains(@text, "{search_terms}")]'

        try:
            logger.info(f"Found product matching '{search_terms}'")
            self.device.xpath(xpath_product).click()
            return True
        except:
            logger.error(f"Product not found in search results")
            return False

    def check_product_availability(self):
        """Check if the product is available at the current store."""
        logger.info("Checking product availability...")

        # XPath selectors for availability
        xpath_not_available = '//*[@text="Niet te koop in mijn winkel"]'
        xpath_available = '//*[@text="Te koop in mijn winkel"]'

        # Alternate between checking "available" and "not available"
        for attempt in range(5):
            # Check for "available"
            try:
                self.device.xpath(xpath_available).get(timeout=1)
                logger.info("Product available at this store")
                return True, "Available at this store"
            except:
                pass

            # Check for "not available"
            try:
                self.device.xpath(xpath_not_available).get(timeout=1)
                logger.info("Product not available at this store")
                return False, "Not available at this store"
            except:
                pass

        logger.warning("Could not determine availability")
        return None, "Unknown"

    def get_current_store_info(self):
        """Extract current store name and address from the app."""
        logger.info("Getting store information...")

        store_name = "Unknown Store"
        store_address = "Unknown Address"

        # Try to extract store info from the store selector button
        xpath_store_selector = '//*[@resource-id="shoppingIntentToolbar_text_title"]'
        try:
            elem = self.device.xpath(xpath_store_selector).get()
            store_text = elem.attrib.get('text', '')
            if store_text:
                store_name = store_text
                store_address = store_text
                logger.info(f"Found store: {store_name}")
        except Exception as e:
            logger.warning(f"Could not get store info: {e}")

        return {
            "name": store_name,
            "address": store_address
        }

    def navigate_to_producten_tab(self):
        """Navigate to the Producten tab (relative to Home button)."""
        logger.info("Navigating to Producten tab...")

        # XPath that finds Producten relative to Home button
        xpath_producten = '//*[@text="Producten"]'

        try:
            self.device.xpath(xpath_producten).click()
            logger.info("Clicked Producten tab")
            return True
        except Exception as e:
            logger.error(f"Failed to click Producten tab: {e}")
            return False

    def check_stores(self, product_name, postcodes_to_check):
        """Check product availability across multiple stores by postcode."""
        logger.info("="*60)
        logger.info(f"Checking product: {product_name}")
        logger.info(f"Number of postcodes to check: {len(postcodes_to_check)}")
        logger.info(f"Postcodes: {', '.join(postcodes_to_check)}")
        logger.info("="*60)

        self.launch_app()

        # Navigate to Producten tab to register the product there
        if not self.navigate_to_producten_tab():
            logger.error("Failed to navigate to Producten tab in setup")
            return
        
        # Search for product once at the beginning
        logger.info("Searching for product (one-time setup)...")
        if not self.search_for_product(product_name):
            logger.error("Failed to search for product")
            return

        if not self.click_product_in_results(product_name):
            logger.error("Failed to find product in search results")
            return

        logger.info("Product found and registered in Producten tab! Now checking each store...")

        for idx, postcode in enumerate(postcodes_to_check, 1):
            logger.info(f"[{idx}/{len(postcodes_to_check)}] Processing postcode: {postcode}")
            logger.info("-" * 60)

            # Go to Home tab
            xpath_home = '//android.widget.TextView[@text="Home"]'
            try:
                self.device.xpath(xpath_home).click()
                logger.info("Switched to Home tab")
            except Exception as e:
                logger.warning(f"Failed to click Home tab: {e}")

            # Navigate to store selection
            self.navigate_to_store_selection()

            # Select the store by postcode
            if not self.select_store_by_postcode(postcode):
                logger.warning(f"Skipping postcode: {postcode}")
                continue

            # Get store info
            store_info = self.get_current_store_info()

            # Navigate to Producten tab to see the product
            if not self.navigate_to_producten_tab():
                logger.error(f"Failed to navigate to product at {postcode}")
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

            logger.info(f"Result: Available={available} ({status})")

        logger.info("="*60)
        logger.info(f"Completed checking {len(self.results)} stores")
        logger.info("="*60)

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
            logger.error(f"Unknown format: {format}")
            return

        logger.info(f"Results saved to: {filename}")

    def _save_csv(self, filename):
        """Save results as CSV."""
        if not self.results:
            logger.warning("No results to save")
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
        logger.warning(f"Config file '{config_file}' not found. Using defaults.")
        return None


def main():
    """Main entry point."""
    logger.info("Albert Heijn Product Store Checker")
    logger.info("="*60)

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
        logger.error("Product name and postcodes are required")
        return

    # Create checker and run
    try:
        checker = AHProductChecker(device_serial)
        checker.check_stores(product_name, postcodes)
        checker.print_summary()
        # Optionally save results to file (commented out by default)
        # checker.save_results(format=output_format)
    except Exception as e:
        logger.error(f"Error occurred: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    main()
