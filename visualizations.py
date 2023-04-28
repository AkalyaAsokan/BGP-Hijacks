import networkx as nx
import matplotlib.pyplot as plt
from collections import Counter
from collections import defaultdict
# Creating a NetworkX graph object
G = nx.Graph()
as_paths = {}

# Open the file in read mode
with open('training_data.txt', 'r') as f:
    lines = f.readlines()

# Parse the lines and create the dictionary
for i in range(len(lines)):
    if lines[i].startswith('Prefix: '):
        prefix = lines[i].strip().split(' ')[1]
        as_paths[prefix] = []
        for j in range(i+2, len(lines)):
            if lines[j].startswith('AS path: '):
                as_path = lines[j].split(': ')[-1].strip().split(' -> ')
                as_paths[prefix].append(as_path)
            else:
                break

# Print the dictionary
# print(as_paths)
# Printing the AS paths for each prefix
for prefix, paths in as_paths.items():
    print(paths)
    # Converting inner lists to tuples
    paths = [tuple(path) for path in paths]
    # Adding nodes for the origin ASes
    origin_ases = set([path[-1] for path in paths])
    for as_node in origin_ases:
        G.add_node(as_node)

    # Adding edges between ASes that appear in the same path
    for path in paths:
        src = path[0]
        dest = path[len(path) - 1]
        G.add_edge(src, dest, weight=len(path))

# Calculating and printing basic graph metrics
print("Number of nodes:", G.number_of_nodes())
print("Number of edges:", G.number_of_edges())
print("Average degree:", sum(dict(G.degree()).values()) / G.number_of_nodes())

# Drawing the graph
pos = nx.spring_layout(G)
nx.draw_networkx(G, pos, node_size=400, font_size=10)
edge_labels = {(u, v): str(G[u][v]['weight']) for u, v in G.edges()}
nx.draw_networkx_edge_labels(G, pos, edge_labels=edge_labels, font_size=8)
plt.show()

as_paths = []
for i in range(len(lines)):
    if lines[i].startswith('Update to '):
        as_paths.append(lines[i+1].split('AS Path: ')[1].strip("[").strip("]\n").replace("'", "").split(", "))

print(len(as_paths))
# Count frequency of each ASN in AS paths
# Count the number of times the origin prefix has repeated itself in an AS path
origin_prefix_count = [path.count(path[-1]) for path in as_paths]
count = {}
for i in range(len(as_paths)):
    count[as_paths[i][-1]] = []
for i in range(len(as_paths)):
    count[as_paths[i][-1]].append(as_paths[i].count(as_paths[i][-1]))

print(count)

count1 = sum(1 for values in count.values() if len(set(values)) > 1)
max_values = {key: max(values) for key, values in count.items()}

fig, ax2 = plt.subplots()
# Bar chart for max value for each key
ax2.bar(max_values.keys(), max_values.values(), color='tab:orange')
ax2.set_title('Max value for each key')
ax2.set_xlabel('Key')
ax2.set_ylabel('Max Value')
ax2.tick_params(axis='x', labelrotation=45)

# Set title for the figure
fig.suptitle('Multi-series bar chart')

# Display the plot
plt.show()
