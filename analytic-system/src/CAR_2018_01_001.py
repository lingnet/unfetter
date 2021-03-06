'''

This is a place holder until we get a better interaction with Unfetter Discover Analytic creating system.
'''

CAR_NUMBER = "CAR_2018_01_001"
CAR_NAME = "Reg.exe called from Command Shell"
CAR_DESCRIPTION = "Registry modifications are often essential in establishing persistence via known Windows mechanisms.Many legitimate modifications are done graphically via regedit.exe or by using the corresponding channels, or even calling the Registry APIs directly.  The built-in utility reg.exe provides a command-line interface to the registry, so that queries and modifications can be performed from a shell, such as cmd.exe. When a user is responsible for these actions, the parent of cmd.exe will likely be explorer.exe. Occasionally, power users and administrators write scripts that do this behavior as well, but likely from a different process tree. These background scripts must be learned so they can be tuned out accordingly."
ATTACK_TACTIC = "Defense Evasion, Persistence, Privilege Escalation"
CAR_URL = "https://??"
ES_INDEX = "sysmon_process-*"
ES_TYPE = "_doc"
ALERT_INDEX = "alert"
INDICATOR_ID = "indicator--7f506572-63a9-4176-b008-a3da322b28bd"

class CAR_2018_01_001():
    def __init__(self):

        self.car_data = dict(car_name=CAR_NAME,
                             car_number=CAR_NUMBER,
                             car_description=CAR_DESCRIPTION,
                             car_url=CAR_URL,
                             alert_index=ALERT_INDEX,
                             alert_type=CAR_NUMBER,
                             es_type=ES_TYPE,
                             indicator_id=INDICATOR_ID, es_index=ES_INDEX)

    def analyze(self, rdd, begin_timestamp, end_timestamp):
        end = end_timestamp.strftime("%Y-%m-%dT%H:%M:%SZ")
        begin = begin_timestamp.strftime("%Y-%m-%dT%H:%M:%SZ")

        # filter on process create
        print len(rdd.collect())
        rdd = rdd.filter(lambda item: (item[1]['data_model']['action'] == "create"))
        print len(rdd.collect())
        # Map in the CAR information and rename fields the analytic needs for ease of use
        # This needs to happen after the filter on process create, or some of the fields won't be there
        rdd = rdd.map(lambda item: (
            item[0],
            {'@timestamp': item[1]["@timestamp"],
             'car_id': CAR_NUMBER,
             'car_name': CAR_NAME,
             'car_description': CAR_DESCRIPTION,
             'attack_tactic': ATTACK_TACTIC,
             'car_url': CAR_URL,
             'event_code': item[1]["data_model"]["fields"]["event_code"],
             'exe': item[1]["data_model"]["fields"]["exe"],
             'parent_exe': item[1]["data_model"]["fields"]["parent_exe"],
             'utc_time': item[1]["data_model"]["fields"]["utc_time"],
             'command_line': item[1]["data_model"]["fields"]["command_line"],
             'pid': item[1]["data_model"]["fields"]["pid"],
             'ppid': item[1]["data_model"]["fields"]["ppid"],
             'hostname': item[1]["data_model"]["fields"]["hostname"],
             'process_guid': item[1]["data_model"]["fields"]["process_guid"],
             'parent_process_guid': item[1]["data_model"]["fields"]["parent_process_guid"],
             'action': item[1]["data_model"]["action"],
             'data_model': item[1]["data_model"]
             }))
        print len(rdd.collect())
        # Filter events based on begin and end time
        rdd = rdd.filter(lambda item: (item[1]['@timestamp'] <= end))
        rdd = rdd.filter(lambda item: (item[1]['@timestamp'] >= begin))
        print len(rdd.collect())
        # Get a list of all the process_guid for CMD.exe that were not created by explorer.exe
        # reg_cmd_rdd = rdd.filter(lambda item: (
        #    item[1]['exe'] == "cmd.exe")).filter(lambda item: (item[1]['parent_exe'] != "explorer.exe"))
        # guid_list = reg_cmd_rdd.map(lambda item: (item[1]['process_guid'])).collect()

        # Filter for all the reg.exe, created by cmd.exe, but cmd.exe was not created by explorer.exe
        rdd = rdd.filter(lambda item: (
            item[1]['exe'] == "regsvr32.exe")).filter(lambda item: (item[1]['parent_exe'] == "cmd.exe"))


        return rdd
