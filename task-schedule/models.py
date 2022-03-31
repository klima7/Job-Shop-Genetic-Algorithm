import pandas as pd


class Job:

    def __init__(self, id_):
        self.id_ = id_
        self.tasks = []

    def __repr__(self):
        return f'Job(id={self.id_}, tasks={self.tasks})'

    @staticmethod
    def read_from_excel(path):
        jobs = []
        excel = pd.read_excel(path, header=None)
        data = excel.values[2:]

        for i in range(data.shape[1]//2):
            job = Job(i+1)
            job_cols = data[:, i*2:i*2+2]
            for task in job_cols:
                resource, time = task
                task = Task(resource, time)
                job.tasks.append(task)
            jobs.append(job)

        return jobs


class Task:

    def __init__(self, resource, time):
        self.resource = resource
        self.time = time

    def __repr__(self):
        return f'{self.resource}-{self.time}'
