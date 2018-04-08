import requests
import json
import sys
from datetime import datetime, timedelta
from auth import getHeaders
from attractions import Attraction
from entertainments import Entertainment
from facilities import Facility


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

            self.__character_name = self.__data['name'].replace(u"\u2019", "'").replace(u"\u2013", "-").replace(u"\u2122", "").replace(u"\u2022", "-").replace(u"\u00ae", "").replace(u"\u2014", "-").replace(u"\u00a1", "").replace(u"\u00ee", "i").strip()

        except ValueError:
            print('Character object expects an id value. Must be passed as string.\n Usage: Character(id = None)')
            sys.exit()
        except TypeError:
            print('Character object expects a string argument.')
            sys.exit()
        except Exception:
            print('That character or ID is not available.')
            print('Full list of possible characters and their ID\'s can be found here: https://scaratozzolo.github.io/MouseTools/characters.txt')
            sys.exit()



    def getCharacterName(self):
        """
        Returns the name of the Character
        """
        return self.__character_name

    def getCharacterID(self):
        """
        Returns the ID of the character
        """
        return self.__id

    def getRelatedLocationsType(self):
        """
        Returns the type of location related to the character
        """
        return self.__data['relatedLocations']['primaryLocations'][0]['facilityType']

    def getRelatedLocations(self):
        """
        Gets the locations the character is realted to. Alice:90003819
        """
        try:
            type = self.getRelatedLocationsType()
            loc_id = self.__data['relatedLocations']['primaryLocations'][0]['links']['self']['href'].split('/')[-1]

            if type == 'Attraction':
                return Attraction(loc_id)
            elif type == 'Facility':
                return Facility(loc_id)
            else:
                print('no class for {} at this time'.format(type))

        except:
            return None

    def getAssociatedEvents(self):
        """
        Returns a list of Entertainment objects of events associated with the character.
        Will print an error if the ID does not exist anymore. Unfortunately Disney, lists some events that don't exist, and thus will throw the error
        when it tries to create the Entertainment object.
        """
        entertainments = []

        for entertainment in self.__data['associatedEvents']:
            try:
                entertainments.append(Entertainment(entertainment['links']['self']['href'].split('/')[-1]))
            except:
                pass

        return entertainments

    def __formatDate(self, month, day):
        """
        Formats month and day into proper format
        """
        if len(month) < 2:
            month = '0'+month
        if len(day) < 2:
            day = '0'+day
        return month, day

    def __str__(self):
        return 'Character object for {}'.format(self.__character_name)
