# Waar Is Deze AH Product?

Vind je het ook zo onhandig om steeds tussen winkels te moeten klikken om te vinden in welke lokale AH iets in het assortiment zit?  
Deze tool gebruikt een Android die via ADB verbonden is om de app te automatiseren.  

Getest op Samsung Tab S7+ in portrait mode.

```
# uv run src\main.py
2025-11-17 23:22:30 - INFO - Albert Heijn Product Store Checker
2025-11-17 23:22:30 - INFO - ============================================================
2025-11-17 23:22:30 - INFO - Connecting to Android device...
...
2025-11-17 23:24:28 - INFO - Result: Available=False (Not available at this store)
2025-11-17 23:24:28 - INFO - ============================================================
2025-11-17 23:24:28 - INFO - Completed checking 16 stores
2025-11-17 23:24:28 - INFO - ============================================================

============================================================
SUMMARY
============================================================

Product: Crosta Mollica Garlic & mozzarella flatbread
Available at 5/16 stores

Available at:
  - 9721CX: Helperplein 4 (Available at this store)
  - 9743ES: Siersteenlaan 464 (Available at this store)
  - 9731AB: Rijksweg 16 (Available at this store)
  - 9737TL: Stoepemaheerd 21 (Available at this store)
  - 9731AH: Rijksweg 129A (Available at this store)

Not available at:
  - 9712BA: Akerkhof 1 (Not available at this store)
  - 9711HX: Brugstraat 14 (Not available at this store)
  - 9712HA: Oude Ebbingestraat 19 (Not available at this store)
  - 9711HG: Gedempte Zuiderdiep 14 (Not available at this store)
  - 9712NG: Nieuwe Ebbingestraat 73 (Not available at this store)
  - 9718AR: Westerkade 11 (Not available at this store)
  - 9715HH: Floresplein 13 (Not available at this store)
  - 9741EH: Eikenlaan 39 (Not available at this store)
  - 9742AK: Dierenriemstraat 122 (Not available at this store)
  - 9728WZ: B S F von Suttnerstraat 1 (Not available at this store)
  - 9745AA: Zuiderweg 27 (Not available at this store)
 ```

## Benodigdheden

- Android device met Albert Heijn app geinstalleerd en ingelogd.
- Python

## Setup

1. **Configure your search**

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

## Gebruik

```bash
uv run src/main.py
```

## Troubleshooting

- **Device not found**: Run `adb devices` to verify connection
- **App crashes**: Reinstall uiautomator2 with `uv run python -m uiautomator2 init --reinstall`

## Disclaimer

For personal use only. Use responsibly and comply with the Albert Heijn app's terms of service.
