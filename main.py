
## main.py is run after training.py

# Importing custom detector classes and visualization functions
from moas_detector import MoasDetector
from sub_moas_detector import SubMoasDetector
from fake_path_detector import FakePathDetector
from defcon_16_detector import Defcon16Detector
from visualizations import Visualize

# Importing plotly, a popular library for creating interactive visualizations
import plotly.graph_objects as go
import plotly.express as px
import pandas as pd

# List of [record number with attack, ASN that attacked]
moas_attacks = []
sub_moas_attacks = []
fake_path_attacks = []
defcon_16_attacks = []

def modifyList(lst):
    # Initialize result with the first inner list
    result = [[lst[0][0], lst[0][1]]]  
    for i in range(1, len(lst)):
        diff = lst[i][0] - lst[i-1][0]
        result.append([diff, lst[i][1]])
    return result

# This function helps plot three graphs - Number of Attacks in the first 2000 Records (stored with suffix '_attack_1'), 3000 Records (stored with suffix '_attack_2') and 5000 Records (stored with suffix '_attack_3')
def count_attacks(attack_list):
    attack_times = {'{}_attacks_3'.format(attack_list[0][2]): 0, '{}_attacks_1'.format(attack_list[0][2]): 0, '{}_attacks_2'.format(attack_list[0][2]): 0}
    
    count = 0
    for lst in attack_list:
        count = count + lst[0]
        if(count > 2000):
            attack_times['{}_attacks_2'.format(attack_list[0][2])] += 1
            attack_times['{}_attacks_3'.format(attack_list[0][2])] += 1
        if(count > 3000):
            attack_times['{}_attacks_3'.format(attack_list[0][2])] += 1
        else:
            attack_times['{}_attacks_1'.format(attack_list[0][2])] += 1
            attack_times['{}_attacks_2'.format(attack_list[0][2])] += 1
            attack_times['{}_attacks_3'.format(attack_list[0][2])] += 1
    return attack_times

def plot_attacks(attack_times):
    fig = go.Figure(data=[go.Bar(name='Number of Attacks', x=['moas_attacks', 'sub_moas_attacks', 'fake_path_attacks', 'defcon_16_attacks'], y=[attack_times['MOAS Attack_attacks_1'], attack_times['Sub MOAS Attack_attacks_1'], attack_times['Fake path Hijacks_attacks_1'], attack_times['Defcon #16 Hijacks_attacks_1']])])
    fig.update_layout(title='Number of Attacks for Each Type', xaxis_title='Type of Attack', yaxis_title='Number of Attacks in the first 2000 Records')
    fig.show()
    fig = go.Figure(data=[go.Bar(name='Number of Attacks', x=['moas_attacks', 'sub_moas_attacks', 'fake_path_attacks', 'defcon_16_attacks'], y=[attack_times['MOAS Attack_attacks_2'], attack_times['Sub MOAS Attack_attacks_2'], attack_times['Fake path Hijacks_attacks_2'], attack_times['Defcon #16 Hijacks_attacks_2']])])
    fig.update_layout(title='Number of Attacks for Each Type', xaxis_title='Type of Attack', yaxis_title='Number of Attacks in the first 3000 Records')
    fig.show()
    fig = go.Figure(data=[go.Bar(name='Number of Attacks', x=['moas_attacks', 'sub_moas_attacks', 'fake_path_attacks', 'defcon_16_attacks'], y=[attack_times['MOAS Attack_attacks_3'], attack_times['Sub MOAS Attack_attacks_3'], attack_times['Fake path Hijacks_attacks_3'], attack_times['Defcon #16 Hijacks_attacks_3']])])
    fig.update_layout(title='Number of Attacks for Each Type', xaxis_title='Type of Attack', yaxis_title='Number of Attacks in the first 5000 Records')
    fig.show()

########################### VISUALISING TRAINING DATA ############################

visualize = Visualize()

def visualize_training_data():
    visualize.start()

################################ MOAS DETECTOR ###################################

moas_detector = MoasDetector()

def moas(start_time, end_time):
    moas_detector.start(start_time, end_time)
    return modifyList(moas_detector.attack)

################################ SUB MOAS DETECTOR ###################################

sub_moas_detector = SubMoasDetector()

def sub_moas(start_time, end_time):
    sub_moas_detector.start(start_time, end_time)
    return modifyList(sub_moas_detector.attack)

################################ FAKE PATH DETECTOR ###################################

fake_path_detector = FakePathDetector()

def fake_path(start_time, end_time):
    fake_path_detector.start(start_time, end_time)
    return modifyList(fake_path_detector.attack)

################################ DEFCON #16 DETECTOR ###################################

defcon_16_detector = Defcon16Detector()

def defcon_16(start_time, end_time):
    defcon_16_detector.start(start_time, end_time)
    return modifyList(defcon_16_detector.attack)

#################################### MAIN ########################################


if __name__ == '__main__':

    # Visualising training data
    visualize_training_data()

    # Setting the start and end time for the detection window
    start_time = "2017-07-08 01:00:00"
    end_time = "2017-07-15 01:00:00"

    # Running the MOAS detector with the specified start and end times and storing the result in moas_attacks
    moas_attacks = moas(start_time, end_time)
    print(moas_attacks)

    # Running the Sub-MOAS detector with the specified start and end times and storing the result in sub_moas_attacks
    sub_moas_attacks = sub_moas(start_time, end_time)
    print(sub_moas_attacks)

    # moas = 2 july (works), 2 train
    # Running the Fake Path detector with the specified start and end times and storing the result in fake_path_attacks
    fake_path_attacks = fake_path(start_time, end_time)
    print(fake_path_attacks)

    # Running the Defcon-16 detector with the specified start and end times and storing the result in defcon_16_attacks
    defcon_16_attacks = defcon_16(start_time, end_time)
    print(defcon_16_attacks)

    # Open a file called "attacks.txt" for writing
    with open("attacks1.txt", "w") as f:
        # Write the attacks to the file using the print() function
        print("MOAS Attacks:", moas_attacks, file=f)
        print("Sub-MOAS Attacks:", sub_moas_attacks, file=f)
        print("Fake Path Attacks:", fake_path_attacks, file=f)
        print("DEFCON 16 Attacks:", defcon_16_attacks, file=f)


    # Append it with type of attack for plotting graphs
    moas_attacks = [[count, asn, 'MOAS Attack'] for count, asn in moas_attacks]
    sub_moas_attacks = [[count, asn, 'Sub MOAS Attack'] for count, asn in sub_moas_attacks]
    fake_path_attacks = [[count, asn, 'Fake path Hijacks'] for count, asn in fake_path_attacks]
    defcon_16_attacks = [[count, asn, 'Defcon #16 Hijacks'] for count, asn in defcon_16_attacks]


    # Combine all attack lists into a single list
    all_attacks = moas_attacks + sub_moas_attacks + fake_path_attacks + defcon_16_attacks

    # Create a pandas DataFrame with the combined data
    df_count = pd.DataFrame(all_attacks, columns=['count', 'asn', 'type'])

    # Plot the bar chart
    fig4 = px.bar(
        data_frame=df_count,
        x='type',
        y='count',
        barmode='stack'
    )

    # Set the x-axis title
    fig4.update_xaxes(title_text='Type of Attack')

    # Set the y-axis title
    fig4.update_yaxes(title_text='Occurrence of Attacks by Record Number')

    # Show the plot of the Occurrences of Attacks by Record Number for each of the 4 types of attacks
    fig4.show()

    moas_attack_times = count_attacks(moas_attacks)

    sub_moas_attack_times = count_attacks(sub_moas_attacks)

    fake_path_attack_times = count_attacks(fake_path_attacks)

    defcon_16_attack_times = count_attacks(defcon_16_attacks)

    combined_attack_times = {}
    combined_attack_times.update(moas_attack_times)
    combined_attack_times.update(sub_moas_attack_times)
    combined_attack_times.update(fake_path_attack_times)
    combined_attack_times.update(defcon_16_attack_times)
    plot_attacks(combined_attack_times)

