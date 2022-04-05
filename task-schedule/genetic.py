import math
import matplotlib.pyplot as plt
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
        # chart
        tasks = self.to_phenotype()
        fig, ax = plt.subplots()

        # constants
        height = 7
        space = 3
        total_height = height + space

        # appearance
        ax.set_yticks([total_height * i + height/2 for i in self.machines])
        ax.set_yticklabels(self.machines)
        ax.yaxis.grid(color='gray', linestyle='dashed')
        ax.set_title('Job-Shop Gantt Chart')
        ax.set_xlabel('Time')
        ax.set_ylabel('Machines')
        ax.set_xlim(left=0, right=self.get_fitness())

        # data
        color_map = plt.cm.get_cmap('hsv', len(self.jobs))
        for machine in self.machines:
            machine_periods = [(task.start_time, task.end_time-task.start_time) for task in tasks if task.task.machine == machine]
            colors = [color_map(task.task.job_id) for task in tasks if task.task.machine == machine]
            ax.broken_barh(machine_periods, (total_height * machine, height), facecolors=colors, edgecolor='black')

        plt.show()


class JobShopProblem:

    def __init__(self, jobs):
        self.jobs = jobs

    def solve(self, n_generation=100, n_chromosomes=100):
        generation = [Chromosome(self.jobs) for _ in range(n_chromosomes)]
        tasks = generation[0].to_phenotype()
        temp = [task for task in tasks if task.task.machine == 1]
        print(sorted(temp, key=lambda t: t.start_time))
        generation[0].plot()
        return []
