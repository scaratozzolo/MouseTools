import requests
import json
import sys
from datetime import datetime, timedelta
from auth import Authenticaton, getHeaders


park_ids = {'Magic Kingdom Park':'80007944','Epcot':'80007838',"Disney's Animal Kingdom Theme Park":'80007823',"Disney's Hollywood Studios":'80007998'}


def getParkData(id = None, park_name = None):
    """
    Gets all park data available and returns it in json.
    id and park_value are both optional, but you must pass at least one of them. The argument must be a string.
    """
    try:

        if id == None and park_name == None:
            raise ValueError
        elif id != None and type(id) != str:
            raise TypeError
        elif park_name != None and type(park_name) != str:
            raise TypeError


        if park_name != None:
            id = park_ids[park_name]

        found = False
        for park in park_ids:
            if id == park_ids[park]:
                found = True
                break
        if found == False:
            raise KeyError


    except KeyError:
        print('That park or ID is not available. Current options are:')
        for park in park_ids:
            print('{}:{}'.format(park, park_ids[park]))
        sys.exit()
    except ValueError:
        print('Function expects an id value or park_name value. Must be passed as string.\n Usage: getParkData(id = None, park_name = None)')
        sys.exit()
    except TypeError:
        print('Function getParkData expects string argument.')
        sys.exit()

    s = requests.get("https://api.wdpro.disney.go.com/facility-service/theme-parks/{}".format(id), headers=getHeaders())
    data = json.loads(s.content)

    return data


def getLinks(id = None, park_name = None):
    """
    Gets all the available links that reference other park data. Returns the links in json.

    Links gathered:
    - busStops
    - waitTimes
    - characterAppearances
    - standardTicketProduct
    - entertainments
    - scheduleMax
    - trainStations
    - schedule
    - ancestorResortArea
    - ancestorThemePark
    - self
    - boatLaunches
    - ancestorDestination
    - monorailStations
    """

    try:

        if id == None and park_name == None:
            raise ValueError
        elif id != None and type(id) != str:
            raise TypeError
        elif park_name != None and type(park_name) != str:
            raise TypeError


        if park_name != None:
            id = park_ids[park_name]

        found = False
        for park in park_ids:
            if id == park_ids[park]:
                found = True
                break
        if found == False:
            raise KeyError


    except KeyError:
        print('That park or ID is not available. Current options are:')
        for park in park_ids:
            print('{}:{}'.format(park, park_ids[park]))
        sys.exit()
    except ValueError:
        print('Function expects an id value or park_name value. Must be passed as string.\n Usage: getLinks(id = None, park_name = None)')
        sys.exit()
    except TypeError:
        print('Function getLinks expects string argument.')
        sys.exit()

    links = {}
    data = getParkData(id)

    for link in data['links']:
        links[link] = data['links'][link]['href']

    links = json.dumps(links)
    return links

print(getLinks('80007944'))
