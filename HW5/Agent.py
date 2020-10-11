# Agent.py
#
# This code works only for the testworld that comes with the simulator.

import Action
import Orientation
import Search
import Percept


class Agent:
    def __init__(self):
        '''
        Initialze the Agent for the first time
        '''
        self.Initialize()
        self.searchEngine = Search.SearchEngine()

    def __del__(self):
        pass

    def Initialize(self):
        '''
        Called on Agent between test runs to reset to initial state
        All information gathered about a test world is kept
        '''
        self.agentHasGold = False
        self.agentHasArrow = True
        self.actionList = []
        self.visited = set()
        self.frontier = []
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
        '''
        Process a turn inside the wumpus world

        Args:
            percept: a Percept object containing information about
                the current tile
        Return:
            Action to take on world
        '''

        # Update World state with incoming information
        self.updatePercept(percept)

        # If there is no action list determine actions
        if (len(self.actionList) == 0):
            # Look for gold if it is not found yet
            if (not self.agentHasGold):
                # Grab gold if location is known
                if self.glitter is tuple:
                    self.actionList += self.searchEngine.FindPath(
                        list(self.location), self.direction,
                        list(self.glitter), Orientation.RIGHT)
                # Find new locations to search from frontier
                elif len(self.frontier) > 0:
                    self.actionList += self.searchEngine.FindPath(
                        list(self.location), self.direction,
                        list(self.frontier.pop(0)), Orientation.RIGHT)
                # No locations on frontier, solve wumpus/pit problems
                else:
                    self.findSafeLocation()
                    # If safeLocations adds to frontier pop new location
                    if len(self.frontier) > 0:
                        self.actionList += self.searchEngine.FindPath(
                            list(self.location), self.direction,
                            list(self.frontier.pop(0)), Orientation.RIGHT)
                    # If No more safe locations to search, return to ladder
                    #       without gold
                    else:
                        self.actionList += self.searchEngine.FindPath(
                            self.location, self.direction, [1, 1, ],
                            Orientation.RIGHT)
                        self.actionList.append(Action.CLIMB)
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
        '''
        A function that updates the Agent with the action that is getting
        called.

        Args:
            action: the action update the world for
        Returns:
            None
        '''

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
        self.visited.add(self.location)

        self.percept = percept
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
            self.actionList = [Action.GRAB]
        if percept.scream:
            # Track if wumpus is alive
            self.wumpus = False
        if percept.stench:
            # Track location of wumpus
            self.stench.add(self.location)

        self.searchEngine.AddSafeLocation(self.location[0], self.location[1])

        # Add safe adjacent locations
        self.addAdjacent()

    def addAdjacent(self):
        '''
        Add all valid adjacent locations of the agents current location to the
            frontier
        Args:
            None
        Returns:
            None
        '''
        adjacent = self.getAdjacent(self.location)
        # print("current", self.location)
        # print("breeze", self.breeze)
        # print("stench", self.stench)
        for i in adjacent:
            # if i not in self.breeze and i not in self.stench:
            if self.location not in self.breeze and self.location \
                    not in self.stench:
                if i[0] > 0 and i[1] > 0:
                    if i not in self.visited and i not in self.frontier:
                        self.frontier.append(i)
                        print("adding", i)
                    self.searchEngine.AddSafeLocation(i[0], i[1])
        # print("safe", self.searchEngine.safeLocations)
        # print("visited", self.visited)
        # print("frontier", self.frontier)
        # print("actionList", self.actionList)

    def findSafeLocation(self):
        '''
        Attempt to find a safe location around the wumpus

        Args:
            None
        Return:
            None
        '''
        for i in self.stench:
            adjacent = self.getAdjacent(i)
            unexplored = set()
            for j in adjacent:
                if j not in self.visited and j[0] > 0 and j[1] > 0:
                    unexplored.add(j)
            # Unexplored Adjacent to stench
            for j in unexplored:
                # print("unexplored", j)
                unexploredAdjacent = self.getAdjacent(j)
                # Tiles around unexplored
                for k in unexploredAdjacent:
                    # print("aroundUnexplored", k,
                    #       k in self.visited, k not in self.stench)
                    if k in self.visited and k not in self.stench and \
                            j not in self.frontier and j not in self.visited:
                        self.frontier.append(j)
                        self.searchEngine.AddSafeLocation(j[0], j[1])
                        break
        # print(self.frontier)

    def getAdjacent(self, location: tuple):
        '''
        Get the adjacent tiles for the location passed in

        Args:
            location: location to find adjacent tiles of
        Return:
            List tuples represent "location's" adjacent tiles
        '''
        adjacent = []
        adjacent.append(tuple([location[0] + 1, location[1]]))
        adjacent.append(tuple([location[0] - 1, location[1]]))
        adjacent.append(tuple([location[0], location[1] + 1]))
        adjacent.append(tuple([location[0], location[1] - 1]))
        return adjacent

    def GameOver(self, score):
        '''
        Called when the wumpus world ends

        Args:
            None

        Returns:
            None
        '''
        pass
