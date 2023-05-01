#import required libraries
import pybgpstream as bgp
from datetime import datetime
import numpy as np
import json
import requests
import matplotlib.pyplot as plt
from matplotlib.animation import FuncAnimation
import glob

'''
Implementing class sub_MoAS that detects and keep tracks of sub-MoAS BGP hijacks
'''

class sub_MoAS:
    
    def __init__(self):
        self.true_prefixes = {}
    
    #fetch ASN number
    def get_asn_name(self, asn):
        response = requests.get(f"https://stat.ripe.net/data/as-names/data.json?resource=AS{asn}")
        if response.ok:
            data = json.loads(response.text)
            print(data)
            return data["data"]["names"][str(asn)]
        else:
            return "Cannot fetch the ASN info."
        
    
    def update_plot(self, ax, prefix, x_data, y_data):
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
        for filename in glob.glob('training_data_*.txt'):
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

        
        for prefix in self.true_prefixes:
            curr_as_paths = as_paths.get(prefix, [])
            if as_paths:
                most_common_path = max(set(curr_as_paths), key=curr_as_paths.count)
                self.true_prefixes[prefix] = most_common_path
    
    
    def start(self):
        self.read_from_file()
        print(self.true_prefixes)
        fig, ax = plt.subplots()
        ax.set_title(f"Prefix MOAS Attack Monitor")
        ax.set_xlabel("Time")
        ax.set_ylabel("MOAS Attack Status")


        stream = pybgpstream.BGPStream(
            project="routeviews-stream",
            record_type="updates",
            filter="prefix more 210.180.0.0/16"
        )

        xs = []
        ys = []
        stream.start()
        
    
    def animate(i, x_data:list, y_data:list):
            record = stream.get_next_record()

            # Checks if the record is valid
            if record:
                try:
                    elem = record.get_next_elem()

                    # Extract the AS path and prefix from the BGP update
                    as_path = elem.fields['as-path'].split()
                    prefix = elem.fields['prefix']
                    
                    #Check for sub-MoAS attack
                    if prefix in self.true_prefixes:
                        for existing_as_path in self.true_prefixes[prefix]:
                            if existing_as_path != as_path and existing_as_path[:-1] == as_path[:-1]:
                                print(f"Sub-MoAS detected for prefix {prefix} with AS path {as_path}")
                                print('AS that attacked: %s' % self.get_asn_name(as_path[-1]))
                                self.update_plot(ax, prefix, x_data, y_data)
                             
                            else:
                            y_data.append(0)
                            x_data.append(datetime.now().strftime("%Y-%m-%d %H:%M:%S"))
                            ax.clear()
                            x_data = x_data[-10:]
                            y_data = y_data[-10:]
                            ax.set_ylim([-2,2])
                            ax.text(datetime.now().strftime("%Y-%m-%d %H:%M:%S"), 0, prefix, size=12)
                            ax.plot(x_data, y_data, color="green", linewidth=2)
                            plt.xticks(rotation=90, ha='right')
                    
                    else:
                        y_data.append(0)
                        x_data.append(datetime.now().strftime("%Y-%m-%d %H:%M:%S"))
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
