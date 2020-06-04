import requests
import json
import sys
from datetime import datetime, timedelta
from .auth import getHeaders
from .attractions import Attraction
from .entertainments import Entertainment
from .facilities import Facility


class Character(object):

    def __init__(self, id = ''):
        """
        Constructor Function
        Gets all character data available and stores various elements into variables.
        ID must be a string
        """

        try:
            #Making sure id and character_name are not None, are strings, and exist
            if id == '':
                raise ValueError
            elif id != None and type(id) != str:
                raise TypeError


            self.__id = id

            s = requests.get("https://api.wdpro.disney.go.com/facility-service/characters/{}".format(self.__id), headers=getHeaders())
            self.__data = json.loads(s.content)

            self.__character_name = self.__data['name']

        except ValueError:
            print('Character object expects an id value. Must be passed as string.\n Usage: Character(id)')
            sys.exit()
        except TypeError:
            print('Character object expects a string argument.')
            sys.exit()
        except Exception:
            print('That character or ID is not available.')
            print('Full list of possible characters and their ID\'s can be found here: https://scaratozzolo.github.io/MouseTools/characters.txt')
            sys.exit()



    def get_name(self):
        """
        Returns the name of the Character
        """
        return self.__character_name

    def get_id(self):
        """
        Returns the ID of the character
        """
        return self.__id

    def check_related_locations(self):
        """
        Returns true if it has related locations, false if none
        """
        try:
            check = self.__data['relatedLocations']
            return True
        except:
            return False

    def get_related_locations(self):
        """
        Gets the locations the character is realted to. Alice:90003819
        """
        locs = []
        try:
            if self.check_related_locations():
                for loc in self.__data['relatedLocations']['primaryLocations']:
                    type = loc['facilityType']
                    loc_id = loc['links']['self']['href'].split('/')[-1]

                    if type == 'Attraction':
                        locs.append(Attraction(loc_id))
                    elif type == 'Facility':
                        locs.append(Facility(loc_id))
                    else:
                        print('no class for {} at this time'.format(type))
            return locs
        except:
            return locs

    def get_associated_events(self):
        """
        Returns a list of Entertainment objects of events associated with the character.
        Will print an error if the ID does not exist anymore. Unfortunately Disney, lists some events that don't exist, and thus will throw the error
        when it tries to create the Entertainment object.
        """
        entertainments = []
        try:
            for entertainment in self.__data['associatedEvents']:
                try:
                    entertainments.append(Entertainment(entertainment['links']['self']['href'].split('/')[-1].split('?')[0]))
                except:
                    pass
            return entertainments
        except:
            return entertainments

    def __formatDate(self, num):
        """
        Formats month and day into proper format
        """
        if len(num) < 2:
            num = '0'+num
        return num

    def __str__(self):
        return 'Character object for {}'.format(self.__character_name)
