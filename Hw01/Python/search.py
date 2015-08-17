# search.py
# ---------
# Licensing Information: Please do not distribute or publish solutions to this
# project. You are free to use and extend these projects for educational
# purposes. The Pacman AI projects were developed at UC Berkeley, primarily by
# John DeNero (denero@cs.berkeley.edu) and Dan Klein (klein@cs.berkeley.edu).
# For more info, see http://inst.eecs.berkeley.edu/~cs188/sp09/pacman.html

"""
In search.py, you will implement generic search algorithms which are called 
by Pacman agents (in searchAgents.py).
"""

import util
from game import Directions
#we have to import Directions from game.py

class SearchProblem:
  """
  This class outlines the structure of a search problem, but doesn't implement
  any of the methods (in object-oriented terminology: an abstract class).
  
  You do not need to change anything in this class, ever.
  """
  
  def getStartState(self):
     """
     Returns the start state for the search problem 
     """
     util.raiseNotDefined()
    
  def isGoalState(self, state):
     """
       state: Search state
    
     Returns True if and only if the state is a valid goal state
     """
     util.raiseNotDefined()

  def getSuccessors(self, state):
     """
       state: Search state
     
     For a given state, this should return a list of triples, 
     (successor, action, stepCost), where 'successor' is a 
     successor to the current state, 'action' is the action
     required to get there, and 'stepCost' is the incremental 
     cost of expanding to that successor
     """
     util.raiseNotDefined()

  def getCostOfActions(self, actions):
     """
      actions: A list of actions to take
 
     This method returns the total cost of a particular sequence of actions.  The sequence must
     be composed of legal moves
     """
     util.raiseNotDefined()

def tinyMazeSearch(problem):
  """
  Returns a sequence of moves that solves tinyMaze.  For any other
  maze, the sequence of moves will be incorrect, so only use this for tinyMaze
  """
  from game import Directions
  s = Directions.SOUTH
  w = Directions.WEST
  return  [s,s,w,s,w,w,s,w]

def depthFirstSearch(problem):
  """
  Search the deepest nodes in the search tree first [p 74].
  
  Your search algorithm needs to return a list of actions that reaches
  the goal.  Make sure to implement a graph search algorithm [Fig. 3.18].
  
  To get started, you might want to try some of these simple commands to
  understand the search problem that is being passed in:
  
  print "Start:", problem.getStartState()
  print "Is the start a goal?", problem.isGoalState(problem.getStartState())
  print "Start's successors:", problem.getSuccessors(problem.getStartState())
  """
  "*** YOUR CODE HERE ***"
  DT = {'South': Directions.SOUTH, 'North': Directions.NORTH,'West': Directions.WEST, 'East': Directions.EAST }
  statesort = []
  #list statesort used to store the node with the order sequence
  DFSSTACK=util.Stack()
  DFSSTACK.push((problem.getStartState(),statesort,0))
  #we have to put three argument (node,action,cost) into stack
  while not DFSSTACK.isEmpty():
    currentNode=DFSSTACK.pop()
    # use currentNode to store the node which pop from DFSSTACK
    if problem.isGoalState(currentNode[0]):
        #if currentNode[0]==goal then return currentNode[1] which is action
        return currentNode[1]
    elif currentNode[0] in statesort:
        continue
    else:
        sucList = problem.getSuccessors(currentNode[0])
        #retrieve the currentNode's successors and store the sucList
        for a in sucList:
            DFSSTACK.push((a[0],currentNode[1]+[DT[a[1]]],a[2]))
        #push the successor into the stack  (a[0]is the successors. a[1]is the action. a[2]is the cost.)
        statesort=statesort+[currentNode[0]]
        #store the node which is visited
  return []

def breadthFirstSearch(problem):
  "Search the shallowest nodes in the search tree first. [p 74]"
  "*** YOUR CODE HERE ***"
  DT = {'South': Directions.SOUTH, 'North': Directions.NORTH,'West': Directions.WEST, 'East': Directions.EAST }
  statesort = []
  #list statesort used to store the node with the order sequence
  BFSQUEUE=util.Queue()
  BFSQUEUE.push((problem.getStartState(),statesort))
  #we have to put three argument (node,action,cost) into queue
  while not BFSQUEUE.isEmpty():
    currentNode=BFSQUEUE.pop()
    # use currentNode to store the node which pop from BFSQUEUE
    if problem.isGoalState(currentNode[0]):
    #if currentNode[0]==goal then return currentNode[1] which is action
        return currentNode[1]
    elif currentNode[0] in statesort:
        continue
    else:
        sucList = problem.getSuccessors(currentNode[0])
        #retrieve the currentNode's successors and store the sucList
        for a in sucList:
            BFSQUEUE.push((a[0],currentNode[1]+[DT[a[1]]],a[2]))
            #push the successor into the queue (a[0]is the successors a[1]is the action a[2]is the cost)
        statesort=statesort+[currentNode[0]]
        #store the node which is visited
  return []

      
def uniformCostSearch(problem):
  "Search the node of least total cost first. "
  "*** YOUR CODE HERE ***"
  """
     What is lambda?
     It's a function that redefine the function in StayWestSearchAgent and StayEastSearchAgent 
     And class PositionSearchProblem's def __init__(self, gameState, costFn = lambda x: 1, goal=(1,1), start=None, warn=True):
     
  """
  DT = {'South': Directions.SOUTH, 'North': Directions.NORTH,'West': Directions.WEST, 'East': Directions.EAST }
  statesort = []
  #list statesort used to store the node with the order sequence
  UCSQUEUE=util.PriorityQueueWithFunction(lambda x:x[2])
  #we can use costFn=lambda which is referenced from the class PositionSearchProblem(search.SearchProblem) in SearchAgent.py
  UCSQUEUE.push((problem.getStartState(),statesort,0))
  #we have to put three argument (self, item, self.priorityFunction(item)) into PriorityQueueWithFunction
  while not UCSQUEUE.isEmpty():
    currentNode=UCSQUEUE.pop()
    # use currentNode to store the node which pop from USCQUEUE
    if problem.isGoalState(currentNode[0]):
    #if currentNode[0]==goal then return currentNode[1] which is action
        return currentNode[1]
    elif currentNode[0] in statesort:
        continue
    else:
        sucList = problem.getSuccessors(currentNode[0])
        #retrieve the currentNode's successors and store the sucList
        for a in sucList:
            UCSQUEUE.push((a[0],currentNode[1]+[DT[a[1]]],currentNode[2]+a[2]))
            #currentNode[2](is the cost from past) plus a[2](is the cost of this action) = total cost
        statesort=statesort+[currentNode[0]]
        #store the node which is visited
  return []

def nullHeuristic(state, problem=None):
  """
  A heuristic function estimates the cost from the current state to the nearest
  goal in the provided SearchProblem.  This heuristic is trivial.
  """
  return 0

def aStarSearch(problem, heuristic=nullHeuristic):
  "Search the node that has the lowest combined cost and heuristic first."
  "*** YOUR CODE HERE ***"
  DT = {'South': Directions.SOUTH, 'North': Directions.NORTH,'West': Directions.WEST, 'East': Directions.EAST }
  statesort = []
  #list statesort used to store the node with the order sequence
  ASTARQUEUE=util.PriorityQueueWithFunction(lambda x:x[2]+heuristic(x[0],problem))
  #we can use heuristic like manhattanHeuristic or euclideanHeuristic and plus the costFn lambda
  ASTARQUEUE.push((problem.getStartState(),statesort,0))
  #we have to put three argument (self, item, self.priorityFunction(item)) into PriorityQueueWithFunction
  while not ASTARQUEUE.isEmpty():
    currentNode=ASTARQUEUE.pop()
    # use currentNode to store the node which pop from ASTARQUEUE
    if problem.isGoalState(currentNode[0]):
    #if currentNode[0]==goal then return currentNode[1] which is action
        return currentNode[1]
    elif currentNode[0] in statesort:
        continue
    else:
        sucList = problem.getSuccessors(currentNode[0])
        #retrieve the currentNode's successors and store the sucList
        for a in sucList:
            ASTARQUEUE.push((a[0],currentNode[1]+[DT[a[1]]],currentNode[2]+a[2]))
            #currentNode[2](is the cost from past) plus a[2](is the cost of this action)
        statesort=statesort+[currentNode[0]]
        #store the node which is visited
  return []
    
  
# Abbreviations
bfs = breadthFirstSearch
dfs = depthFirstSearch
astar = aStarSearch
ucs = uniformCostSearch
