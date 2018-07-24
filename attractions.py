import requests
import json
import sys
from datetime import datetime, timedelta
from auth import getHeaders
from parks import Park


class Attraction(object):

    def __init__(self, id = ''):
        """
        Constructor Function
        Gets all attraction data available and stores various elements into variables.
        Must pass id as string
        """

        try:

            if id == '':
                raise ValueError('Attraction object expects an id value. Must be passed as string.\n Usage: Attraction(id)')
            elif id != None and type(id) != str:
                raise TypeError('Attraction object expects a string argument.')

            self.__id = id

            s = requests.get("https://api.wdpro.disney.go.com/global-pool-override-B/facility-service/attractions/{}".format(self.__id), headers=getHeaders())
            self.__data = json.loads(s.content)

            self.__attraction_name = self.__data['name'].replace(u"\u2019", "'").replace(u"\u2013", "-").replace(u"\u2122", "").replace(u"\u2022", "-").replace(u"\u00ae", "").replace(u"\u2014", "-").replace(u"\u00a1", "").replace(u"\u00ee", "i").replace(u"\u25cf", " ").replace(u"\u00e9", "e").replace(u"\u00ad", "").replace(u"\u00a0", " ").replace(u"\u00e8", "e").replace(u"\u00eb", "e").replace(u"\u2026", "...").replace(u"\u00e4", "a").replace(u"\u2018", "'").replace(u"\u00ed", "i").replace(u"\u201c", '"').replace(u"\u201d", '"').strip()
            self.__type = self.__data['type']
            try:
                self.__coordinates = (self.__data["coordinates"]["Guest Entrance"]["gps"]["latitude"], self.__data["coordinates"]["Guest Entrance"]["gps"]["longitude"])
            except:
                self.__coordinates = None

        except ValueError as e:
            print(e)
            sys.exit()
        except TypeError as e:
            print(e)
            sys.exit()
        except Exception as e:
            print(e)
            print('That attraction or ID is not available. ID = {}\n Full list of possible attractions and their ID\'s can be found here: https://scaratozzolo.github.io/MouseTools/attractions.txt'.format(id))
            sys.exit()


    def getAttractionName(self):
        """
        Returns the name of the attraction
        """
        return self.__attraction_name

    def getAttractionID(self):
        """
        Returns the ID of the attraction
        """
        return self.__id

    def getType(self):
        """
        Returns the attraction type, which should just be "Attraction". But if you need it returned for whatever reason.
        """
        return self.__type

    def getAttractionCoordinates(self):
        """
        Returns the coordinates of the attracion
        """
        return self.__coordinates

    def getAncestorDestination(self):
        """
        Returns the ancestor destination of the attraction.
        """
        return self.__data['ancestorDestination']['links']['self']['title']

    def getAncestorThemeParkID(self):
        """
        Returns the ancestor theme park of the attraction.
        """
        try:
            return self.__data['links']['ancestorThemePark']['href'].split('/')[-1]
        except:
            try:
                self.__data['links']['ancestorWaterPark']['href'].split('/')[-1]
                return self.getAncestorWaterParkID()
            except:
                return None

    def getAncestorThemePark(self):
        """
        Returns the ancestor theme park of the attraction.
        """
        try:
            return Park(self.__data['links']['ancestorThemePark']['href'].split('/')[-1])
        except:
            try:
                self.__data['links']['ancestorWaterPark']['href'].split('/')[-1]
                return self.getAncestorWaterPark()
            except:
                return None

    def getAncestorWaterParkID(self):
        """
        Returns the ancestor theme park of the attraction.
        """
        try:
            return self.__data['links']['ancestorWaterPark']['href'].split('/')[-1]
        except:
            try:
                self.__data['links']['ancestorThemePark']['href'].split('/')[-1]
                return self.getAncestorThemeParkID()
            except:
                return None

    def getAncestorWaterPark(self):
        """
        Returns the ancestor water park of the attraction.
        """
        try:
            return Park(self.__data['links']['ancestorWaterPark']['href'].split('/')[-1])
        except:
            try:
                self.__data['links']['ancestorThemePark']['href'].split('/')[-1]
                return self.getAncestorThemePark()
            except:
                return None

    def getAncestorResortArea(self):
        """
        Returns the ancestor resort area of the attraction.
        """
        try:
            return self.__data['links']['ancestorResortArea']['title']
        except:
            return None

    def getAncestorLand(self):
        """
        Retuns the ancestor land of the attracion.
        """
        try:
            return self.__data['links']['ancestorLand']['title']
        except:
            return None

    def getTodayAttractionHours(self):
        """
        Gets the park hours and returns them as a datetime object.
        Returns the park hours in the following order: operating open, operating close, Extra Magic open, Extra Magic close.
        Extra Magic hours will return None if there are none for today.
        """

        DATE = datetime.today()
        s = requests.get("https://api.wdpro.disney.go.com/facility-service/schedules/{}?date={}-{}-{}".format(self.__id, DATE.year, self.__formatDate(str(DATE.month)), self.__formatDate(str(DATE.day))), headers=getHeaders())
        data = json.loads(s.content)

        operating_hours_start = None
        operating_hours_end = None
        extra_hours_start = None
        extra_hours_end = None

        try:
            for i in range(len(data['schedules'])):
                if data['schedules'][i]['type'] == 'Operating':
                    operating_hours_start = datetime(DATE.year, DATE.month, DATE.day, int(data['schedules'][i]['startTime'][0:2]), int(data['schedules'][i]['startTime'][3:5]))
                    if int(data['schedules'][i]['endTime'][0:2]) >= 0 and int(data['schedules'][i]['endTime'][0:2]) <= 7:
                        DATETEMP = DATE + timedelta(days=1)
                        operating_hours_end = datetime(DATETEMP.year, DATETEMP.month, DATETEMP.day, int(data['schedules'][i]['endTime'][0:2]), int(data['schedules'][i]['endTime'][3:5]))
                    else:
                        operating_hours_end = datetime(DATE.year, DATE.month, DATE.day, int(data['schedules'][i]['endTime'][0:2]), int(data['schedules'][i]['endTime'][3:5]))

                if data['schedules'][i]['type'] == 'Extra Magic Hours':
                    extra_hours_start = datetime(DATE.year, DATE.month, DATE.day, int(data['schedules'][i]['startTime'][0:2]), int(data['schedules'][i]['startTime'][3:5]))
                    if int(data['schedules'][i]['endTime'][0:2]) >= 0 and int(data['schedules'][i]['endTime'][0:2]) <= 7:
                        DATETEMP = DATE + timedelta(days=1)
                        extra_hours_end = datetime(DATETEMP.year, DATETEMP.month, DATETEMP.day, int(data['schedules'][i]['endTime'][0:2]), int(data['schedules'][i]['endTime'][3:5]))
                    else:
                        operating_hours_end = datetime(DATE.year, DATE.month, DATE.day, int(data['schedules'][i]['endTime'][0:2]), int(data['schedules'][i]['endTime'][3:5]))

        except KeyError:
            pass
        return operating_hours_start, operating_hours_end, extra_hours_start, extra_hours_end

    def getAttractionHours(self, year, month, day):
        """
        Gets the park hours on a specific day and returns them as a datetime object.
        Returns the park hours in the following order: operating open, operating close, Extra Magic open, Extra Magic close.
        Extra Magic hours will return None if there are none for today.

        If all hours are None then Disney has no hours for that day.

        year = int yyyy
        month = int mm
        day = int dd
        """

        DATE = datetime(year, month, day)
        s = requests.get("https://api.wdpro.disney.go.com/facility-service/schedules/{}?date={}-{}-{}".format(self.__id, DATE.year, self.__formatDate(str(DATE.month)), self.__formatDate(str(DATE.day))), headers=getHeaders())
        data = json.loads(s.content)

        operating_hours_start = None
        operating_hours_end = None
        extra_hours_start = None
        extra_hours_end = None

        try:
            for i in range(len(data['schedules'])):
                if data['schedules'][i]['type'] == 'Operating':
                    operating_hours_start = datetime(DATE.year, DATE.month, DATE.day, int(data['schedules'][i]['startTime'][0:2]), int(data['schedules'][i]['startTime'][3:5]))
                    if int(data['schedules'][i]['endTime'][0:2]) >= 0 and int(data['schedules'][i]['endTime'][0:2]) <= 7:
                        DATETEMP = DATE + timedelta(days=1)
                        operating_hours_end = datetime(DATETEMP.year, DATETEMP.month, DATETEMP.day, int(data['schedules'][i]['endTime'][0:2]), int(data['schedules'][i]['endTime'][3:5]))
                    else:
                        operating_hours_end = datetime(DATE.year, DATE.month, DATE.day, int(data['schedules'][i]['endTime'][0:2]), int(data['schedules'][i]['endTime'][3:5]))

                if data['schedules'][i]['type'] == 'Extra Magic Hours':
                    extra_hours_start = datetime(DATE.year, DATE.month, DATE.day, int(data['schedules'][i]['startTime'][0:2]), int(data['schedules'][i]['startTime'][3:5]))
                    if int(data['schedules'][i]['endTime'][0:2]) >= 0 and int(data['schedules'][i]['endTime'][0:2]) <= 7:
                        DATETEMP = DATE + timedelta(days=1)
                        extra_hours_end = datetime(DATETEMP.year, DATETEMP.month, DATETEMP.day, int(data['schedules'][i]['endTime'][0:2]), int(data['schedules'][i]['endTime'][3:5]))
                    else:
                        operating_hours_end = datetime(DATE.year, DATE.month, DATE.day, int(data['schedules'][i]['endTime'][0:2]), int(data['schedules'][i]['endTime'][3:5]))

        except KeyError:
            pass
        return operating_hours_start, operating_hours_end, extra_hours_start, extra_hours_end

    def checkForAttractionWaitTime(self):
        """
        Checks if the attraction has a wait. Returns True if it exists, False if it doesn't. Also returns the wait time json data.
        """
        self.waitTimeData = requests.get("https://api.wdpro.disney.go.com/facility-service/attractions/{}/wait-times".format(self.__id), headers=getHeaders()).json()
        # data = json.loads(s.content)
        try:
            check = self.waitTimeData['waitTime']['postedWaitMinutes']
            return True
        except:
            return False

    def getAttractionStatus(self):
        """
        Returns the current status of the attraction as reported by Disney
        """
        try:
            if self.checkForAttractionWaitTime():
                return self.waitTimeData['waitTime']['status']
            else:
                return None
        except:
            return None

    def getAttractionWaitTime(self):
        """
        Returns the current wait time of the attraction as reported by Disney, in minutes

        """
        try:
            if self.checkForAttractionWaitTime():
                return self.waitTimeData['waitTime']['postedWaitMinutes']
            else:
                return None
        except:
            return None

    def getAttractionWaitTimeFromData(self):
        """
        Returns the current wait time of the attraction as reported by Disney, in minutes, from self.waitTimeData
        In order to properly use this function, you must call self.checkForAttractionWaitTime() before calling this function.
        The idea is if you're creating a list of objects with wait times, you can parse over the list and not have to make another request to Disney to get the wait times.
        This function was created with WWDWaits in mind.
        """
        try:
            if self.waitTimeData != None:
                return self.waitTimeData['waitTime']['postedWaitMinutes']
            elif self.checkForAttractionWaitTime():
                return self.waitTimeData['waitTime']['postedWaitMinutes']
            else:
                return None
        except:
            return None

    def getAttractionWaitTimeMessage(self):
        """
        Returns the current roll up wait time message of the attraction as reported by Disney
        """
        try:
            if self.checkForAttractionWaitTime():
                return self.waitTimeData['waitTime']['rollUpWaitTimeMessage']
            else:
                return None
        except:
            return None

    def getAttractionFastPassAvailable(self):
        """
        Returns boolean of whether fast pass is available
        """
        try:
            if self.checkForAttractionWaitTime():
                if self.waitTimeData['waitTime']['fastPass']['available'] == 'true':
                    return True
                else:
                    return False
            else:
                return False
        except:
            return False

    def checkAssociatedCharacters(self):
        """
        Checks if an attracion has any associated characters
        """
        s = requests.get("https://api.wdpro.disney.go.com/global-pool-override-B/facility-service/associated-characters/{};entityType=Attraction".format(self.__id), headers=getHeaders())
        data = json.loads(s.content)

        if data['total'] > 0:
            return True
        else:
            return False

    def getNumberAssociatedCharacters(self):
        """
        Gets the total number of characters associated with the attraction_name
        """
        s = requests.get("https://api.wdpro.disney.go.com/global-pool-override-B/facility-service/associated-characters/{};entityType=Attraction".format(self.__id), headers=getHeaders())
        data = json.loads(s.content)

        return data['total']

    def getAssociatedCharacters(self):
        """
        Returns a list of associated character objects
        """
        from characters import Character
        chars = []
        s = requests.get("https://api.wdpro.disney.go.com/global-pool-override-B/facility-service/associated-characters/{};entityType=Attraction".format(self.__id), headers=getHeaders())
        data = json.loads(s.content)

        for i in range(len(data['entries'])):
            try:
                chars.append(Character(data['entries'][i]['links']['self']['href'].split('/')[-1]))
            except:
                pass
        return chars

    def getAssociatedCharacterIDs(self):
        """
        Returns a list of associated characters IDs
        """
        from characters import Character
        chars = []
        s = requests.get("https://api.wdpro.disney.go.com/global-pool-override-B/facility-service/associated-characters/{};entityType=Attraction".format(self.__id), headers=getHeaders())
        data = json.loads(s.content)

        for i in range(len(data['entries'])):
            try:
                chars.append(data['entries'][i]['links']['self']['href'].split('/')[-1])
            except:
                pass
        return chars

    def __formatDate(self, num):
        """
        Formats month and day into proper format
        """
        if len(num) < 2:
            num = '0'+num
        return num

    def __str__(self):
        return 'Attraction object for {}'.format(self.__attraction_name)
