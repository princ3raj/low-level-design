import time

class RetryPolicy:
    def __init__(self, max_retries: int = 3, delay: float = 0.1):
        self.max_retries = max_retries
        self.delay = delay

    def execute(self, action, *args, **kwargs):
        attempts = 0
        while attempts < self.max_retries:
            try:
                return action(*args, **kwargs)
            except Exception as e:
                attempts += 1
                print(f"Attempt {attempts} failed: {e}")
                if attempts == self.max_retries:
                    print("Max retries reached. Action failed.")
                    raise e
                time.sleep(self.delay)
