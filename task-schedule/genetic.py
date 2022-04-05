import math
from random import shuffle
from models import ScheduledTask, Task


class Chromosome:

    def __init__(self, jobs):
        self.jobs = jobs
        self.genotype = self._random_genotype()
        self.machines = self._extract_machines()

    def _random_genotype(self):
        jobs_ids = [job.id for job in self.jobs.values() for _ in range(len(job.tasks))]
        shuffle(jobs_ids)
        return jobs_ids

    def _extract_machines(self):
        machines = {task.machine for job in self.jobs.values() for task in job.tasks}
        return list(machines)

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

    def get_fitness(self):
        scheduled_tasks = self.to_phenotype()
        last_task = scheduled_tasks[1]

        for task in scheduled_tasks[1:]:
            if task.end_time > last_task.end_time:
                last_task = task

        return last_task.end_time

    def plot(self):
        pass


class JobShopProblem:

    def __init__(self, jobs):
        self.jobs = jobs

    def solve(self, n_generation=100, n_chromosomes=100):
        generation = [Chromosome(self.jobs) for _ in range(n_chromosomes)]
        tasks = generation[0].to_phenotype()
        temp = [task for task in tasks if task.task.job_id == 2]
        print(sorted(temp, key=lambda t: t.start_time))
        return []
