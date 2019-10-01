### DISTANCE COMPUTATION ###
from geopy import distance
distance_computation = distance.vincenty
#distance_computation = distance.distance -> slower

### IGC FILE CONSTANTS ###
IGC_ALTITUDE = 'gps_alt'
IGC_LAT = 'lat'
IGC_LON = 'lon'