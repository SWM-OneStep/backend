class LexoRank:
    def __init__(self, rank: str):
        self.rank = rank

    def compare_to(self, other):
        if other is None:
            return 0
        if self is other:
            return 0
        if not isinstance(other, LexoRank):
            raise ValueError(
                f"Object must be of type {self.__class__.__name__}"
            )
        return (self.rank > other.rank) - (self.rank < other.rank)
