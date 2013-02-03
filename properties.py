#!/usr/bin/env python

""" Hello Air BnB!

Here's a description of how my code works:

1. Parses input. (This is strightforward.) Generates dictionaries that map
property_id and search_id to their searches for easy lookup.

2. Performs the spatial searches. I used the KDTree implementation in the scipy
library for this. The method KDTree.query_ball_tree takes another tree as a
parameter, and for each point in the calling tree, it generates a list of
neighbors within a given radius in the other tree.

I hold that using KDTrees is a good approach. Quoth wikipedia: "In computer
science, a k-d tree (short for k-dimensional tree) is a space-partitioning data
structure for organizing points in a k-dimensional space. k-d trees are a useful
data structure for several applications, such as searches involving a
multidimensional search key (e.g. range searches and nearest neighbor
searches)." The scipy documentation also says that their KDTree implementation
"use[s] a reasonably efficient algorithm" for this kind of search.
   
3. Generate a map of (property_id, date) tuples to any "date" objects with data
on the availability for that night. This is so we have fast lookup later.

4. For each search, look through the list of search results. For each result,
check the availability data for each night that the guest wants to stay. If all
nights are available, total up the cost.

5. Sort the results for each search by cost. Print the best ten.

I don't know what the big-O runtime complexity of this all is. It's going to
depend on the KDTree's implementation, and the scipy docs don't give the big-O
complexity. (But it's probably good enough.)
"""


import sys
import csv
import scipy.spatial
import datetime

def parse_input():
    """ Returns a tuple of 3 elements where the first is a dictionary of
    properties (with their id as the key), the second is a list of dates, and
    the third is a dictionary of searches (with their id as the key) """
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
        else:
            if cur_list is not None:
                cur_list.append(line)
    
    property_reader = csv.DictReader(properties_lines, fieldnames=["property_id", "lat", "lng", "nightly_price"])
    date_reader = csv.DictReader(dates_lines, fieldnames=["property_id", "date", "availability", "price"])
    search_reader = csv.DictReader(searches_lines, fieldnames=["search_id", "lat", "lng", "checkin", "checkout"])
    
    properties = {prop["property_id"]: prop for prop in property_reader}
    dates = list(date_reader)
    searches = {search["search_id"]: search for search in search_reader}
    
    return properties, dates, searches


def perform_searches(properties, searches):
    """ Returns a dictionary mapping every search_id to a list of results within
    1.0 degree lat/lng. """
    
    # Generate KDTree of property locations
    locs = [(float(prop["lat"]), float(prop["lng"])) for prop in properties.values()]
    loc_tree = scipy.spatial.KDTree(locs)
    
    # Generate KDTree of search locations
    search_locs = [(float(search["lat"]), float(search["lng"])) for search in searches.values()]
    search_loc_tree = scipy.spatial.KDTree(search_locs)
    
    # Find locations within radius of 1.0 from the search.
    raw_results = search_loc_tree.query_ball_tree(loc_tree, 1.0)
    
    # Create and return a dictionary of search_id mapped to its search results
    results = {}
    for search_idx, prop_idx_list in enumerate(raw_results):
        results[searches.values()[search_idx]["search_id"]] = [properties.values()[prop_idx] for prop_idx in prop_idx_list]
    return results


def get_total_cost(prop, availability_map, checkin, checkout):
    one_day = datetime.timedelta(days=1)
    dates = [checkin + one_day * night for night in range((checkout - checkin).days)]
    
    cost = 0
    for date in dates:
        key = (prop["property_id"], date)
        if key not in availability_map:
            cost += int(prop["nightly_price"])
        else:
            availability = availability_map[key]
            if availability["availability"] == "0":
                return None
            else:
                cost += int(availability["price"])
    return cost


def main():
    properties, dates, searches = parse_input()
    
    search_results = perform_searches(properties, searches)
    
    # Create a dictionary with key (property_id, datetime) and the date object as the value
    availability_map = {}
    for date in dates:
        property_and_date = (date["property_id"], datetime.datetime.strptime(date["date"], "%Y-%m-%d"))
        availability_map[property_and_date] = date
        
    for search_id, results in search_results.items():
        # Find total prices for each property
        search = searches[search_id]
        properties_and_costs = []  # List of tuples (property_id, cost)
        for prop in results:
            checkin = datetime.datetime.strptime(search["checkin"], "%Y-%m-%d")
            checkout = datetime.datetime.strptime(search["checkout"], "%Y-%m-%d")
            cost = get_total_cost(prop, availability_map, checkin, checkout)
            
            if cost is not None:
                properties_and_costs.append((prop, cost))
        
        sorted_results = sorted(properties_and_costs, key=lambda k: k[1])[0:10]
        for idx, final_result in enumerate(sorted_results):
            prop = final_result[0]
            cost = final_result[1]
            print(",".join([search_id, str(idx + 1), prop["property_id"], str(cost)]))
            

if __name__ == "__main__":
    main()