# valueIterationAgents.py
# -----------------------
# Licensing Information: Please do not distribute or publish solutions to this
# project. You are free to use and extend these projects for educational
# purposes. The Pacman AI projects were developed at UC Berkeley, primarily by
# John DeNero (denero@cs.berkeley.edu) and Dan Klein (klein@cs.berkeley.edu).
# For more info, see http://inst.eecs.berkeley.edu/~cs188/sp09/pacman.html

import mdp, util

from learningAgents import ValueEstimationAgent

class ValueIterationAgent(ValueEstimationAgent):
  """
      * Please read learningAgents.py before reading this.*

      A ValueIterationAgent takes a Markov decision process
      (see mdp.py) on initialization and runs value iteration
      for a given number of iterations using the supplied
      discount factor.
  """
  def __init__(self, mdp, discount = 0.9, iterations = 100):
    """
      Your value iteration agent should take an mdp on
      construction, run the indicated number of iterations
      and then act according to the resulting policy.
    
      Some useful mdp methods you will use:
          mdp.getStates()
          mdp.getPossibleActions(state)
          mdp.getTransitionStatesAndProbs(state, action)
          mdp.getReward(state, action, nextState)
    """
    self.mdp = mdp
    self.discount = discount
    self.iterations = iterations
    self.values = util.Counter() # A Counter is a dict with default 0
     
    "*** YOUR CODE HERE ***"
    
    #Because we have to coordination util.Count , so we have to use dict
  
    self.P = dict()
    self.R = dict()
    self.S = dict()
    
    for state in self.mdp.getStates():
        if self.mdp.isTerminal(state):
            continue
    #get possible action from state
        actions = self.mdp.getPossibleActions(state)
        for action in actions:
            #get the destination and prob from (state,action)
            for (destination, prob ) in mdp.getTransitionStatesAndProbs(state, action):
                #store the prob and reward
                self.P[(state, action, destination)] = prob
                self.R[(state, action, destination)] = self.mdp.getReward(state, action, destination)
                
                if (state,action) not in self.S:
                    self.S[(state, action)] = [destination]
                else:
                    self.S[(state, action)] += [destination]
    
    for _ in range(iterations):
        copyVals = util.Counter()
        for state in self.mdp.getStates():
            if self.mdp.isTerminal(state):
                continue
            actions = self.mdp.getPossibleActions(state)
                          
            bestVals = []
            #call getQValue U(s)=max a belong to A(s) Q(s,a)
            for action in actions:
                bestVals += [self.getQValue(state,action)]
            copyVals[state] = max(bestVals)
                                          
        self.values = copyVals.copy()
        
  def getValue(self, state):
    """
      Return the value of the state (computed in __init__).
    """
    return self.values[state]


  def getQValue(self, state, action):
    """
      The q-value of the state action pair
      (after the indicated number of value iteration
      passes).  Note that value iteration does not
      necessarily create this quantity and you may have
      to derive it on the fly.
    """
    "*** YOUR CODE HERE ***"
    
    #Q(s,a)=P(s'|s,a)*(R(s'|s,a)+U(s')) for every dest
    return sum([ self.P[state,action,dest]*(self.R[state,action,dest] + self.discount*self.values[dest])
                for dest in self.S[state,action] ] )

  def getPolicy(self, state):
    """
      The policy is the best action in the given state
      according to the values computed by value iteration.
      You may break ties any way you see fit.  Note that if
      there are no legal actions, which is the case at the
      terminal state, you should return None.
    """
    "*** YOUR CODE HERE ***"
    if self.mdp.isTerminal(state):
        return None
    #return the action that results in the maximum value
    return max([(self.getQValue(state,action),action) for action in self.mdp.getPossibleActions(state)])[1]

  def getAction(self, state):
    "Returns the policy at the state (no exploration)."
    return self.getPolicy(state)
  
