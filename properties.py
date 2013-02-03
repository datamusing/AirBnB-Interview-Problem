#!/usr/bin/env python

import sys
import csv
import scipy.spatial

def parse_input():
properties_lines, dates_lines, searches_lines = [], [], []

with open('input00.txt') as input_file:
    lines = input_file.readlines()
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

properties = list(csv.DictReader(properties_lines, fieldnames=["property_id", "lat", "lng", "nightly_price"]))
dates = list(csv.DictReader(dates_lines, fieldnames=["property_id", "date", "availability", "price"]))
searches = list(csv.DictReader(searches_lines, fieldnames=["search_id", "lat", "lng", "checkin", "checkout"]))

# Generate KDTree of property locations
locs = [(float(prop["lat"]), float(prop["lng"])) for prop in properties]
loc_tree = scipy.spatial.KDTree(locs)

# Generate KDTree of search locations
search_locs = [(float(search["lat"]), float(search["lng"])) for search in searches]
search_loc_tree = scipy.spatial.KDTree(search_locs)

# Find locations within radius of 1.0 from the search
raw_results = search_loc_tree.query_ball_tree(loc_tree, 1.0)
results = [ [properties[i] for i in result] for result in search_results]
print (results)

#availability = {}
#for date in dates:
#    property_id = date["property_id"]
#    if property_id not in availability:
#        availability[property_id] = []
#    availability[property_id].append(date)
#    
#print (availability)
