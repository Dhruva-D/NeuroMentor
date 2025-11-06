from pymongo import MongoClient
from dotenv import load_dotenv
import os

load_dotenv()

MONGODB_URL = os.getenv("MONGODB_URL")

client = MongoClient(MONGODB_URL)
db = client.neuromentor

# Collections
users_collection = db.users
student_learning_state_collection = db.student_learning_state
question_attempts_collection = db.question_attempts
generated_questions_cache_collection = db.generated_questions_cache
concept_mastery_collection = db.concept_mastery
