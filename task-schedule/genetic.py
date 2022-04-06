import math
import matplotlib.pyplot as plt
from random import shuffle, choices, random, randrange
from models import ScheduledTask
from functools import total_ordering


@total_ordering
class Chromosome:

    def __init__(self, jobs, machines, genotype=None):
        self.jobs = jobs
        self.machines = machines
        self.genotype = genotype if genotype is not None else self._random_genotype()
        self.fitness = self._get_fitness()

    def _random_genotype(self):
        jobs_ids = [job.id for job in self.jobs.values() for _ in range(len(job.tasks))]
        shuffle(jobs_ids)
        return jobs_ids

    def to_phenotype(self):
        tasks = self._get_tasks_from_genotype()
        scheduled_tasks = self._schedule_tasks(tasks)
        return scheduled_tasks

    def _get_tasks_from_genotype(self):
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
        left_guard = ScheduledTask(start_time=-math.inf, end_time=0)
        right_guard = ScheduledTask(start_time=+math.inf, end_time=+math.inf)
        machine_queues = {machine: [left_guard, right_guard] for machine in self.machines}
        last_task_finish_times = {job_id: 0 for job_id in self.jobs.keys()}

        for task in tasks:
            queue = machine_queues[task.machine]
            last_finish_time = last_task_finish_times[task.job_id]
            scheduled_task = self._schedule_task(task, queue, last_finish_time)
            last_task_finish_times[task.job_id] = scheduled_task.end_time
            scheduled_tasks.append(scheduled_task)

        return scheduled_tasks

    @staticmethod
    def _schedule_task(task, machine_queue, last_finish_time):
        for i in range(len(machine_queue) - 1):
            prev_task, next_task = machine_queue[i:i+2]
            start_time = max(last_finish_time, prev_task.end_time)
            free_time = next_task.start_time - start_time
            if free_time >= task.time:
                scheduled_task = ScheduledTask(start_time=start_time, task=task)
                machine_queue.insert(i+1, scheduled_task)
                return scheduled_task
        assert False, "This shouldn't happen"

    def get_timespan(self):
        scheduled_tasks = self.to_phenotype()
        last_task = scheduled_tasks[1]

        for task in scheduled_tasks[1:]:
            if task.end_time > last_task.end_time:
                last_task = task

        return last_task.end_time

    def _get_fitness(self):
        return (3000 / self.get_timespan()) ** 2

    def mutate(self):
        pos_1 = randrange(0, len(self.genotype))
        pos_2 = randrange(0, len(self.genotype))
        new_genotype = self.genotype.copy()
        new_genotype[pos_1], new_genotype[pos_2] = new_genotype[pos_2], new_genotype[pos_1]
        return Chromosome(self.jobs, self.machines, genotype=new_genotype)

    def mutate_reverse(self):
        pos_1 = randrange(0, len(self.genotype)-2)
        pos_2 = randrange(pos_1+1, len(self.genotype))
        new_genotype = self.genotype.copy()
        new_genotype[pos_1:pos_2] = reversed(new_genotype[pos_1:pos_2])
        return Chromosome(self.jobs, self.machines, genotype=new_genotype)

    @classmethod
    def cross(cls, a, b):
        return cls.cross_single(a, b), cls.cross_single(b, a)

    @classmethod
    def cross_single(cls, a, b):
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

    def __init__(self, jobs, *, n_generations=20000, n_chromosomes=200, n_elite=10, cross_prob=0.7, mutate_prob=0.2):
        self.jobs = {job.id: job for job in jobs}
        self.n_generations = n_generations
        self.n_chromosomes = n_chromosomes
        self.n_elite = n_elite if (n_chromosomes - n_elite) % 2 == 0 else n_elite + 1
        self.cross_prob = cross_prob
        self.mutate_prob = mutate_prob

        self.machines = list({task.machine for job in jobs for task in job.tasks})
        self.population = None

    def solve(self):
        self.population = [Chromosome(self.jobs, self.machines) for _ in range(self.n_chromosomes)]

        for i in range(self.n_generations):
            self._next_generation()

            if i % 10 == 0:
                best_chromosome = sorted(self.population, reverse=True)[0]
                print(f'{i:<10} - {best_chromosome.get_timespan():>10}')
                if i % 100 == 0:
                    self.plot(best_chromosome.to_phenotype(), best_chromosome.get_timespan())

        best_chromosome = sorted(self.population, reverse=True)[0]
        print(best_chromosome.get_timespan())
        self.plot(best_chromosome.to_phenotype())
        return []

    def _next_generation(self):
        ordered = sorted(self.population, reverse=True)
        elite = ordered[:self.n_elite]
        selected = self._selection(ordered)
        crossed = self._cross(selected)
        mutated = self._mutate(crossed)
        self.population = [*elite, *mutated]

    def _selection(self, chromosomes):
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

    def plot(self, scheduled_tasks, timespan, numbers=False):
        # chart
        fig, ax = plt.subplots(figsize=(15, 5))

        # constants
        height = 6
        space = 2
        total_height = height + space

        # appearance
        ax.set_yticks([total_height * i + height/2 for i in self.machines])
        ax.set_yticklabels(self.machines)
        ax.yaxis.grid(color='gray', linestyle='dashed')
        ax.set_title('Job-Shop Gantt Chart')
        ax.set_xlabel('Time')
        ax.set_ylabel('Machines')
        ax.set_xlim([0, timespan])

        # data
        color_map = plt.cm.get_cmap('hsv', len(self.jobs))
        for machine in self.machines:
            machine_periods = [(task.start_time, task.end_time-task.start_time) for task in scheduled_tasks if task.task.machine == machine]
            colors = [color_map(task.task.job_id) for task in scheduled_tasks if task.task.machine == machine]
            ax.broken_barh(machine_periods, (total_height * machine, height), facecolors=colors, edgecolor='black')

        if numbers:
            for task in scheduled_tasks:
                job_id = task.task.job_id
                y = total_height * task.task.machine + 0.5 * height
                x = (task.start_time + task.end_time) / 2
                ax.text(x, y, job_id, fontsize='xx-small', horizontalalignment='center', verticalalignment='center')

        plt.show()
