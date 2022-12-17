import requests
import pytz
from datetime import datetime, timedelta
from .auth import get_headers
from .ids import WDW_ID, DLR_ID


class PointOfInterest(object):

    def __init__(self, id = None):
        """
        Constructor Function
        Gets all points of interest data available and stores various elements into variables.
        """

        error = True
        self.__data = requests.get("https://api.wdpro.disney.go.com/global-pool-override-B/facility-service/points-of-interest/{}".format(id), headers=get_headers()).json()
        try:
            if self.__data['id'] is not None:
                error = False
        except:
            pass

        if error:
            raise ValueError('That point of interest is not available. id: ' + str(id))

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
                    self.__anc_park_id = self.__data['ancestorThemeParkId'].split(';')[0]
                except:
                    try:
                        self.__anc_park_id = self.__data['ancestorWaterParkId'].split(';')[0]
                    except:
                        self.__anc_park_id = None

        try:
            self.__anc_resort_id = self.__data['links']['ancestorResort']['href'].split('/')[-1].split('?')[0]
        except:
            try:
                self.__anc_resort_id = self.__data['ancestorResortId'].split(';')[0]
            except:
                self.__anc_resort_id = None

        try:
            self.__anc_land_id = self.__data['links']['ancestorLand']['href'].split('/')[-1].split('?')[0]
        except:
            try:
                self.__anc_land_id = self.__data['ancestorLandId'].split(';')[0]
            except:
                self.__anc_land_id = None

        try:
            self.__anc_ra_id = self.__data['links']['ancestorResortArea']['href'].split('/')[-1].split('?')[0]
        except:
            try:
                self.__anc_ra_id = self.__data['ancestorResortAreaId'].split(';')[0]
            except:
                self.__anc_ra_id = None

        try:
            self.__anc_ev_id = self.__data['links']['ancestorEntertainmentVenue']['href'].split('/')[-1].split('?')[0]
        except:
            try:
                self.__anc_ev_id = self.__data['ancestorEntertainmentVenueId'].split(';')[0]
            except:
                self.__anc_ev_id = None

        if self.__anc_dest_id == WDW_ID:
            self.__time_zone = pytz.timezone('US/Eastern')
        elif self.__anc_dest_id == DLR_ID:
            self.__time_zone = pytz.timezone('US/Pacific')
        else:
            self.__time_zone = pytz.utc



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

    def get_links(self):
        """Returns a dictionary of related links"""
        return self.__data['links']

    def get_time_zone(self):
        """Returns pytz timezone object"""
        return self.__time_zone

    def get_raw_data(self):
        """Returns the raw data from global-facility-service"""
        return self.__data

    def get_coordinates(self):
        """Returns the object's latitude and longitude"""
        try:
            return self.__data['coordinates']['Guest Entrance']['gps']
        except:
            return None

    def get_description(self):
        """Returns the object's description"""
        facility_data = self.__data
        if facility_data is None:
            return None
        else:
            try:
                return facility_data['descriptions']['shortDescription']['sections']['body']
            except:
                return None

    def get_media(self):
        """Returns a dictionary of dictionaries of media relating to the entity"""
        facility_data = self.__data
        if facility_data is None:
            return None
        else:
            return facility_data['media']

    def admission_required(self):
        """Returns boolean of admission required"""
        return self.__data['admissionRequired']

    def __formatDate(self, num):
        """
        Formats month and day into proper format
        """
        if len(num) < 2:
            num = '0'+num
        return num

    def __str__(self):
        return 'PointOfInterest object for {}'.format(self.__name)
