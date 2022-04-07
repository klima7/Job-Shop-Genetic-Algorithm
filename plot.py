import matplotlib.pyplot as plt


def plot(scheduled_tasks, timespan, iteration):
    machines = list(sorted({task[2].machine for task in scheduled_tasks}))
    jobs = list(sorted({task[2].job_id for task in scheduled_tasks}))

    # chart
    fig, axs = plt.subplots(2, 1, figsize=(15, 5), gridspec_kw={'height_ratios': [1, 15]})
    ax2, ax = axs

    # constants
    height = 6
    space = 2
    total_height = height + space

    # appearance
    ax.set_yticks([total_height * i + height / 2 for i in machines])
    ax.set_yticklabels(machines)
    ax.yaxis.grid(color='gray', linestyle='dashed')
    ax.set_title('Gantt Chart')
    ax.set_xlabel('Time')
    ax.set_ylabel('Machines')
    ax.set_xlim([0, timespan])

    # data
    color_map = plt.cm.get_cmap('hsv', len(jobs))
    for machine in machines:
        machine_periods = [(s_task[0], s_task[1] - s_task[0]) for s_task in scheduled_tasks if s_task[2].machine == machine]
        colors = [color_map(s_task[2].job_id) for s_task in scheduled_tasks if s_task[2].machine == machine]
        ax.broken_barh(machine_periods, (total_height * machine, height), facecolors=colors, edgecolor='black')

    # text info
    ax2.axis('off')
    ax2.set_xlim([0, 1])
    ax2.set_ylim([-1, 1])
    ax2.text(0.25, 0, f'Generation: {iteration}', fontsize='xx-large',
             horizontalalignment='center', verticalalignment='center')
    ax2.text(0.75, 0, f'Timespan: {timespan}', fontsize='xx-large',
             horizontalalignment='center', verticalalignment='center')

    # plt.savefig(fname=str(time())+'.svg')
    plt.show()
