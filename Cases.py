import random
from dataclasses import dataclass
from typing import List, Tuple

@dataclass
class Present:
    cost: int

class Case:
    def __init__(self, cost: int, presents_with_probabilities: List[Tuple[Present, float]]):
        self.cost = cost
        self.presents = presents_with_probabilities
        self._validate_probabilities()  

    def _validate_probabilities(self):
        total_prob = sum(prob for _, prob in self.presents)
        if not (99.99 <= total_prob <= 100.01):  
            raise ValueError(f"Сумма вероятностей должна быть 100%, а не {total_prob}%")

    def get_random_present(self) -> Present:
        rand = random.uniform(0, 100)
        cumulative_prob = 0

        for present, prob in self.presents:
            cumulative_prob += prob
            if rand <= cumulative_prob:
                return present

        return self.presents[-1][0]

def get_random_gift() -> Present:
    default_presents = [
        (Present(100), 30.0),
        (Present(200), 50.0),
        (Present(500), 20.0),
    ]
    case = Case(1000, default_presents)  
    return case.get_random_present()     