"""
Learning API Routes
Handles adaptive learning endpoints
"""

from fastapi import APIRouter, HTTPException, Depends
from pydantic import BaseModel, Field
from typing import Dict, List, Optional, Any
import logging
from datetime import datetime

from services.gemini_service import gemini_service
from services.adaptive_engine import AdaptiveEngine
from database import (
    student_learning_state_collection,
    generated_questions_cache_collection
)

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api/learning", tags=["learning"])

# Initialize adaptive engine
adaptive_engine = AdaptiveEngine(gemini_service)


# ==================== Request/Response Models ====================

class ProcessAnswerRequest(BaseModel):
    studentId: int | str  # MongoDB ObjectId string or integer
    questionId: int | str  # Can be int or string
    selectedAnswer: int
    isCorrect: bool
    currentState: Dict[str, Any]
    questionData: Dict[str, Any]
    
    class Config:
        populate_by_name = True


class ProcessAnswerResponse(BaseModel):
    action: str
    data: Dict
    reward: int
    nextState: Dict
    message: Optional[str] = None


class GenerateQuestionRequest(BaseModel):
    originalQuestion: str
    correctAnswer: str
    conceptTags: List[str]
    difficulty: str
    classLevel: int
    questionId: Optional[int] = None


class StartAdaptiveModeRequest(BaseModel):
    studentId: int | str  # MongoDB ObjectId string or integer
    questionData: Dict
    classLevel: int


# ==================== Endpoints ====================

@router.post("/process-answer", response_model=ProcessAnswerResponse)
async def process_answer(request: ProcessAnswerRequest):
    """
    Process student's answer and decide next action
    
    This is the main endpoint for adaptive learning flow
    """
    try:
        logger.info(f"Processing answer for student {request.studentId}, question {request.questionId}")
        logger.debug(f"Request data: {request.model_dump()}")
        
        result = await adaptive_engine.process_answer(
            student_id=request.studentId,
            question_id=request.questionId,
            selected_answer=request.selectedAnswer,
            is_correct=request.isCorrect,
            state=request.currentState,
            question_data=request.questionData
        )
        
        # Save updated state to database
        await _save_learning_state(
            request.studentId,
            request.questionId,
            result['nextState']
        )
        
        logger.info(f"Returning result: action={result.get('action')}, has_explanation={bool(result.get('data', {}).get('explanation'))}")
        logger.debug(f"Full result: {result}")
        
        return result
        
    except Exception as e:
        logger.error(f"Error processing answer: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/generate-question")
async def generate_question(request: GenerateQuestionRequest):
    """
    Generate similar question at specified difficulty
    Uses caching to reduce API costs
    """
    try:
        # Check cache first
        if request.questionId:
            cached = await _get_cached_question(
                request.questionId,
                request.difficulty,
                request.classLevel
            )
            if cached:
                logger.info(f"Using cached question for {request.questionId}/{request.difficulty}")
                return cached
        
        # Generate new question
        logger.info(f"Generating {request.difficulty} question for concepts: {request.conceptTags}")
        
        question = await gemini_service.generate_similar_question(
            original_question=request.originalQuestion,
            correct_answer=request.correctAnswer,
            concept_tags=request.conceptTags,
            difficulty=request.difficulty,
            class_level=request.classLevel
        )
        
        # Cache the generated question
        if request.questionId:
            await _cache_question(
                request.questionId,
                request.difficulty,
                request.classLevel,
                question
            )
        
        return question
        
    except Exception as e:
        logger.error(f"Error generating question: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/start-adaptive-mode")
async def start_adaptive_mode(request: StartAdaptiveModeRequest):
    """
    Start adaptive practice mode for a student
    Easy → Medium → Hard progression system
    """
    try:
        logger.info(f"Starting practice mode for student {request.studentId}")
        
        result = await adaptive_engine.start_practice_mode(
            student_id=request.studentId,
            original_question=request.questionData,
            concept_tags=request.questionData.get('conceptTags', []),
            class_level=request.classLevel
        )
        
        # Add generated question ID for frontend tracking
        if 'question' in result.get('data', {}):
            result['data']['question']['id'] = f"practice_{request.questionData.get('id', 0)}_easy"
        
        logger.info(f"Practice mode started: {result.get('action')}")
        
        return result
        
    except Exception as e:
        logger.error(f"Error starting adaptive mode: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/mastery/{student_id}")
async def get_mastery_status(student_id: int):
    """
    Get student's concept mastery status
    """
    try:
        from database import concept_mastery_collection
        
        mastery_records = list(concept_mastery_collection.find(
            {'student_id': student_id}
        ))
        
        # Convert ObjectId to string for JSON serialization
        for record in mastery_records:
            record['_id'] = str(record['_id'])
        
        return {
            'studentId': student_id,
            'masteryRecords': mastery_records,
            'totalConcepts': len(mastery_records),
            'masteredConcepts': sum(1 for r in mastery_records if r.get('mastery_level', 0) >= 4)
        }
        
    except Exception as e:
        logger.error(f"Error getting mastery status: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/review-concepts/{student_id}")
async def get_review_concepts(student_id: int):
    """
    Get concepts that need review for a student
    """
    try:
        from database import concept_mastery_collection
        
        review_concepts = list(concept_mastery_collection.find({
            'student_id': student_id,
            'needs_review': True
        }))
        
        # Convert ObjectId to string
        for concept in review_concepts:
            concept['_id'] = str(concept['_id'])
        
        return {
            'studentId': student_id,
            'reviewConcepts': review_concepts,
            'totalToReview': len(review_concepts)
        }
        
    except Exception as e:
        logger.error(f"Error getting review concepts: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=str(e))


# ==================== Helper Functions ====================

async def _save_learning_state(student_id: int, question_id: int, state: Dict):
    """Save or update learning state in database"""
    try:
        student_learning_state_collection.update_one(
            {
                'student_id': student_id,
                'question_id': question_id
            },
            {
                '$set': {
                    **state,
                    'updated_at': datetime.utcnow()
                },
                '$setOnInsert': {
                    'created_at': datetime.utcnow()
                }
            },
            upsert=True
        )
    except Exception as e:
        logger.error(f"Error saving learning state: {e}")


async def _get_cached_question(question_id: int, difficulty: str, class_level: int) -> Optional[Dict]:
    """Get cached generated question"""
    try:
        cached = generated_questions_cache_collection.find_one({
            'original_question_id': question_id,
            'difficulty': difficulty,
            'class_level': class_level
        })
        
        if cached:
            # Increment usage count
            generated_questions_cache_collection.update_one(
                {'_id': cached['_id']},
                {'$inc': {'usage_count': 1}}
            )
            
            return cached.get('question_data')
        
        return None
        
    except Exception as e:
        logger.error(f"Error getting cached question: {e}")
        return None


async def _cache_question(question_id: int, difficulty: str, class_level: int, question_data: Dict):
    """Cache generated question for reuse"""
    try:
        generated_questions_cache_collection.insert_one({
            'original_question_id': question_id,
            'difficulty': difficulty,
            'class_level': class_level,
            'question_data': question_data,
            'generated_by': 'gemini',
            'usage_count': 0,
            'created_at': datetime.utcnow()
        })
        
        logger.info(f"Cached question {question_id}/{difficulty}")
        
    except Exception as e:
        logger.error(f"Error caching question: {e}")
