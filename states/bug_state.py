from enum import Enum


class BugState(Enum):
    SEARCHING = 1
    FOLLOWING = 2
    AVOIDING = 3
    SLEEPING = 4
    SEARCHING_FOR_MATE = 5
    EATING = 6