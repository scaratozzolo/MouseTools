import requests
import json
import sys
from datetime import datetime, timedelta
from auth import getHeaders

all_attraction_ids = json.loads(requests.get("https://scaratozzolo.github.io/MouseTools/all_attraction_ids.json").content)
attraction_ids = all_attraction_ids['Attraction']
entertainment_ids = all_attraction_ids['Entertainment']


class Attraction(object):

    def __init__(self, id = None, attraction_name = None):
        """
        Constructor Function
        Gets all attraction data available and stores various elements into variables.
        id and attraction_name are both optional, but you must pass at least one of them. The argument must be a string.
        """

        try:
            """Making sure id and attraction_name are not None, are strings, and exist"""
            if id == None and attraction_name == None:
                raise ValueError
            elif id != None and type(id) != str:
                raise TypeError
            elif attraction_name != None and type(attraction_name) != str:
                raise TypeError


            if attraction_name != None:
                id = attraction_ids[attraction_name] #raises KeyError if attraction_name doesn't exist

            found = False
            for attraction in attraction_ids:
                if id == attraction_ids[attraction]:
                    self.__attraction_name = attraction
                    found = True
                    break
            if found == False:
                raise KeyError


        except KeyError:
            print('That attraction or ID is not available. Current options are:')
            print('Full list of attractions and their ID\'s can be found here: insert link')
            sys.exit()
        except ValueError:
            print('Attraction object expects an id value or attraction_name value. Must be passed as string.\n Usage: Attraction(id = None, attraction_name = None)')
            sys.exit()
        except TypeError:
            print('Attraction object expects a string argument.')
            sys.exit()



    def __str__(self):
        return 'Attraction object for {}'.format(self.__attraction_name)




class Entertainment(object):

    def __init__(self, id = None, entertainment_name = None):
        """
        Constructor Function
        Gets all entertainment data available and stores various elements into variables.
        id and entertainment_name are both optional, but you must pass at least one of them. The argument must be a string.
        """

        try:
            """Making sure id and entertainment_name are not None, are strings, and exist"""
            if id == None and entertainment_name == None:
                raise ValueError
            elif id != None and type(id) != str:
                raise TypeError
            elif entertainment_name != None and type(entertainment_name) != str:
                raise TypeError


            if entertainment_name != None:
                id = entertainment_ids[entertainment_name] #raises KeyError if entertainment_name doesn't exist

            found = False
            for entertainment in entertainment_ids:
                if id == entertainment_ids[entertainment]:
                    self.__entertainment_name = entertainment
                    found = True
                    break
            if found == False:
                raise KeyError


        except KeyError:
            print('That entertainment or ID is not available. Current options are:')
            print('Full list of entertainments and their ID\'s can be found here: insert link')
            sys.exit()
        except ValueError:
            print('Entertainment object expects an id value or entertainment_name value. Must be passed as string.\n Usage: Entertainment(id = None, entertainment_name = None)')
            sys.exit()
        except TypeError:
            print('Entertainment object expects a string argument.')
            sys.exit()



    def __str__(self):
        return 'Entertainment object for {}'.format(self.__entertainment_name)
