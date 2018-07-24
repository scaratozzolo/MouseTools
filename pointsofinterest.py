import requests
import json
import sys
from datetime import datetime, timedelta
from auth import getHeaders

class PointOfInterest(object):

    def __init__(self, id = ''):
        """
        Constructor Function
        Gets all points of interest data available and stores various elements into variables.
        ID must be a string.
        """

        try:

            if id == '':
                raise ValueError
            elif id != None and type(id) != str:
                raise TypeError

            self.__id = id

            s = requests.get("https://api.wdpro.disney.go.com/global-pool-override-B/facility-service/points-of-interest/{}".format(self.__id), headers=getHeaders())
            self.__data = json.loads(s.content)

            self.__point_of_interest_name = self.__data['name'].replace(u"\u2019", "'").replace(u"\u2013", "-").replace(u"\u2122", "").replace(u"\u2022", "-").replace(u"\u00ae", "").replace(u"\u2014", "-").replace(u"\u00a1", "").replace(u"\u00ee", "i").replace(u"\u25cf", " ").replace(u"\u00e9", "e").replace(u"\u00ad", "").replace(u"\u00a0", " ").replace(u"\u00e8", "e").replace(u"\u00eb", "e").replace(u"\u2026", "...").replace(u"\u00e4", "a").replace(u"\u2018", "'").replace(u"\u00ed", "i").replace(u"\u201c", '"').replace(u"\u201d", '"').strip()
            self.__type = self.__data['type']
            try:
                self.__coordinates = (self.__data["coordinates"]["Guest Entrance"]["gps"]["latitude"], self.__data["coordinates"]["Guest Entrance"]["gps"]["longitude"])
            except:
                self.__coordinates = None


        except ValueError:
            print('PointOfInterest object expects an id value. Must be passed as string.\n Usage: PointOfInterest(id)')
            sys.exit()
        except TypeError:
            print('PointOfInterest object expects a string argument.')
            sys.exit()
        except Exception:
            print('That point of interest or ID is not available. {}'.format(id))
            print('Full list of possible points of interest and their ID\'s can be found here: https://scaratozzolo.github.io/MouseTools/pointsofinterest.txt')
            sys.exit()

    def getPointOfInterestName(self):
        """
        Returns the name of the point of interest
        """
        return self.__point_of_interest_name

    def getPointOfInterestID(self):
        """
        Returns the ID of the point of interest
        """
        return self.__id

    def getPointOfInterestCoordinates(self):
        """
        Returns the coordinates for the Point of Interest
        """
        return self.__coordinates

    def getAncestorDestination(self):
        """
        Returns the Ancestor Destination of the point of interest
        """
        try:
            return self.__data['ancestorDestination']['links']['self']['title']
        except:
            return None
    def getAncestorResortArea(self):
        """
        Returns the Ancestor Resort Area for the point of interest
        """
        try:
            return self.__data['links']['ancestorResortArea']['title']
        except:
            return None

    def getAncestorThemePark(self):
        """
        Returns the Ancestor Theme Park for the point of interest
        """
        try:
            return self.__data['links']['ancestorThemePark']['title']
        except:
            return None
    def getAncestorLand(self):
        """
        Returns the Ancestor Land for the point of interest
        """
        try:
            return self.__data['links']['ancestorLand']['title']
        except:
            return None

    def __formatDate(self, num):
        """
        Formats month and day into proper format
        """
        if len(num) < 2:
            num = '0'+num
        return num

    def __str__(self):
        return 'PointOfInterest object for {}'.format(self.__point_of_interest_name)
