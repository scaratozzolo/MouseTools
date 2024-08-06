# DEVELOPMENT HAS MOVED TO GITLAB https://gitlab.com/caratozzoloxyz/public/MouseTools


# MouseTools
[![PyPI version](https://badge.fury.io/py/MouseTools.svg)](https://badge.fury.io/py/MouseTools) [![Downloads](https://pepy.tech/badge/mousetools)](https://pepy.tech/project/mousetools)


A Python wrapper for the Disney API. Data is pulled directly from Disney. This package supports Walt Disney World and Disneyland.


### Installation
You can install using pip:
```bash
pip install MouseTools
```
You can also install directly from this repo in case of any changes not uploaded to Pypi.
```bash
pip install git+https://github.com/scaratozzolo/MouseTools
```


### Example usage:
```python
import mousetools

wdw_dest = mousetools.Destination(80007798)
print(wdw_dest.get_park_ids())

dlr_dest = mousetools.Destination(80008297)
print(dlr_dest.get_attraction_ids())

mk = mousetools.Park(80007944)
print(mk.get_wait_times())

pirates = mousetools.Attraction(80010177)
print(pirates.get_wait_time())


# You don't have to know any ids to get started.
mousetools.ids.WDW_ID     # Walt Disney World Resort
mousetools.ids.DLR_ID     # Disneyland Resort

# Single park ids
mousetools.ids.MK_ID      # Magic Kingdom
mousetools.ids.EPCOT_ID   # EPCOT
mousetools.ids.HS_ID      # Hollywood Studios
mousetools.ids.AK_ID      # Animal Kingdom
mousetools.ids.TL_ID      # Typhoon Lagoon
mousetools.ids.BB_ID      # Blizzard Beach
mousetools.ids.DLP_ID     # Disneyland Park
mousetools.ids.CA_ID      # California Adventure

# List of ids
# Parks
mousetools.ids.WDW_PARK_IDS
mousetools.ids.DLR_PARK_IDS

# Entertainment Venues
mousetools.ids.WDW_EV_IDS
mousetools.ids.DLR_EV_IDS

# Attractions
mousetools.ids.WDW_ATTRACTION_IDS
mousetools.ids.DLR_ATTRACTION_IDS

# Entertainments
mousetools.ids.WDW_ENTERTAINMENT_IDS
mousetools.ids.DLR_ENTERTAINMENT_IDS

```

For more documentation go to the [wiki](https://github.com/scaratozzolo/MouseTools/wiki) or run the following command from a termainal:
```Bash
python -m pydoc mousetools
```


I created this project to help with another project found [here](https://github.com/scaratozzolo/WDWWaits). Some parts of the wrapper were created with that in mind.

If you notice any issues please open a new issue with a "bug" label. Furthermore, if you have any feature requests, open a new issue with a "feature request" label.

This package uses the [ThemeParks.wiki API](https://api.themeparks.wiki/). 

### License
This project is distributed under the MIT license. For more information see [LICENSE](https://github.com/scaratozzolo/MouseTools/blob/master/LICENSE)

https://github.com/scaratozzolo/MouseTools

### Disclaimer
This project is in no way affiliated with The Walt Disney Company and all use of Disney Services is subject to the [Disney Terms of Use](https://disneytermsofuse.com/).
