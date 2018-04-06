import requests
import json
import sys
from datetime import datetime, timedelta
from auth import getHeaders


class Park(object):

    def __init__(self, id = None):
        """
        Constructor Function
        Gets all park data available and stores various elements into variables.
        ID must be a string
        """

        try:
            #Making sure id and attraction_name are not None, are strings, and exist
            if id == None or id == '':
                raise ValueError
            elif id != None and type(id) != str:
                raise TypeError

            self.__id = id
            try:
                s = requests.get("https://api.wdpro.disney.go.com/facility-service/theme-parks/{}".format(self.__id), headers=getHeaders())
                self.__data = json.loads(s.content)
                if self.__data['errors'] != []:
                    s = requests.get("https://api.wdpro.disney.go.com/facility-service/water-parks/{}".format(self.__id), headers=getHeaders())
                    self.__data = json.loads(s.content)
            except:
                pass

            self.__park_name = self.__data['name'].replace(u"\u2019", "'").replace(u"\u2013", "-").replace(u"\u2122", "").replace(u"\u2022", "-").replace(u"\u00ae", "").replace(u"\u2014", "-").replace(u"\u00a1", "").replace(u"\u00ee", "i").strip()

            links = {}
            for link in self.__data['links']:
                links[link] = self.__data['links'][link]['href']
            self.__links = json.dumps(links)

            self.__long_id = self.__data['id']      #id;entityType=
            self.__type = self.__data['type']
            self.__content_type = self.__data['contentType']
            self.__sub_type = self.__data['subType']
            #advisories may update even when everything else doesn't. maybe create a seperate request to the data to get updated advisories
            self.__advisories = self.__data['advisories']
            self.__weblink = self.__data['webLinks']['wdwDetail']['href']  #check if other parks have multiple. If they do create array or json


        except ValueError:
            print('Park object expects an id value. Must be passed as string.\n Usage: Park(id = None)')
            sys.exit()
        except TypeError:
            print('Park object expects a string argument.')
            sys.exit()
        except Exception:
            print('That park or ID is not available.')
            print('Full list of possible parks and their ID\'s can be found here: https://scaratozzolo.github.io/MouseTools/parks.txt')
            sys.exit()

    def getParkID(self):
        """
        Returns the ID of the park
        """
        return self.__id

    def getParkName(self):
        """
        Returns the true park name; the park name as referenced by Disney.
        """
        return self.__park_name

    def getTodayParkHours(self):
        """
        Gets the park hours and returns them as a datetime object.
        Returns the park hours in the following order: operating open, operating close, Extra Magic open, Extra Magic close.
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

    def getParkHours(self, year, month, day):
        """
        Gets the park hours on a specific day and returns them as a datetime object.
        Returns the park hours in the following order: operating open, operating close, Extra Magic open, Extra Magic close.
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


    def getParkAdvisories(self):
        """
        Gets all the advisories for the park and returns them in json: {id:advisory}.
        May take some time because it has to go to every link for each advisory.
        """

        print('May take some time. {} advisories to parse.'.format(len(self.__advisories)))
        advisories = {}

        for i in range(len(self.__advisories)):
            s = requests.get(self.__advisories[i]['links']['self']['href'], headers=getHeaders())
            data = json.loads(s.content)
            advisories[data['id']] = data['name'].replace(u"\u2019", "'").replace(u"\u2013", "-")

        advisories = json.dumps(advisories)

        return advisories

    def getCurrentWaitTimes(self):
        """
        Gets all current wait times for the park. Returns them in json {park:time in minutes}. May take some time as it goes through all attractions.
        """

        s = requests.get("https://api.wdpro.disney.go.com/facility-service/theme-parks/{}/wait-times".format(self.__id), headers=getHeaders())
        loaded_times = json.loads(s.content)

        times = {}
        for i in range(len(loaded_times['entries'])):
            if 'postedWaitMinutes' in loaded_times['entries'][i]['waitTime']:
                times[loaded_times['entries'][i]['name']] = loaded_times['entries'][i]['waitTime']['postedWaitMinutes']

        json_times = json.dumps(times)
        return json_times

    def getAncestorResortArea(self):
        """
        Returns ancestor resort area.
        """
        return self.__data['links']['ancestorResortArea']['title']

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
        return 'Park object for {}'.format(self.__park_name)
