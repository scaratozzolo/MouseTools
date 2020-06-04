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
            error = False
            self.__data = requests.get("https://api.wdpro.disney.go.com/facility-service/characters/{}".format(id), headers=getHeaders()).json()
            try:
                if len(self.__data['errors']) > 0:
                    error = True
            except:
                pass

            if error:
                raise ValueError()

            self.__id = id
            self.__character_name = self.__data['name']

        except Exception as e:
            # print(e)
            print('That character is not available.')
            sys.exit()


    def get_possible_ids(self):
        """Returns a list of possible ids of this entityType"""
        ids = []

        data = requests.get("https://api.wdpro.disney.go.com/facility-service/characters", headers=getHeaders()).json()

        for entry in data['entries']:
            try:
                ids.append(entry['links']['self']['href'].split('/')[-1].split('?')[0])
            except:
                pass

        return ids

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
