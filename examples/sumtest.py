from curtsies.formatstring import FmtStr, Chunk
import time

def add_things(n):
    part = Chunk('hi', {'fg':36})
    whole = FmtStr(part)
    return sum([whole for _ in range(n)], FmtStr())

def timeit(n):
    t0 = time.time()
    add_things(n)
    t1 = time.time()
    print(n, ':', t1 - t0)
    return (t1 - t0)

if __name__ == '__main__':
    ns = range(100, 2000, 100)

    times = [timeit(i) for i in ns]
