import time
from datetime import timedelta


def log_time(func=None, human_readable: bool = False):
	if func is None:
		return lambda inner_func: log_time(inner_func, human_readable)

	def wrapper(*args, **kwargs):
		start_time = time.time()
		result = func(*args, **kwargs)
		end_time = time.time()

		took_time = end_time - start_time
		took_time_to_show = str(timedelta(seconds=took_time)) if human_readable else f'{took_time:.6f} seconds'
		print(f"'{func.__name__}' took {took_time_to_show} to execute.")

		return result

	return wrapper
