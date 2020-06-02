import requests
import json
import sys
import sqlite3
from datetime import datetime, timedelta
from .auth import getHeaders
from .parks import Park
from .entertainments import Entertainment
from .attractions import Attraction
from .database import DisneyDatabase

WDW_ID = '80007798'
DLR_ID = '80008297'
DEST_IDS = [WDW_ID, DLR_ID]

WDW_CODE = 'wdw'
DLR_CODE = 'dlr'
DEST_CODES = [WDW_CODE, DLR_CODE]

class Destination(object):

    def __init__(self, dest_code = ''):
        """
        Constructor Function
        Gets all destination data available and stores various elements into variables.
        ID must be a string.
        """
        try:

            if dest_code == '':
                raise ValueError('Destination object expects an id value. Must be passed as string.\n Usage: Destination(id)')
            elif dest_code != None and type(dest_code) != str:
                raise TypeError('Destination object expects a string argument.')

            self.__dest_code = dest_code

            self.__db = DisneyDatabase()
            conn = sqlite3.connect(self.__db.db_name)
            c = conn.cursor()

            if not self.__db.channel_exists('{}.facilities.1_0.en_us'.format(self.__dest_code)):
                self.__db.create_channel('{}.facilities.1_0.en_us'.format(self.__dest_code))


            self.__id = c.execute("""SELECT id FROM facilities WHERE entityType = 'Destination' and destination_code = '{}'""".format(self.__dest_code))

            conn.commit()
            conn.close()

        except ValueError as e:
            print(e)
            sys.exit()
        except TypeError as e:
            print(e)
            sys.exit()
        except Exception as e:
            print(e)
            print('That destination or ID is not available. ID = {}\nFull list of possible destinations and their ID\'s can be found here: https://scaratozzolo.github.io/MouseTools/destinations.txt'.format(id))
            sys.exit()


    def get_destination_code(self):
        return self.__dest_code

    def get_id(self):
        return self.__id



    def __str__(self):
        return 'Destination object for {}'.format(self.__destination_name)
