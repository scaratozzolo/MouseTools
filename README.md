# MouseTools

An unofficial Walt Disney World API. Data is pulled directly from Disney.
Yeah you could look at the code and figure it out yourself, but here's a library incase you're lazy.

If you needs something specific from the API open a new issue with a "feature request" label

### TODO:

- [x] Authentication
- [x] Function to get park data
- [x] Gather links to more info
- [ ] Functions to handle data found from links (schedules, stations, etc.)
- [x] Park advisories (returns in json {id:advisory})
- [x] Wait times obviously (returns json {ride:id})
- [x] Park IDs/Names
- [x] Water Parks
- [x] Attraction IDs/Names
- [ ] Restaurant IDs/Names txt file
- [x] Return IDs somehow...Github link
- [x] Attraction types
- [x] Today park hours
- [x] Other park hours
- [ ] GPS Locations?
- [ ] Creating some docs
- [x] Investigate destinations (web/json crawler finished)
- [x] Disneyland?
- [x] Nice file for names and ids: attractions, entertainments, parks uploaded to github
- [x] Characters/Character IDs (txt file)
- [x] Associated Characters Entertainment/events
- [x] Entertainment Start/End/Duration
- [ ] Entertainment classifications
- [ ] Entertain ancestors places (point of interest links)
- [ ] Points of interest (create class)
- [ ] Character relatedLocations classes to handle their related areas (facility, attraction, point of interest)
- [ ] character associated events
- [x] recreate entertainments list, from sorted.json to get them all
- [ ] handle entertainments without start or end date
- [ ] rewrite get ids (destinations - parks - attractions/entertainments - characters (find more things later?))
- [ ] some ids are listed by Disney but don't exist? Do something about it.
- [ ] Get related locations needs to be changed because some characters have multiple primary locations
- [ ] Ancestor locations, return IDs
- [ ] ancestor location classes?
- [x] rewrite id verifications to check id, remove name argument
- [ ] remove json files, leave just text files as possible reference.
- [ ] IDError
