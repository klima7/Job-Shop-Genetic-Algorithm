from random import shuffle


class Chromosome:

    def __init__(self, jobs):
        self.jobs = jobs
        self.genotype = self.random_genotype()

    def random_genotype(self):
        jobs_ids = [job.id for job in self.jobs.values() for _ in range(len(job.tasks))]
        shuffle(jobs_ids)
        return jobs_ids

    def to_phenotype(self):
        phenotype = []
        counters = {job_id: 0 for job_id in self.jobs.keys()}

        for gen in self.genotype:
            job = self.jobs[gen]
            task_no = counters[gen]
            task = job.tasks[task_no]
            phenotype.append(task)
            counters[gen] += 1

        return phenotype

    def get_fitness(self):
        pass


class JobShopProblem:

    def __init__(self, jobs):
        self.jobs = jobs

    def solve(self, n_generation=100, n_chromosomes=100):
        generation = [Chromosome(self.jobs) for _ in range(n_chromosomes)]
        return []
