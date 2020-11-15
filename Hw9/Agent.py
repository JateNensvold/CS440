# Agent.py
#
# Fall 2020 HW9 Solution
#
# Author: Larry Holder Hw5, Nate Jensvold Hw9

import Action
import Orientation
import Search
import itertools


class Agent:
    def __init__(self):
        # Initialize new agent based on new, unknown world
        self.agentLocation = [1, 1]
        self.agentOrientation = Orientation.RIGHT
        self.agentHasGold = False
        self.lastAction = Action.CLIMB  # dummy action
        self.actionList = []
        self.searchEngine = Search.SearchEngine()
        self.worldSize = 3  # HW5: somewhere between 3x3 and 9x9
        self.worldSizeKnown = False
        self.wumpusLocation = [0, 0]  # unknown
        self.goldLocation = [0, 0]  # unknown
        self.stenchLocations = []
        self.breezeLocations = []
        self.pits = []
        self.visitedLocations = []
        self.safeLocations = []
        self.wumpusDead = False
        self.arrow = True

    def Initialize(self):
        # Initialize agent back to the beginning of the world
        self.agentLocation = [1, 1]
        self.agentOrientation = Orientation.RIGHT
        self.agentHasGold = False
        self.lastAction = Action.CLIMB  # dummy action
        self.actionList = []
        self.wumpusDead = False
        self.arrow = True

    def Process(self, percept):
        actionList2 = []
        self.UpdateState(self.lastAction, percept)
        if (self.actionList == []):
            if (percept.glitter):
                # If there is gold, then GRAB it
                print("Found gold. Grabbing it.")
                self.actionList.append(Action.GRAB)
            elif (self.agentHasGold and (self.agentLocation == [1, 1])):
                # If agent has gold and is in (1,1), then CLIMB
                print("Have gold and in (1,1). Climbing.")
                self.actionList.append(Action.CLIMB)
            elif ((not self.agentHasGold) and (self.goldLocation != [0, 0])):
                # If agent doesn't have gold, but knows its location,
                # then navigate to that location
                print("Moving to known gold location (" + str(
                    self.goldLocation[0]) + "," + str(
                        self.goldLocation[1]) + ").")
                actionList2 = self.searchEngine.FindPath(
                    self.agentLocation, self.agentOrientation,
                    self.goldLocation, self.agentOrientation)
                self.actionList.extend(actionList2)
            elif (self.agentHasGold and (self.agentLocation != [1, 1])):
                # If agent has gold, but isn't in (1,1), then navigate to (1,1)
                print("Having gold. Moving to (1,1).")
                actionList2 = self.searchEngine.FindPath(
                    self.agentLocation, self.agentOrientation,
                    [1, 1], self.agentOrientation)
                self.actionList.extend(actionList2)
            else:
                # Determine safe unvisited location and navigate there if one
                # exists
                safeUnvisitedLocation = self.SafeUnvisitedLocation()
                if safeUnvisitedLocation is not None:
                    print("Moving to safe unvisited location " +
                          str(safeUnvisitedLocation))
                    actionList2 = self.searchEngine.FindPath(
                        self.agentLocation, self.agentOrientation,
                        safeUnvisitedLocation, self.agentOrientation)
                if actionList2:
                    self.actionList.extend(actionList2)
                else:
                    # If the agent knows the location of the live Wumpus, and
                    #   there is a safe location facing the Wumpus, then the
                    #   agent should move there and shoot the Wumpus
                    shootLocation, shootDirection = self.shootInstruction()
                    if shootLocation and shootDirection:
                        actionList2 = self.searchEngine.FindPath(
                            self.agentLocation, self.agentOrientation,
                            shootLocation, shootDirection)
                        actionList2.append(Action.SHOOT)
                        self.arrow = False
                        actionList2.extend(self.searchEngine.FindPath(
                            self.agentLocation, self.agentOrientation,
                            self.wumpusLocation, self.agentOrientation))
                        self.wumpusDead = True
                    else:
                        possiblePits = self.pitProbability()
                        # Pop last item from list, aka lowest probability item
                        newLocation, prob = possiblePits.pop()
                        self.safeLocations.append(newLocation)
                        self.searchEngine.safeLocations.append(newLocation)
                        actionList2 = self.searchEngine.FindPath(
                            self.agentLocation, self.agentOrientation,
                            newLocation, self.agentOrientation)
                    if actionList2:
                        self.actionList.extend(actionList2)

        action = self.actionList.pop(0)
        self.lastAction = action
        return action

    def UpdateState(self, lastAction, percept):
        X = self.agentLocation[0]
        Y = self.agentLocation[1]
        orientation = self.agentOrientation
        if (lastAction == Action.TURNLEFT):
            self.agentOrientation = (orientation + 1) % 4
        if (lastAction == Action.TURNRIGHT):
            if (orientation == Orientation.RIGHT):
                self.agentOrientation = Orientation.DOWN
            else:
                self.agentOrientation = orientation - 1
        if (lastAction == Action.GOFORWARD):
            if percept.bump:
                if (orientation == Orientation.RIGHT) or (
                        orientation == Orientation.UP):
                    print("World size known to be " +
                          str(self.worldSize) + "x" + str(self.worldSize))
                    self.worldSizeKnown = True
                    self.RemoveOutsideLocations()
            else:
                if orientation == Orientation.UP:
                    self.agentLocation = [X, Y+1]
                elif orientation == Orientation.DOWN:
                    self.agentLocation = [X, Y-1]
                elif orientation == Orientation.LEFT:
                    self.agentLocation = [X-1, Y]
                elif orientation == Orientation.RIGHT:
                    self.agentLocation = [X+1, Y]
        if (lastAction == Action.GRAB):
            # Assume GRAB only done if Glitter was present
            self.agentHasGold = True
        if (lastAction == Action.CLIMB):
            pass  # do nothing; if CLIMB worked, this won't be executed anyway
        # HW5.2 state update requirements (note: 2g no longer required)
        if percept.stench and (self.agentLocation not in self.stenchLocations):
            self.stenchLocations.append(self.agentLocation)
        if percept.breeze and (self.agentLocation not in self.breezeLocations):
            self.breezeLocations.append(self.agentLocation)
        if percept.glitter:
            self.goldLocation = self.agentLocation
            print("Found gold at " + str(self.goldLocation))
        new_max = max(self.agentLocation[0], self.agentLocation[1])
        if new_max > self.worldSize:
            self.worldSize = new_max
        if (self.wumpusLocation == [0, 0]):
            self.LocateWumpus()
        self.UpdateSafeLocations(self.agentLocation)
        if self.agentLocation not in self.visitedLocations:
            self.visitedLocations.append(self.agentLocation)

    def GameOver(self, score):

        X = self.agentLocation[0]
        Y = self.agentLocation[1]
        if self.agentOrientation == Orientation.UP:
            self.agentLocation = [X, Y+1]
        elif self.agentOrientation == Orientation.DOWN:
            self.agentLocation = [X, Y-1]
        elif self.agentOrientation == Orientation.LEFT:
            self.agentLocation = [X-1, Y]
        elif self.agentOrientation == Orientation.RIGHT:
            self.agentLocation = [X+1, Y]
        # Update pits with pit that killed Agent
        if score < -1000:
            self.safeLocations.remove(self.agentLocation)
            self.searchEngine.safeLocations.remove(self.agentLocation)
            self.pits.append(self.agentLocation)
            print("Killed at", self.agentLocation)

    def UpdateSafeLocations(self, location):
        # Add location to safe locations. Also add adjacent locations,
        # if no stench or breeze. Or just no breeze, if stench to be ignored
        if location not in self.safeLocations:
            self.safeLocations.append(location)
            self.searchEngine.AddSafeLocation(location[0], location[1])
        ignore_stench = False
        if (self.wumpusLocation != [0, 0]):
            ignore_stench = True  # we know location of wumpus
        if ((location not in self.stenchLocations) or ignore_stench) and (
                location not in self.breezeLocations):
            for adj_loc in self.AdjacentLocations(location):
                if (adj_loc != self.wumpusLocation) and (
                        adj_loc not in self.safeLocations):
                    self.safeLocations.append(adj_loc)
                    self.searchEngine.AddSafeLocation(adj_loc[0], adj_loc[1])
            if self.worldSizeKnown:
                self.RemoveOutsideLocations()

    def SafeUnvisitedLocation(self):
        # Find and return safe unvisited location
        for location in self.safeLocations:
            if location not in self.visitedLocations:
                return location
        return None

    def RemoveOutsideLocations(self):
        # Know exact world size, so remove locations outside the world.
        boundary = self.worldSize + 1
        for i in range(1, boundary):
            if [i, boundary] in self.safeLocations:
                self.safeLocations.remove([i, boundary])
                self.searchEngine.RemoveSafeLocation(i, boundary)
            if [boundary, i] in self.safeLocations:
                self.safeLocations.remove([boundary, i])
                self.searchEngine.RemoveSafeLocation(boundary, i)
        if [boundary, boundary] in self.safeLocations:
            self.safeLocations.remove([boundary, boundary])
            self.searchEngine.RemoveSafeLocation(boundary, boundary)

    def AdjacentLocations(self, location):
        # Return list of locations adjacent to given location. One row/col
        # beyond unknown world size is okay. Locations outside the world will
        # be removed later.
        X = location[0]
        Y = location[1]
        adj_locs = []
        if X > 1:
            adj_locs.append([X-1, Y])
        if Y > 1:
            adj_locs.append([X, Y-1])
        if self.worldSizeKnown:
            if (X < self.worldSize):
                adj_locs.append([X+1, Y])
            if (Y < self.worldSize):
                adj_locs.append([X, Y+1])
        else:
            adj_locs.append([X+1, Y])
            adj_locs.append([X, Y+1])
        return adj_locs

    def LocateWumpus(self):
        # Check stench and safe location info to see if wumpus can be located.
        # If so, then stench locations should be safe.
        for stench_location_1 in self.stenchLocations:
            x1 = stench_location_1[0]
            y1 = stench_location_1[1]
            for stench_location_2 in self.stenchLocations:
                x2 = stench_location_2[0]
                y2 = stench_location_2[1]
                if (x1 == x2-1) and (y1 == y2 - 1) and (
                        [x1+1, y1] in self.safeLocations):
                    self.wumpusLocation = [x1, y1+1]
                if (x1 == x2-1) and (y1 == y2 - 1) and (
                        [x1, y1+1] in self.safeLocations):
                    self.wumpusLocation = [x1+1, y1]
                if (x1 == x2+1) and (y1 == y2 - 1) and (
                        [x1-1, y1] in self.safeLocations):
                    self.wumpusLocation = [x1, y1+1]
                if (x1 == x2+1) and (y1 == y2 - 1) and (
                        [x1, y1+1] in self.safeLocations):
                    self.wumpusLocation = [x1-1, y1]
        if (self.wumpusLocation != [0, 0]):
            print("Found wumpus at " + str(self.wumpusLocation))

    def shootInstruction(self) -> tuple:
        r'''
        Find the orientation to face as well as location to shoot at the wumpus
            from
        Args:
            None
        Return:
            Tuple(location, direction) if valid shoot location is found,
            otherwise None
        '''
        location = None
        direction = None
        if not self.wumpusDead and (self.wumpusLocation != [0, 0]):
            for i in range(1, self.worldSize):
                if [self.wumpusLocation[0], i] \
                        in self.safeLocations:
                    location = [self.wumpusLocation[0], i]
                    break
                elif [i, self.wumpusLocation[1]] \
                        in self.safeLocations:
                    location = [i, self.wumpusLocation[1]]
                    break
        if location:
            if self.wumpusLocation[0] == location[0]:
                if self.wumpusLocation[1] > location[1]:
                    direction = Orientation.UP
                else:
                    direction = Orientation.DOWN
            elif self.wumpusLocation[1] == location[1]:
                if self.wumpusLocation[0] > location[0]:
                    direction = Orientation.LEFT
                else:
                    direction = Orientation.RIGHT
        return (location, direction)

    def pitProbability(self):
        r'''
        Generate a list of pit probabilities for all locations on the frontier
        Pit probability is predictied using inference by enumeration

        Args:
           None
        Return:
            a list of tuple(location, probability)
        '''
        known = self.pits + self.safeLocations
        # Known = {locations where you definitely know there is a pit or not}
        preliminaryFrontier = []
        boundary = self.worldSize + 1

        for i in self.breezeLocations:
            for j in self.AdjacentLocations(i):
                if self.worldSizeKnown:
                    if j[0] >= boundary or j[1] >= boundary:
                        pass
                    else:
                        preliminaryFrontier.append(j)
                else:
                    preliminaryFrontier.append(j)

        frontier = []
        for i in preliminaryFrontier:
            if i not in self.visitedLocations or i not in self.pits and \
                    i not in self.safeLocations:
                frontier.append(i)
        # Remove duplicates from frontier
        frontier.sort()
        frontier = list(k for k, _ in itertools.groupby(frontier))
        # Remove known locations from frontier
        for i in known:
            if i in frontier:
                frontier.remove(i)
        probabilitySet = []
        # foreach location (x,y) in Frontier {
        print("visited", self.visitedLocations)
        print("frontier", frontier)
        print("pits", self.pits)
        for i in frontier:
            print(i)
            # P(Pitx,y=true) = 0.0
            probTrue = 0
            # P(Pitx,y=false) = 0.0
            probFalse = 0

            # Frontier’ = Frontier – {(x,y)}
            frontierP = [*frontier]
            frontierP.remove(i)
            # [list(zip(frontierP, x)) for x in itertools.product(
            #     [True, False], repeat=len(frontierP))]
            frontierCombo = [{tuple(frontierP[y]):x[y] for y in range(0, len(
                frontierP))} for x in itertools.product(
                    [True, False], repeat=len(frontierP))]

            # frontierCombo=[x for x in itertools.product(
            #     [True, False], repeat= len(frontierP))]
            for j in frontierCombo:
                probFrontierP = pow(0.2, list(j.values()).count(True)) * \
                    pow(0.8, list(j.values()).count(False))
                # check if consistent
                consistent = True
                for location, value in j.items():
                    if list(location) in known:
                        consistent = False
                    numBreeze = 0
                    for adj in self.AdjacentLocations(location):
                        if adj in self.breezeLocations:
                            numBreeze += 1
                    if numBreeze == 0 and value:
                        consistent = False
                    elif numBreeze > 0 and not value:
                        consistent = False
                # pitxTrue
                numBreeze = 0
                for adj in self.AdjacentLocations(i):
                    if adj in self.breezeLocations:
                        numBreeze += 1
                pitxTrue = True if numBreeze > 0 else False

                # pitxFalse
                numBreeze = 0
                for adj in self.AdjacentLocations(i):
                    if adj in self.breezeLocations:
                        for adjAdj in self.AdjacentLocations(adj):
                            # print(adjAdj, j)
                            if tuple(adjAdj) in j and j[tuple(adjAdj)]:
                                numBreeze += 1
                # print("breeze", numBreeze)
                pitxFalse = True if numBreeze == 0 else False

                if pitxTrue:
                    probTrue += probFrontierP
                if pitxFalse:
                    probFalse += probFrontierP
                # print(probTrue, probFalse)
            probTrue *= 0.2
            probFalse *= 0.8
            # print("true", probTrue, "false", probFalse)
            probTrue = probTrue / (probTrue + probFalse)
            probabilitySet.append([i, probTrue])

        # Sort list so highest probability is first
        probabilitySet.sort(key=lambda tup: tup[1], reverse=True)
        print("Pit probabilities", probabilitySet)
        return probabilitySet
