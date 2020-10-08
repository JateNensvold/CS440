# Agent.py
#
# This code works only for the testworld that comes with the simulator.

import Action
import Orientation
import Search
import Percept


class location():
    '''
    A class that checks if a location is valid
    '''

    def __init__(self, Agent, x, y):
        '''

        '''


class Agent:
    def __init__(self):
        self.searchEngine = Search.SearchEngine()
        self.Initialize()

    def __del__(self):
        pass

    def Initialize(self):

        self.agentHasGold = False
        self.agentHasArrow = True
        self.actionList = []
        self.visited = set()
        self.frontier = set()
        self.direction = Orientation.RIGHT
        self.location = (1, 1)
        self.stench = set()
        self.glitter = None
        self.breeze = set()
        self.scream = set()
        self.wumpus = True
        self.lastAction = None
        self.lastLocation = None

    # Input percept is a dictionary [perceptName: boolean]
    def Process(self, percept: Percept.Percept) -> int:

        # Update World state with incoming information
        self.updatePercept(percept)

        # If there is no action list determine actions
        if (not self.actionList):
            # Look for gold if it is not found yet
            if (not self.agentHasGold):
                # Grab gold if location is known
                if self.glitter is tuple:
                    self.actionList += self.searchEngine.FindPath(
                        list(self.location), self.direction,
                        list(self.glitter), Orientation.RIGHT)
                # Find new locations to search
                else:
                    self.actionList += self.searchEngine.FindPath(
                        list(self.location), self.direction,
                        list(self.frontier.pop()), Orientation.RIGHT)
            # Go to ladder if gold is already collected
            else:
                self.actionList += self.searchEngine.FindPath(
                    self.location, self.direction, [1, 1, ], Orientation.RIGHT)
                self.actionList.append(Action.CLIMB)
        action = self.actionList.pop(0)
        # Update world with information about action that is returned
        self.processAction(action)
        return action

    def processAction(self, action: int):

        def CLIMB():
            # Update action for climbing
            pass

        def GRAB():
            # Update action for grabbing
            self.agentHasGold = True

        def SHOOT():
            # Update action for shooting
            self.arrow = False

        def GOFORWARD():
            # Update action for moving
            self.lastLocation = self.location
            if self.direction == Orientation.LEFT:
                self.location = tuple([self.location[0] - 1, self.location[1]])
            elif self.direction == Orientation.RIGHT:
                self.location = tuple([self.location[0] + 1, self.location[1]])
            elif self.direction == Orientation.UP:
                self.location = tuple([self.location[0], self.location[1] + 1])
            elif self.direction == Orientation.DOWN:
                self.location = tuple([self.location[0], self.location[1] - 1])

        def TURNLEFT():
            # Update action for turning left
            self.direction = (self.direction + 1) % 4

        def TURNRIGHT():
            # Update action for turning right
            tempDirection = self.direction - 1
            self.direction = Orientation.DOWN if tempDirection < 0 \
                else tempDirection

        # Correlate actions to action updates
        actionsDict = {Action.CLIMB: CLIMB,
                       Action.GOFORWARD: GOFORWARD,
                       Action.GRAB: GRAB,
                       Action.SHOOT: SHOOT,
                       Action.TURNLEFT: TURNLEFT,
                       Action.TURNRIGHT: TURNRIGHT}

        # Update map state by calling action update method
        actionsDict[action]()
        self.lastAction = action

    def updatePercept(self, percept: Percept.Percept):
        '''
        Updates world state based on percepts found

        Args:
            percept: Percept.Percept with information about current location
        Returns:
            None
        '''
        self.worldSize = max(self.location[0], self.location[1])
        if percept.breeze:
            self.breeze.add(self.location)
        if percept.bump:
            # Update location to last location
            self.visited.add(self.location)
            self.location = self.lastLocation
        if percept.glitter:
            # Track location of glitter
            self.glitter = self.location
            self.actionList.append(Action.GRAB)
        if percept.scream:
            # Track if wumpus is alive
            self.wumpus = False
        if percept.stench:
            # Track location of wumpus
            self.stench.add(self.location)

        self.searchEngine.AddSafeLocation(self.location[0], self.location[1])

        # Add safe adjacent locations
        self.addAdjacent()

        self.visited.add(self.location)

    def addAdjacent(self):
        adjacent = []
        adjacent.append(tuple([self.location[0] + 1, self.location[1]]))
        adjacent.append(tuple([self.location[0] - 1, self.location[1]]))
        adjacent.append(tuple([self.location[0], self.location[1] + 1]))
        adjacent.append(tuple([self.location[0], self.location[1] - 1]))
        print("current", self.location)
        for i in adjacent:
            print(i)
            if i not in self.breeze and i not in self.stench:
                if i[0] > 0 and i[1] > 0 and i[0]:
                    if i not in self.visited:
                        self.frontier.add(i)
                    self.searchEngine.AddSafeLocation(i[0], i[1])
        print("safe", self.searchEngine.safeLocations)

    def GameOver(self, score):
        pass
