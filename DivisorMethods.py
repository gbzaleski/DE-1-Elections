
from queue import PriorityQueue
from abc import abstractmethod
from math import floor

class DivisorMethodNode:
    def __init__(self, name, votes, seats = 0) -> None:
        self.name = name
        self.votes = votes
        self.seats = seats
    
    @abstractmethod
    def __gt__(self, other) -> bool:
         pass    
    
    def __eq__(self, other) -> bool:
        return self.name == other.name
    
    def __str__(self):
        return f"Party {self.name} - {self.votes} votes, holds {self.seats} seats"
    
    def __repr__(self):
        return self.__str__()
    
    def data(self):
        return (self.votes, self.seats, self.votes/(self.seats))
    

class DHondtMethod(DivisorMethodNode):
    def __gt__(self, other):
            return self.votes / (self.seats + 1) < other.votes / (other.seats + 1)
    
class SainteLagueMethod(DivisorMethodNode):
    def __gt__(self, other):
            return self.votes / (2 * self.seats + 1) < other.votes / (2 * other.seats + 1)
    

def last_seat(win, los):
    return floor(win.votes - los.votes * win.seats / los.seats)

def parse_last_win(win, los):
    return f"{win.name} won last seat over {los.name} by {last_seat(win, los)} votes"

def runDHondt(data, seats): 
    nodes = [DHondtMethod(name, votes) for (name, votes) in data]

    q = PriorityQueue()
    for node in nodes:
        q.put(node)

    for _ in range(seats):
        next = q.get()
        second_last = next
        next.seats += 1
        q.put(next)
        
    last = q.get()
    q.put(last)
    if last.name == second_last.name:
        last = q.get()
        q.put(last)
        
    last = DHondtMethod(last.name, last.votes, last.seats)
    last.seats += 1

    return ([(node.name, int(node.seats)) for node in q.queue], parse_last_win(second_last, last))


def runSainteLague(data, seats):
    nodes = [SainteLagueMethod(name, votes) for (name, votes) in data]

    q = PriorityQueue()
    for node in nodes:
        q.put(node)

    for _ in range(seats):
        next = q.get()
        next.seats += 1
        q.put(next)
        
    return ([(node.name, int(node.seats)) for node in q.queue], None)


def test():
    dt = [("KO", 741_286), ("PIS", 345_380), ("NL", 230_648), ("TD", 227_127), ("KF", 124_220)]
    ss = 20
    print(runDHondt(dt, ss))
    print(runSainteLague(dt, ss))

    print("#############")
    dt = [("KO", 161_241), ("PIS", 150_022), ("NL", 34_763), ("TD", 61_155 ), ("KF", 31_150), ("MN", 25_778)]
    ss = 12
    print(runDHondt(dt, ss))
    print(runSainteLague(dt, ss))
