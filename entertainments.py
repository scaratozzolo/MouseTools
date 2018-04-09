import requests
import json
import sys
from datetime import datetime, timedelta
from auth import getHeaders
from pointsofinterest import PointOfInterest


class Entertainment(object):

    def __init__(self, id = ''):
        """
        Constructor Function
        Gets all entertainment data available and stores various elements into variables.
        ID must be a string.
        """

        try:

            if id == '':
                raise ValueError
            elif id != None and type(id) != str:
                raise TypeError

            self.__id = id

            s = requests.get("https://api.wdpro.disney.go.com/facility-service/entertainments/{}".format(self.__id), headers=getHeaders())
            self.__data = json.loads(s.content)

            self.__entertainment_name = self.__data['name'].replace(u"\u2019", "'").replace(u"\u2013", "-").replace(u"\u2122", "").replace(u"\u2022", "-").replace(u"\u00ae", "").replace(u"\u2014", "-").replace(u"\u00a1", "").replace(u"\u00ee", "i").strip()
            self.__type = self.__data['type']
            self.__subType = self.__data['subType']

        except ValueError:
            print('Entertainment object expects an id value. Must be passed as string.\n Usage: Entertainment(id = None)')
            sys.exit()
        except TypeError:
            print('Entertainment object expects a string argument.')
            sys.exit()
        except Exception:
            print('That entertainment or ID is not available. {}'.format(id))
            print('Full list of possible entertainments and their ID\'s can be found here: https://scaratozzolo.github.io/MouseTools/entertainments.txt')
            sys.exit()

    def getEntertainmentName(self):
        """
        Returns the name of the entertainment
        """
        return self.__entertainment_name

    def getEntertainmentID(self):
        """
        Returns the id of the entertainment
        """
        return self.__id

    def getEntertainmentSubType(self):
        """
        Returns the Entertainment Sub Type
        """
        return self.__subType

    def checkAssociatedCharacters(self):
        """
        Checks if an attracion has any associated characters
        """
        s = requests.get("https://api.wdpro.disney.go.com/global-pool-override-B/facility-service/associated-characters/{};entityType=Entertainment".format(self.__id), headers=getHeaders())
        data = json.loads(s.content)

        if data['total'] > 0:
            return True
        else:
            return False

    def getNumberAssociatedCharacters(self):
        """
        Gets the total number of characters associated with the attraction_name
        """
        s = requests.get("https://api.wdpro.disney.go.com/global-pool-override-B/facility-service/associated-characters/{};entityType=Entertainment".format(self.__id), headers=getHeaders())
        data = json.loads(s.content)

        return data['total']

    def getAssociatedCharacters(self):
        """
        Returns a list of associated characters IDs (maybe Character class in future)
        """
        charIDs = []

        s = requests.get("https://api.wdpro.disney.go.com/global-pool-override-B/facility-service/associated-characters/{};entityType=Entertainment".format(self.__id), headers=getHeaders())
        data = json.loads(s.content)

        for i in range(len(data['entries'])):
            charIDs.append(data['entries'][i]['links']['self']['href'].split('/')[-1])

        return charIDs

    def getEntertainmentStatus(self):
        """
        Returns the current status of the entertainment as reported by Disney
        """
        try:
            s = requests.get("https://api.wdpro.disney.go.com/facility-service/entertainments/{}/wait-times".format(self.__id), headers=getHeaders())
            data = json.loads(s.content)

            return data['waitTime']['status']
        except:
            return None

    def getEntertainmentWaitTime(self):
        """
        Returns the current wait time of the entertainment as reported by Disney, in minutes
        TODO: test all entertainment for a wait time

        """
        try:
            s = requests.get("https://api.wdpro.disney.go.com/facility-service/entertainments/{}/wait-times".format(self.__id), headers=getHeaders())
            data = json.loads(s.content)

            return data['waitTime']['postedWaitMinutes']
        except:
            return None

    def getEntertainmentWaitTimeMessage(self):
        """
        Returns the current roll up wait time message of the entertainment as reported by Disney
        """
        try:
            s = requests.get("https://api.wdpro.disney.go.com/facility-service/entertainments/{}/wait-times".format(self.__id), headers=getHeaders())
            data = json.loads(s.content)

            return data['waitTime']['rollUpWaitTimeMessage']
        except:
            return None

    def getStartDate(self):
        """
        Gets the start date of the entertainment and returns it as a datetime object. If there is no start date, returns None
        """
        date = self.__data['startDate']
        if date == "":
            return None

        date = date.split('-')
        return datetime(int(date[0]), int(date[1]), int(date[2]))

    def getEndDate(self):
        """
        Gets the start date of the entertainment and returns it as a datetime object. If there is no start date, returns None.
        """
        date = self.__data['endDate']
        if date == "":
            return None

        date = date.split('-')
        return datetime(int(date[0]), int(date[1]), int(date[2]))

    def getDuration(self):
        """
        Returns the string format of the duration of the entertainment as provided by Disney
        """
        return self.__data['duration']

    def getDurationMinutes(self):
        """
        Returns the duration of the entertainment in minutes as a float
        """
        dur = self.__data['duration'].split(':')
        return int(dur[0])*60 + int(dur[1]) + int(dur[2])/60

    def getDurationSeconds(self):
        """
        Returns the duration of the entertainment in seconds as an integer
        """
        dur = self.__data['duration'].split(':')
        return int(self.getDurationMinutes())*60

    def getEntertainmentFastPassAvailable(self):
        """
        Returns True if fast pass is available
        """
        bool = self.__data['fastPass']
        if bool == 'true':
            return True
        else:
            return False

    def getEntertainmentFastPassPlusAvailable(self):
        """
        Returns True if fast pass plus is available
        """
        bool = self.__data['fastPassPlus']
        if bool == 'true':
            return True
        else:
            return False

    def checkRelatedLocations(self):
        """
        Returns true if it has related locations, false if none
        """
        try:
            check = self.__data['relatedLocations']
            return True
        except:
            return False

    def getRelatedLocations(self):
        """
        Returns the related locations of the entertainment
        """
        locs = []
        if self.checkRelatedLocations():
            for loc in self.__data['relatedLocations']['primaryLocations']:
                type = loc['facilityType']
                loc_id = loc['links']['self']['href'].split('/')[-1]

                if type == 'point-of-interest':
                    locs.append(PointOfInterest(loc_id))
                else:
                    print('no class for {} at this time'.format(type))
        return locs


    def getAncestorDestination(self):
        """
        Returns the Ancestor Destination of the entertainment
        """
        return self.__data['ancestorDestination']['links']['self']['title']

    def getAncestorResortArea(self):
        """
        Returns the Ancestor Resort Area for the Entertainment
        """
        if self.checkRelatedLocations():
            s = requests.get(self.__data['relatedLocations']['primaryLocations'][0]['links']['self']['href'], headers=getHeaders())
            data = json.loads(s.content)

            return data['links']['ancestorResortArea']['title']
        else:
            return None

    def getAncestorThemePark(self):
        """
        Returns the Ancestor Theme Park for the Entertainment
        """
        if self.checkRelatedLocations():
            s = requests.get(self.__data['relatedLocations']['primaryLocations'][0]['links']['self']['href'], headers=getHeaders())
            data = json.loads(s.content)

            return data['links']['ancestorThemePark']['title']
        else:
            return None

    def getAncestorLand(self):
        """
        Returns the Ancestor Land for the Entertainment
        """
        if self.checkRelatedLocations():
            s = requests.get(self.__data['relatedLocations']['primaryLocations'][0]['links']['self']['href'], headers=getHeaders())
            data = json.loads(s.content)

            return data['links']['ancestorLand']['title']
        else:
            return None

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
        return 'Entertainment object for {}'.format(self.__entertainment_name)
