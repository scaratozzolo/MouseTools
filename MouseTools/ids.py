from auth import get_headers
import requests
import json

WDW_ID = '80007798'
DLR_ID = '80008297'
DESTINATION_IDS = [WDW_ID, DLR_ID]

MK_ID = "80007944"
EPCOT_ID = "80007838"
HS_ID = "80007998"
AK_ID = "80007823"
DLP_ID = "330339"
CA_ID = "336894"
TL_ID = "80007981"
BB_ID = "80007834"
WDW_PARK_IDS = [MK_ID, EPCOT_ID, HS_ID, AK_ID, TL_ID, BB_ID]
DLR_PARK_IDS = [DLP_ID, CA_ID]

themeparkapi_ids = {MK_ID: "WaltDisneyWorldMagicKingdom", EPCOT_ID: "WaltDisneyWorldEpcot", HS_ID: "WaltDisneyWorldHollywoodStudios",
                    AK_ID: "WaltDisneyWorldAnimalKingdom", DLP_ID: "DisneylandResortMagicKingdom", CA_ID: "DisneylandResortCaliforniaAdventure"}


def ids(dest, type):
    dest_data = requests.get("https://api.wdpro.disney.go.com/facility-service/destinations/{}".format(dest), headers=get_headers()).json()
    ids = []

    data = requests.get(dest_data['links'][type]['href'], headers=get_headers()).json()

    for enter in data['entries']:
        try:
            ids.append(enter['links']['self']['href'].split('/')[-1].split('?')[0])
        except:
            pass
    return ids

WDW_EV_IDS = ids(WDW_ID, "entertainmentVenues")
DLR_EV_IDS = ids(DLR_ID, "entertainmentVenues")

WDW_ATTRACTION_IDS = ids(WDW_ID, "attractions")
DLR_ATTRACTION_IDS = ids(DLR_ID, "attractions")

WDW_ENTERTAINMENT_IDS = ids(WDW_ID, "entertainments")
DLR_ENTERTAINMENT_IDS = ids(DLR_ID, "entertainments")
