# TIMER

Tool for measuring execution time (highly inspired from standard library `timeit` )

## Usage

```pycon
t = Timer(func=lambda: '-'.join(str(n) for n in range(100)))
t.repeat(repeat=10)

print(t)
```

Or, using the context manager
```pycon
with Timer() as t:
    '-'.join(str(n) for n in range(100))

print(t)
```