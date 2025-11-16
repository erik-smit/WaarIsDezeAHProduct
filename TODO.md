# TODO - Future Improvements

## Product Search
- [ ] Make product search more robust when multiple results exist
  - Currently clicks the first matching product
  - Should verify we're clicking the exact product (maybe by checking full product name)
  - Consider using more specific search terms or exact match after finding results
  - Could add a parameter to specify which result to click (default: first)

## Error Handling
- [ ] Add retry logic for network timeouts
- [ ] Better handling of unexpected modals/popups
- [ ] Graceful recovery when UI elements are not found

## Store Selection
- [ ] Verify store actually changed by comparing before/after store names
- [ ] Handle case when postcode has no stores nearby

## Availability Checking
- [ ] Add more availability states (e.g., "temporarily out of stock" vs "not in assortment")
- [ ] Capture product price if available
- [ ] Check stock levels if displayed

## Performance
- [ ] Reduce wait times where possible (currently conservative for reliability)
- [ ] Parallel checking of multiple products at same store

## Reporting
- [ ] Add HTML report generation
- [ ] Include timestamps for when each store was checked
- [ ] Add screenshots of product detail page for verification

## Configuration
- [ ] Support multiple products in one run
- [ ] Allow customization of wait times
- [ ] Support for different AH app versions/layouts
