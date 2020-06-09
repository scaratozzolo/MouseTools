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

        error = True
        self.__data = requests.get("https://api.wdpro.disney.go.com/facility-service/characters/{}".format(id), headers=getHeaders()).json()
        try:
            if self.__data['id'] is not None:
                error = False
        except:
            pass

        if error:
            raise ValueError('That character is not available.')

        self.__id = id
        self.__character_name = self.__data['name']



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

    def get_links(self):
        """Returns a dictionary of related links"""
        return self.__data['links']

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
        Gets the locations the character is realted to.
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

    def get_related_location_ids(self):
        """
        Gets the locations the character is realted to as a list of tuples [(id, type)]
        """
        locs = []
        try:
            if self.check_related_locations():
                for loc in self.__data['relatedLocations']['primaryLocations']:
                    type = loc['facilityType']
                    loc_id = loc['links']['self']['href'].split('/')[-1]

                    locs.append((loc_id, type))

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

    def get_associated_event_ids(self):
        """
        Returns a list of Entertainment ids of events associated with the character.
        Will print an error if the ID does not exist anymore. Unfortunately Disney, lists some events that don't exist, and thus will throw the error
        when it tries to create the Entertainment object.
        """
        entertainments = []
        try:
            for entertainment in self.__data['associatedEvents']:
                try:
                    entertainments.append(entertainment['links']['self']['href'].split('/')[-1].split('?')[0])
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
