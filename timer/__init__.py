import gc
import numpy as np

from functools import wraps
from time import perf_counter

default_timer = perf_counter
default_number = 10_000
default_repeat = 3


class Timer:
    __slots__ = ('_total', '_times', '_number', '_timer', '_func', '_start')

    def __init__(self, func: callable = lambda: None, timer: type(perf_counter) = default_timer):
        """Tool for measuring execution time"""
        assert callable(func), f'argument must be a callable, got {type(func)}'
        self._timer = timer

        @wraps(func)
        def wrapped(n):
            with Timer() as t:
                for _ in range(n):
                    func()
            return t.time

        self._func = wrapped
        self._total = None
        self._times = np.array([])
        self._number = 0

    def __enter__(self):
        self._start = self._timer()
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self._total = self._timer() - self._start
        self._number = 1

    def __call__(self) -> float:
        return self.time

    def __repr__(self) -> str:
        return str(self.time)

    def __str__(self) -> str:
        if len(self._times) > 1:
            avg, std = (self.__format_time__(dt, precision=2) for dt in (self._times.mean(), self._times.std()))
            a, b = (self.__format_time__(dt, precision=2) for dt in (self.best, self.worst))
            return f'{avg} ± {std} per loop of {self._number} evaluations ' \
                   f'(mean ± std. dev. of {self._times.size}; range = [{a}, {b}])'
        else:
            return self.__format_time__(self.time, precision=2)

    def __sub__(self, other, verify=False):
        assert isinstance(other, Timer)
        if verify:
            assert self._number == other._number
            assert len(self._times) == len(other._times)

        timer = Timer()
        timer._total = self._total - other._total
        return timer

    def __add__(self, other, verify=False):
        assert isinstance(other, Timer)
        if verify:
            assert self._number == other._number
            assert len(self._times) == len(other._times)

        timer = Timer()
        timer._total = self._total + other._total
        return timer

    def timeit(self, number=None):
        """Time a single execution of the callable"""
        if number is None:
            number, time_taken = self.auto_number()
        else:
            time_taken = self.__timeit__(number)

        self._times = np.append(self._times, time_taken)
        self._number = number
        self.__update_total_time__()
        return self

    def repeat(self, repeat=default_repeat, number=None):
        """Time multiple executions of the callable"""
        self.timeit(number=number)

        for _ in range(1, repeat):
            self._times = np.append(self._times, self.__timeit__(self._number))
        self.__update_total_time__()

        return self

    def auto_number(self):
        i = 1
        while True:
            for j in 1, 2, 5:
                number = i * j
                time_taken = self.__timeit__(number)
                if time_taken >= 0.2:
                    return number, time_taken
            i *= 10

    @property
    def time(self) -> float:
        """Elapsed time (in seconds)"""
        return self._total

    @property
    def best(self) -> float:
        """Best time (in seconds)"""
        return min(self._times)

    @property
    def worst(self) -> float:
        """Worst time (in seconds)"""
        return max(self._times)

    @property
    def all_times(self) -> object:
        """List of elapsed time (in seconds)"""
        return self._times.tolist()

    @staticmethod
    def __format_time__(dt: float, precision: int) -> str:
        units = ['s', 'ms', 'µs', 'ns']
        scaling = [1, 1e3, 1e6, 1e9]
        order = min(-int(np.floor(np.log10(dt)) // 3), 3) if dt > 0.0 else 3

        return f'{dt * scaling[order]:.{precision}f} {units[order]}'

    def __timeit__(self, number):
        gcold = gc.isenabled()
        gc.disable()
        try:
            time_taken = self._func(number)
        finally:
            if gcold:
                gc.enable()

        return time_taken

    def __update_total_time__(self):
        self._total = self._times.sum()
