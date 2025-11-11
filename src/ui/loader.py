from rich.live import Live
from rich.padding import Padding
from rich.spinner import Spinner


class Loader:
    def __init__(self, text: str, padding: int = 4):
        self.spinner = Live(Padding(Spinner("dots", text=text), (0, 0, 0, padding)), transient=True, refresh_per_second=10)

    def start(self):
        self.spinner.start()

    def stop(self):
        self.spinner.stop()
