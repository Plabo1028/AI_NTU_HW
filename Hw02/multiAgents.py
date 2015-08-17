# multiAgents.py
# --------------
# Licensing Information: Please do not distribute or publish solutions to this
# project. You are free to use and extend these projects for educational
# purposes. The Pacman AI projects were developed at UC Berkeley, primarily by
# John DeNero (denero@cs.berkeley.edu) and Dan Klein (klein@cs.berkeley.edu).
# For more info, see http://inst.eecs.berkeley.edu/~cs188/sp09/pacman.html

from util import manhattanDistance
from game import Directions
import random, util , sys

from game import Agent

class ReflexAgent(Agent):
  """
    A reflex agent chooses an action at each choice point by examining
    its alternatives via a state evaluation function.

    The code below is provided as a guide.  You are welcome to change
    it in any way you see fit, so long as you don't touch our method
    headers.
  """


  def getAction(self, gameState):
    """
    You do not need to change this method, but you're welcome to.

    getAction chooses among the best options according to the evaluation function.

    Just like in the previous project, getAction takes a GameState and returns
    some Directions.X for some X in the set {North, South, West, East, Stop}
    """
    # Collect legal moves and successor states
    legalMoves = gameState.getLegalActions()
    
    # Choose one of the best actions
    scores = [self.evaluationFunction(gameState, action) for action in legalMoves]
    bestScore = max(scores)
    bestIndices = [index for index in range(len(scores)) if scores[index] == bestScore]
    chosenIndex = random.choice(bestIndices) # Pick randomly among the best

    "Add more of your code here if you want to"

    return legalMoves[chosenIndex]

  def evaluationFunction(self, currentGameState, action):
    """
    Design a better evaluation function here.

    The evaluation function takes in the current and proposed successor
    GameStates (pacman.py) and returns a number, where higher numbers are better.

    The code below extracts some useful information from the state, like the
    remaining food (oldFood) and Pacman position after moving (newPos).
    newScaredTimes holds the number of moves that each ghost will remain
    scared because of Pacman having eaten a power pellet.

    Print out these variables to see what you're getting, then combine them
    to create a masterful evaluation function.
    """
    # Useful information you can extract from a GameState (pacman.py)
    successorGameState = currentGameState.generatePacmanSuccessor(action)
    #print successorGameState
    newPos = successorGameState.getPacmanPosition()
    oldFood = currentGameState.getFood()
    newGhostStates = successorGameState.getGhostStates()
    newScaredTimes = [ghostState.scaredTimer for ghostState in newGhostStates]
    "*** YOUR CODE HERE ***"
    
    #print "newPos",newPos
    
    #compute the distances between ghost and pacman
    ghostDistances = []
    for gs in newGhostStates:
        ghostDistances += [manhattanDistance(gs.getPosition(),newPos)]
    #print "ghostDist",ghostDistances
    
    #Sum all of the ScaredTimes
    totalScaredTime = sum(newScaredTimes)
    
    #Compute the distances between food and pacman
    newFood = successorGameState.getFood()
    foodList = newFood.asList()
    foodDistances = []
    for f in foodList:
        foodDistances += [manhattanDistance(newPos,f)]
    
    #print foodDistances
    
    inverseFoodDist = 0
    if len(foodDistances) > 0:
        inverseFoodDist = 1.0/(min(foodDistances))
    
    #if Ghost Scared then chase the Ghost else far away the Ghost in the main goal to the closest food
    heuristic = successorGameState.getScore() + (min(ghostDistances)*((inverseFoodDist)))
    
    #print successorGameState.getScore()
    #print heuristic
    
    return heuristic


def scoreEvaluationFunction(currentGameState):
  """
    This default evaluation function just returns the score of the state.
    The score is the same one displayed in the Pacman GUI.

    This evaluation function is meant for use with adversarial search agents
    (not reflex agents).
  """
  return currentGameState.getScore()

class MultiAgentSearchAgent(Agent):
  """
    This class provides some common elements to all of your
    multi-agent searchers.  Any methods defined here will be available
    to the MinimaxPacmanAgent, AlphaBetaPacmanAgent & ExpectimaxPacmanAgent.

    You *do not* need to make any changes here, but you can if you want to
    add functionality to all your adversarial search agents.  Please do not
    remove anything, however.

    Note: this is an abstract class: one that should not be instantiated.  It's
    only partially specified, and designed to be extended.  Agent (game.py)
    is another abstract class.
  """

  def __init__(self, evalFn = 'scoreEvaluationFunction', depth = '2'):
    self.index = 0 # Pacman is always agent index 0
    self.evaluationFunction = util.lookup(evalFn, globals())
    self.depth = int(depth)
    self.agentCount = 0
  
  def utility(self,state):
    return self.evaluationFunction(state)
  
  def result(self,state,agent,action):
    return state.generateSuccessor(agent,action)
  
  def terminalTest(self,state,depth):
    if depth == (self.depth*self.agentCount) or state.isWin() or state.isLose():
        return True
    else:
        return False

class MinimaxAgent(MultiAgentSearchAgent):
  """
    Your minimax agent (question 2)
  """

  def getAction(self, gameState):
    """
      Returns the minimax action from the current gameState using self.depth
      and self.evaluationFunction.

      Here are some method calls that might be useful when implementing minimax.

      gameState.getLegalActions(agentIndex):
        Returns a list of legal actions for an agent
        agentIndex=0 means Pacman, ghosts are >= 1

      Directions.STOP:
        The stop direction, which is always legal

      gameState.generateSuccessor(agentIndex, action):
        Returns the successor game state after an agent takes an action

      gameState.getNumAgents():
        Returns the total number of agents in the game
    """
    "*** YOUR CODE HERE ***"
    return self.MinimaxSearch(gameState,1,0)
    util.raiseNotDefined()

  def MinimaxSearch(self, gameState, currentDepth, agentIndex):
    #check if the depth over the tree or state is win or lose
    if currentDepth > self.depth or gameState.isWin() or gameState.isLose():
        return self.utility(gameState)
    
    legalMoves = [action for action in gameState.getLegalActions(agentIndex) if action!='Stop']
    
    # update next depth
    #agentIndex = 0 if is pacman else is ghost
    nextIndex = agentIndex + 1
    nextDepth = currentDepth
    if nextIndex >= gameState.getNumAgents():
        nextIndex = 0
        nextDepth += 1

    # Choose one of the best actions or keep query the minimax result
    results = [self.MinimaxSearch( gameState.generateSuccessor(agentIndex, action),nextDepth, nextIndex) for action in legalMoves]
    if agentIndex == 0 and currentDepth == 1: # pacman first move
        bestMove = max(results)
        best = [index for index in range(len(results)) if results[index] == bestMove]
        chosen = random.choice(best) # Pick randomly among the best
        return legalMoves[chosen]
    #max level return max
    if agentIndex == 0:
        bestMove = max(results)
        #print bestMove
        return bestMove
    #min level return min
    else:
        bestMove = min(results)
        return bestMove

class AlphaBetaAgent(MultiAgentSearchAgent):
  """
    Your minimax agent with alpha-beta pruning (question 3)
  """

  def getAction(self, gameState):
    """
      Returns the minimax action using self.depth and self.evaluationFunction
    """
    "*** YOUR CODE HERE ***"
    return self.AlphaBeta(gameState, 1, 0, -sys.maxint, sys.maxint)
    util.raiseNotDefined()
  
  #almost like minmax
  def AlphaBeta(self,gameState,currentDepth,agentIndex,alpha,beta):
    if currentDepth > self.depth or gameState.isWin() or gameState.isLose():
        return self.utility(gameState)

    legalMoves = [action for action in gameState.getLegalActions(agentIndex) if action!='Stop']

    # update next depth
    #agentIndex = 0 if is pacman else is ghost
    nextIndex = agentIndex + 1
    nextDepth = currentDepth
    if nextIndex >= gameState.getNumAgents():
        nextIndex = 0
        nextDepth += 1
    

    if agentIndex==0 and currentDepth==1 : #pacman move first
        results=[self.AlphaBeta(gameState.generateSuccessor(agentIndex,action),nextDepth,nextIndex,alpha,beta)for action in legalMoves]
        bestMove = max(results)
        best=[index for index in range(len(results)) if results[index] ==bestMove ]
        chosen=random.choice(best)
        return legalMoves[chosen]

    if agentIndex == 0:#max tree level
        bestMove = -sys.maxint
        for action in legalMoves:
            bestMove=max(bestMove,self.AlphaBeta( gameState.generateSuccessor(agentIndex, action) , nextDepth, nextIndex, alpha, beta))
            #in alphabeta if the subtree's alpha and beta overlap then return bestMoves
            if bestMove >= beta:
                return bestMove
            #modify alpha from less number to big number
            alpha = max(alpha, bestMove)
        return bestMove
    else:#min tree level
        bestMove = sys.maxint
        for action in legalMoves:
            bestMove = min(bestMove,\
                           self.AlphaBeta( gameState.generateSuccessor(agentIndex, action) , nextDepth, nextIndex, alpha,beta))
            #in alphabeta if the subtree's alpha and beta overlap then return bestMoves
            if alpha >= bestMove:
                return bestMove
            #modify beta from big number to less number
            beta = min(beta, bestMove)
        return bestMove

class ExpectimaxAgent(MultiAgentSearchAgent):
  """
    Your expectimax agent (question 4)
  """

  def getAction(self, gameState):
    """
      Returns the expectimax action using self.depth and self.evaluationFunction

      All ghosts should be modeled as choosing uniformly at random from their
      legal moves.
    """
    "*** YOUR CODE HERE ***"
    return self.Expectimax(gameState, 1, 0, -sys.maxint, sys.maxint)
    util.raiseNotDefined()

  #90% like minmax but return the average the min value
  def Expectimax(self,gameState,currentDepth,agentIndex,alpha,beta):
    if currentDepth > self.depth or gameState.isWin() or gameState.isLose():
        return self.utility(gameState)
    
    legalMoves = [action for action in gameState.getLegalActions(agentIndex) if action!='Stop']

    # update next depth
    #agentIndex = 0 if is pacman else is ghost
    nextIndex = agentIndex + 1
    nextDepth = currentDepth
    if nextIndex >= gameState.getNumAgents():
        nextIndex = 0
        nextDepth += 1

    results=[self.Expectimax(gameState.generateSuccessor(agentIndex,action),nextDepth,nextIndex,alpha,beta)for action in legalMoves]

    if agentIndex==0 and currentDepth==1 : #pacman move first
        bestMove = max(results)
        best=[index for index in range(len(results)) if results[index] ==bestMove ]
        chosen=random.choice(best)
        return legalMoves[chosen]
    
    if agentIndex == 0:#max tree level
        bestMove = max(results)
        return bestMove
            
    else:#the ghost return the average min value
        bestMove = sum(results)/len(results)
        return bestMove


def betterEvaluationFunction(currentGameState):
  """
    Your extreme ghost-hunting, pellet-nabbing, food-gobbling, unstoppable
    evaluation function (question 5).

    DESCRIPTION: <write something here so we know what you did>
  """
  "*** YOUR CODE HERE ***"
  
  if currentGameState.isWin() :  return sys.maxint
  if currentGameState.isLose() :  return -sys.maxint
  
  ####initial state####
  currentPos=currentGameState.getPacmanPosition()
  currentFood=currentGameState.getFood()
  GhostStates=currentGameState.getGhostStates()
  capsulePos=currentGameState.getCapsules()

  heuristic = 0

  weightFood, weightGhost, weightCapsule, weightHunter = 5.0, 5.0, 5.0, 0.0

  ghostScore, capsuleScore, hunterScore = 0.0, 0.0, 0.0

  #obtain food score
  currentFoodList = currentFood.asList()
  closestFood = min([util.manhattanDistance(currentPos, foodPos) for foodPos in currentFoodList])
  foodScore = 1.0 / closestFood

  #consider ghost, capsule, food
  #if ghost's scaredTimer >0 then chase the ghost else eat the food and the far away ghost
  if GhostStates:
    ghostPositions=[a.getPosition() for a in GhostStates]
    ScaredTimes = [b.scaredTimer for b in GhostStates]
    ghostDistances = [util.manhattanDistance(currentPos,c) for c in ghostPositions]
    
    if sum(ScaredTimes)==0: #escape and eat food
        closestGhost = min(ghostDistances) #find the closetGhost
        #because almost the ghost > 1 compute the center of the ghosts
        ghostCenterPos = ( sum([ghostPos[0] for ghostPos in ghostPositions])/len(GhostStates),\
                          sum([ghostPos[1] for ghostPos in ghostPositions])/len(GhostStates))
        ghostCenterDist = util.manhattanDistance(currentPos, ghostCenterPos)
        
        if ghostCenterDist <= closestGhost and closestGhost >= 1 and closestGhost <= 5:
            if len(capsulePos) != 0:
                closestCapsule = min([util.manhattanDistance(capsule,currentPos) for capsule in capsulePos]) #find the closetCapsule
                if closestCapsule <= 3: #let the weightCapsule became high
                        weightCapsule, capsuleScore = 20.0, (1.0 / closestCapsule)
                        weightGhost, ghostScore = 3.0, (-1.0 / (ghostCenterDist+1))
                else:
                        weightGhost, ghostScore = 10.0, (-1.0 / (ghostCenterDist+1))
            else: #because eat the capsule then weightGhost became high
                weightGhost, ghostScore = 15.0, (-1.0 / (ghostCenterDist+1))
        elif ghostCenterDist >= closestGhost and closestGhost >= 1 :
            weightFood *= 3 #because we are not in trouble so eat food
            if len(capsulePos) != 0:
                closestCapsule = min([util.manhattanDistance(capsule,currentPos) for capsule in capsulePos])
                if closestCapsule <= 3:
                        weightCapsule, capsuleScore = 10.0, (1.0 / closestCapsule)
                        weightGhost, ghostScore = 3.0, (-1.0 / closestGhost)
                else:
                        ghostScore = -1.0 / closestGhost
            else:
                ghostScore = -1.0 / closestGhost
        elif closestGhost == 0:
            return -sys.maxint
        elif closestGhost == 1:
            weightGhost, ghostScore = 15.0, (-1.0 / closestGhost)
        else:
            ghostScore = -1.0 / closestGhost

    else: # hunter mode
        #when we eat the capusule then we can eat the ghost
        #and use the closestPrey we can chase the closet ghost
        normalGhostDist = []
        closestPrey = sys.maxint
        ghostCenterX, ghostCenterY = 0.0, 0.0
        for (index, ghostDist) in enumerate(ghostDistances): # use enumerate that can take the ghostDistances
            if ScaredTimes[index] == 0 :
                normalGhostDist.append(ghostDist)
                ghostCenterX += ghostPositions[index][0]
                ghostCenterY += ghostPositions[index][1]
            else:
                if ghostDist <= ScaredTimes[index] : #we have enough time to chase the ghost
                    if ghostDist < closestPrey:
                        closestPrey = ghostDistances[index]

        if normalGhostDist:
            closestGhost = min(normalGhostDist)
            ghostCenterPos = ( ghostCenterX/len(normalGhostDist), ghostCenterY/len(normalGhostDist))
            ghostCenterDist = util.manhattanDistance(currentPos, ghostCenterPos)
            #we can move the center of ghost and then determine which ghost we want chase
            if ghostCenterDist <= closestGhost and closestGhost >= 1 and closestGhost <= 5: #let the weightGhost became high
                weightGhost, ghostScore = 10.0, (- 1.0 / (ghostCenterDist+1))
            elif ghostCenterDist >= closestGhost and closestGhost >= 1 :
                ghostScore = -1.0 / closestGhost
            elif closestGhost == 0:
                return -sys.maxint
            elif closestGhost == 1: #if the closetGhost == 1 then chase
                weightGhost, ghostScore = 15.0, (-1.0 / closestGhost)
            else:
                ghostScore = - 1.0 / closestGhost
        weightHunter, hunterScore = 35.0, (1.0 / closestPrey)

    #evaluation function related food , ghost , capsule of their wight and score and mode between hunter and 
    heuristic = currentGameState.getScore() + \
        weightFood*foodScore + weightGhost*ghostScore + \
        weightCapsule*capsuleScore + weightHunter*hunterScore
    return heuristic

# Abbreviation
better = betterEvaluationFunction


