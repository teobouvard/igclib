import re

### DISTANCE COMPUTATION ###

from geopy import distance
distance_computation = distance.great_circle
#distance_computation = distance.vincenty -> slower
#distance_computation = distance.distance -> slowest


### NUMERICAL APPROXIMATION 

MIN_TURNPOINTS_DISTANCE = 1 # meters


### IGC FILE CONSTANTS ###

IGC_RECORDS = 'fix_records'
IGC_HEADER = 'header'
IGC_TIME = 'time'
IGC_ALTITUDE = 'gps_alt'
IGC_LAT = 'lat'
IGC_LON = 'lon'


### XCTRACK FILE CONSTANTS ### (https://xctrack.org/Competition_Interfaces.html)

XC_EARTH = 'earthModel'
XC_TASK_TYPE = 'taskType'
XC_TIME_FORMAT = '%H:%M:%SZ'
XC_TYPE = 'type'
XC_VERSION = 'version'

XC_GOAL = 'goal'
XC_GOAL_DEADLINE = 'deadline'

XC_SSS = 'sss'
XC_SSS_DIRECTION = 'direction'
XC_SSS_TIMEGATES = 'timeGates'

XC_TURNPOINTS = 'turnpoints'
XC_TURNPOINTS_RADIUS = 'radius'
XC_WAYPOINT = 'waypoint'
XC_WAYPOINT_ALT = 'altSmoothed'
XC_WAYPOINT_DESC = 'description'
XC_WAYPOINT_LAT = 'lat'
XC_WAYPOINT_LON = 'lon'
XC_WAYPOINT_NAME = 'name'


### CRAWLERS ###

MIN_YEAR = 2010
DEFAULT_PROVIDER = 'PWCA'
MAX_TASKS_PER_EVENT = 11
TASK_PROVIDERS = {
    'PWCA': {
        'NAME' : 'PWCA',
        'BASE_URL' : 'http://pwca.org/view/tour/',
        'TASKS_URL' : 'http://pwca.org/sites/default/files/taskboards/pwctb',
        'TASK_PATTERN' : re.compile('xctask.map.taskjsn = (.*?);')
    },
}