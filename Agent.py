import math
import copy
import random
import time
from Simulator import Simulator


# Main Agent class
class Agent:
    def __init__(self, size, timeLimit):
        self.simulator = Simulator(size)  # Simulator instance of the farm
        self.monteCarlo = MonteCarloTreeSearch(size)  # Instance of the MonteCarloTreeSearch
        self.timeLimit = timeLimit  # Limit of time for action (in seconds)
        self.totalFood = 0  # Total food harvested by the agent

    def run(self):
        while not self.simulator.complete:
            nextMove = self.monteCarlo.findNextMove(self.simulator, self.timeLimit)  # Decide next action
            self.totalFood += makeMove(self.simulator, nextMove)  # Execute it
            print(nextMove.actionName)  # Print action completed
        print("Total food units: " + str(self.totalFood))


# Helper function that applies the action contained in move to the simulator instance
def makeMove(simulator, move):
    if move.action == 0:
        return simulator.plantBean(move.actionX, move.actionY)
    elif move.action == 1:
        return simulator.plantCorn(move.actionX, move.actionY)
    elif move.action == 2:
        return simulator.harvest(move.actionX, move.actionY)
    else:
        return simulator.simulateDay()


# Class that implements the MonteCarloTreeSearch
class MonteCarloTreeSearch:
    def __init__(self, size):
        self.size = size
        self.tree = Tree(size)
        self.maxScore = 15 * size * size  # this is an approximation of the max score possible,
        # to have the scores in a range from 0 to 1

    def findNextMove(self, simulator, timeLimit):
        start_time = time.time()
        while time.time() - start_time < timeLimit:
            # Creates a copy of the simulator, all the moves will be applied in this copy
            tempSimulator = copy.deepcopy(simulator)
            # Select a Leaf Node from the tree and applies all the moves to the simulator
            leaf = self.selectLeafNode(self.tree.root, tempSimulator)
            if not tempSimulator.complete:
                # If the node is not terminal expands it
                self.expandNode(leaf)
            nodeToExplore = leaf
            if len(leaf.children) > 0:
                # Selects a random Child from the Leaf and applies that action to the simulator
                nodeToExplore = leaf.getRandomChild(tempSimulator)
            # Applies random movements to the last node and gets the final score
            simulationResult = self.simulateRandomPlay(nodeToExplore, tempSimulator)
            # Applies the score to the all the explored nodes involved
            self.backPropagation(nodeToExplore, simulationResult)
        # Selects the best child
        bestChild = self.tree.root.getBestChild()
        self.tree.root = bestChild
        bestChild.parent = False
        # Return the action
        return bestChild.action

    # Selects the best child now using UCB score until reach a leaf Node, if one of the actions is not possible,
    # removes it from the children and selects another
    def selectLeafNode(self, node, simulator):
        while len(node.children) > 0:
            success = -1
            while success == -1:
                best = None
                bestScore = -1
                for child in node.children:
                    score = child.getUCBscore()
                    if score > bestScore:
                        best = child
                        bestScore = score
                success = makeMove(simulator, best.action)
                if success == -1:
                    node.children.remove(best)
            best.food = node.food + success
            node = best
        return node

    # Expand the node, creating a new child for each possible Move
    def expandNode(self, node):
        possibleMoves = node.getPossibleMoves()
        for action in possibleMoves:
            newNode = Node(self.size, action)
            newNode.parent = node
            node.children.append(newNode)

    # Simulate 'random' plays from the simulator and returns the efficiency of the farm
    def simulateRandomPlay(self, node, simulator):
        food = node.food
        while not simulator.complete:
            food += self.randomMove(simulator)
        return food / self.maxScore

    # Applies the score to all the nodes until reach the root
    def backPropagation(self, node, score):
        while node:
            node.score += score
            node.visitCount += 1
            node = node.parent

    # Generate a 'random' move, it will only call simulateDay() if there is not any other option
    def randomMove(self, simulator):
        possibleMoves = self.size * self.size * 3
        move = random.randint(0, possibleMoves - 1)
        success = -1
        count = 0
        while count < possibleMoves and success == -1:
            opt = move % 3
            posX = int(move / 3) % self.size
            posY = int(int(move / 3) / self.size)
            if opt == 0:
                success = simulator.plantBean(posX, posY)
            elif opt == 1:
                success = simulator.plantCorn(posX, posY)
            else:
                success = simulator.harvest(posX, posY)
            count += 1
            move = (move + 1) % possibleMoves
        if success == -1:
            success = simulator.simulateDay()
        return success


# Tree class used by the MonteCarlo Tree Search
class Tree:
    def __init__(self, size):
        action = Action(-1, 0, 0)
        self.root = Node(size, action)


# Node class
class Node:
    def __init__(self, size, action):
        self.size = size
        self.action = action  # Information about the last action performed to reach the node
        self.parent = None  # Parent of the Node
        self.children = []  # List of child nodes
        self.visitCount = 0.0  # Number of visits to this node
        self.score = 0.0  # Sum of all the scores obtained by this node
        self.c = 1.41
        self.food = 0  # Food harvested until this node

    # Returns the UCB score of the node
    def getUCBscore(self):
        if self.visitCount == 0.0:
            return 1000000
        else:
            return self.score / self.visitCount + self.c * math.sqrt(math.log(self.parent.visitCount) / self.visitCount)

    # Returns the child with best average score
    def getBestChild(self):
        best = None
        bestScore = -1
        for child in self.children:
            score = child.score / child.visitCount if child.visitCount > 0 else 0
            if score > bestScore:
                bestScore = score
                best = child
        return best

    # Returns a random child node and applies the action contained by it to the simulator,
    # if the action is not valid it chooses a different child and remove the previous from the list
    def getRandomChild(self, simulator):
        success = -1
        while success == -1:
            childNumber = random.randint(0, len(self.children) - 1)
            success = makeMove(simulator, self.children[childNumber].action)
            if success == -1:
                self.children.remove(self.children[childNumber])
        self.children[childNumber].food = self.food + success
        return self.children[childNumber]

    # Generate an array containing all the possible actions
    def getPossibleMoves(self):
        possibleMoves = []
        action = Action(3, 0, 0)
        action.actionName = "Next day"
        possibleMoves.append(action)

        for i in range(self.size):
            for j in range(self.size):
                action = Action(0, i, j)
                action.actionName = "Plant beans in: " + str(i) + "," + str(j)
                possibleMoves.append(action)
                action = Action(1, i, j)
                action.actionName = "Plant corn in: " + str(i) + "," + str(j)
                possibleMoves.append(action)
                action = Action(2, i, j)
                action.actionName = "Harvest: " + str(i) + "," + str(j)
                possibleMoves.append(action)
        return possibleMoves


# Indicates an action performed by the agent
class Action:
    def __init__(self, action, x, y):
        self.actionName = None  # Description of the action
        self.action = action  # 0 plant beans, 1 plant corn, 2 harvest, 3 next day
        self.actionX = x  # coordinate x of the action (for plant or harvest)
        self.actionY = y  # coordinate y of the action (for plant or harvest)
