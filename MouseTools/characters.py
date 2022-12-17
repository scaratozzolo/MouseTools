import requests
import pytz
from datetime import datetime, timedelta
from .auth import get_headers
from .attractions import Attraction
from .entertainments import Entertainment
from .facilities import Facility
from .ids import WDW_ID, DLR_ID



class Character(object):

    def __init__(self, id = None):
        """
        Constructor Function
        Gets all character data available and stores various elements into variables.
        """

        error = True
        self.__data = requests.get("https://api.wdpro.disney.go.com/facility-service/characters/{}".format(id), headers=get_headers()).json()
        try:
            if self.__data['id'] is not None:
                error = False
        except:
            pass

        if error:
            raise ValueError('That character is not available. id: ' + str(id))

        self.__id = id
        self.__name = self.__data['name']
        self.__entityType = self.__data['type']
        try:
            self.__subType = self.__data['subType']
        except:
            self.__subType = None
        try:
            self.__anc_dest_id = self.__data['ancestorDestination']['id'].split(';')[0]
        except:
            self.__anc_dest_id = None

        try:
            self.__anc_park_id = self.__data['links']['ancestorThemePark']['href'].split('/')[-1].split('?')[0]
        except:
            try:
                self.__anc_park_id = self.__data['links']['ancestorWaterPark']['href'].split('/')[-1].split('?')[0]
            except:
                try:
                    self.__anc_park_id = self.__facilities_data['ancestorThemeParkId'].split(';')[0]
                except:
                    try:
                        self.__anc_park_id = self.__facilities_data['ancestorWaterParkId'].split(';')[0]
                    except:
                        self.__anc_park_id = None

        try:
            self.__anc_resort_id = self.__data['links']['ancestorResort']['href'].split('/')[-1].split('?')[0]
        except:
            try:
                self.__anc_resort_id = self.__facilities_data['ancestorResortId'].split(';')[0]
            except:
                self.__anc_resort_id = None

        try:
            self.__anc_land_id = self.__data['links']['ancestorLand']['href'].split('/')[-1].split('?')[0]
        except:
            try:
                self.__anc_land_id = self.__facilities_data['ancestorLandId'].split(';')[0]
            except:
                self.__anc_land_id = None

        try:
            self.__anc_ra_id = self.__data['links']['ancestorResortArea']['href'].split('/')[-1].split('?')[0]
        except:
            try:
                self.__anc_ra_id = self.__facilities_data['ancestorResortAreaId'].split(';')[0]
            except:
                self.__anc_ra_id = None

        try:
            self.__anc_ev_id = self.__data['links']['ancestorEntertainmentVenue']['href'].split('/')[-1].split('?')[0]
        except:
            try:
                self.__anc_ev_id = self.__facilities_data['ancestorEntertainmentVenueId'].split(';')[0]
            except:
                self.__anc_ev_id = None

        if self.__anc_dest_id == WDW_ID:
            self.__time_zone = pytz.timezone('US/Eastern')
        elif self.__anc_dest_id == DLR_ID:
            self.__time_zone = pytz.timezone('US/Pacific')
        else:
            self.__time_zone = pytz.timezone('US/UTC')


    def get_id(self):
        """Return object id"""
        return self.__id

    def get_name(self):
        """Return object name"""
        return self.__name

    def get_entityType(self):
        """Return object entityType"""
        return self.__entityType

    def get_subType(self):
        """Return object subType"""
        return self.__subType

    def get_ancestor_destination_id(self):
        """Return object ancestor destination id"""
        return self.__anc_dest_id

    def get_ancestor_park_id(self):
        """Return object ancestor theme or water park id"""
        return self.__anc_park_id

    def get_ancestor_resort_id(self):
        """Return object ancestor resort id"""
        return self.__anc_resort_id

    def get_ancestor_land_id(self):
        """Return object land id"""
        return self.__anc_land_id

    def get_ancestor_resort_area_id(self):
        """Return object resort area id"""
        return self.__anc_ra_id

    def get_ancestor_entertainment_venue_id(self):
        """Return object entertainment venue id"""
        return self.__anc_ev_id

    def get_time_zone(self):
        """Returns pytz timezone object"""
        return self.__time_zone

    def get_raw_data(self):
        """Returns the raw data from global-facility-service"""
        return self.__data

    def get_links(self):
        """Returns a dictionary of related links"""
        return self.__data['links']


    def check_related_locations(self):
        """
        Returns true if it has related locations, false if none
        """
        try:
            check = self.__data['relatedLocations']
            return True
        except:
            return False

    def get_related_locations(self):
        """
        Gets the locations the character is realted to.
        """
        locs = []
        try:
            if self.check_related_locations():
                for loc in self.__data['relatedLocations']['primaryLocations']:
                    type = loc['facilityType']
                    loc_id = loc['links']['self']['href'].split('/')[-1].split('?')[0]

                    if type == 'Attraction':
                        locs.append(Attraction(loc_id))
                    elif type == 'Facility':
                        locs.append(Facility(loc_id))
                    else:
                        print('no class for {} at this time'.format(type))
            return locs
        except:
            return locs

    def get_related_location_ids(self):
        """
        Gets the locations the character is realted to as a list of tuples [(id, type)]
        """
        locs = []
        try:
            if self.check_related_locations():
                for loc in self.__data['relatedLocations']['primaryLocations']:
                    type = loc['facilityType']
                    loc_id = loc['links']['self']['href'].split('/')[-1].split('?')[0]

                    locs.append((loc_id, type))

            return locs
        except:
            return locs

    def get_associated_events(self):
        """
        Returns a list of Entertainment objects of events associated with the character.
        Will print an error if the ID does not exist anymore. Unfortunately Disney, lists some events that don't exist, and thus will throw the error
        when it tries to create the Entertainment object.
        """
        entertainments = []
        try:
            for entertainment in self.__data['associatedEvents']:
                try:
                    entertainments.append(Entertainment(entertainment['links']['self']['href'].split('/')[-1].split('?')[0]))
                except:
                    pass
            return entertainments
        except:
            return entertainments

    def get_associated_event_ids(self):
        """
        Returns a list of Entertainment ids of events associated with the character.
        Will print an error if the ID does not exist anymore. Unfortunately Disney, lists some events that don't exist, and thus will throw the error
        when it tries to create the Entertainment object.
        """
        entertainments = []
        try:
            for entertainment in self.__data['associatedEvents']:
                try:
                    entertainments.append(entertainment['links']['self']['href'].split('/')[-1].split('?')[0])
                except:
                    pass
            return entertainments
        except:
            return entertainments

    def __formatDate(self, num):
        """
        Formats month and day into proper format
        """
        if len(num) < 2:
            num = '0'+num
        return num

    def __str__(self):
        return 'Character object for {}'.format(self.__name)
