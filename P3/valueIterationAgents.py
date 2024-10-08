import mdp, util

from learningAgents import ValueEstimationAgent
import collections

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
              mdp.isTerminal(state)
        """
        self.mdp = mdp
        self.discount = discount
        self.iterations = iterations
        self.values = util.Counter() # A Counter is a dict with default 0
        self.runValueIteration()

    def runValueIteration(self):
        # Write value iteration code here
        "*** YOUR CODE HERE ***"
        new_values = self.values.copy()
        for i in range(self.iterations):
            for state in self.mdp.getStates():
                if self.mdp.isTerminal(state):
                    continue
                new_values[state] = max([self.getQValue(state, action) for action in self.mdp.getPossibleActions(state)])
            self.values = new_values.copy()

    def getValue(self, state):
        """
          Return the value of the state (computed in __init__).
        """
        return self.values[state]


    def computeQValueFromValues(self, state, action):
        """
          Compute the Q-value of action in state from the
          value function stored in self.values.
        """
        "*** YOUR CODE HERE ***"
        """
              mdp.getStates()
              mdp.getPossibleActions(state)
              mdp.getTransitionStatesAndProbs(state, action)
              mdp.getReward(state, action, nextState)
              mdp.isTerminal(state)
        """
        list = self.mdp.getTransitionStatesAndProbs(state, action)
        result = 0
        for nextState, prob in list:
            reward = self.mdp.getReward(state, action, nextState)
            result += prob * (reward + self.discount * self.values[nextState])
        return result
        
        util.raiseNotDefined()

    def computeActionFromValues(self, state):
        """
          The policy is the best action in the given state
          according to the values currently stored in self.values.

          You may break ties any way you see fit.  Note that if
          there are no legal actions, which is the case at the
          terminal state, you should return None.
        """
        "*** YOUR CODE HERE ***"
        actions = self.mdp.getPossibleActions(state)
        values = util.Counter()
        for action in actions:
            values[action] = self.getQValue(state, action)
        return values.argMax()
        util.raiseNotDefined()

    def getPolicy(self, state):
        return self.computeActionFromValues(state)

    def getAction(self, state):
        "Returns the policy at the state (no exploration)."
        return self.computeActionFromValues(state)

    def getQValue(self, state, action):
        return self.computeQValueFromValues(state, action)

class AsynchronousValueIterationAgent(ValueIterationAgent):
    """
        * Please read learningAgents.py before reading this.*

        An AsynchronousValueIterationAgent takes a Markov decision process
        (see mdp.py) on initialization and runs cyclic value iteration
        for a given number of iterations using the supplied
        discount factor.
    """
    def __init__(self, mdp, discount = 0.9, iterations = 1000):
        """
          Your cyclic value iteration agent should take an mdp on
          construction, run the indicated number of iterations,
          and then act according to the resulting policy. Each iteration
          updates the value of only one state, which cycles through
          the states list. If the chosen state is terminal, nothing
          happens in that iteration.

          Some useful mdp methods you will use:
              mdp.getStates()
              mdp.getPossibleActions(state)
              mdp.getTransitionStatesAndProbs(state, action)
              mdp.getReward(state)
              mdp.isTerminal(state)
        """
        ValueIterationAgent.__init__(self, mdp, discount, iterations)

    def runValueIteration(self):
        "*** YOUR CODE HERE ***"
        states = self.mdp.getStates()
        for i in range(self.iterations):
            state = states[i%len(states)]
            if self.mdp.isTerminal(state): continue
            actions = self.mdp.getPossibleActions(state)
            maxVal = float('-inf')
            for action in actions:
                maxVal = max(maxVal, self.getQValue(state, action))
            self.values[state] = maxVal
            
            

class PrioritizedSweepingValueIterationAgent(AsynchronousValueIterationAgent):
    """
        * Please read learningAgents.py before reading this.*

        A PrioritizedSweepingValueIterationAgent takes a Markov decision process
        (see mdp.py) on initialization and runs prioritized sweeping value iteration
        for a given number of iterations using the supplied parameters.
    """
    def __init__(self, mdp, discount = 0.9, iterations = 100, theta = 1e-5):
        """
          Your prioritized sweeping value iteration agent should take an mdp on
          construction, run the indicated number of iterations,
          and then act according to the resulting policy.
        """
        self.theta = theta
        ValueIterationAgent.__init__(self, mdp, discount, iterations)

    def runValueIteration(self):
        "*** YOUR CODE HERE ***"
        # compute predecessors of all states
        predecessors = {}
        states = self.mdp.getStates()
        for state in states:
            predecessors[state] = set()
        for state in states:
            if self.mdp.isTerminal(state): continue
            actions = self.mdp.getPossibleActions(state)
            for action in actions:
                list = self.mdp.getTransitionStatesAndProbs(state, action)
                for succState, prob in list:
                    if self.mdp.isTerminal(succState): continue
                    predecessors[succState].add(state)
        
        q = util.PriorityQueue()

        # push states intro q with priority
        for state in self.mdp.getStates():
            if self.mdp.isTerminal(state): continue
            maxQ = float('-inf')
            for action in self.mdp.getPossibleActions(state):
                maxQ = max(maxQ, self.getQValue(state, action))
            diff = abs(maxQ-self.getValue(state))
            q.push(state, -diff)
        
        for i in range(self.iterations):
            if q.isEmpty(): break
            s = q.pop()
            if self.mdp.isTerminal(s): continue

            # update value of state
            actions = self.mdp.getPossibleActions(s)
            maxVal = float('-inf')
            for action in actions:
                maxVal = max(maxVal, self.getQValue(s, action))
            self.values[s] = maxVal
            
            for p in predecessors[s]:
                maxQ = float('-inf')
                for action in self.mdp.getPossibleActions(p):
                    maxQ = max(maxQ, self.getQValue(p, action))
                diff = abs(maxQ-self.values[p])
                if diff > self.theta:
                    q.update(p, -diff)
            

