import requests
import json
import sys
from datetime import datetime, timedelta
from auth import getHeaders
from attractions import Attraction
from entertainments import Entertainment

character_ids = json.loads(requests.get("https://scaratozzolo.github.io/MouseTools/character_ids.json").content)

class Character(object):

    def __init__(self, id = None, character_name = None):
        """
        Constructor Function
        Gets all character data available and stores various elements into variables.
        id and character_name are both optional, but you must pass at least one of them. The argument must be a string.
        """

        try:
            #Making sure id and character_name are not None, are strings, and exist
            if id == None and character_name == None:
                raise ValueError
            elif id != None and type(id) != str:
                raise TypeError
            elif character_name != None and type(character_name) != str:
                raise TypeError


            if character_name != None:
                id = character_ids[character_name] #raises KeyError if character_name doesn't exist

            found = False
            for character in character_ids:
                if id == character_ids[character]:
                    self.__character_name = character
                    found = True
                    break
            if found == False:
                raise KeyError


        except KeyError:
            print('That character or ID is not available.')
            print('Full list of characters and their ID\'s can be found here: https://scaratozzolo.github.io/MouseTools/characters.txt')
            sys.exit()
        except ValueError:
            print('Character object expects an id value or character_name value. Must be passed as string.\n Usage: Character(id = None, character_name = None)')
            sys.exit()
        except TypeError:
            print('Character object expects a string argument.')
            sys.exit()

        self.__id = id

        s = requests.get("https://api.wdpro.disney.go.com/facility-service/characters/{}".format(self.__id), headers=getHeaders())
        self.__data = json.loads(s.content)

    def getCharacterName(self):
        """
        Returns the name of the Character
        """
        return self.__character_name

    def getRelatedLocationsType(self):
        """
        Returns the type of location related to the character
        """
        return self.__data['relatedLocations']['primaryLocations'][0]['facilityType']

    def getRelatedLocations(self):
        """
        Gets the locations the character is realted to
        """
        try:
            type = self.getRelatedLocationsType()
            loc_id = self.__data['relatedLocations']['primaryLocations'][0]['links']['self']['href'].split('/')[-1]

            if type == 'Attraction':
                return Attraction(loc_id)
            elif type == 'Facility':
                print('no class for facility at this time')
            else:
                print('no class for {} at this time'.format(type))

        except:
            return None

    def getAssociatedEvents(self):
        """
        Returns a list of Entertainment objects of events associated with the character
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
