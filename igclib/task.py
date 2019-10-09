import logging
from datetime import datetime, time, timedelta
from parser import xctrack

from constants import distance_computation as distance
from utils.optimizer import optimize

## DEBUG
import matplotlib.pyplot as plt
import cartopy.crs as ccrs
import cartopy
import math

# fast distance computations do not validate waypoints without tolerances
TOLERANCE = 20


class Task():

    optimize 

    def __init__(self, task_file, task_type='xctrack'):
        if task_type == 'xctrack':
            task = xctrack.XCTask(task_file)
        elif task_type == 'pwca':
            # TODO pwca parser
            raise NotImplementedError('{} tasks are not yet supported'.format(task_type))
        else:
            raise NotImplementedError('{} tasks are not yet supported'.format(task_type))

        self.start = task.start
        self.stop = task.stop
        self.takeoff = task.takeoff
        self.sss = task.sss
        self.waypoints = task.waypoints
        self.ess = task.ess
        self.optimized_distance = optimize(self.takeoff, self.waypoints)[0]
        #self.debug_plot(self.takeoff, self.waypoints, self.waypoints)


    def timerange(self, start=None, stop=None):
        start = start if start is not None else self.start
        stop = stop if stop is not None else self.stop
        if stop < start:
            start, stop = stop, start

        # all this mess is necessary because you can't add datetime.time objects, which are used by aerofiles parser
        current = datetime(1, 1, 1, start.hour, start.minute, start.second)
        stop = datetime(1, 1, 1, stop.hour, stop.minute, stop.second)

        while current < stop:
            yield current.time()
            current += timedelta(seconds=1)
    

    @staticmethod
    def debug_plot(pos, waypoints, remaining_waypoints):
        _, fast_waypoints = optimize(pos, remaining_waypoints)

        lats = [wp['lat'] for wp in waypoints]
        lons = [wp['lon'] for wp in waypoints]
        rads = [wp['radius'] for wp in waypoints]
        
        fast_lats = [wp['lat'] for wp in fast_waypoints]
        fast_lons = [wp['lon'] for wp in fast_waypoints]
        
        plt.ioff()
        ax = plt.axes(projection=ccrs.PlateCarree())
        ax.coastlines()
        ax.plot(fast_lons, fast_lats, alpha=0.5, transform=ccrs.PlateCarree())
        # no working display with radius
        #ax.scatter(lons, lats, s=rads, alpha=0.5, transform=ccrs.PlateCarree())
        ax.scatter(pos['lon'], pos['lat'], s= 10, transform=ccrs.PlateCarree())
        plt.pause(0.00001)
        plt.clf()
        #plt.show()


    def validate(self, flight):
        remaining_waypoints = self.waypoints.copy()
        start_passed = False
        
        for timestamp, point in flight.points.items():
            position = (point['lat'], point['lon'])

            # race has not started yet
            if timestamp < self.start:
                flight.points[timestamp]['goal_dist'] = optimize(point, remaining_waypoints)[0]
                continue
            
            #if len(remaining_waypoints) < 6:
                #self.debug_plot(point, self.waypoints, remaining_waypoints)

            # race has started, checking for start validation
            if start_passed == False:
                flight.points[timestamp]['goal_dist'] = optimize(point, remaining_waypoints)[0]

                # this will not work for start without a turnpoint inside !
                if self.sss['direction'] == 'EXIT' and self.is_in(position, self.sss) or self.sss['direction'] == 'ENTER' and not self.is_in(position, self.sss):
                    start_passed = True
                    del remaining_waypoints[0]
                    logging.info('START {}, {} wp remaining'.format(timestamp, len(remaining_waypoints)))

                continue
                
            # at least two turnpoints remaining, check for concentric ones
            if len(remaining_waypoints) > 1:
                flight.points[timestamp]['goal_dist'] = optimize(point, remaining_waypoints)[0]

                if self.is_in(position, remaining_waypoints[0]) and not self.concentric_case(remaining_waypoints[0], remaining_waypoints[1]):
                    del remaining_waypoints[0]
                    logging.info('IN {}, {} wp remaining'.format(timestamp, len(remaining_waypoints)))
                elif self.concentric_case(remaining_waypoints[0], remaining_waypoints[1]) and not self.is_in(position, remaining_waypoints[0]):
                    del remaining_waypoints[0]
                    logging.info('OUT OR ESS {}, {} wp remaining'.format(timestamp, len(remaining_waypoints)))

            # only one turnpoint remaining, check for goal
            elif len(remaining_waypoints) == 1:
                flight.points[timestamp]['goal_dist'] = optimize(point, remaining_waypoints)[0]

                if self.is_in(position, remaining_waypoints[0]):
                    del remaining_waypoints[0]
                    logging.info('GOAL {}'.format(timestamp))

            # in goal, fill zeros until landing
            else:
                flight.points[timestamp]['goal_dist'] = 0


    def __len__(self):
        return int(self.optimized_distance)

    @staticmethod
    def is_in(pos, wpt):
        return True if distance(pos, (wpt['lat'], wpt['lon'])).meters <= wpt['radius'] + TOLERANCE else False

    @staticmethod
    def concentric_case(wptA, wptB):
        return True if wptA['lat'] == wptB['lat'] and wptA['lon'] == wptB['lon'] and wptB['radius'] < wptA['radius'] else False
