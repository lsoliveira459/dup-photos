import random
from collections import defaultdict
from time import process_time_ns

import numba as nb


class DynamicBuffer:
    """
    Sources:
    - https://colab.research.google.com/drive/1nDO-XfgkAgABCe2jYNAFwmi4plr2xJoc#scrollTo=Jm812oPv46rq
    """
    def __init__(self: "DynamicBuffer",
                 get_legal_actions: int,
                 alpha: float = 0.5,
                 epsilon: float = 0.25,
                 discount: float = 0.99):
        """
        Q-Learning Agent
        based on http://inst.eecs.berkeley.edu/~cs188/sp09/pacman.html
        Instance variables you have access to
          - self.epsilon (exploration prob)
          - self.alpha (learning rate)
          - self.discount (discount rate aka gamma)

        Functions you should use
          - self.get_legal_actions(state) {state, hashable -> list of actions, each is hashable}
            which returns legal actions for a state
          - self.get_qvalue(state,action)
            which returns Q(state,action)
          - self.set_qvalue(state,action,value)
            which sets Q(state,action) := value

        !!!Important!!!
        Note: please avoid using self._qValues directly.
            There's a special self.get_qvalue/set_qvalue for that.
        """

        self.last_action = None
        self.get_legal_actions = lambda: range(get_legal_actions)
        self._qvalues = defaultdict(lambda: 0)
        self.alpha = alpha
        self.epsilon = epsilon
        self.discount = discount
        self.latest_get_value = process_time_ns()

    @nb.jit(forceobj=True)
    def get_qvalue(self, action):
        """ Returns Q(action) """
        return self._qvalues[action]

    @nb.jit(forceobj=True)
    def set_qvalue(self, action, value):
        """ Sets the Qvalue for [state,action] to the given value """
        self._qvalues[action] = value

    @nb.jit(forceobj=True)
    def get_value(self):
        """
        Compute your agent's estimate of V(s) using current q-values
        V(s) = max_over_action Q(state,action) over possible actions.
        Note: please take into account that q-values can be negative.
        """
        possible_actions = self.get_legal_actions()

        #If there are no legal actions, return 0.0
        if len(possible_actions) == 0:
            return 0.0

        q = [self.get_qvalue(a) for a in possible_actions]
        value = max(q)

        return value

    @nb.jit(forceobj=True)
    def update(self, action, reward):
        """
        You should do your Q-Value update here:
           Q(s,a) := (1 - alpha) * Q(s,a) + alpha * (r + gamma * V(s'))
        """

        #agent parameters
        gamma = self.discount
        learning_rate = self.alpha

        Q = (1 - learning_rate) * self.get_qvalue(action) + learning_rate * (reward + gamma * self.get_value())

        self.set_qvalue(action, Q)

        return self.get_action()

    @nb.jit(forceobj=True)
    def get_and_update(self, action):
    # def update(self, state, action, reward, next_state):
        """
        You should do your Q-Value update here:
           Q(s,a) := (1 - alpha) * Q(s,a) + alpha * (r + gamma * V(s'))
        """

        #agent parameters
        gamma = self.discount
        learning_rate = self.alpha

        reward = process_time_ns() - self.latest_get_value

        Q = (1 - learning_rate) * self.get_qvalue(action) + learning_rate * (reward + gamma * self.get_value())

        self.set_qvalue(action, Q)

        return self.get_action()

    @nb.jit(forceobj=True)
    def get_best_action(self):
        """
        Compute the best action to take in a state (using current q-values).
        """
        possible_actions = self.get_legal_actions()

        #If there are no legal actions, return None
        if len(possible_actions) == 0:
            return None

        q = [self.get_qvalue(a) for a in possible_actions]
        maxQ = max(q)
        i = q.index(maxQ)
        best_action = possible_actions[i]

        return best_action

    @nb.jit(forceobj=True)
    def get_action(self):
        """
        Compute the action to take in the current state, including exploration.
        With probability self.epsilon, we should take a random action.
            otherwise - the best policy action (self.getPolicy).

        Note: To pick randomly from a list, use random.choice(list).
              To pick True or False with a given probablity, generate uniform number in [0, 1]
              and compare it with your probability
        """

        # Pick Action
        possible_actions = self.get_legal_actions()
        action = None

        #If there are no legal actions, return None
        if len(possible_actions) == 0:
            return None

        #agent parameters:
        epsilon = self.epsilon

        if random.random() < epsilon:
            action = random.choice(possible_actions)
        else:
            action = self.get_best_action()
        chosen_action = action

        self.latest_get_value = process_time_ns()

        return chosen_action

    @nb.jit(forceobj=True)
    def next(self):
        next_action = self.get_and_update(self.last_action)\
            if self.last_action\
            else self.get_action()
        self.last_action = next_action
        return next_action+1

class StaticBuffer:
    @nb.jit(forceobj=True)
    def __init__(self, buffer):
        self.buffer = buffer

    @nb.jit(forceobj=True)
    def next(self):
        return self.buffer