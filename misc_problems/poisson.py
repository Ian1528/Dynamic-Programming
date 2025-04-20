import numpy as np
import matplotlib.pyplot as plt

def simulate_poisson_process(rate, time_duration):
    """
    Simulates a Poisson process.

    Args:
        rate (float): The average rate of events per unit of time (lambda).
        time_duration (float): The total time duration for the simulation.

    Returns:
        numpy.ndarray: An array of event times.
    """
    # Generate inter-arrival times from an exponential distribution
    inter_arrival_times = np.random.exponential(1/rate, size=1000)
    
    # Calculate event arrival times by cumulatively summing the inter-arrival times
    arrival_times = np.cumsum(inter_arrival_times)
    
    # Filter arrival times within the specified time duration
    arrival_times_within_duration = arrival_times[arrival_times <= time_duration]
    
    return arrival_times_within_duration

sim_results = np.empty(10000)
for i in range(10000):
    n = np.random.poisson(1)
    probs = [.5, 1/3, 1/6]
    n_friends = np.random.choice([0, 1, 2], n, p=probs)
    total_people = n + np.sum(n_friends)
    sim_results[i] = total_people

total_people_freq_counts = np.bincount(sim_results.astype(int))

# plot a poisson process with rate 5/3
poisson_samples = np.random.poisson(5/3, 10000)
poisson_frequency_counts = np.bincount(poisson_samples)

# plot the distribution of total people
plt.figure(figsize=(10, 6))
plt.bar(np.arange(len(total_people_freq_counts)), total_people_freq_counts, alpha=0.5, color='blue', label="Simualte")
plt.xlabel("number of people")
plt.ylabel("number of frequency of occurance")
plt.title('Distribution of Total People in the Poisson Process')

print("mean of simulation: ", np.mean(sim_results))
print("variance of simulation: ", np.var(sim_results))

print("mean of poisson: ", np.mean(poisson_samples))
print("variance of poisson: ", np.var(poisson_samples))

plt.bar(np.arange(len(poisson_frequency_counts)), poisson_frequency_counts, alpha=0.5, color='red', label="Poisson")
plt.legend()
plt.show()
