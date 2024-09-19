# Location Finder

A simple Flask app which returns the country/state/city/suburb name for given coordinates, using OpenStreetMap data.

## Endpoints
- `/lat/lon` : Get local names
- `/lang/lat/lon` : Get names for specified language. See https://wiki.openstreetmap.org/wiki/Names#Localization

## Example request

`/fr/50.843388/4.349016`
```json
{
  "city": "Bruxelles",
  "country": "Belgique",
  "country_code": "BE",
  "state": "Bruxelles-Capitale",
  "suburb": "Quartier Midi-Lemonnier"
}
```
- If no name was found (most often suburb), empty string is returned.
- Country code is ISO3166-1.

## Credits
- Data from [OpenStreetMap](https://osm.org)
- Overpass instance used : [Private.coffee](https:///overpass.private.coffee)