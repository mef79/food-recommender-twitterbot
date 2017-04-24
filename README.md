Made as a project as an intern at Vertical Knowledge

## What does this do?
When a Twitter user who has enabled the sharing of location data tweets "I'm hungry" (or #hangry, "getting hangry", or "I'm hangry), this bot will tweet a response at them with the name and address of a nearby restaurant, as indexed by Google Places.

## Tools used
- `Twython` - Python Twitter API wrapper
- `Google Places` - for searching for restuarants near a location
- `Beautiful Soup` - Python web scraping library, loads a list of top 100 cities by location
