from abc import ABCMeta, abstractmethod


class Problem(object):

    __metaclass__ = ABCMeta

    @abstractmethod
    def init(self, *args, **kwargs):
        """Initialize the problem"""
        raise NotImplementedError

    @abstractmethod
    def fitness_score(self, state):
        """Calculate the fitness score of the given ``state``

        :returns: fitness score
        """
        raise NotImplementedError

    @abstractmethod
    def mutation(self, state):
        """Mutates the given ``state`` to a new state

        :returns: new state
        """
        raise NotImplementedError
