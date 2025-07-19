import asyncio
import os

from data_ingestor.data_ingestor_imp import DataIngestor

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
env_path = os.path.join(BASE_DIR, '.env')

async def main():
    database = DataIngestor()
    await database.initialize()

if __name__ == "__main__":
    asyncio.run(main())