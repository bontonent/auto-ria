import time
import asyncio

def work1(kol):
    time.sleep(kol)
    print(kol)


kols =  [1,2,3,4,1,2,3,4,5,5,6]
asyncio.gather(*(work1(k) for k in kols))



