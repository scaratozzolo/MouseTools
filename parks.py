import requests
import json
import sys
from datetime import datetime, timedelta
from auth import Authentication, getHeaders


park_ids = {'Magic Kingdom Park':'80007944','Epcot':'80007838',"Disney's Animal Kingdom Theme Park":'80007823',"Disney's Hollywood Studios":'80007998'}

class Park(object):

    def __init__(self, id = None, park_name = None):
        """
        Constructor Function
        Gets all park data available and stores various elements into variables.
        id and park_value are both optional, but you must pass at least one of them. The argument must be a string.
        """

        try:
            """Making sure id and park_name are not null, are strings, and exist"""
            if id == None and park_name == None:
                raise ValueError
            elif id != None and type(id) != str:
                raise TypeError
            elif park_name != None and type(park_name) != str:
                raise TypeError


            if park_name != None:
                id = park_ids[park_name] #raises KeyError if park_name doesn't exist

            found = False
            for park in park_ids:
                if id == park_ids[park]:
                    self.__park_name = park
                    found = True
                    break
            if found == False:
                raise KeyError


        except KeyError:
            print('That park or ID is not available. Current options are:')
            for park in park_ids:
                print('{}:{}'.format(park, park_ids[park]))
            sys.exit()
        except ValueError:
            print('Park object expects an id value or park_name value. Must be passed as string.\n Usage: Park(id = None, park_name = None)')
            sys.exit()
        except TypeError:
            print('Park object expects a string argument.')
            sys.exit()

        self.__id = id

        s = requests.get("https://api.wdpro.disney.go.com/facility-service/theme-parks/{}".format(self.__id), headers=getHeaders())
        data = json.loads(s.content)

        self.__links = data['links']
        self.__long_id = data['id']
        self.__type = data['type']
        self.__content_type = data['contentType']
        self.__sub_type = data['subType']
        self.__advisories = data['advisories']
        self.__weblink = data['webLinks']['wdwDetail']['href']  #check if other parks have multiple


    def getLinks(self):
        """
        Gets all the available links that reference other park data. Returns the links in json.
        id and park_value are both optional, but you must pass at least one of them. The argument must be a string.

        Links gathered:
        - busStops
        - waitTimes
        - characterAppearances
        - standardTicketProduct
        - entertainments
        - scheduleMax
        - trainStations
        - schedule
        - ancestorResortArea
        - ancestorThemePark
        - self
        - boatLaunches
        - ancestorDestination
        - monorailStations
        """

        links = {}

        for link in self.__links:
            links[link] = data['links'][link]['href']

        links = json.dumps(links)

        return links

    def getTodayParkHours(self):
        """
        Gets the park hours and returns them as a datetime object
        """

        s = requests.get("https://api.wdpro.disney.go.com/facility-service/schedules/{}?days=1".format(self.__id), headers=getHeaders())
        data = json.loads(s.content)

        YEAR = str(datetime.today().year)
        MONTH, DAY = self.__formatDate(str(datetime.today().month), str(datetime.today().day))

        operating_hours_start = None
        operating_hours_end = None
        extra_hours_start = None
        extra_hours_end = None

        for i in range(len(data['schedules'])):
            if data['schedules'][i]['date'] == '{}-{}-{}'.format(YEAR, MONTH, DAY):
                if data['schedules'][i]['type'] == 'Operating':
                    operating_hours_start = datetime(int(YEAR), int(MONTH), int(DAY), int(data['schedules'][i]['startTime'][0:2]), int(data['schedules'][i]['startTime'][3:5]))
                    operating_hours_end = datetime(int(YEAR), int(MONTH), int(DAY), int(data['schedules'][i]['endTime'][0:2]), int(data['schedules'][i]['endTime'][3:5]))

                if data['schedules'][i]['type'] == 'Extra Magic Hours':
                    extra_hours_start = datetime(int(YEAR), int(MONTH), int(DAY), int(data['schedules'][i]['startTime'][0:2]), int(data['schedules'][i]['startTime'][3:5]))
                    extra_hours_end = datetime(int(YEAR), int(MONTH), int(DAY), int(data['schedules'][i]['endTime'][0:2]), int(data['schedules'][i]['endTime'][3:5]))

        return operating_hours_start, operating_hours_end, extra_hours_start, extra_hours_end

    def getParkAdvisories(self):
        """
        Gets all the advisories for the park and returns them in json: {id:advisory}. Make take some time because it has to go to every link for each advisory.
        """

        print('May take some time. {} advisories to parse.'.format(len(self.__advisories)))
        advisories = {}

        for i in range(len(self.__advisories)):
            s = requests.get(self.__advisories[i]['links']['self']['href'], headers=getHeaders())
            data = json.loads(s.content)
            advisories[data['id']] = data['name'].replace(u"\u2019", "'").replace(u"\u2013", "-")

        advisories = json.dumps(advisories)

        return advisories


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
        return 'Park object for {}'.format(self.park_name)

# park = Park('80007944')
# links = park.getParkData
# print(links['links'])
