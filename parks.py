import requests
import json
import sys
from datetime import datetime, timedelta
from auth import getHeaders
from tqdm import tqdm


class Park(object):

    def __init__(self, id = ''):
        """
        Constructor Function
        Gets all park data available and stores various elements into variables.
        ID must be a string
        """

        try:
            #Making sure id and attraction_name are not None, are strings, and exist
            if id == '':
                raise ValueError
            elif id != None and type(id) != str:
                raise TypeError

            self.__id = id

            try:
                s = requests.get("https://api.wdpro.disney.go.com/global-pool-override-B/facility-service/theme-parks/{}".format(self.__id), headers=getHeaders())
                self.__data = json.loads(s.content)
                if self.__data['errors'] != []:
                    s = requests.get("https://api.wdpro.disney.go.com/global-pool-override-B/facility-service/water-parks/{}".format(self.__id), headers=getHeaders())
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


        except ValueError:
            print('Park object expects an id value. Must be passed as string.\n Usage: Park(id = None)')
            sys.exit()
        except TypeError:
            print('Park object expects a string argument.')
            sys.exit()
        except Exception:
            print('That park or ID is not available. ID = {}'.format(id))
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

    def getAttractionIDs(self):
        """
        Returns a list of all attraction IDs in the park
        There is a huge discrepancy between the number of attractions reported and the actual number (This is why it errors out so much).
        I suggest getting the attractions from the Destination class and sorting by Attraction.ancestorThemePark()
        """
        ids = []
        s = requests.get("https://api.wdpro.disney.go.com/facility-service/theme-parks/{}/wait-times".format(self.__id), headers=getHeaders())
        loaded = json.loads(s.content)

        for i in range(len(loaded['entries'])):
            ids.append(loaded['entries'][i]['id'].split(';')[0])
        return ids

    def getAttractions(self):
        """
        Returns a list of Attraction objects
        There is a huge discrepancy between the number of attractions reported and the actual number (This is why it errors out so much).
        I suggest getting the attractions from the Destination class and sorting by Attraction.ancestorThemePark()
        """
        from attractions import Attraction
        attractions = []

        data = self.getAttractionIDs()

        for attract in tqdm(data):
            try:
                attractions.append(Attraction(attract))
            except:
                pass
        return attractions

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

    def __formatDate(self, num):
        """
        Formats month and day into proper format
        """
        if len(num) < 2:
            num = '0'+num
        return num

    def __eq__(self, other):
        """
        Checks if two parks are equal
        """
        return self.__id == other.getParkID()

    def __str__(self):
        return 'Park object for {}'.format(self.__park_name)
