import requests
import json
import sys
from datetime import datetime, timedelta
from auth import getHeaders

facility_ids = json.loads(requests.get("https://scaratozzolo.github.io/MouseTools/facility_ids.json").content)

class Facility(object):

    def __init__(self, id = None, facility_name = None):
        """
        Constructor Function
        Gets all facility data available and stores various elements into variables.
        id and facility_name are both optional, but you must pass at least one of them. The argument must be a string.
        """

        try:
            #Making sure id and facility_name are not None, are strings, and exist
            if id == None and facility_name == None:
                raise ValueError
            elif id != None and type(id) != str:
                raise TypeError
            elif facility_name != None and type(facility_name) != str:
                raise TypeError


            if facility_name != None:
                id = facility_ids[facility_name] #raises KeyError if facility_name doesn't exist

            found = False
            for facility in facility_ids:
                if id == facility_ids[facility]:
                    self.__facility_name = facility
                    found = True
                    break
            if found == False:
                raise KeyError


        except KeyError:
            print('That facility or ID is not available.')
            print('Full list of facilities and their ID\'s can be found here: https://scaratozzolo.github.io/MouseTools/facility.txt')
            sys.exit()
        except ValueError:
            print('Facility object expects an id value or facility_name value. Must be passed as string.\n Usage: Facility(id = None, facility_name = None)')
            sys.exit()
        except TypeError:
            print('Facility object expects a string argument.')
            sys.exit()

        self.__id = id

        s = requests.get("https://api.wdpro.disney.go.com/facility-service/facilities/{}".format(self.__id), headers=getHeaders())
        self.__data = json.loads(s.content)
        self.__subType = self.__data['subType']

    def getFacilityName(self):
        """
        Returns the name of the facility
        """
        return self.__facility_name

    def getFacilityID(self):
        """
        Returns the id of the facility
        """
        return self.__id

    def getFacilitySubType(self):
        """
        Returns the facility sub type.
        """
        return self.__subType

    def getAncestorResortArea(self):
        """
        Returns ancestor resort area
        """
        return self.__data['links']['ancestorResortArea']['title']

    def getAncestorThemePark(self):
        """
        Returns ancestor theme park
        """
        return self.__data['links']['ancestorThemePark']['title']

    def getAncestorLand(self):
        """
        Returns ancestor land
        """
        return self.__data['links']['ancestorLand']['title']

    def getAncestorDestination(self):
        """
        Returns ancestor destination
        """
        return self.__data['links']['ancestorDestination']['title']

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
        return 'Facility object for {}'.format(self.__facility_name)
