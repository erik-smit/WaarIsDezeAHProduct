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

