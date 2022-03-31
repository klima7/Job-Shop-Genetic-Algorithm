from random import randint, random, shuffle


class Chromosome:

    MUTATION_PROBABILITY = 0.05

    def __init__(self, n_tasks):
        self.genotype = self._random_genotype(n_tasks)
        self.fitness = self.calc_fitness()

    def _random_genotype(self, n_tasks):
        genotype = list(range(n_tasks))
        shuffle(genotype)
        return genotype

    def calc_fitness(self):
        taken_items = self.get_phenotype()
        taken_value = 0
        taken_weight = 0

        for item in taken_items:
            taken_value += item.value
            taken_weight += item.weight

        return taken_value if taken_weight <= self.max_weight else 0


class JobSchedulingProblem:

    def __init__(self):
        pass