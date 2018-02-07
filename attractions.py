import requests
import json
import sys
from datetime import datetime, timedelta
from auth import getHeaders

all_attraction_ids = json.loads(requests.get("https://scaratozzolo.github.io/MouseTools/all_attraction_ids.json").content)
attraction_ids = all_attraction_ids['Attraction']
entertainment_ids = all_attraction_ids['Entertainment']


class Attraction(object):

    def __init__(self, id = None, attraction_name = None):
        """
        Constructor Function
        Gets all attraction data available and stores various elements into variables.
        id and attraction_name are both optional, but you must pass at least one of them. The argument must be a string.
        """

        try:
            #Making sure id and attraction_name are not None, are strings, and exist
            if id == None and attraction_name == None:
                raise ValueError
            elif id != None and type(id) != str:
                raise TypeError
            elif attraction_name != None and type(attraction_name) != str:
                raise TypeError


            if attraction_name != None:
                id = attraction_ids[attraction_name] #raises KeyError if attraction_name doesn't exist

            found = False
            for attraction in attraction_ids:
                if id == attraction_ids[attraction]:
                    self.__attraction_name = attraction
                    found = True
                    break
            if found == False:
                raise KeyError


        except KeyError:
            print('That attraction or ID is not available. Current options are:')
            print('Full list of attractions and their ID\'s can be found here: https://scaratozzolo.github.io/MouseTools/attractions.txt')
            sys.exit()
        except ValueError:
            print('Attraction object expects an id value or attraction_name value. Must be passed as string.\n Usage: Attraction(id = None, attraction_name = None)')
            sys.exit()
        except TypeError:
            print('Attraction object expects a string argument.')
            sys.exit()

        self.__id = id

        s = requests.get("https://api.wdpro.disney.go.com/facility-service/attractions/{}".format(self.__id), headers=getHeaders())
        self.__data = json.loads(s.content)

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

    #associated characters research

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




class Entertainment(object):

    def __init__(self, id = None, entertainment_name = None):
        """
        Constructor Function
        Gets all entertainment data available and stores various elements into variables.
        id and entertainment_name are both optional, but you must pass at least one of them. The argument must be a string.
        """

        try:
            """Making sure id and entertainment_name are not None, are strings, and exist"""
            if id == None and entertainment_name == None:
                raise ValueError
            elif id != None and type(id) != str:
                raise TypeError
            elif entertainment_name != None and type(entertainment_name) != str:
                raise TypeError


            if entertainment_name != None:
                id = entertainment_ids[entertainment_name] #raises KeyError if entertainment_name doesn't exist

            found = False
            for entertainment in entertainment_ids:
                if id == entertainment_ids[entertainment]:
                    self.__entertainment_name = entertainment
                    found = True
                    break
            if found == False:
                raise KeyError


        except KeyError:
            print('That entertainment or ID is not available. Current options are:')
            print('Full list of entertainments and their ID\'s can be found here: https://scaratozzolo.github.io/MouseTools/entertainments.txt')
            sys.exit()
        except ValueError:
            print('Entertainment object expects an id value or entertainment_name value. Must be passed as string.\n Usage: Entertainment(id = None, entertainment_name = None)')
            sys.exit()
        except TypeError:
            print('Entertainment object expects a string argument.')
            sys.exit()



    def __str__(self):
        return 'Entertainment object for {}'.format(self.__entertainment_name)
