import asyncio

from .parser import process


async def main():
    while True:
        await process()
        await asyncio.sleep(3600)


if __name__ == "__main__":
    asyncio.run(main())
