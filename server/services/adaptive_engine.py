"""
Adaptive Learning Engine
Implements rule-based decision making for adaptive learning flow
"""

from typing import Dict, List, Optional
from enum import Enum
import logging
from datetime import datetime, timedelta
from database import (
    student_learning_state_collection,
    question_attempts_collection,
    concept_mastery_collection
)

logger = logging.getLogger(__name__)


class ActionType(Enum):
    """Possible actions the engine can decide"""
    NEXT_QUESTION = "next_question"
    SHOW_EXPLANATION = "show_explanation"
    GENERATE_PRACTICE = "generate_practice"
    GENERATE_EASY = "generate_easy"
    GENERATE_MEDIUM = "generate_medium"
    GENERATE_HARD = "generate_hard"
    CONCEPT_MASTERED = "concept_mastered"
    MARK_FOR_REVIEW = "mark_for_review"
    OFFER_HINT = "offer_hint"


class MasteryLevel(Enum):
    """Concept mastery levels (0-4)"""
    NOT_ATTEMPTED = 0
    STRUGGLING = 1      # Failed original + easy
    LEARNING = 2        # Passed easy, failed medium
    COMPETENT = 3       # Passed medium, failed hard
    MASTERED = 4        # Passed hard


class AdaptiveEngine:
    """
    Rule-based adaptive learning engine
    Decides what happens next based on student performance
    """
    
    def __init__(self, gemini_service):
        self.gemini = gemini_service
    
    async def process_answer(
        self,
        student_id: int,
        question_id: int,
        selected_answer: int,
        is_correct: bool,
        state: Dict,
        question_data: Dict
    ) -> Dict:
        """
        Main decision engine - decides what happens next
        
        Args:
            student_id: User ID
            question_id: Question ID
            selected_answer: Index of selected option
            is_correct: Whether answer was correct
            state: Current learning state
            question_data: Full question object
        
        Returns:
            {
                'action': ActionType,
                'data': {...},
                'reward': int,
                'nextState': {...},
                'message': str
            }
        """
        
        # Log the attempt
        await self._log_attempt(
            student_id,
            question_id,
            selected_answer,
            is_correct,
            state,
            question_data
        )
        
        if is_correct:
            return await self._handle_correct(student_id, question_id, state, question_data)
        else:
            return await self._handle_wrong(
                student_id,
                question_id,
                selected_answer,
                state,
                question_data
            )
    
    async def _handle_correct(
        self,
        student_id: int,
        question_id: int,
        state: Dict,
        question_data: Dict
    ) -> Dict:
        """Handle correct answer logic"""
        
        # Update state
        new_state = state.copy()
        new_state['consecutiveCorrect'] = state.get('consecutiveCorrect', 0) + 1
        new_state['consecutiveWrong'] = 0
        
        # Add to recent performance (keep last 5)
        recent = state.get('recentPerformance', [])
        recent.append(True)
        new_state['recentPerformance'] = recent[-5:]
        
        # Check if in adaptive practice mode
        if state.get('isInAdaptiveMode'):
            # Use the new progression system
            return await self.progress_difficulty(student_id, new_state, question_data)
        
        # Normal mode - just move to next question
        return {
            'action': ActionType.NEXT_QUESTION.value,
            'data': {
                'message': 'Correct! Well done! 🎯',
                'showConfetti': state.get('consecutiveCorrect', 0) >= 2
            },
            'reward': 10,
            'nextState': new_state
        }
    
    async def _handle_wrong(
        self,
        student_id: int,
        question_id: int,
        selected_answer: int,
        state: Dict,
        question_data: Dict
    ) -> Dict:
        """Handle wrong answer logic"""
        
        # Update state
        new_state = state.copy()
        new_state['consecutiveWrong'] = state.get('consecutiveWrong', 0) + 1
        new_state['consecutiveCorrect'] = 0
        
        # Add to recent performance (keep last 5)
        recent = state.get('recentPerformance', [])
        recent.append(False)
        new_state['recentPerformance'] = recent[-5:]
        
        # Get correct answer text
        correct_answer = self._get_correct_answer_text(question_data)
        student_answer = question_data['options'][selected_answer]['text']
        
        # Always show explanation on wrong answers in normal mode (not in adaptive practice mode)
        if not state.get('isInAdaptiveMode'):
            # Generate explanation
            try:
                explanation = await self.gemini.generate_explanation(
                    question=question_data.get('question', ''),
                    correct_answer=correct_answer,
                    student_answer=student_answer,
                    class_level=state.get('classLevel', 1),
                    concept_tags=question_data.get('conceptTags', []),
                    attempt_number=new_state['consecutiveWrong']
                )
                
                logger.info(f"Student {student_id}: Wrong answer (attempt {new_state['consecutiveWrong']}), showing explanation")
                
                return {
                    'action': ActionType.SHOW_EXPLANATION.value,
                    'data': {
                        'explanation': explanation,
                        'correctAnswer': correct_answer,
                        'offerPractice': new_state['consecutiveWrong'] >= 2,  # Offer practice after 2+ failures
                        'message': 'Let me help you understand this! 📚'
                    },
                    'reward': -5,
                    'nextState': new_state
                }
            except Exception as e:
                logger.error(f"Error generating explanation: {e}", exc_info=True)
                # Fallback to simple message
                return {
                    'action': ActionType.SHOW_EXPLANATION.value,
                    'data': {
                        'explanation': {
                            'encouragement': 'Good try! Let\'s learn together! 🦉',
                            'explanation': f'The correct answer is: {correct_answer}',
                            'example': 'Think about it carefully and try again!',
                            'tip': 'You can do it! 💪'
                        },
                        'correctAnswer': correct_answer,
                        'offerPractice': new_state['consecutiveWrong'] >= 2
                    },
                    'reward': -5,
                    'nextState': new_state
                }
        
        # In adaptive mode - struggling with practice questions
        if state.get('isInAdaptiveMode'):
            current_diff = state.get('currentDifficulty', 'easy')
            
            if new_state['consecutiveWrong'] == 1:
                # First failure in adaptive mode - show simpler explanation
                try:
                    explanation = await self.gemini.generate_explanation(
                        question=question_data.get('question', ''),
                        correct_answer=correct_answer,
                        student_answer=student_answer,
                        class_level=state.get('classLevel', 1),
                        concept_tags=question_data.get('conceptTags', []),
                        attempt_number=2  # Simpler explanation
                    )
                    
                    logger.info(f"Student {student_id}: Struggling in {current_diff} mode")
                    
                    return {
                        'action': ActionType.SHOW_EXPLANATION.value,
                        'data': {
                            'explanation': explanation,
                            'correctAnswer': correct_answer,
                            'offerPractice': False,
                            'message': 'That\'s okay! Let\'s try this again! 💙'
                        },
                        'reward': -3,
                        'nextState': new_state
                    }
                except Exception as e:
                    logger.error(f"Error in adaptive mode explanation: {e}")
            
            else:
                # Failed twice in adaptive mode - mark for review and continue
                concept_tags = question_data.get('conceptTags', [])
                await self._mark_for_review(student_id, concept_tags)
                
                logger.info(f"Student {student_id}: Marked {concept_tags} for review")
                
                return {
                    'action': ActionType.MARK_FOR_REVIEW.value,
                    'data': {
                        'message': 'We\'ll practice this more later! 📝 Let\'s move on for now.',
                        'moveToNext': True,
                        'conceptsForReview': concept_tags
                    },
                    'reward': -10,
                    'nextState': {
                        **new_state,
                        'isInAdaptiveMode': False,
                        'consecutiveWrong': 0
                    }
                }
        
        # This shouldn't be reached if we're in normal mode (explanation is shown above)
        # This is only for edge cases in adaptive mode
        logger.warning(f"Unexpected flow: student_id={student_id}, isInAdaptiveMode={state.get('isInAdaptiveMode')}")
        return {
            'action': ActionType.NEXT_QUESTION.value,
            'data': {
                'message': 'Not quite right. Try the next one! 💪',
                'correctAnswer': correct_answer
            },
            'reward': -3,
            'nextState': new_state
        }
    
    def _get_correct_answer_text(self, question_data: Dict) -> str:
        """Extract correct answer text from question"""
        for option in question_data.get('options', []):
            if option.get('correct'):
                return option.get('text', '')
        return ''
    
    async def start_practice_mode(
        self,
        student_id: int | str,
        original_question: Dict,
        concept_tags: List[str],
        class_level: int
    ) -> Dict:
        """
        Start adaptive practice mode
        Generates first EASY question for the concept
        
        Returns:
            {
                'action': 'generate_easy',
                'data': {
                    'question': {...},  # Generated question
                    'difficulty': 'easy',
                    'message': '...'
                },
                'nextState': {...}
            }
        """
        try:
            # Generate first EASY practice question
            correct_answer = self._get_correct_answer_text(original_question)
            
            question = await self.gemini.generate_similar_question(
                original_question=original_question.get('question', ''),
                correct_answer=correct_answer,
                concept_tags=concept_tags,
                difficulty='easy',
                class_level=class_level
            )
            
            # Initialize practice state
            practice_state = {
                'classLevel': class_level,
                'consecutiveCorrect': 0,
                'consecutiveWrong': 0,
                'currentDifficulty': 'easy',
                'isInAdaptiveMode': True,
                'recentPerformance': [],
                'conceptTags': concept_tags,
                'practiceLevel': 1  # Easy=1, Medium=2, Hard=3
            }
            
            logger.info(f"Student {student_id}: Starting practice mode for {concept_tags}")
            
            return {
                'action': ActionType.GENERATE_EASY.value,
                'data': {
                    'question': question,
                    'difficulty': 'easy',
                    'message': '🎯 Let\'s practice with an EASY question!',
                    'progress': {'current': 1, 'total': 3}  # Easy (1/3)
                },
                'reward': 0,
                'nextState': practice_state
            }
            
        except Exception as e:
            logger.error(f"Error starting practice mode: {e}", exc_info=True)
            raise
    
    async def progress_difficulty(
        self,
        student_id: int | str,
        state: Dict,
        question_data: Dict
    ) -> Dict:
        """
        Progress to next difficulty level after success
        Easy → Medium → Hard → Mastered
        
        Returns next question or mastery completion
        """
        current_level = state.get('practiceLevel', 1)
        concept_tags = state.get('conceptTags', [])
        class_level = state.get('classLevel', 1)
        
        # Level 1 (Easy) → Level 2 (Medium)
        if current_level == 1:
            try:
                correct_answer = self._get_correct_answer_text(question_data)
                
                question = await self.gemini.generate_similar_question(
                    original_question=question_data.get('question', ''),
                    correct_answer=correct_answer,
                    concept_tags=concept_tags,
                    difficulty='medium',
                    class_level=class_level
                )
                
                new_state = state.copy()
                new_state['currentDifficulty'] = 'medium'
                new_state['practiceLevel'] = 2
                new_state['consecutiveCorrect'] = 0
                
                logger.info(f"Student {student_id}: Progressing to MEDIUM")
                
                return {
                    'action': ActionType.GENERATE_MEDIUM.value,
                    'data': {
                        'question': question,
                        'difficulty': 'medium',
                        'message': '🌟 Great! Now try a MEDIUM question!',
                        'progress': {'current': 2, 'total': 3},
                        'showCelebration': True
                    },
                    'reward': 15,
                    'nextState': new_state
                }
            except Exception as e:
                logger.error(f"Error generating medium question: {e}")
                raise
        
        # Level 2 (Medium) → Level 3 (Hard)
        elif current_level == 2:
            try:
                correct_answer = self._get_correct_answer_text(question_data)
                
                question = await self.gemini.generate_similar_question(
                    original_question=question_data.get('question', ''),
                    correct_answer=correct_answer,
                    concept_tags=concept_tags,
                    difficulty='hard',
                    class_level=class_level
                )
                
                new_state = state.copy()
                new_state['currentDifficulty'] = 'hard'
                new_state['practiceLevel'] = 3
                new_state['consecutiveCorrect'] = 0
                
                logger.info(f"Student {student_id}: Progressing to HARD")
                
                return {
                    'action': ActionType.GENERATE_HARD.value,
                    'data': {
                        'question': question,
                        'difficulty': 'hard',
                        'message': '🔥 Excellent! Final challenge - HARD question!',
                        'progress': {'current': 3, 'total': 3},
                        'showCelebration': True
                    },
                    'reward': 20,
                    'nextState': new_state
                }
            except Exception as e:
                logger.error(f"Error generating hard question: {e}")
                raise
        
        # Level 3 (Hard) → MASTERED!
        elif current_level == 3:
            # Update mastery to MASTERED (level 4)
            await self._update_mastery(
                student_id,
                concept_tags,
                MasteryLevel.MASTERED.value
            )
            
            new_state = state.copy()
            new_state['isInAdaptiveMode'] = False
            new_state['consecutiveCorrect'] = 0
            
            logger.info(f"Student {student_id}: MASTERED {concept_tags}!")
            
            return {
                'action': ActionType.CONCEPT_MASTERED.value,
                'data': {
                    'message': '🎉 AMAZING! You\'ve MASTERED this concept! 🏆',
                    'conceptTags': concept_tags,
                    'masteryLevel': 4,
                    'showConfetti': True,
                    'badgeEarned': True
                },
                'reward': 50,
                'nextState': new_state
            }
        
        # Shouldn't reach here
        return {
            'action': ActionType.NEXT_QUESTION.value,
            'data': {'message': 'Great job! Continue practicing! 💪'},
            'reward': 5,
            'nextState': state
        }
    
    async def _update_mastery(
        self,
        student_id: int,
        concept_tags: List[str],
        level: MasteryLevel
    ):
        """Update concept mastery in database"""
        for concept in concept_tags:
            try:
                # Update or insert mastery record
                concept_mastery_collection.update_one(
                    {
                        'student_id': student_id,
                        'concept_tag': concept
                    },
                    {
                        '$set': {
                            'mastery_level': level.value,
                            'updated_at': datetime.utcnow()
                        },
                        '$setOnInsert': {
                            'created_at': datetime.utcnow(),
                            'total_attempts': 0,
                            'successful_attempts': 0
                        }
                    },
                    upsert=True
                )
                
                logger.info(f"Updated mastery for {student_id}/{concept} to {level.name}")
            except Exception as e:
                logger.error(f"Error updating mastery: {e}")
    
    async def _mark_for_review(
        self,
        student_id: int,
        concept_tags: List[str]
    ):
        """Mark concepts for future review"""
        review_date = datetime.utcnow() + timedelta(days=1)
        
        for concept in concept_tags:
            try:
                concept_mastery_collection.update_one(
                    {
                        'student_id': student_id,
                        'concept_tag': concept
                    },
                    {
                        '$set': {
                            'next_review_date': review_date,
                            'needs_review': True,
                            'updated_at': datetime.utcnow()
                        }
                    },
                    upsert=True
                )
                
                logger.info(f"Marked {concept} for review for student {student_id}")
            except Exception as e:
                logger.error(f"Error marking for review: {e}")
    
    async def _log_attempt(
        self,
        student_id: int,
        question_id: int,
        selected_answer: int,
        is_correct: bool,
        state: Dict,
        question_data: Dict
    ):
        """Log question attempt to database"""
        try:
            question_attempts_collection.insert_one({
                'student_id': student_id,
                'question_id': question_id,
                'question_type': state.get('questionType', 'original'),
                'selected_answer': selected_answer,
                'is_correct': is_correct,
                'time_spent': state.get('timeSpent', 0),
                'hints_used': state.get('hintsUsed', 0),
                'difficulty': state.get('currentDifficulty', 'easy'),
                'is_adaptive_mode': state.get('isInAdaptiveMode', False),
                'created_at': datetime.utcnow()
            })
        except Exception as e:
            logger.error(f"Error logging attempt: {e}")


# Create singleton instance (will be initialized with gemini_service in main.py)
adaptive_engine = None
