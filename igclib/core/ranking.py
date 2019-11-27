class Ranking():
    def __init__(self, race):
        self.pilots = self.get_ranking(race)
        self.pilots_in_goal = self.get_pilots_in_goal(race)

    def get_ranking(self, race):
        ranking = {}
        for pilot_id, flight in race.flights.items():
            ranking[pilot_id] = {
                'name': str(flight),
                'id': pilot_id,
                'distance': flight.race_distance,
                'time': flight.race_time
            }

        ranking = sorted(ranking.values(),
                         key=lambda x: (-x['distance'], x['time'])
                         if hasattr(x, 'distance') else x['name'])
        return ranking

    def get_pilots_in_goal(self, race):
        in_goal = []
        for pilot_id, flight in race.flights.items():
            for point in list(flight.points.values())[::-1]:
                if point.goal_distance == 0:
                    in_goal.append(pilot_id)
                    break
        return in_goal
