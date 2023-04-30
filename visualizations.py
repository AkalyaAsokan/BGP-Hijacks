# To plot graph
import networkx as nx
import matplotlib.pyplot as plt
# To AS information from an AS Number
import json
import requests
# To read from files
import os

class Visualize:
    """
    Visualize class that collects stats and visualise components of the training data
    """

    def __init__(self):
        # Dictionary to store the prefixes with multiple origin ASes
        self.lines = {}

        # Creating a NetworkX graph object
        self.G = nx.Graph()

        # Creating a dictionary 
        # to store the AS paths and origins
        self.as_paths = {}

        # Dictionary storing AS Names
        self.as_names = {}

    def read_from_file(self):
        # Define the base filename
        base_filename = 'training_data_'

        # Define the list to store all lines from all files
        all_lines = []

        # Initialize the file number to 1
        file_num = 1

        while True:
            # Construct the filename for this iteration
            filename = base_filename + str(file_num).zfill(2) + '.txt'
            #filename = 'training_data_042820231148.txt'

            # Check if the file exists
            if os.path.isfile(filename):
                # Open the file and read its contents
                with open(filename, 'r') as f:
                    lines = f.readlines()

                # Add the lines to the list of all lines
                all_lines.extend(lines)

                # Increment the file number
                file_num += 1
            else:
                # If the file doesn't exist, exit the loop
                break

        return all_lines
    
    def get_asn_name(self, asn):
        # API to get AS information from an AS Number
        response = requests.get(f"https://stat.ripe.net/data/as-names/data.json?resource=AS{asn}")
        if response.ok:
            data = json.loads(response.text)
            
            # Return the AS Name
            return data["data"]["names"][str(asn)]
        else:
            return "Error fetching ASN information"

    def start(self):

        self.lines = self.read_from_file()

        # Parse the lines and create the dictionary
        for i in range(len(self.lines)):
            if self.lines[i].startswith('Prefix: '):
                prefix = self.lines[i].strip().split(' ')[1]
                if prefix not in self.as_paths:
                    self.as_paths[prefix] = []
                for j in range(i+2, len(self.lines)):
                    if self.lines[j].startswith('AS path: '):
                        self.as_path = self.lines[j].split(': ')[-1].strip().split(' -> ')
                        self.as_paths[prefix].append(self.as_path)
                    else:
                        break

        # Printing the AS paths for each prefix
        for prefix, paths in self.as_paths.items():
            # Converting inner lists to tuples
            paths = [tuple(path) for path in paths]
            # Adding nodes for the origin ASes
            origin_ases = set([path[-1] for path in paths])
            for as_node in origin_ases:
                if as_node not in self.as_names:
                    as_name = self.get_asn_name(as_node)
                    self.G.add_node(as_name)
                    self.as_names[as_node] = as_name
                else:
                    self.G.add_node(self.as_names[as_node])

            # Adding edges between ASes that appear in the same path
            for path in paths:
                if path[0] not in self.as_names:
                    src = self.get_asn_name(path[0])
                    self.G.add_node(src)
                    self.as_names[path[0]] = src
                else:
                    src = self.as_names[path[0]]
                    self.G.add_node(src)

                if path[0] not in self.as_names:
                    dest = self.get_asn_name(path[len(path) - 1])
                    self.G.add_node(dest)
                    self.as_names[path[len(path) - 1]] = dest
                else:
                    dest = self.as_names[path[len(path) - 1]]
                    self.G.add_node(dest)

                self.G.add_edge(src, dest, weight=len(path))

        # Calculating and printing basic graph metrics
        print("Number of nodes:", self.G.number_of_nodes())
        print("Number of edges:", self.G.number_of_edges())
        print("Average degree:", sum(dict(self.G.degree()).values()) / self.G.number_of_nodes())

        # Drawing the graph
        pos = nx.spring_layout(self.G)
        nx.draw_networkx(self.G, pos, node_size=400, font_size=10)
        edge_labels = {(u, v): str(self.G[u][v]['weight']) for u, v in self.G.edges()}
        nx.draw_networkx_edge_labels(self.G, pos, edge_labels=edge_labels, font_size=8)
        plt.show()

        as_paths = []
        for i in range(len(self.lines)):
            if self.lines[i].startswith('Update to '):
                as_paths.append(self.lines[i+1].split('AS Path: ')[1].strip("[").strip("]\n").replace("'", "").split(", "))

        # Count frequency of each ASN in AS paths
        # Count the number of times the origin prefix has repeated itself in an AS path
        # origin_prefix_count = [path.count(path[-1]) for path in as_paths]
        count = {}
        for i in range(len(as_paths)):
            count[as_paths[i][-1]] = []
        for i in range(len(as_paths)):
            count[as_paths[i][-1]].append(as_paths[i].count(as_paths[i][-1]))

        # Find the maximum value in the dictionary
        max_val = max([max(count[key]) for key in count])

        # Create a list of counts for each index for each key
        counts = {key: [0] * (max_val+1) for key in count}
        fig, ax = plt.subplots()
        for asn in count:
            for val in count[asn]:
                counts[asn][val] += 1
            ax.plot(range(2,max_val+1), counts[asn][2:], label=self.get_asn_name(asn))

        ax.set_xlabel('X Axis')
        ax.set_ylabel('Y Axis')
        ax.set_xticks(range(2,max_val+1))
        #ax.set_xticklabels(range(min_val, max_val+1))
        ax.legend()
        plt.show()
