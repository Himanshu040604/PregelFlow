import operator
from typing import Annotated, TypedDict, List

class TotalState(TypedDict):
    """ This file defines the structure of the graph's memory (e.g the State)
    Each key here is a 'Channel' in the Pregel architecture"""
    '''This will store the initial topic which will be provided by the user 
    as this has no reducer it is immutable by default untill a node rewrites it'''

    topic : str
    #without this one node will override each other thats why we use Annotated with operator.add
    results: Annotated[List[str], operator.add]
    final_report: str

  