from motor.motor_asyncio import AsyncIOMotorClient
from app.settings import settings

client = AsyncIOMotorClient(settings.MONGO_URI)
db = client[settings.MONGO_DB_NAME]
documents_collection = db['documents']
