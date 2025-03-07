import asyncio

from .parser import process

"""
Данная реализация загружает данные быстрее, но менее безопасна, 
т.к загружает данные в БД не используя транзакции, там, где они нужны
"""


async def main():
    while True:
        await process()
        await asyncio.sleep(3600)


if __name__ == "__main__":
    asyncio.run(main())
