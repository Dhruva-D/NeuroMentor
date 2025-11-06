"""
Gemini AI Service for Adaptive Learning
Handles AI-powered explanations and question generation
"""

import google.generativeai as genai
import os
import json
from typing import Dict, List, Optional
import logging
from dotenv import load_dotenv

load_dotenv()

logger = logging.getLogger(__name__)


class GeminiService:
    """Service for interacting with Google Gemini AI"""
    
    def __init__(self):
        api_key = os.getenv("GEMINI_API_KEY")
        if not api_key:
            raise ValueError("GEMINI_API_KEY not found in environment variables")
        
        genai.configure(api_key=api_key)
        # Use gemini-2.5-flash (the latest model)
        self.model = genai.GenerativeModel('gemini-2.0-flash-exp')
        
        # Configure generation settings
        self.generation_config = {
            "temperature": 0.7,
            "top_p": 0.95,
            "top_k": 40,
            "max_output_tokens": 1024,
        }
        
        # Safety settings - allow educational content
        self.safety_settings = [
            {
                "category": "HARM_CATEGORY_HARASSMENT",
                "threshold": "BLOCK_NONE"
            },
            {
                "category": "HARM_CATEGORY_HATE_SPEECH",
                "threshold": "BLOCK_NONE"
            },
            {
                "category": "HARM_CATEGORY_SEXUALLY_EXPLICIT",
                "threshold": "BLOCK_NONE"
            },
            {
                "category": "HARM_CATEGORY_DANGEROUS_CONTENT",
                "threshold": "BLOCK_NONE"
            }
        ]
    
    async def generate_explanation(
        self,
        question: str,
        correct_answer: str,
        student_answer: str,
        class_level: int,
        concept_tags: List[str],
        attempt_number: int = 1
    ) -> Dict:
        """
        Generate age-appropriate explanation for wrong answer
        
        Args:
            question: The original question text
            correct_answer: The correct answer text
            student_answer: What the student selected
            class_level: Student's class (1-3)
            concept_tags: Related concept tags
            attempt_number: 1 for first wrong, 2+ for subsequent
        
        Returns:
            Dict with encouragement, explanation, example, tip
        """
        
        # Adjust tone based on attempt number
        tone = "gentle and encouraging" if attempt_number == 1 else "simpler and more detailed"
        age = class_level + 4  # Class 1 = age 5-6
        
        prompt = f"""
You are a friendly, patient AI teacher for Class {class_level} students (age {age} years old).

QUESTION: {question}
STUDENT'S ANSWER: {student_answer}
CORRECT ANSWER: {correct_answer}
CONCEPTS: {', '.join(concept_tags)}
ATTEMPT: {attempt_number}

Generate a {tone} explanation that:
1. ENCOURAGES the student (never criticize, always positive)
2. Explains WHY the correct answer is right in VERY SIMPLE terms
3. Uses emojis, fun examples, and relatable scenarios
4. Keeps it SHORT (2-3 sentences per section)
5. Age-appropriate language for {age} year olds

Return ONLY a valid JSON object (no markdown, no code blocks, no extra text):
{{
  "encouragement": "Warm, positive message with emoji (1 sentence)",
  "explanation": "Why correct answer is right in simple terms (2 sentences max)",
  "example": "Real-world example with emojis (1 sentence)",
  "tip": "Memory trick or helpful tip (1 sentence)"
}}
"""
        
        try:
            response = self.model.generate_content(
                prompt,
                generation_config=self.generation_config,
                safety_settings=self.safety_settings
            )
            
            # Parse response
            explanation = self._parse_json_response(response.text)
            
            # Validate required fields
            required_fields = ['encouragement', 'explanation', 'example', 'tip']
            if not all(field in explanation for field in required_fields):
                logger.warning("Missing fields in AI response, using fallback")
                return self._get_fallback_explanation(class_level)
            
            logger.info(f"Generated explanation for question: {question[:50]}...")
            return explanation
            
        except Exception as e:
            logger.error(f"Error generating explanation: {str(e)}")
            # Return fallback explanation
            return self._get_fallback_explanation(class_level)
    
    async def generate_similar_question(
        self,
        original_question: str,
        correct_answer: str,
        concept_tags: List[str],
        difficulty: str,
        class_level: int
    ) -> Dict:
        """
        Generate similar question at specified difficulty
        
        Args:
            original_question: Original question text
            correct_answer: Correct answer from original
            concept_tags: Concepts being tested
            difficulty: 'easy', 'medium', or 'hard'
            class_level: Student's class
        
        Returns:
            Complete question object with options
        """
        
        difficulty_guidelines = {
            'easy': "Very simple, direct question. Almost obvious answer. Use clear visual cues. Numbers should be small (1-5).",
            'medium': "Moderate difficulty. Requires basic understanding. One step reasoning. Numbers can be 1-10.",
            'hard': "Challenging. Requires deeper understanding. Multi-step or less obvious. Numbers can be larger."
        }
        
        age = class_level + 4
        
        prompt = f"""
You are creating a quiz question for Class {class_level} students (age {age}).

ORIGINAL QUESTION: {original_question}
CORRECT ANSWER: {correct_answer}
CONCEPTS TO TEST: {', '.join(concept_tags)}
DIFFICULTY: {difficulty}

Create a NEW question that:
1. Tests the SAME concept as the original
2. Uses DIFFERENT wording, numbers, or examples
3. Is {difficulty_guidelines[difficulty]}
4. Appropriate for Class {class_level} (age {age})
5. Includes helpful emojis in question and options

Return ONLY a valid JSON object (no markdown, no code blocks, no extra text):
{{
  "question": "The question text with emoji",
  "options": [
    {{"text": "Option 1", "emoji": "🔵", "correct": false}},
    {{"text": "Option 2", "emoji": "🟢", "correct": true}},
    {{"text": "Option 3", "emoji": "🔴", "correct": false}},
    {{"text": "Option 4", "emoji": "🟡", "correct": false}}
  ],
  "explanation": "Brief explanation of why correct answer is right (1-2 sentences)",
  "conceptTags": {json.dumps(concept_tags)},
  "difficulty": "{difficulty}"
}}

IMPORTANT RULES:
- Shuffle the options so correct answer is NOT always second
- Make wrong options plausible but clearly incorrect
- Use age-appropriate vocabulary for {age} year olds
- Keep it simple and fun with emojis
"""
        
        try:
            response = self.model.generate_content(
                prompt,
                generation_config=self.generation_config,
                safety_settings=self.safety_settings
            )
            
            question_data = self._parse_json_response(response.text)
            
            # Validate structure
            if not self._validate_question_structure(question_data):
                logger.warning("Invalid question structure, using fallback")
                return self._get_fallback_question(concept_tags, difficulty, class_level)
            
            logger.info(f"Generated {difficulty} question for concept: {concept_tags}")
            return question_data
            
        except Exception as e:
            logger.error(f"Error generating question: {str(e)}")
            # Return fallback question
            return self._get_fallback_question(concept_tags, difficulty, class_level)
    
    def _parse_json_response(self, text: str) -> Dict:
        """Clean and parse JSON from Gemini response"""
        # Remove markdown code blocks if present
        text = text.strip()
        if text.startswith('```'):
            lines = text.split('\n')
            # Remove first and last lines (``` markers)
            text = '\n'.join(lines[1:-1])
            if text.startswith('json'):
                text = text[4:].strip()
        
        # Try to extract JSON if there's extra text
        if '{' in text and '}' in text:
            start = text.index('{')
            end = text.rindex('}') + 1
            text = text[start:end]
        
        try:
            return json.loads(text)
        except json.JSONDecodeError as e:
            logger.error(f"JSON parse error: {str(e)}\nText: {text[:200]}")
            raise
    
    def _validate_question_structure(self, question: Dict) -> bool:
        """Validate generated question has correct structure"""
        required_fields = ['question', 'options', 'explanation']
        if not all(field in question for field in required_fields):
            logger.error(f"Missing required fields. Got: {question.keys()}")
            return False
        
        # Check options
        if not isinstance(question['options'], list) or len(question['options']) != 4:
            logger.error(f"Invalid options length: {len(question.get('options', []))}")
            return False
        
        # Check exactly one correct answer
        correct_count = sum(1 for opt in question['options'] if opt.get('correct'))
        if correct_count != 1:
            logger.error(f"Invalid correct answer count: {correct_count}")
            return False
        
        return True
    
    def _get_fallback_explanation(self, class_level: int) -> Dict:
        """Fallback explanation if AI fails"""
        return {
            "encouragement": "Good try! Let's learn together! 🦉",
            "explanation": "Think carefully about the question and look at each option. Take your time!",
            "example": "Remember, practice makes perfect! You can do it! 💪",
            "tip": "Read the question twice before answering!"
        }
    
    def _get_fallback_question(
        self,
        concept_tags: List[str],
        difficulty: str,
        class_level: int
    ) -> Dict:
        """Fallback question if AI fails"""
        concept_name = concept_tags[0] if concept_tags else "this topic"
        
        return {
            "question": f"Let's practice {concept_name}! 📚",
            "options": [
                {"text": "Option A", "emoji": "①", "correct": True},
                {"text": "Option B", "emoji": "②", "correct": False},
                {"text": "Option C", "emoji": "③", "correct": False},
                {"text": "Option D", "emoji": "④", "correct": False}
            ],
            "explanation": "This is a practice question to help you learn!",
            "conceptTags": concept_tags,
            "difficulty": difficulty
        }


# Create singleton instance
gemini_service = GeminiService()
