from intervals.ratio_interval_builder import Ratio_interval_builder
from fuzzy.fuzzifier import Fuzzifier
from fuzzy.flrg_manager import Flrg_manager
import numpy as np

class Fuzzy_time_series(object):

    def __init__(self):
        self.__flrg_managers = []
        self.__fuzzifier = None
        self.__fts = None

    def order(self):
        return len(self.__flrg_managers)

    def build_fts(self, order, time_series):
        ratio_builder = Ratio_interval_builder(time_series)
        intervals = ratio_builder.calculate_intervals()
        self.tick_builder = time_series.builder

        self.__fuzzifier = Fuzzifier(intervals)
        self.__fts = self.__fuzzifier.fuzzify_time_series(time_series)

        for i in xrange(1,order+1):
            self.add_order(i)

    def add_order(self, order):
        if order not in [n.order for n in self.__flrg_managers]:
            fuzzy_logical_relationships =  self.__fuzzifier.fuzzy_logical_relationships(self.__fts, order)
            flrg_manager = Flrg_manager(order)
            flrg_manager.import_relationships(fuzzy_logical_relationships)
            self.__flrg_managers.append(flrg_manager)

    def forecast(self, mini_series):
        if self.__fuzzifier is None:
            print "FTS not built yet"
        forecast = []
        for idx, flrg_manager in enumerate(reversed(self.__flrg_managers)):
            fuzzified = self.__fuzzifier.fuzzify_input(mini_series[idx])
            matching_flrg = flrg_manager.find(fuzzified)
            forecast.append(matching_flrg)
        intersection = self.__fuzzy_intersection_intervals(forecast)
        if len(intersection) == 0:
            return mini_series[-1]
        midpoints = [member.interval.midpoint() for member in intersection]
        average = np.mean(midpoints)
        return average

    def __fuzzy_intersection_intervals(self, flrgs):
        total_intervals_found = []
        for flrg in flrgs:
            current_flrg_intervals_found = []
            for fuzzy_set in flrg.rhs:
                for member in fuzzy_set.set:
                    if member.membership == 1.0:
                        current_flrg_intervals_found.append(member)
            total_intervals_found.append(current_flrg_intervals_found)
        return self.__intersect_fuzzy_sets(total_intervals_found)

    def __intersect_fuzzy_sets(self, total_intervals_found):
        if len(total_intervals_found) == 0:
            return []
        found_in_all_new = []
        found_in_all_check = total_intervals_found[0]
        for intervals_found in total_intervals_found[1:]:
            for member in intervals_found:
                if member in found_in_all_check and member not in found_in_all_new:
                    found_in_all_new.append(member)
            found_in_all_check = found_in_all_new
            found_in_all_new = []
        return  found_in_all_check