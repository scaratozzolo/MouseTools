from .auth import couchbaseHeaders
import sqlite3
import requests
import json
import re


class DisneyDatabase:

    def __init__(self):
        self.db_name = "MouseTools.db"
        conn = sqlite3.connect(self.db_name)
        c = conn.cursor()

        self.create_last_sequence_table()
        self.create_sync_table()
        self.create_facilities_table()

        last_sequence = c.execute("""SELECT COUNT(value) FROM lastSequence""").fetchone()[0]
        if last_sequence != 0:
            self.sync_database()


        conn.close()

    def create_last_sequence_table(self):

        conn = sqlite3.connect(self.db_name)
        c = conn.cursor()

        c.execute("""CREATE TABLE IF NOT EXISTS lastSequence (channel TEXT PRIMARY KEY, value TEXT)""")

        conn.commit()
        conn.close()


    def create_facilities_table(self):

        conn = sqlite3.connect(self.db_name)
        c = conn.cursor()

        c.execute("""CREATE TABLE IF NOT EXISTS facilities (id TEXT PRIMARY KEY, name TEXT, entityType TEXt, couchbase_id TEXT, destination_code TEXT, park_id TEXT, resort_id TEXT, land_id TEXT, resort_area_id TEXT)""")

        conn.commit()
        conn.close()


    def create_sync_table(self):

        conn = sqlite3.connect(self.db_name)
        c = conn.cursor()

        c.execute("""CREATE TABLE IF NOT EXISTS sync (id TEXT PRIMARY KEY, rev TEXT, body TEXT, channel TEXT)""")

        conn.commit()
        conn.close()


    def channel_exists(self, channel):

        conn = sqlite3.connect(self.db_name)
        c = conn.cursor()

        facility_channel_exists = c.execute("""SELECT COUNT(value) FROM lastSequence WHERE channel = '{}'""".format(channel)).fetchone()[0]
        return facility_channel_exists != 0

        conn.commit()
        conn.close()

    def create_channel(self, channel):
        # wdw.facilities.1_0.en_us
        # dlr.facilities.1_0.en_us
        # wdw.facilitystatus.1_0
        # dlr.facilitystatus.1_0
        # wdw.calendar.1_0
        # dlr.calendar.1_0
        payload = {
            "channels": channel,
            "style": 'all_docs',
            "filter": 'sync_gateway/bychannel',
            "feed": 'normal',
            "heartbeat": 30000,
        }
        r = requests.post("https://realtime-sync-gw.wdprapps.disney.com/park-platform-pub/_changes?feed=normal&heartbeat=30000&style=all_docs&filter=sync_gateway%2Fbychannel", data=json.dumps(payload), headers=couchbaseHeaders())
        s = json.loads(r.text)

        conn = sqlite3.connect(self.db_name)
        c = conn.cursor()

        c.execute("""INSERT INTO lastSequence (channel, value) VALUES ('{}', '{}')""".format(channel, s['last_seq']))

        docs = []
        for i in s['results']:
            this = {}
            this['id'] = i['id']

            docs.append(this)

        # print('getting {} docs'.format(len(docs)))

        payload = {"docs": docs, "json":True}
        r = requests.post("https://realtime-sync-gw.wdprapps.disney.com/park-platform-pub/_bulk_get?revs=true&attachments=true", data=json.dumps(payload), headers=couchbaseHeaders())
        s = r.text

        cont_reg = re.compile("\w+-\w+:\s\w+\/\w+")
        s = re.sub(cont_reg, "", s)
        s = s.splitlines()
        for x in s:
            if x != '':
                try:
                    x = json.loads(x)
                    c.execute("""INSERT INTO sync (id, rev, body, channel) VALUES ('{}', '{}', '{}', '{}')""".format(x['_id'], x['_rev'], json.dumps(x), channel))

                    this['id'] = x['id'].split(';')[0]
                    this['name'] = x['name']
                    this['entityType'] = x['type']
                    this['cb_id'] = x['_id']
                    this['dest_code'] = x['_id'].split('.')[0]

                    try:
                        this['park_id'] = x['ancestorThemeParkId'].split(';')[0]
                    except:
                        this['park_id'] = '0'

                    try:
                        this['land_id'] = x['ancestorLandId'].split(';')[0]
                    except:
                        this['land_id'] = '0'

                    try:
                        this['resort_id'] = x['ancestorResortId'].split(';')[0]
                    except:
                        this['resort_id'] = '0'

                    try:
                        this['ra_id'] = x['ancestorResortAreaId'].split(';')[0]
                    except:
                        this['ra_id'] = '0'

                    c.execute("""INSERT INTO facilities (id, name, entityType, couchbase_id, destination_code, park_id, land_id, resort_id, resort_area_id) VALUES ('{}', '{}', '{}', '{}', '{}', '{}', '{}', '{}', '{}')""".format(this['id'], this['name'], this['entityType'], this['cb_id'], this['dest_code'], this['park_id'], this['land_id'], this['resort_id'], this['ra_id']))
                except Exception as e:
                    # print(e)
                    continue



        conn.commit()
        conn.close()

    def sync_database(self):

        conn = sqlite3.connect(self.db_name)
        c = conn.cursor()

        for row in c.execute("""SELECT * FROM lastSequence""").fetchall():
            payload = {
                "channels": row[0],
                "style": 'all_docs',
                "filter": 'sync_gateway/bychannel',
                "feed": 'normal',
                "heartbeat": 30000,
            }
            r = requests.post("https://realtime-sync-gw.wdprapps.disney.com/park-platform-pub/_changes?feed=normal&heartbeat=30000&style=all_docs&since={}&filter=sync_gateway%2Fbychannel".format(row[1]), data=json.dumps(payload), headers=couchbaseHeaders())
            s = json.loads(r.text)

            conn = sqlite3.connect(self.db_name)
            c = conn.cursor()

            c.execute("""INSERT OR REPLACE INTO lastSequence (channel, value) VALUES ('{}', '{}')""".format(row[0], s['last_seq']))

            docs = []
            for i in s['results']:
                this = {}
                this['id'] = i['id']

                docs.append(this)

            # print('updating {} docs'.format(len(docs)))

            payload = {"docs": docs, "json":True}
            r = requests.post("https://realtime-sync-gw.wdprapps.disney.com/park-platform-pub/_bulk_get?revs=true&attachments=true", data=json.dumps(payload), headers=couchbaseHeaders())
            s = r.text

            cont_reg = re.compile("\w+-\w+:\s\w+\/\w+")
            s = re.sub(cont_reg, "", s)
            s = s.splitlines()
            for x in s:
                if x != '':
                    try:
                        x = json.loads(x)
                        c.execute("""INSERT OR INTO sync (id, rev, body, channel) VALUES ('{}', '{}', '{}', '{}')""".format(x['_id'], x['_rev'], json.dumps(x), channel))

                        this['id'] = x['id'].split(';')[0]
                        this['name'] = x['name']
                        this['entityType'] = x['type']
                        this['cb_id'] = x['_id']
                        this['dest_code'] = x['_id'].split('.')[0]

                        try:
                            this['park_id'] = x['ancestorThemeParkId'].split(';')[0]
                        except:
                            this['park_id'] = '0'

                        try:
                            this['land_id'] = x['ancestorLandId'].split(';')[0]
                        except:
                            this['land_id'] = '0'

                        try:
                            this['resort_id'] = x['ancestorResortId'].split(';')[0]
                        except:
                            this['resort_id'] = '0'

                        try:
                            this['ra_id'] = x['ancestorResortAreaId'].split(';')[0]
                        except:
                            this['ra_id'] = '0'

                        c.execute("""INSERT OR INTO facilities (id, name, entityType, couchbase_id, destination_code, park_id, land_id, resort_id, resort_area_id) VALUES ('{}', '{}', '{}', '{}', '{}', '{}', '{}', '{}', '{}')""".format(this['id'], this['name'], this['entityType'], this['cb_id'], this['dest_code'], this['park_id'], this['land_id'], this['resort_id'], this['ra_id']))
                    except Exception as e:
                        # print(e)
                        continue


            conn.commit()
            conn.close()
