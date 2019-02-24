# Leah Stern
# Roomba Vacuum Behavior Tree

import click

# Functions to print in color. I found these in GeeksforGeeks article "Print
# Colors in Python terminal." 
# https://www.geeksforgeeks.org/print-colors-python-terminal/.
def prRed(skk): print("\033[91m {}\033[00m".format(skk), end="\n")
def prPurple(skk): print("\033[95m {}\033[00m".format(skk), end="\n")
def prCyan(skk): print("\033[96m {}\033[00m".format(skk), end="\n")

####### CONSTANTS ##############
# Composite types
SEQ = "sequence"
SEL = "selection"

# Condition types
SPOT = "spot"
GENERAL = "general"
DUSTY = "dusty spot"
BATT = "battery check"

# Task types
CLN_SPOT = "clean spot"
CLN_GEN = "clean general"
CLN_DUSTY = "clean dusty spot"
DONE_SPOT = "done spot cleaning"
DONE_GEN = "done general cleaning"
FIND_HOME = "find home"
GO_HOME = "go home"
DOCK = "dock"
NOTHING = "do nothing"

# Decorator types
T20 = "20s timer"
T35 = "35s timer"
UFAIL = "until fail"
NEGATE = "negate"

# States
RUN = "running"
SUCCESS = "success"
FAIL = "failure"
##############################

# Blackboard for input, represented as dictionary including battery level,
# commands, and path home
roomba_blackboard = {
	"battery_level" : 100,
	"spot_clean"    : False,
	"general_clean" : False,
	"dusty_spot"    : False,
	"path_home"     : None
}

@click.command()
# Option that allows user to choose spot, general, and/or dusty spot cleaning
@click.option(
	'--clean',
	'-c',
	type=click.Choice(['spot', 'general', 'dusty']),
	multiple=True,
	help='use "-c" as a flag before each type of cleaning you would like!' 
	)

# Main!
def main(clean):
	# Greet the user, reiterate the options they chose
	print("Welcome to Roomba!")
	print("Looks like you need", ' and '.join(x for x in clean), "cleaning.")

	# Update blackboard with user preferences
	if 'spot' in clean:
		roomba_blackboard["spot_clean"] = True
	if 'general' in clean:
		roomba_blackboard["general_clean"] = True
	if 'dusty' in clean:
		roomba_blackboard["dusty_spot"] = True

	# Build behavior tree
	tree = buildTree(roomba_blackboard)

	# Print blackboard before running tree
	prPurple("\n\033[4mBlackboard before running tree:\033[0m")
	print(roomba_blackboard)

	# Run and print tree traversal
	printTreeStatus(tree, roomba_blackboard)

	# Print blackboard after running tree
	prPurple("\n\033[4mBlackboard after running tree:\033[0m")
	print(roomba_blackboard)

# Class for composite nodes, including string value, children nodes, 
# a decorator if necessary, and state of node.
class Composite(object):
	def __init__(self, value, children, decorator=None, state=None):
		self.value = value
		self.children = children
		self.decorator = decorator
		self.state = state

# Class for condition nodes, including string value, a decorator if necessary, 
# and state of node.
class Condition(object):
	def __init__(self, value, decorator=None, state=None):
		self.value = value
		self.decorator = decorator
		self.state = state

# Class for task nodes, including string value, a decorator if necessary, 
# and state of node.
class Task(object):
	def __init__(self, value, decorator=None, state=None):
		self.value = value
		self.decorator = decorator
		self.state = state

# Class for decorator nodes, including string value and state of node.
class Decorator(object):
	def __init__(self, value, state=None):
		self.value = value
		self.state = state

# Class for full behavior tree, made up of the left, middle, and right subtrees.
class behaviorTree(object):
	def __init__ (self, leftTree, middleTree, rightTree):
		self.left = leftTree
		self.middle = middleTree
		self.right = rightTree

# Builds behavior tree by creating subtrees and joining them into one whole
# behavior tree.
def buildTree(blackboard):
	# Left subtree
	# Initialize state values as SUCCESS since the path home is trivial
	leftTree = Composite("sequence", [Condition(BATT, None, SUCCESS), 
		                              Task(FIND_HOME, None, SUCCESS),
		                              Task(GO_HOME, None, SUCCESS),
		                              Task(DOCK, None, SUCCESS)], None, FAIL)

	# Middle subtree
	# Initialize all state values as FAIL to begin
	middleTree = Composite(SEL, [Composite(SEQ, 
								  [Condition(SPOT, None, FAIL),
		            			   Task(CLN_SPOT, Decorator(T20), FAIL), 
		            			   Task(DONE_SPOT, None, FAIL)], FAIL),
								 Composite(SEQ, 
								  [Condition(GENERAL, None, FAIL),
								   Composite(SEQ, 
								    [Composite(SEQ, 
								      [Condition(BATT, Decorator(NEGATE), FAIL),
									   Composite(SEL, 
									    [Composite(SEQ, 
										  [Condition(DUSTY, None, FAIL), 
										   Task(CLN_DUSTY, Decorator(T35), FAIL)],
										  FAIL),
										 Task(CLN_GEN, None, FAIL)], None, FAIL)], 
									  Decorator(UFAIL), FAIL),
									  Task(DONE_GEN, None, FAIL)], None, FAIL)], None, FAIL)],
						   None, FAIL)

	# Right subtree
	# Initialize state to FAIL to begin
	rightTree = Task(NOTHING, None, FAIL)

	return behaviorTree(leftTree, middleTree, rightTree)

# Run each subtree and get its status
def printTreeStatus(tree, blackboard):
	if tree == None: return

	# Get left subtree status and print
	left = runTree(tree, blackboard, 1)
	prettyPrintTreeStatus("Left", left)

	# Get middle subtree status and print
	middle = runTree(tree, blackboard, 2)
	prettyPrintTreeStatus("Middle", middle)

	# Get right subtree status and print
	right = runTree(tree, blackboard, 3)
	prettyPrintTreeStatus("Right", right)

# Runs given portion of behavior tree based on the priority value
def runTree(tree, blackboard, priority):
	# If priority is 1, traverse left subtree
	if priority == 1:
		prPurple("\n\033[4mLEFT SUBTREE:\033[0m")
		status = runLeft(tree.left, blackboard)
		return status

	# If priority is 3, traverse middle subtree
	elif priority == 2:
		prPurple("\n\033[4mMIDDLE SUBTREE:\033[0m")
		status = runMiddle(tree.middle, blackboard)
		return status

	# If priority is 3, traverse right subtree
	elif priority == 3:
		prPurple("\n\033[4mRIGHT SUBTREE:\033[0m")
		status = runRight(tree.right, blackboard)
		return status

# Traverse left subtree
def runLeft(tree, blackboard):
	# Set current state to running until it returns success or failure
	tree.state = RUN

	# Loop through children
	for idx in range(len(tree.children)):
		curr = tree.children[idx]

		# Go home to charge battery if battery < 30%
		if curr.value == BATT:
		 	if blackboard["battery_level"] < 30:
		 		# Set battery check condition to FAIL
		 		prRed("\nBattery low. Going home to charge.\n")
		 		curr.state = FAIL

		 	# Return if battery level is sufficient
		 	else: 
		 		print("\nBattery sufficient.")
		 		return SUCCESS
		
		# Print current node and its status
		print(curr.value, ": ", curr.state, sep="")

		# Once we reach dock, set battery_level to 100% and set
		# battery check condition to SUCCESS
		if curr.value == DOCK and tree.children[idx-3].state == FAIL:
			if curr.state == SUCCESS:
				blackboard["battery_level"] = 100

				tree.children[idx-3].state = SUCCESS
				print(tree.children[idx-3].value, ": ", tree.children[idx-3].state, sep="")

	return checkStatus(tree)

# Traverse middle subtree
def runMiddle(tree, blackboard):
	# Set current state to running until it returns success or failure
	tree.state = RUN

	if tree.children:
		for idx in range(len(tree.children)):
			curr = tree.children[idx]

			if curr.value == SPOT:
				# If spot clean is true in blackboard, clean spot
				if blackboard["spot_clean"] == True:
					# SPOT condition is true
					curr.state = SUCCESS

					# Run spot clean for as long as decorator entails
					timer = tree.children[idx+1].decorator.value
					spotClean(timer, blackboard)

					# Set clean spot and done spot tasks to SUCCESS
					tree.children[idx+1].state = SUCCESS
					tree.children[idx+2].state = SUCCESS

					# Set blackboard value to False
					blackboard["spot_clean"] = False

				# If spot clean is false in blackboard, set to FAIL
				else: 
					curr.state = FAIL
					print("\n", curr.value, ": ", curr.state, sep="", end="")
					print("\nNo spot cleaning. Breaking from sequence.")
					break

			if curr.value == GENERAL:
				# If general clean is true in blackboard, general clean
				if blackboard["general_clean"] == True:
					# GENERAL condition is true
					curr.state = SUCCESS

				# If general clean is false in blackboard, set to FAIL and break
				else: 
					curr.state = FAIL
					print("\n", curr.value, ": ", curr.state, sep="", end="")
					print("\nNo general cleaning. Breaking from sequence.")
					break

			if curr.value == BATT:
				# If BATT condition has a negation decorator, negate it
				if curr.decorator.value == NEGATE:
					if blackboard["battery_level"] >= 30:
						curr.state = SUCCESS

					# If battery level is insufficient, set to FAIL
					else: curr.state = FAIL

			if curr.value == DUSTY:
				# If dusty spot is true in blackboard, set condition to SUCCESS
				if blackboard["dusty_spot"] == True:
					curr.state = SUCCESS

					# Run spot clean for as long as decorator entails
					timer = tree.children[idx+1].decorator.value
					spotClean(timer, blackboard)

					# Set clean spot task to SUCCESS
					tree.children[idx+1].state = SUCCESS

					# Set blackboard value back to False
					blackboard["dusty_spot"] = False

				# If dusty spot is false in blackboard, set to FAIL
				else: 
					curr.state = FAIL
					print("\n", curr.value, ": ", curr.state, sep="", end="")
					print("\nNo dusty spot. Breaking from sequence.")
					break

			if curr.value == CLN_GEN:
				if blackboard["general_clean"] == True:
					# Run general cleaning until battery needs recharging
					generalClean(blackboard)
					curr.state = SUCCESS

				# If general clean is false in blackboard, set to FAIL
				else: curr.state = FAIL

			if curr.value == DONE_GEN:
				if blackboard["general_clean"] == True:
					curr.state = SUCCESS
					blackboard["general_clean"] = False

			# Keep traversing if we find a composite
			if curr.value == SEQ or curr.value == SEL:
				runMiddle(curr, blackboard)
			else:
				print("\n", curr.value, ": ", curr.state, sep="")

	return checkStatus(tree)

# Traverse right subtree
def runRight(tree, blackboard):
	# Set current state to running until it returns success or failure
	tree.state = RUN

	# Do nothing!
	tree.state = SUCCESS
	print("\n", tree.value, ": ", tree.state, sep="")

	return tree.state

# Performs spot cleaning for a given number of seconds
def spotClean(timer, blackboard):
	# Clean for 20 seconds
	if timer == T20:
		for timeStamp in range(20):
			blackboard["battery_level"] -= 1

	# Clean for 35 seconds
	elif timer == T35:
		for timeStamp in range(35):
			blackboard["battery_level"] -= 1

# Performs general cleaning until battery needs to be recharged
def generalClean(blackboard):
	while blackboard["battery_level"] >= 30:
		blackboard["battery_level"] -=1

# Checks status of tree based on whether the root node is a composite and is 
# either a sequence or a selection.
def checkStatus(tree):
	# Find number of children that return SUCCESS
	num_success = 0
	for child in tree.children:
		if child.state == SUCCESS: num_success += 1

	# If root node is a sequence, all children must return success
	if tree.value == SEQ:
		# Return success if all children succeed, otherwise return failure
		if num_success == len(tree.children): tree.state = SUCCESS
		else: tree.state = FAIL

	# If root node is a selection, only one child must return success
	elif tree.value == SEL:
		# Return success if at least one child succeeded
		if num_success >= 1: tree.state = SUCCESS
		else: tree.state = FAIL

	prettyPrintCompositeStatus(tree, tree.state)
	return tree.state

# Prints composite statuses in blue if SUCCESS and red if FAIL
def prettyPrintCompositeStatus(tree, status):
	# Print in blue if SUCCESS
	if status == SUCCESS:
		print("\n", tree.value, ": ", sep='', end="")
		prCyan(status)

	# Print in red if FAIL
	elif status == FAIL:
		print("\n", tree.value, ": ", sep='', end="")
		prRed(status)

# Prints subtree statuses in blue if SUCCESS and red if FAIL
def prettyPrintTreeStatus(subtree, status):
	# Print in blue if SUCCESS
	if status == SUCCESS:
		print("\n>>", subtree, "subtree status: ", end="")
		prCyan(status)

	# Print in red if FAIL
	elif status == FAIL:
		print("\n>>", subtree, "subtree status: ", end="")
		prRed(status)

# Run main() when program executed as script
if __name__ == "__main__":
	main()