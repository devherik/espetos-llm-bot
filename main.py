import asyncio

from data_ingestor.data_ingestor_imp import DataIngestor


async def main():
    database = DataIngestor()
    await database.initialize()

if __name__ == "__main__":
    asyncio.run(main())