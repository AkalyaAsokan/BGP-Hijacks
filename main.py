
## main.py is run after training.py

# Importing cProfile, a built-in python module that can perform profiling
# to get total run time taken by each detector
import cProfile
# Importing moas_detector.py
from moas_detector import MoasDetector
# Importing visualizations.py
from visualizations import Visualize

########################### VISUALISING TRAINING DATA ############################

visualize = Visualize()

def visualize_training_data():
    visualize.start()

################################ MOAS DETECTOR ###################################

moas_detector = MoasDetector()

def moas():
    moas_detector.start()

#################################### MAIN ########################################

if __name__ == '__main__':
    # Visualising training data
    visualize_training_data()
    cProfile.run('moas()')
    # plot graph
