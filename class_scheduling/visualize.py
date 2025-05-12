import matplotlib.pyplot as plt
from matplotlib.patches import Rectangle

def visualize_schedule(people, n_people=10, person_type="Student"):
    fig, ax = plt.subplots(figsize=(10, 8))
    blocks = ['A', 'B', 'C', 'D', 'E', 'F', 'G']
    colors = ['#f4d03f', '#76d7c4', '#85c1e9', '#f1948a', '#bb8fce', '#FFA500', '#aed6f1']

    for block_idx, block in enumerate(blocks):
        # ax.add_patch(Rectangle((0, block_idx), 1, 1, color=colors[block_idx], label=f'{block} Block'))
        ax.text(-0.1, block_idx + 0.5, f'{block} Block', va='center', ha='right', fontsize=10, weight='bold')

    for person_idx, person in enumerate(people[:n_people]):  # Visualize only the first n students
        for block_idx, course in person.schedule.items():
            if course:
                ax.add_patch(Rectangle((person_idx, block_idx), 1, 1, color=colors[block_idx], alpha=0.7))
                ax.text(person_idx + .5, block_idx + 0.5, course.name, va='center', ha='center', fontsize=8)

    ax.set_xlim(0, len(people[:n_people]))
    ax.set_ylim(0, len(blocks))
    ax.set_xticks(range(1, len(people[:n_people]) + 1))
    ax.set_xticklabels([f'{person_type} {i+1}' for i in range(len(people[:n_people]))], rotation=45, ha='right')
    ax.set_yticks([])
    ax.set_aspect('equal')
    plt.tight_layout()
    plt.show()

