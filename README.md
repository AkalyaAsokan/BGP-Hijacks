# Detecting BGP hijacks on the Internet
## CS4450/CS5456

This repository contains code for detecting and visualizing BGP hijacks. Below are the instructions for running the code:

1. Clone the repository

2. Run training.py to extract the training data and create a file. 

_(Please note that the data collected for the project is not present in the repository as it is about 20GB in size, and GitHub does not allow uploading such large files. Instead, smaller files have been created for debugging and testing purposes from different route collectors and various times, which are present in the /Data folder. When you use these data, make sure to change the path of the file when running any other code to the name of the file that you want to train the model on. Additionally, note that the project uses specific route collectors for specific time frames, so using data in the folder may or may not give accurate results. For accurate results, it is recommended to download the code, run training.py and use the training data obtained from that.)_

3. Run main.py to execute the program. 
    - This file is the central point of contact for all the remaining files. 
    - It runs visualizations.py to visualize the data (shows some network graphs about connections between ASes and interesting facts about AS prepending and information on ASes that frequently do this)
    - It also runs each of the detectors, and collects data about the attacks. _Note that when each detector is run, a live animation of the hijacks will be shown. Once a particular detector completes running, the graph has to be closed to continue running the rest of the code._
    - Finally, main.py displays graphs regarding the time of attacks and the number of attacks split across various stages and types of hijacks.
