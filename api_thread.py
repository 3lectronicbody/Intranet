from PySide6.QtCore import QObject, Signal
import requests
from config import API_PATH

class ApiWorker(QObject):
    success_signal = Signal(object)
    fail_signal = Signal(str)
    def __init__(self, method, url, data = None, params = None):
        super().__init__()

        self.method = method
        self.url = url
        self.data = data # for patch and post methods
        self.params = params # for get method if path parameters are needed

    def run(self):
        print("METHOD:", self.method)
        print("URL:", self.url)
        print("PARAMS:", self.params)
        print("DATA:", self.data)
        try:
            if self.data:
                response = requests.request(self.method, self.url,json=self.data)
                response.raise_for_status()
                self.success_signal.emit(response.json())
            elif self.params:
                response = requests.request(self.method, self.url, params=self.params)# request is generic method of requests module
                response.raise_for_status()
                self.success_signal.emit(response.json())
            else:
                response = requests.request(self.method, self.url)
                response.raise_for_status()
                self.success_signal.emit(response.json())


        except requests.exceptions.HTTPError as e:
            try:
                error_data = e.response.json()
                self.fail_signal.emit(error_data.get("detail", str(e)))
            except ValueError:
                self.fail_signal.emit(str(e))
        except requests.exceptions.RequestException as e:
            self.fail_signal.emit(str(e))





