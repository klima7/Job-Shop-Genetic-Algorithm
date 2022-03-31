from models import Job

jobs = Job.read_from_excel('tasks.xlsx')
print(jobs)