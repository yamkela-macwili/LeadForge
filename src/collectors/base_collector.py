from abc import ABC, abstractmethod
import pandas as pd
import time
import random

class BaseCollector(ABC):
    def __init__(self, niche_name):
        self.niche_name = niche_name
        self.data = []

    @abstractmethod
    def collect(self):
        """
        Main method to execute the collection process.
        Should populate self.data with dictionaries.
        """
        pass

    def save_to_csv(self, filename):
        """
        Saves the collected data to a CSV file.
        """
        if not self.data:
            print("No data to save.")
            return
        
        df = pd.DataFrame(self.data)
        df.to_csv(filename, index=False)
        print(f"Data saved to {filename}")

    def random_delay(self, min_seconds=1, max_seconds=3):
        """
        Sleeps for a random amount of time to avoid rate limiting.
        """
        time.sleep(random.uniform(min_seconds, max_seconds))
