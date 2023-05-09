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

class SubMoasDetector:
    """
    Sub MOAS Detector class that keeps track of multiple origin AS (SubMOAS) events
    """

    def __init__(self):
        
        # Nested dictionary that has mapping between prefixes and mask + true origin ASN
        self.prefix_dict = {}

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

    def read_from_file(self):

        # Reading data from file and creating a dict of prefix and unique mask + true origin mapping
        # as_paths is a temp datastructure that has a dictionary mapping from prefix to list of mask, ASN 
        as_paths = {}
        for filename in glob.glob('training_data_2017_2.txt'):
            with open(filename) as f:
                for line in f:
                    if line.startswith('Prefix: '):
                        curr_prefix = line.split()[1]
                        # If Prefix not already present, create a new list
                        if curr_prefix.split('/')[0] not in as_paths:
                            as_paths[curr_prefix.split('/')[0]] = []
                    elif line.startswith('AS path: '):

                        # Extracting origin ASN from testing data
                        origin_as = line.split(': ')[-1].strip().split(' -> ')[-1]

                        # Extracting Mask from testing data
                        mask = curr_prefix.split('/')[1]
                        as_path = {'mask': mask, 'origin_as': origin_as}
                        if curr_prefix.split('/')[0] not in as_paths:
                            as_paths[curr_prefix.split('/')[0]] = [as_path]
                        else:
                            as_paths[curr_prefix.split('/')[0]].append(as_path)

        # Using the as_path, make a mapping from prefix to unique mask
        # Each mask is mapped to the most frequently occuring ASN
        self.prefix_dict = {}
        for prefix, as_path_list in as_paths.items():
            self.prefix_dict[prefix] = {}
            mask_counts = {}
            for as_path in as_path_list:
                mask = as_path['mask']
                origin_as = as_path['origin_as']
                mask_counts[mask] = mask_counts.get(mask, {})
                mask_counts[mask][origin_as] = mask_counts[mask].get(origin_as, 0) + 1
            for mask, count_dict in mask_counts.items():
                max_origin_as = max(count_dict, key=count_dict.get)
                self.prefix_dict[prefix][mask] = max_origin_as
    
    def start(self, start_time, end_time):

        # Populate the true prefixes after reading data from file
        self.read_from_file()
        print(self.prefix_dict)
        fig, ax = plt.subplots()
        ax.set_title(f"SubMOAS Attack Monitor")
        ax.set_xlabel("Time")
        ax.set_ylabel("SubMOAS Attack Status")

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
                print('Processing Record %d' % count)
                try:
                    elem = record.get_next_elem()

                    # Extract the AS path, prefix and time from the BGP update
                    as_path = elem.fields['as-path'].split()
                    prefix = elem.fields['prefix']
                    record_time = record.time

                    # Apppending current time for uniqueness to get the animation working
                    time = str(datetime.now()) + str(datetime.fromtimestamp(record_time))

                    # Check for SubMOAS attacks
                    # Ignore if new prefix that does not exist in training data, comes in
                    if prefix.split('/')[0] in self.prefix_dict:

                        # Find the longest mask in the nested dict for the prefix and make that as the ground truth
                        max_key = 0
                        my_dict_items = self.prefix_dict[prefix.split('/')[0]].items()
                        max_key = max(k for k, v in my_dict_items)
                        max_val = self.prefix_dict[prefix.split('/')[0]][max_key]

                        # Check for two conditions to mark the routing information as an attack
                        # 1. The origin prefix is different
                        # 2. The mask of current record is longer than the ground truth
                        if max_val != as_path[-1] and prefix.split('/')[1] > max_key:
                            self.attack.append([count, as_path[-1]])
                            print('SubMOAS attack detected for prefix %s!' % prefix)
                            print('AS path: %s' % ' -> '.join(as_path))
                            print('AS that attacked: %s' % self.get_asn_name(as_path[-1]))
                            # red spike in the plot when an attack is detected
                            self.update_plot(time, ax, prefix, x_data, y_data, "red", 1)
                        else:
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
