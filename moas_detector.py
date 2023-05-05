import numpy as np
from datetime import datetime
# Importing pybgpstream to collect BGP updates 
# from various route collectors
import pybgpstream
# To AS information from an AS Number
import json
import requests
# To plot graph
import matplotlib.pyplot as plt
from matplotlib.animation import FuncAnimation
# To read from files
import glob

class MoasDetector:
    """
    MOAS Detector class that keeps track of multiple origin AS (MOAS) events
    """

    def __init__(self):
        # Load the true prefixes from file
        self.true_prefixes = {}

    def get_asn_name(self, asn):
        response = requests.get(f"https://stat.ripe.net/data/as-names/data.json?resource=AS{asn}")
        if response.ok:
            data = json.loads(response.text)
            print(data)
            return data["data"]["names"][str(asn)]
        else:
            return "Error fetching ASN information"
        
    def update_plot(self, ax, prefix, x_data, y_data):
        # Define a function to update the plot when an attack is detected

        # Append the current time to the x data array
        x_data.append(datetime.now().strftime("%Y-%m-%d %H:%M:%S"))
        y_data.append(1)
        ax.clear()
        x_data = x_data[-10:]
        y_data = y_data[-10:]
        ax.set_ylim([-2,2])
        ax.text(datetime.now().strftime("%Y-%m-%d %H:%M:%S"), 1, prefix, size=12)
        ax.plot(x_data, y_data, color="red", linewidth=2)
        plt.xticks(rotation=90, ha='right')

    def read_from_file(self):
        as_paths = {}
        for filename in glob.glob('training_data_2017_2.txt'):
            with open(filename) as f:
                for line in f:
                    if line.startswith('Prefix: '):
                        if line.split()[1] not in self.true_prefixes:
                            self.true_prefixes[line.split()[1]] = None
                        curr_prefix = line.split()[1]
                        if curr_prefix not in as_paths:
                            as_paths[curr_prefix] = []
                    elif line.startswith('AS path: '):
                        as_path = line.split(': ')[-1].strip().split(' -> ')[-1]
                        as_paths[curr_prefix].append(as_path)

        # Choose most common AS path for each prefix
        for prefix in self.true_prefixes:
            curr_as_paths = as_paths.get(prefix, [])
            if as_paths:
                most_common_path = max(set(curr_as_paths), key=curr_as_paths.count)
                self.true_prefixes[prefix] = most_common_path

    
    def start(self):
        # Load the true prefixes from file
        self.read_from_file()
        print(self.true_prefixes)
        fig, ax = plt.subplots()
        ax.set_title(f"Prefix MOAS Attack Monitor")
        ax.set_xlabel("Time")
        ax.set_ylabel("MOAS Attack Status")
        # Setting the time interval for the BGP data
        from datetime import datetime, timedelta
        now = datetime.now()

        # Collecting roughly 15 days of data 
        # to identify the true origin of prefixes
        from_time = now - timedelta(days=1)
        until_time = now - timedelta(days=0)

        # Initialize the BGPStream and set the filtering options
        stream = pybgpstream.BGPStream(
            # accessing routeview-stream
            #from_time= from_time.strftime("%Y-%m-%d %H:%M:%S"), until_time=until_time.strftime("%Y-%m-%d %H:%M:%S"),
            from_time= "2017-07-03 01:00:00", until_time="2017-07-18 01:00:00",
            collectors=["route-views.sydney",
                "route-views.sg",
                "route-views2.routeviews.org"],
            # Filtering with only BGP updates
            record_type="updates",
            # Using the same prefix that was used for training
            #filter="prefix more 0.0.0.0/0"
        )

        xs = []
        ys = []
        stream.start()

        def animate(i, x_data:list, y_data:list):
            record = stream.get_next_record()
            #print(record)
            # Check if the record is valid
            if record:
                try:
                    elem = record.get_next_elem()
                    print(elem)
                    # Extract the AS path and prefix from the BGP update
                    as_path = elem.fields['as-path'].split()
                    prefix = elem.fields['prefix']
                    #prefix = '210.180.74.0/23'
                    #as_path = ['37271', '4766']

                    # Check for MOAS attacks
                    if prefix in self.true_prefixes:
                        if self.true_prefixes[prefix] != as_path[-1]:
                            print('MOAS attack detected for prefix %s!' % prefix)
                            print('AS path: %s' % ' -> '.join(as_path))
                            print('AS that attacked: %s' % self.get_asn_name(as_path[-1]))
                            #self.update_plot(ax, prefix, x_data, y_data)
                            raise Exception("Sorry, no numbers below zero")
                        else:
                            # Append 0 to the y data array to represent no MOAS attack
                            y_data.append(0)
                            # Append the current time to the x data array
                            x_data.append(datetime.now().strftime("%Y-%m-%d %H:%M:%S"))
                            # Update the plot with the new data
                            ax.clear()
                            x_data = x_data[-10:]
                            y_data = y_data[-10:]
                            ax.set_ylim([-2,2])
                            ax.text(datetime.now().strftime("%Y-%m-%d %H:%M:%S"), 0, prefix, size=12)
                            ax.plot(x_data, y_data, color="green", linewidth=2)
                            plt.xticks(rotation=90, ha='right')
                    else:
                        # Append 0 to the y data array to represent no MOAS attack
                        y_data.append(0)
                        # Append the current time to the x data array
                        x_data.append(datetime.now().strftime("%Y-%m-%d %H:%M:%S"))
                        # Update the plot with the new data
                        ax.clear()
                        x_data = x_data[-10:]
                        y_data = y_data[-10:]
                        ax.set_ylim([-2,2])
                        ax.text(datetime.now().strftime("%Y-%m-%d %H:%M:%S"), 0, prefix, size=12)
                        ax.plot(x_data, y_data, color="green", linewidth=2)
                        plt.xticks(rotation=90, ha='right')

                except:
                    None

        plt.style.use('fivethirtyeight')
        ani = FuncAnimation(plt.gcf(), animate, fargs=(xs,ys), interval = 500)
        plt.show()
