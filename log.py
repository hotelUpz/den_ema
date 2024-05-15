import inspect
import json
from datetime import datetime
from io import BytesIO

class Logger():
    def __init__(self) -> None:
        self.logs_buffer = []
        self.all_errors = {}
        
    def log_to_buffer(self, file_name, line_number, exception_message):
        self.logs_buffer.append((file_name, line_number, exception_message))

    def log_all_errors(self, file_name, timestamp, exception_message):
        if file_name in self.all_errors:
            if exception_message not in self.all_errors[file_name]:
                self.all_errors[file_name].append((timestamp, exception_message))
        else:
            self.all_errors[file_name] = [(timestamp, exception_message)]

    def get_logs(self):
        print(f"logs list 23str: {self.logs_buffer}")
        file = BytesIO()
        file.write(str(self.logs_buffer).encode('utf-8'))
        file.name = "logs.txt"
        file.seek(0)
        self.logs_buffer = []
        return file

class JsonLogger(Logger):
    def __init__(self):
        super().__init__()
        self.json_logs_buffer = []

    def json_to_buffer(self, target, cur_time, data):
        self.json_logs_buffer.append((target, cur_time, data))

    def get_json_data(self):
        # print(self.json_logs_buffer)
        file = BytesIO()
        file.write(json.dumps(self.json_logs_buffer, indent=4).encode('utf-8'))
        file.name = "data.json"
        file.seek(0)
        self.json_logs_buffer = []
        return file

class Total_Logger(JsonLogger):
    def __init__(self):
        super().__init__()

total_log_instance = Total_Logger()

def log_exceptions_decorator(func):
    def wrapper(*args, **kwargs):
        try:
            return func(*args, **kwargs)
        except Exception as ex:
            timestamp = datetime.utcnow()
            current_frame = inspect.currentframe()
            caller_frame = current_frame.f_back
            file_name = caller_frame.f_code.co_filename
            line_number = caller_frame.f_lineno
            exception_message = str(ex)
            error_info = (file_name, line_number, exception_message)
            total_log_instance.log_to_buffer(*error_info)
            total_log_instance.log_all_errors(file_name, timestamp, exception_message)
            print(f"Error occurred in file '{file_name}', line {line_number}: {exception_message}")
    return wrapper
