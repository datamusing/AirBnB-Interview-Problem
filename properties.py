#!/usr/bin/env python

""" This is my solution to Air BnB's coding challenge on Interview Street. It
only passes 2/4 tests. I don't know why. If you find the bug, please let me
know. """


import sys
import csv
import operator
import datetime
import bisect

def parse_input():
    """ Returns 3 dictionaries. The first has property_id as the key and the
    property data as the value. The second has a tuple (property_id, date) as
    the key and the availability information for that property on that night as
    the value. The third has a search_id as the key and the search data as the
    value. """
    properties_lines, dates_lines, searches_lines = [], [], []
    lines = sys.stdin.readlines()
    cur_list = None
    for line in lines:
        line = line.strip()
        if line == "Properties":
            cur_list = properties_lines
        elif line == "Dates":
            cur_list = dates_lines
        elif line == "Searches":
            cur_list = searches_lines
        elif cur_list is not None:
            cur_list.append(line)
    
    property_reader = csv.DictReader(properties_lines, fieldnames=["property_id", "lat", "lng", "nightly_price"])
    date_reader = csv.DictReader(dates_lines, fieldnames=["property_id", "date", "availability", "price"])
    search_reader = csv.DictReader(searches_lines, fieldnames=["search_id", "lat", "lng", "checkin", "checkout"])
    
    properties = {}
    for prop_dict in property_reader:
        prop_dict["lat"] = float(prop_dict["lat"])
        prop_dict["lng"] = float(prop_dict["lng"])
        prop_dict["nightly_price"] = int(prop_dict["nightly_price"])
        properties[prop_dict["property_id"]] = prop_dict
        
    dates = {}
    for date_dict in date_reader:
        date_dict["date"] = datetime.datetime.strptime(date_dict["date"], "%Y-%m-%d")
        date_dict["price"] = int(date_dict["price"])
        date_dict["availability"] = int(date_dict["availability"])
        dates[(date_dict["property_id"], date_dict["date"])] = date_dict
        
    searches = {}
    for search_dict in search_reader:
        search_dict["lat"] = float(search_dict["lat"])
        search_dict["lng"] = float(search_dict["lng"])
        search_dict["checkin"] = datetime.datetime.strptime(search_dict["checkin"], "%Y-%m-%d")
        search_dict["checkout"] = datetime.datetime.strptime(search_dict["checkout"], "%Y-%m-%d")
        searches[search_dict["search_id"]] = search_dict
    
    return properties, dates, searches


def perform_searches(properties, searches):
    """ Returns a dictionary mapping every search_id to a list of results within
    a bounding box with lat and lng +/- 1.0 from the search coordinates.
    
    We sort the properties by latitude and longitude so we can do a binary
    search over them efficiently. Sorting them is O(n log n), and then
    subsequent searches are O(log n), where n is the number of properties. Since
    we search these lists k times, where k is the number of total searches, the
    big-O for this function is O(n log n + k log n). We use the bisect module
    for binary search.
    
    NOTE: In earlier submissions, I was searching for properties within a radius
    of 1.0 degrees, instead of a bounding box. This made for a very different
    approach (using KD trees). Upon re-reading the problem, it became clear that
    this wasn't what you were looking for, but searching in a radius rather than
    a bounding box seems like a more intuitive way to handle spatial
    coordinates. It also wound up being fewer lines of code. Just something to
    think about... """
    
    sorted_by_lat = sorted(properties.values(), key=operator.itemgetter("lat"))
    sorted_by_lng = sorted(properties.values(), key=operator.itemgetter("lng"))
    lats = [prop["lat"] for prop in sorted_by_lat]
    lngs = [prop["lng"] for prop in sorted_by_lng]
    
    results = {}
    for search in searches.values():
        lo = bisect.bisect_left(lats, search["lat"] - 1.0)
        hi = bisect.bisect_right(lats, search["lat"] + 1.0)
        prop_ids_in_lat_range = set([prop["property_id"] for prop in sorted_by_lat[lo:hi]])
        
        lo = bisect.bisect_left(lngs, search["lng"] - 1.0)
        hi = bisect.bisect_right(lngs, search["lng"] + 1.0)
        prop_ids_in_lng_range = set([prop["property_id"] for prop in sorted_by_lng[lo:hi]])
        
        prop_ids = prop_ids_in_lat_range.intersection(prop_ids_in_lng_range)
        results[search["search_id"]] = [properties[prop_id] for prop_id in prop_ids]
        
    return results


def get_total_cost(prop, dates, checkin, checkout):
    one_day = datetime.timedelta(days=1)
    nights = [checkin + one_day * i for i in range((checkout - checkin).days)]
    
    cost = 0
    for night in nights:
        key = (prop["property_id"], night)
        if key not in dates:
            cost += prop["nightly_price"]
        else:
            date = dates[key]
            if date["availability"] == 0:
                return None
            else:
                cost += date["price"]
    return cost


def main():
    properties, dates, searches = parse_input()
    
    search_results = perform_searches(properties, searches)
        
    for search_id, results in search_results.items():
        # Find total prices for each property
        search = searches[search_id]
        properties_and_costs = []  # List of tuples (property_id, cost)
        for prop in results:
            cost = get_total_cost(prop, dates, search["checkin"], search["checkout"])
            if cost is not None:
                properties_and_costs.append((prop, cost))
        
        sorted_results = sorted(properties_and_costs, key=lambda k: k[1])
        for idx, final_result in enumerate(sorted_results[:10]):
            prop, cost = final_result
            print(",".join([search_id, str(idx + 1), prop["property_id"], str(cost)]))
            

if __name__ == "__main__":
    main()