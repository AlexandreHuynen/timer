import time

from timer import Timer


def test_timer(wait=1):
    with Timer() as t:
        time.sleep(round(wait))
    assert round(t.time) == round(wait)

    t = Timer(func=lambda: '-'.join(str(n) for n in range(100)))
    t.repeat(repeat=10)
    assert len(t._times) == 10
