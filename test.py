import asyncio

SENTINEL = object()

async def worker(name, queue):
    while True:
        item = await queue.get()
        if item is SENTINEL:
            queue.task_done()
            print(f"{name} received sentinel, exiting")
            return
        # process item (use run_in_executor for blocking work)
        print(f"{name} processing {item}")
        await asyncio.sleep(0.5)
        queue.task_done()

async def main():
    q = asyncio.Queue()
    # produce items
    for i in range(10):
        await q.put(i)

    # start 3 workers
    tasks = [asyncio.create_task(worker(f"worker-{i+1}", q)) for i in range(3)]

    # put one sentinel per worker so each can exit when work is done
    for _ in tasks:
        await q.put(SENTINEL)

    # wait until all tasks exit
    await asyncio.gather(*tasks)
    print("all workers done")

asyncio.run(main())
