#################################
##### README: CLI_roomba.py #####
######### Leah Stern ############
#################################

##### How to run this program
This program simulates the actions of a Roomba vacuum cleaner using a node-based behavior
tree. The program uses click and runs as a CLI. Run the program with the following command:
    
    python3 CLI_roomba.py --help

in a terminal for help running the program with the proper tags. As the help page states,
use '-c' as a tag before each type of cleaning you would like the Roomba to perform. For
example,

    python3 CLI_roomba.py -c general -c spot

will tell the Roomba to do both general cleaning and spot cleaning.

##### Background information
I created this program for an assignment on behavior trees in an artificial intelligence
course. My program's architecture is based on the behavior tree structure provided for
the assignment. An image of the behavior tree is included in this repository under the 
file name "behavior_tree.jpg."