# Importing pybgpstream to collect BGP updates from various route collectors
import pybgpstream

# Importing json and requests, Python libraries used for getting AS Information using RIPE Stat API
import json
import requests

# Importing matplotlib, a popular library for creating interactive visualizations
import matplotlib.pyplot as plt
from matplotlib.animation import FuncAnimation

# Importing glob, to read data from files
import glob

# Importing datetime, the datetime module provides classes for working with dates and times.
from datetime import datetime

from typing import Dict, List

class Graph:
    
    def __init__(self):
        # Initialize an empty graph
        self.graph = {}
        
    def add_edge(self, u: int, v: int) -> None:
        # Add an edge between two vertices
        # If the vertices are not in the graph, add them to the graph
        if u not in self.graph:
            self.graph[u] = []
        if v not in self.graph:
            self.graph[v] = []
        # If the edge does not already exist, add it to both vertices
        if v not in self.graph[u]:
            self.graph[u].append(v)
        if u not in self.graph[v]:
            self.graph[v].append(u)

    def get_vertices(self) -> List[int]:
        # Return a list of all vertices in the graph
        return list(self.graph.keys())
        
class FakePathDetector:
    """
    Fake Path Detector class that keeps track of multiple Fake Path Hijack events
    """

    def __init__(self):
        
        # Initialise a connected graoh for each prefix 
        self.graphs = {}
        
        # Has mapping between prefixes and their true origin ASN
        self.true_prefixes = {}

        # A list of list containing [record when attack was found, ASN that caused the attack]
        self.attack = []

    def get_asn_name(self, asn):

        # API to get name from ASN
        response = requests.get(f"https://stat.ripe.net/data/as-names/data.json?resource=AS{asn}")

        if response.ok:
            data = json.loads(response.text)
            print(data)
            return data["data"]["names"][str(asn)]
        else:
            return "Error fetching ASN information"
        
    def update_plot(self, time, ax, prefix, x_data, y_data, color, val):

        # Animation visualise real time data incoming and whether or not it is an attack, and 
        # 1. show a red spike in the plot when an attack is detected
        # 2. show green line is no attack is detected
        # 3. show a yellow line when it is a new prefix comes in the testing data
        x_data.append(time)
        y_data.append(val)
        ax.clear()
        x_data = x_data[-10:]
        y_data = y_data[-10:]
        ax.set_ylim([-2,2])
        ax.text(time, val, prefix, size=12)
        ax.plot(x_data, y_data, color=color, linewidth=2)
        plt.xticks(rotation=90, ha='right')

    def read_from_file(self) -> Dict[str, Graph]:

        with open("training_data_2017_2.txt") as f:
            prefix = None

            # temp datastructure to create a dict of prefix and true origin mapping
            as_paths = {}
            for line in f:
                if line.startswith("Prefix: "):
                    if line.split()[1] not in self.true_prefixes:
                        self.true_prefixes[line.split()[1]] = None
                    curr_prefix = line.split()[1]

                    # If prefix is not already in the dictionary, create a new list
                    if curr_prefix not in as_paths:
                        as_paths[curr_prefix] = []
                    prefix = line.split(": ")[1].strip()

                    # Creating a graph for each prefix
                    self.graphs[prefix] = Graph()
                elif line.startswith("AS path: "):
                    temp = line.split(': ')[-1].strip().split(' -> ')[-1]
                    as_paths[curr_prefix].append(temp)
                    as_path = line.split(": ")[1].strip()
                    try: 
                        # Accommodating inconsistencies with datas
                        # Sometimes data come with {}
                        as_numbers = [int(as_num.strip('{}')) for as_num in as_path.split(" -> ")]

                        # Add an edge if the nodes arent the same. This is possible in case of AS prepending
                        for i in range(len(as_numbers)-1):
                            u, v = as_numbers[i], as_numbers[i+1]
                            if u != v:
                                self.graphs[prefix].add_edge(u, v)
                    except:
                        None
            
        # Choose most common AS path for each prefix
        # This is to check the second condition of fake path hijack - ie, the origin ASes are the same
        for prefix in self.true_prefixes:
            curr_as_paths = as_paths.get(prefix, [])
            if as_paths:
                most_common_path = max(set(curr_as_paths), key=curr_as_paths.count)
                self.true_prefixes[prefix] = most_common_path
    
    def start(self, start_time, end_time):

        # Populate the true prefixes after reading data from file
        self.read_from_file()
        print(self.graphs)
        fig, ax = plt.subplots()
        ax.set_title(f"Fake Path Hijack Monitor")
        ax.set_xlabel("Time")
        ax.set_ylabel("Fake Path Hijack Status")

        # Setting the time interval for the BGP data
        #now = datetime.now()

        # Collecting roughly 15 days of data 
        # to identify the true origin of prefixes
        # from_time = now - timedelta(days=1)
        # until_time = now - timedelta(days=0)

        # Initialize the BGPStream and set the filtering options
        stream = pybgpstream.BGPStream(
            # using the same filters as the training data
            from_time= start_time, until_time=end_time,
            collectors=["route-views.sydney",
                "route-views.sg",
                "route-views2.routeviews.org"],
            # Filtering with only BGP updates
            record_type="updates",
        )

        xs = []
        ys = []
        stream.start()
        global count
        count = 0

        def animate(i, x_data:list, y_data:list):
            global count
            count = count + 1

            # Get the record from BGP Stream
            record = stream.get_next_record()

            # Check if the record is valid and get the first 5000 records
            if record and count < 5000:
                try:
                    elem = record.get_next_elem()
                    print('Processing Record %d' % count)

                    # Extract the AS path, prefix and time from the BGP update
                    as_path = elem.fields['as-path'].split()
                    prefix = elem.fields['prefix']
                    record_time = record.time

                    # Apppending current time for uniqueness to get the animation working
                    time = str(datetime.now()) + str(datetime.fromtimestamp(record_time))

                    # Check for Fake Path hijacks
                    # Ignore if new prefix that does not exist in training data, comes in
                    if prefix in self.graphs:
                        #graph = self.graphs[prefix].graph
                        as_numbers = as_path

                        # If not same origin, then this may be a MOAS or Sub Moas attack. Not fake path
                        if self.true_prefixes[prefix] != as_path[-1]:
                            return
                        
                        # Check if all the edges of the current record is present in the 
                        # graph computed for each prefix from training data
                        for i in range(len(as_numbers)-1):
                            u, v = as_numbers[i], as_numbers[i+1]
                            if u == v: 
                                continue
                            if int(v) not in self.graphs[prefix].graph[int(u)]:
                                self.attack.append([count, v])
                                print('Fake path hijack detected for prefix %s!' % prefix)
                                print('AS path: %s' % ' -> '.join(as_path))
                                print('AS that attacked: %s' % self.get_asn_name(as_path[-1]))
                                # red spike in the plot when an attack is detected
                                self.update_plot(time, ax, prefix, x_data, y_data, "red", 1)
                                return

                        # green line is no attack is detected
                        self.update_plot(time, ax, prefix, x_data, y_data, "green", -1)
                    else:
                        # new prefix comes in the testing data
                        self.update_plot(time, ax, prefix, x_data, y_data, "yellow", 0)
                except:
                    None
            else:
                # Once 5000 records are processed or records are not obtaineable, stop the animation
                ani.event_source.stop()

        # Animation visualise real time data incoming and whether or not it is an attack, and 
        # 1. show a red spike in the plot when an attack is detected
        # 2. show green line is no attack is detected
        # 3. show a yellow line when it is a new prefix comes in the testing data
        plt.style.use('fivethirtyeight')
        ani = FuncAnimation(plt.gcf(), animate, fargs=(xs,ys), interval = 500)
        plt.show()
