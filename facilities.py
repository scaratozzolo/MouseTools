import requests
import json
import sys
from datetime import datetime, timedelta
from auth import getHeaders


class Facility(object):

    def __init__(self, id = None):
        """
        Constructor Function
        Gets all facility data available and stores various elements into variables.
        ID must be a string
        """

        try:

            if id == None or id == '':
                raise ValueError
            elif id != None and type(id) != str:
                raise TypeError

            self.__id = id

            s = requests.get("https://api.wdpro.disney.go.com/facility-service/facilities/{}".format(self.__id), headers=getHeaders())
            self.__data = json.loads(s.content)

            self.__facility_name = self.__data['name'].replace(u"\u2019", "'").replace(u"\u2013", "-").replace(u"\u2122", "").replace(u"\u2022", "-").replace(u"\u00ae", "").replace(u"\u2014", "-").replace(u"\u00a1", "").replace(u"\u00ee", "i").strip()
            self.__subType = self.__data['subType']

        except ValueError:
            print('Facility object expects an id value. Must be passed as string.\n Usage: Facility(id = None)')
            sys.exit()
        except TypeError:
            print('Facility object expects a string argument.')
            sys.exit()
        except Exception:
            print('That facility or ID is not available.')
            print('Full list of possible facilities and their ID\'s can be found here: https://scaratozzolo.github.io/MouseTools/facility.txt')
            sys.exit()


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
