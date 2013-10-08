from fmtstr.fmtstr import FmtStr, BaseFmtStr
import time

def add_things(n):
    part = BaseFmtStr('hi', {'fg':36})
    whole = FmtStr(part)
    return sum([whole for _ in range(n)], FmtStr())

def timeit(n):
    t0 = time.time()
    add_things(n)
    t1 = time.time()
    print n, ':', t1 - t0
    return (t1 - t0)

ns = range(100, 2000, 100)

times = [timeit(i) for i in ns]
