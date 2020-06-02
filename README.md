# MouseTools

A Python wrapper for the Disney API. Data is pulled directly from Disney.

I created this project to help with another project found [here](https://github.com/scaratozzolo/WDWWaits). Some parts of the wrapper were created with that in mind.

Installation will take some time as the initial database is set up and created. There is a lot of data to load and parse so just be patient.

You can install using pip:
```bash
pip install MouseTools
```

This package supports Walt Disney World and Disneyland.

Example usage:
```python
import MouseTools

wdw_dest = MouseTools.Destination('wdw')
print(wdw_dest.get_attraction_ids())

dlr_dest = MouseTools.Destination('dlr')
print(dlr_dest.get_entertainment_ids())
```
