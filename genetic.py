import math
from random import shuffle, choices, random, randrange
from functools import total_ordering
from plot import plot


@total_ordering
class Chromosome:

    def __init__(self, jobs, machines, genotype=None):
        self.jobs = jobs
        self.machines = machines
        self.genotype = genotype if genotype is not None else self._random_genotype()
        self.phenotype = self._get_phenotype()
        self.timespan = self._get_timespan()
        self.fitness = self._get_fitness()

    def _random_genotype(self):
        jobs_ids = [job.id for job in self.jobs.values() for _ in range(len(job.tasks))]
        shuffle(jobs_ids)
        return jobs_ids

    def _get_phenotype(self):
        tasks = self._get_tasks()
        scheduled_tasks = self._schedule_tasks(tasks)
        return scheduled_tasks

    def _get_tasks(self):
        tasks = []
        counters = {job_id: 0 for job_id in self.jobs.keys()}

        for gen in self.genotype:
            job = self.jobs[gen]
            task_no = counters[gen]
            task = job.tasks[task_no]
            tasks.append(task)
            counters[gen] += 1

        return tasks

    def _schedule_tasks(self, tasks):
        scheduled_tasks = []
        queues = {machine: [(-math.inf, 0), (math.inf, math.inf)] for machine in self.machines}
        last_times = {job_id: 0 for job_id in self.jobs.keys()}

        for task in tasks:
            start_time = self._schedule_task(task, queues[task.machine], last_times[task.job_id])
            end_time = start_time + task.time
            last_times[task.job_id] = end_time
            scheduled_tasks.append((start_time, start_time + task.time, task))

        return scheduled_tasks

    @staticmethod
    def _schedule_task(task, queue, after_time):
        for i in range(len(queue) - 1):
            prev_period, next_period = queue[i:i + 2]
            start_time = max(after_time, prev_period[1])
            free_time = next_period[0] - start_time
            if free_time >= task.time:
                new_period = (start_time, start_time + task.time)
                queue.insert(i + 1, new_period)
                return start_time
        assert False

    def _get_timespan(self):
        last_task = sorted(self.phenotype, key=lambda x: x[1])[-1]
        return last_task[1]

    def _get_fitness(self):
        return 3000 / self.timespan

    def mutate(self):
        pos_1 = randrange(0, len(self.genotype))
        pos_2 = randrange(0, len(self.genotype))
        new_genotype = self.genotype.copy()
        new_genotype[pos_1], new_genotype[pos_2] = new_genotype[pos_2], new_genotype[pos_1]
        return Chromosome(self.jobs, self.machines, genotype=new_genotype)

    @classmethod
    def cross(cls, a, b):
        return cls._cross_single(a, b), cls._cross_single(b, a)

    @classmethod
    def _cross_single(cls, a, b):
        cross_pos = randrange(1, len(a.genotype))
        child_genotype = a.genotype[:cross_pos]
        b_genotype = b.genotype.copy()
        for gen in child_genotype:
            b_genotype.remove(gen)
        child_genotype.extend(b_genotype)
        return cls(a.jobs, a.machines, genotype=child_genotype)

    def __lt__(self, other):
        return self.fitness < other.fitness


class JobShopGA:

    def __init__(self, jobs, *, max_generations=10000, max_no_change_gens=50,
                 n_chromosomes=200, n_elite=10, cross_prob=0.7, mutate_prob=0.2):

        self.jobs = {job.id: job for job in jobs}
        self.max_generations = max_generations
        self.max_no_change_generations = max_no_change_gens
        self.n_chromosomes = n_chromosomes
        self.n_elite = n_elite if (n_chromosomes - n_elite) % 2 == 0 else n_elite + 1
        self.cross_prob = cross_prob
        self.mutate_prob = mutate_prob

        self.machines = list({task.machine for job in jobs for task in job.tasks})
        self.population = sorted([Chromosome(self.jobs, self.machines) for _ in range(self.n_chromosomes)], reverse=True)

    def solve(self):

        best_chromosome = None
        no_change_generations = 0

        for i in range(self.max_generations):

            # evolving
            self._replace_generation()

            # best chromosome in current population
            best_gen_chromosome = self.population[0]

            # early stopping
            if best_chromosome is None or best_gen_chromosome.timespan < best_chromosome.timespan:
                best_chromosome = best_gen_chromosome
                no_change_generations = 0
            else:
                no_change_generations += 1

            if no_change_generations > self.max_no_change_generations:
                break

            # logging
            if i % 10 == 0:
                print(f'{i:<10} - {best_chromosome.timespan:>10}')
                if i % 50 == 0:
                    plot(best_chromosome.phenotype, best_chromosome.timespan, i)

        return best_chromosome.phenotype, best_chromosome.timespan

    def _replace_generation(self):
        elite = self.population[:self.n_elite]
        selected = self._select(self.population)
        crossed = self._cross(selected)
        mutated = self._mutate(crossed)
        self.population = sorted([*elite, *mutated], reverse=True)

    def _select(self, chromosomes):
        all_fitness = [chromosome.fitness for chromosome in chromosomes]
        n_selected_chromosomes = self.n_chromosomes - self.n_elite
        selected_chromosomes = choices(chromosomes, all_fitness, k=n_selected_chromosomes)
        return selected_chromosomes

    def _cross(self, chromosomes):
        n_chromosomes = len(chromosomes)
        assert n_chromosomes % 2 == 0
        center = int(n_chromosomes / 2)
        parents_1, parents_2 = chromosomes[:center], chromosomes[center:]

        crossed = []
        for parent_1, parent_2 in zip(parents_1, parents_2):
            cross = random() < self.cross_prob
            if cross:
                child_1, child_2 = Chromosome.cross(parent_1, parent_2)
                crossed.extend([child_1, child_2])
            else:
                crossed.extend([parent_1, parent_2])

        return crossed

    def _mutate(self, chromosomes):
        mutated = []
        for chromosome in chromosomes:
            mutate = random() < self.mutate_prob
            if mutate:
                mutated.append(chromosome.mutate())
            else:
                mutated.append(chromosome)
        return mutated
