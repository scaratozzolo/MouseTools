import requests
import json
import sys
from datetime import datetime, timedelta
from auth import getHeaders


class Attraction(object):

    def __init__(self, id = ''):
        """
        Constructor Function
        Gets all attraction data available and stores various elements into variables.
        Must pass id as string
        """

        try:

            if id == '':
                raise ValueError
            elif id != None and type(id) != str:
                raise TypeError

            self.__id = id

            s = requests.get("https://api.wdpro.disney.go.com/facility-service/attractions/{}".format(self.__id), headers=getHeaders())
            self.__data = json.loads(s.content)

            self.__attraction_name = self.__data['name'].replace(u"\u2019", "'").replace(u"\u2013", "-").replace(u"\u2122", "").replace(u"\u2022", "-").replace(u"\u00ae", "").replace(u"\u2014", "-").replace(u"\u00a1", "").replace(u"\u00ee", "i").strip()
            self.__type = self.__data['type']

        except ValueError:
            print('Attraction object expects an id value. Must be passed as string.\n Usage: Attraction(id = None)')
            sys.exit()
        except TypeError:
            print('Attraction object expects a string argument.')
            sys.exit()
        except Exception:
            print('That attraction or ID is not available.')
            print('Full list of possible attractions and their ID\'s can be found here: https://scaratozzolo.github.io/MouseTools/attractions.txt')
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

    def getAncestorDestination(self):
        """
        Returns the ancestor destination of the attraction.
        """
        return self.__data['ancestorDestination']['links']['self']['title']

    def getAncestorThemePark(self):
        """
        Returns the ancestor theme park of the attraction.
        """
        return self.__data['links']['ancestorThemePark']['title']

    def getAncestorResortArea(self):
        """
        Returns the ancestor resort area of the attraction.
        """
        return self.__data['links']['ancestorResortArea']['title']

    def getAncestorLand(self):
        """
        Retuns the ancestor land of the attracion.
        """
        return self.__data['links']['ancestorLand']['title']

    def getTodayAttractionHours(self):
        """
        Gets the attraction hours and returns them as a datetime object.
        Returns the attraction hours in the following order: operating open, operating close, Extra Magic open, Extra Magic close.
        Extra Magic hours will return None if there are none for today.
        """

        YEAR = str(datetime.today().year)
        MONTH, DAY = self.__formatDate(str(datetime.today().month), str(datetime.today().day))

        s = requests.get("https://api.wdpro.disney.go.com/facility-service/schedules/{}?date={}-{}-{}".format(self.__id, YEAR, MONTH, DAY), headers=getHeaders())
        data = json.loads(s.content)

        operating_hours_start = None
        operating_hours_end = None
        extra_hours_start = None
        extra_hours_end = None

        try:
            for i in range(len(data['schedules'])):
                if data['schedules'][i]['type'] == 'Operating':
                    operating_hours_start = datetime(int(YEAR), int(MONTH), int(DAY), int(data['schedules'][i]['startTime'][0:2]), int(data['schedules'][i]['startTime'][3:5]))
                    operating_hours_end = datetime(int(YEAR), int(MONTH), int(DAY), int(data['schedules'][i]['endTime'][0:2]), int(data['schedules'][i]['endTime'][3:5]))

                if data['schedules'][i]['type'] == 'Extra Magic Hours':
                    extra_hours_start = datetime(int(YEAR), int(MONTH), int(DAY), int(data['schedules'][i]['startTime'][0:2]), int(data['schedules'][i]['startTime'][3:5]))
                    extra_hours_end = datetime(int(YEAR), int(MONTH), int(DAY), int(data['schedules'][i]['endTime'][0:2]), int(data['schedules'][i]['endTime'][3:5]))
        except KeyError:
            pass
        return operating_hours_start, operating_hours_end, extra_hours_start, extra_hours_end

    def getAttractionHours(self, year, month, day):
        """
        Gets the attraction hours on a specific day and returns them as a datetime object.
        Returns the attraction hours in the following order: operating open, operating close, Extra Magic open, Extra Magic close.
        Extra Magic hours will return None if there are none for today.

        If all hours are None then Disney has no hours for that day.

        year = int yyyy
        month = int mm
        day = int dd
        """

        YEAR = str(year)
        MONTH, DAY = self.__formatDate(str(month), str(day))

        s = requests.get("https://api.wdpro.disney.go.com/facility-service/schedules/{}?date={}-{}-{}".format(self.__id, YEAR, MONTH, DAY), headers=getHeaders())
        data = json.loads(s.content)

        operating_hours_start = None
        operating_hours_end = None
        extra_hours_start = None
        extra_hours_end = None

        try:
            for i in range(len(data['schedules'])):
                if data['schedules'][i]['type'] == 'Operating':
                    operating_hours_start = datetime(int(YEAR), int(MONTH), int(DAY), int(data['schedules'][i]['startTime'][0:2]), int(data['schedules'][i]['startTime'][3:5]))
                    operating_hours_end = datetime(int(YEAR), int(MONTH), int(DAY), int(data['schedules'][i]['endTime'][0:2]), int(data['schedules'][i]['endTime'][3:5]))

                if data['schedules'][i]['type'] == 'Extra Magic Hours':
                    extra_hours_start = datetime(int(YEAR), int(MONTH), int(DAY), int(data['schedules'][i]['startTime'][0:2]), int(data['schedules'][i]['startTime'][3:5]))
                    extra_hours_end = datetime(int(YEAR), int(MONTH), int(DAY), int(data['schedules'][i]['endTime'][0:2]), int(data['schedules'][i]['endTime'][3:5]))
        except KeyError:
            pass
        return operating_hours_start, operating_hours_end, extra_hours_start, extra_hours_end

    def getAttractionStatus(self):
        """
        Returns the current status of the attraction as reported by Disney
        """
        s = requests.get("https://api.wdpro.disney.go.com/facility-service/attractions/{}/wait-times".format(self.__id), headers=getHeaders())
        data = json.loads(s.content)

        return data['waitTime']['status']

    def getAttractionWaitTime(self):
        """
        Returns the current wait time of the attraction as reported by Disney, in minutes
        TODO: test all attractions for a wait time

        """
        s = requests.get("https://api.wdpro.disney.go.com/facility-service/attractions/{}/wait-times".format(self.__id), headers=getHeaders())
        data = json.loads(s.content)

        return data['waitTime']['postedWaitMinutes']

    def getAttractionWaitTimeMessage(self):
        """
        Returns the current roll up wait time message of the attraction as reported by Disney
        """
        s = requests.get("https://api.wdpro.disney.go.com/facility-service/attractions/{}/wait-times".format(self.__id), headers=getHeaders())
        data = json.loads(s.content)

        return data['waitTime']['rollUpWaitTimeMessage']

    def getAttractionFastPassAvailable(self):
        """
        Returns boolean of whether fast pass is available
        """
        s = requests.get("https://api.wdpro.disney.go.com/facility-service/attractions/{}/wait-times".format(self.__id), headers=getHeaders())
        data = json.loads(s.content)

        if data['waitTime']['fastPass']['available'] == 'true':
            return True
        else:
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
        Returns a list of associated characters IDs (maybe Character class in future)
        """
        charIDs = []

        s = requests.get("https://api.wdpro.disney.go.com/global-pool-override-B/facility-service/associated-characters/{};entityType=Attraction".format(self.__id), headers=getHeaders())
        data = json.loads(s.content)

        for i in range(len(data['entries'])):
            charIDs.append(data['entries'][i]['links']['self']['href'].split('/')[-1])

        return charIDs


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
        return 'Attraction object for {}'.format(self.__attraction_name)
