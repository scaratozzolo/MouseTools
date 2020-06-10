from .destinations import *
from .parks import *
from .entertainmentvenues import *
from .attractions import *
from .entertainments import *
from .characters import *
from .pointsofinterest import *

DESTINATION_IDS = [WDW_ID, DLR_ID]
wdw_dest = Destination(WDW_ID)
dlr_dest = Destination(DLR_ID)

WDW_PARK_IDS = wdw_dest.get_park_ids()
DLR_PARK_IDS = dlr_dest.get_park_ids()

WDW_EV_IDS = wdw_dest.get_entertainment_venue_ids()
DLR_EV_IDS = dlr_dest.get_entertainment_venue_ids()

WDW_ATTRACTION_IDS = wdw_dest.get_attraction_ids()
DLR_ATTRACTION_IDS = dlr_dest.get_attraction_ids()

WDW_ENTERTAINMENT_IDS = wdw_dest.get_entertainment_ids()
DLR_ENTERTAINMENT_IDS = dlr_dest.get_entertainment_ids()
