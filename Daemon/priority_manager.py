class PriorityManager:
    def __init__(self):
        # Fixed priority classes: A is highest, E is lowest
        self.priority_map = {
            'A': 1,
            'B': 2,
            'C': 3,
            'D': 4,
            'E': 5
        }

    def get_priority_value(self, job_class, priority=0):
        """
        Converts job class and priority into a single numeric value.
        Lower values have higher priority in the queue.

        Args:
            job_class (str): The job class (e.g., 'A', 'B', 'C').
            priority (int): The sub-priority within the class (default is 0).

        Returns:
            int: Combined priority value.
        """
        base_priority = self.priority_map.get(job_class.upper(), 99)  # Default to very low if unknown class
        return (base_priority * 100) + priority  # Combines class and priority into one value
