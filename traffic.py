from params_proto import Proto, ParamsProto, PrefixProto

class TrafficArgs(PrefixProto):
    """SolveArgs is a ParamsProto class that contains all the parameters
    needed for the solver.
    """

    num_players: int = 5

    # Fix this to use eval
    u = lambda x: x
    graph = None

    



class TrafficGame:
