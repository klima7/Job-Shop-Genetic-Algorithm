import pandas as pd
from random import seed
from models import Job, Task
from genetic import JobShopGA
from plot import plot


def read_jobs_from_excel(path):
    jobs = []
    excel = pd.read_excel(path, header=None)
    data = excel.values[2:]

    for i in range(data.shape[1] // 2):
        job = Job(i + 1)
        job_cols = data[:, i * 2:i * 2 + 2]
        for task in job_cols:
            machine, time = task
            task = Task(job, machine, time)
            job.tasks.append(task)
        jobs.append(job)

    return jobs


def find_lower_boundary(jobs):
    times_sums = []
    for machine in {task.machine for job in jobs for task in job.tasks}:
        machine_times = [task.time for job in jobs for task in job.tasks if task.machine == machine]
        times_sum = sum(machine_times)
        times_sums.append(times_sum)
    boundary = max(times_sums)
    return boundary


if __name__ == '__main__':
    seed(42)
    jobs = read_jobs_from_excel('tasks.xlsx')
    lower_boundary = find_lower_boundary(jobs)
    print('Lower boundary:', lower_boundary)    # 2073

    # 2074
    ga1 = JobShopGA(jobs, n_chromosomes=200, n_elite=10, cross_prob=0.7, mutate_prob=0.2, max_no_change_gens=200)

    # 2093 (210 generations)
    ga2 = JobShopGA(jobs, n_chromosomes=100, n_elite=4, cross_prob=0.7, mutate_prob=0.2, max_no_change_gens=100)

    # 2080 (70 generations)
    ga3 = JobShopGA(jobs, n_chromosomes=200, n_elite=10, cross_prob=1, mutate_prob=0.2, max_no_change_gens=50)

    tasks, timespan = ga1.solve()
    print('Best found timespan:', timespan)
    plot(tasks, timespan, 'Finished')
