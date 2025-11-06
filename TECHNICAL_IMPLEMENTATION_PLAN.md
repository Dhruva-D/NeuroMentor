# Technical Implementation Plan: Adaptive Learning System
## Using Reinforcement Learning Concepts (Not Full RL)

---

## 🧠 **CLARIFICATION: Is This True Reinforcement Learning?**

### **Short Answer: No, it's Adaptive Learning inspired by RL concepts**

### **What We're Actually Building:**

We're building an **Adaptive Learning System** that uses:
- ✅ **Reward-based progression** (RL concept)
- ✅ **State-based decision making** (RL concept)
- ✅ **Policy-based actions** (RL concept)
- ❌ NOT a full RL model with Q-learning, neural networks, etc.

### **Why Not Full Reinforcement Learning?**

Traditional RL (like Q-Learning, Deep Q-Networks) would require:
- Training on thousands of students over months
- Complex state-action-reward matrices
- Neural network models
- Extensive computational resources
- Long training periods

**Our Approach is Better Because:**
1. ✅ Works immediately (no training needed)
2. ✅ Uses AI (Gemini) for intelligent responses
3. ✅ Rule-based + AI hybrid (best of both worlds)
4. ✅ Lower complexity, easier to maintain
5. ✅ Predictable behavior for students

---

## 🎯 **OUR TECHNICAL APPROACH: Rule-Based Adaptive Learning + AI**

### **Architecture Overview:**

```
┌─────────────────────────────────────────────────────────────┐
│                    ADAPTIVE LEARNING ENGINE                  │
├─────────────────────────────────────────────────────────────┤
│                                                               │
│  ┌──────────────┐      ┌──────────────┐     ┌─────────────┐│
│  │   Student    │      │   Question   │     │   Gemini    ││
│  │   State      │──────│   Selector   │─────│     AI      ││
│  │   Tracker    │      │   Engine     │     │   Service   ││
│  └──────────────┘      └──────────────┘     └─────────────┘│
│         │                      │                    │        │
│         │                      │                    │        │
│         ▼                      ▼                    ▼        │
│  ┌──────────────┐      ┌──────────────┐     ┌─────────────┐│
│  │  Performance │      │  Difficulty  │     │  Explanation││
│  │   Analyzer   │      │  Adapter     │     │  Generator  ││
│  └──────────────┘      └──────────────┘     └─────────────┘│
│         │                      │                    │        │
│         └──────────────────────┴────────────────────┘        │
│                                │                              │
│                                ▼                              │
│                         ┌─────────────┐                       │
│                         │   Action    │                       │
│                         │  Decision   │                       │
│                         └─────────────┘                       │
└─────────────────────────────────────────────────────────────┘
```

### **Components Breakdown:**

#### **1. Student State Tracker**
```typescript
interface StudentState {
  currentQuestionId: number;
  consecutiveCorrect: number;
  consecutiveWrong: number;
  currentDifficulty: 'easy' | 'medium' | 'hard';
  conceptMastery: Map<string, MasteryLevel>;
  recentPerformance: boolean[]; // Last 5 questions
  needsHelp: boolean;
  helpRequestCount: number;
}

enum MasteryLevel {
  NOT_ATTEMPTED = 0,
  STRUGGLING = 1,    // Failed original + easy
  LEARNING = 2,       // Passed easy, failed medium
  COMPETENT = 3,      // Passed medium, failed hard
  MASTERED = 4        // Passed hard
}
```

#### **2. Rule-Based Decision Engine**
```typescript
class AdaptiveLearningEngine {
  // Decision tree based on student state
  async decideNextAction(state: StudentState, answer: Answer): Promise<Action> {
    if (answer.isCorrect) {
      return this.handleCorrectAnswer(state);
    } else {
      return this.handleWrongAnswer(state);
    }
  }
  
  private handleCorrectAnswer(state: StudentState): Action {
    state.consecutiveCorrect++;
    state.consecutiveWrong = 0;
    
    // Rule 1: In adaptive mode, progress difficulty
    if (state.isInAdaptiveMode) {
      if (state.currentDifficulty === 'easy') {
        return { type: 'GENERATE_MEDIUM', reward: 15 };
      } else if (state.currentDifficulty === 'medium') {
        return { type: 'GENERATE_HARD', reward: 25 };
      } else if (state.currentDifficulty === 'hard') {
        return { type: 'CONCEPT_MASTERED', reward: 50 };
      }
    }
    
    // Rule 2: Normal mode progression
    return { type: 'NEXT_QUESTION', reward: 10 };
  }
  
  private async handleWrongAnswer(state: StudentState): Promise<Action> {
    state.consecutiveWrong++;
    state.consecutiveCorrect = 0;
    
    // Rule 1: First wrong attempt
    if (state.consecutiveWrong === 1 && !state.isInAdaptiveMode) {
      const explanation = await this.geminiService.getExplanation(...);
      return {
        type: 'SHOW_EXPLANATION_AND_OFFER_PRACTICE',
        explanation,
        penalty: -5
      };
    }
    
    // Rule 2: In adaptive mode, failed easy/medium
    if (state.isInAdaptiveMode) {
      if (state.currentDifficulty === 'easy' && state.consecutiveWrong === 1) {
        const explanation = await this.geminiService.getExplanation(...);
        return {
          type: 'EXPLAIN_AND_RETRY_EASIER',
          explanation,
          penalty: -3
        };
      } else {
        // Failed twice, mark for review and move on
        return {
          type: 'MARK_FOR_REVIEW_AND_CONTINUE',
          penalty: -10
        };
      }
    }
    
    // Rule 3: Multiple failures, offer hint
    if (state.consecutiveWrong >= 2) {
      return {
        type: 'OFFER_HINT',
        penalty: -5
      };
    }
  }
}
```

#### **3. Difficulty Adaptation Algorithm**
```typescript
class DifficultyAdapter {
  calculateNextDifficulty(state: StudentState): Difficulty {
    const recentAccuracy = this.calculateAccuracy(state.recentPerformance);
    
    // Algorithm based on sliding window performance
    if (recentAccuracy >= 0.9) {
      // Student is doing great, challenge them
      return this.increaseDifficulty(state.currentDifficulty);
    } else if (recentAccuracy >= 0.6) {
      // Steady progress, maintain level
      return state.currentDifficulty;
    } else {
      // Struggling, make it easier
      return this.decreaseDifficulty(state.currentDifficulty);
    }
  }
  
  private calculateAccuracy(recent: boolean[]): number {
    const correct = recent.filter(x => x).length;
    return correct / recent.length;
  }
}
```

---

## 📋 **PHASE-WISE IMPLEMENTATION PLAN**

---

## **PHASE 1: Foundation Setup (Week 1)**

### **Day 1-2: Environment & Dependencies**

#### Backend Setup
```bash
# Terminal 1: Backend setup
cd server

# Install Gemini AI
pip install google-generativeai

# Install additional dependencies
pip install python-dotenv pydantic

# Update requirements.txt
pip freeze > requirements.txt
```

#### Environment Configuration
```bash
# Create .env file
touch .env

# Add API keys
GEMINI_API_KEY=your_gemini_api_key_here
DATABASE_URL=postgresql://user:pass@localhost/neuromentor
```

#### Database Migration
```sql
-- Create migration file: migrations/001_adaptive_learning.sql

-- Student state tracking
CREATE TABLE student_learning_state (
    id SERIAL PRIMARY KEY,
    student_id INTEGER REFERENCES users(id),
    session_id VARCHAR(100),
    question_id INTEGER,
    chapter_id VARCHAR(100),
    quiz_set_id VARCHAR(100),
    
    -- State variables
    consecutive_correct INTEGER DEFAULT 0,
    consecutive_wrong INTEGER DEFAULT 0,
    current_difficulty VARCHAR(20) DEFAULT 'easy',
    is_in_adaptive_mode BOOLEAN DEFAULT FALSE,
    
    -- Performance tracking
    recent_performance JSONB,  -- Array of last 5 attempts
    concept_mastery JSONB,     -- Map of concept -> mastery level
    
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW()
);

-- Question attempts log
CREATE TABLE question_attempts (
    id SERIAL PRIMARY KEY,
    student_id INTEGER REFERENCES users(id),
    question_id INTEGER,
    question_type VARCHAR(20), -- 'original', 'generated_easy', 'generated_medium', 'generated_hard'
    
    selected_answer INTEGER,
    is_correct BOOLEAN,
    time_spent INTEGER, -- seconds
    hints_used INTEGER DEFAULT 0,
    
    -- AI interaction
    ai_explanation_shown BOOLEAN DEFAULT FALSE,
    ai_explanation TEXT,
    
    created_at TIMESTAMP DEFAULT NOW()
);

-- AI-generated questions cache
CREATE TABLE generated_questions_cache (
    id SERIAL PRIMARY KEY,
    original_question_id INTEGER,
    difficulty VARCHAR(20),
    class_level INTEGER,
    
    question_data JSONB,  -- Complete question object
    generated_by VARCHAR(50) DEFAULT 'gemini',
    usage_count INTEGER DEFAULT 0,
    
    created_at TIMESTAMP DEFAULT NOW(),
    
    INDEX idx_cache_lookup (original_question_id, difficulty, class_level)
);

-- Concept mastery tracking
CREATE TABLE concept_mastery (
    id SERIAL PRIMARY KEY,
    student_id INTEGER REFERENCES users(id),
    concept_tag VARCHAR(100),
    
    mastery_level INTEGER DEFAULT 0, -- 0-4 scale
    total_attempts INTEGER DEFAULT 0,
    successful_attempts INTEGER DEFAULT 0,
    
    last_practiced TIMESTAMP,
    next_review_date TIMESTAMP,
    
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW(),
    
    UNIQUE(student_id, concept_tag)
);
```

**Tasks:**
- [ ] Set up Gemini API account
- [ ] Install dependencies
- [ ] Create environment file
- [ ] Run database migrations
- [ ] Test database connection

---

### **Day 3-4: Backend Core Services**

#### File Structure
```
server/
├── services/
│   ├── __init__.py
│   ├── gemini_service.py       # NEW
│   ├── adaptive_engine.py      # NEW
│   └── difficulty_adapter.py   # NEW
├── models/
│   ├── learning_state.py       # NEW
│   └── question_attempt.py     # NEW
├── routes/
│   └── learning.py             # NEW
└── utils/
    └── state_manager.py        # NEW
```

#### Gemini Service Implementation
```python
# server/services/gemini_service.py

import google.generativeai as genai
import os
import json
from typing import Dict, List, Optional
import logging

logger = logging.getLogger(__name__)

class GeminiService:
    def __init__(self):
        api_key = os.getenv("GEMINI_API_KEY")
        if not api_key:
            raise ValueError("GEMINI_API_KEY not found in environment")
        
        genai.configure(api_key=api_key)
        self.model = genai.GenerativeModel('gemini-pro')
        
        # Configure safety settings
        self.safety_settings = {
            'HARASSMENT': 'BLOCK_NONE',
            'HATE_SPEECH': 'BLOCK_NONE',
            'SEXUALLY_EXPLICIT': 'BLOCK_NONE',
            'DANGEROUS_CONTENT': 'BLOCK_NONE',
        }
    
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
            correct_answer: The correct answer
            student_answer: What the student selected
            class_level: Student's class (1-3)
            concept_tags: Related concept tags
            attempt_number: 1 for first wrong, 2+ for subsequent
        
        Returns:
            Dict with encouragement, explanation, example, tip
        """
        
        # Adjust tone based on attempt number
        tone = "gentle and encouraging" if attempt_number == 1 else "simpler and more detailed"
        
        prompt = f"""
You are a friendly, patient AI teacher for Class {class_level} students (age {class_level + 4} years old).

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
5. Age-appropriate language for {class_level + 4} year olds

Return ONLY a JSON object (no markdown, no code blocks):
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
                safety_settings=self.safety_settings
            )
            
            # Parse response
            explanation = self._parse_json_response(response.text)
            
            # Validate required fields
            required_fields = ['encouragement', 'explanation', 'example', 'tip']
            if not all(field in explanation for field in required_fields):
                raise ValueError("Missing required fields in response")
            
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
            'easy': "Very simple, direct question. Almost obvious answer. Use clear visual cues.",
            'medium': "Moderate difficulty. Requires basic understanding. One step reasoning.",
            'hard': "Challenging. Requires deeper understanding. Multi-step or less obvious."
        }
        
        prompt = f"""
You are creating a quiz question for Class {class_level} students.

ORIGINAL QUESTION: {original_question}
CORRECT ANSWER: {correct_answer}
CONCEPTS TO TEST: {', '.join(concept_tags)}
DIFFICULTY: {difficulty}

Create a NEW question that:
1. Tests the SAME concept as the original
2. Uses DIFFERENT wording, numbers, or examples
3. Is {difficulty_guidelines[difficulty]}
4. Appropriate for Class {class_level} (age {class_level + 4})
5. Includes helpful emojis

Return ONLY a JSON object (no markdown, no code blocks):
{{
  "question": "The question text with emoji",
  "options": [
    {{"text": "Option 1", "emoji": "relevant emoji", "correct": false}},
    {{"text": "Option 2", "emoji": "relevant emoji", "correct": true}},
    {{"text": "Option 3", "emoji": "relevant emoji", "correct": false}},
    {{"text": "Option 4", "emoji": "relevant emoji", "correct": false}}
  ],
  "explanation": "Brief explanation of why correct answer is right",
  "conceptTags": {json.dumps(concept_tags)},
  "difficulty": "{difficulty}"
}}

IMPORTANT: 
- Shuffle the options so correct answer is NOT always second
- Make wrong options plausible but clearly incorrect
- Use age-appropriate vocabulary
"""
        
        try:
            response = self.model.generate_content(
                prompt,
                safety_settings=self.safety_settings
            )
            
            question_data = self._parse_json_response(response.text)
            
            # Validate structure
            if not self._validate_question_structure(question_data):
                raise ValueError("Invalid question structure")
            
            logger.info(f"Generated {difficulty} question for concept: {concept_tags}")
            return question_data
            
        except Exception as e:
            logger.error(f"Error generating question: {str(e)}")
            # Return fallback question
            return self._get_fallback_question(concept_tags, difficulty, class_level)
    
    def _parse_json_response(self, text: str) -> Dict:
        """Clean and parse JSON from Gemini response"""
        # Remove markdown code blocks
        text = text.strip()
        if text.startswith('```'):
            text = text.split('```')[1]
            if text.startswith('json'):
                text = text[4:]
        text = text.strip()
        
        try:
            return json.loads(text)
        except json.JSONDecodeError as e:
            logger.error(f"JSON parse error: {str(e)}\nText: {text}")
            raise
    
    def _validate_question_structure(self, question: Dict) -> bool:
        """Validate generated question has correct structure"""
        required_fields = ['question', 'options', 'explanation']
        if not all(field in question for field in required_fields):
            return False
        
        # Check options
        if len(question['options']) != 4:
            return False
        
        # Check exactly one correct answer
        correct_count = sum(1 for opt in question['options'] if opt.get('correct'))
        if correct_count != 1:
            return False
        
        return True
    
    def _get_fallback_explanation(self, class_level: int) -> Dict:
        """Fallback explanation if AI fails"""
        return {
            "encouragement": "Good try! Let's learn together! 🦉",
            "explanation": "Think carefully about the question and look at each option.",
            "example": "Take your time and you'll get it! 💪",
            "tip": "Read the question twice before answering!"
        }
    
    def _get_fallback_question(
        self,
        concept_tags: List[str],
        difficulty: str,
        class_level: int
    ) -> Dict:
        """Fallback question if AI fails"""
        return {
            "question": f"Let's practice {concept_tags[0]}! 📚",
            "options": [
                {"text": "Option A", "emoji": "①", "correct": True},
                {"text": "Option B", "emoji": "②", "correct": False},
                {"text": "Option C", "emoji": "③", "correct": False},
                {"text": "Option D", "emoji": "④", "correct": False}
            ],
            "explanation": "This is a practice question!",
            "conceptTags": concept_tags,
            "difficulty": difficulty
        }
```

**Tasks for Day 3-4:**
- [ ] Implement GeminiService class
- [ ] Add error handling and retries
- [ ] Add logging
- [ ] Test with sample questions
- [ ] Implement caching logic

---

### **Day 5-7: Adaptive Engine**

```python
# server/services/adaptive_engine.py

from typing import Dict, List, Optional
from enum import Enum
import logging

logger = logging.getLogger(__name__)

class ActionType(Enum):
    NEXT_QUESTION = "next_question"
    SHOW_EXPLANATION = "show_explanation"
    GENERATE_PRACTICE = "generate_practice"
    GENERATE_MEDIUM = "generate_medium"
    GENERATE_HARD = "generate_hard"
    CONCEPT_MASTERED = "concept_mastered"
    MARK_FOR_REVIEW = "mark_for_review"
    OFFER_HINT = "offer_hint"

class MasteryLevel(Enum):
    NOT_ATTEMPTED = 0
    STRUGGLING = 1
    LEARNING = 2
    COMPETENT = 3
    MASTERED = 4

class AdaptiveEngine:
    def __init__(self, gemini_service, db_session):
        self.gemini = gemini_service
        self.db = db_session
    
    async def process_answer(
        self,
        student_id: int,
        question_id: int,
        selected_answer: int,
        is_correct: bool,
        state: Dict
    ) -> Dict:
        """
        Main decision engine - decides what happens next
        
        Returns:
            {
                'action': ActionType,
                'data': {...},
                'reward': int,
                'next_state': {...}
            }
        """
        
        if is_correct:
            return await self._handle_correct(student_id, question_id, state)
        else:
            return await self._handle_wrong(student_id, question_id, selected_answer, state)
    
    async def _handle_correct(
        self,
        student_id: int,
        question_id: int,
        state: Dict
    ) -> Dict:
        """Handle correct answer logic"""
        
        # Update state
        state['consecutiveCorrect'] = state.get('consecutiveCorrect', 0) + 1
        state['consecutiveWrong'] = 0
        
        # Check if in adaptive mode
        if state.get('isInAdaptiveMode'):
            current_diff = state.get('currentDifficulty', 'easy')
            
            if current_diff == 'easy':
                return {
                    'action': ActionType.GENERATE_MEDIUM,
                    'data': {'message': 'Great! Let\'s try something harder! 💪'},
                    'reward': 15,
                    'next_state': {**state, 'currentDifficulty': 'medium'}
                }
            
            elif current_diff == 'medium':
                return {
                    'action': ActionType.GENERATE_HARD,
                    'data': {'message': 'Wow! You\'re doing amazing! 🌟'},
                    'reward': 25,
                    'next_state': {**state, 'currentDifficulty': 'hard'}
                }
            
            elif current_diff == 'hard':
                # MASTERED!
                await self._update_mastery(student_id, state.get('conceptTags', []), MasteryLevel.MASTERED)
                return {
                    'action': ActionType.CONCEPT_MASTERED,
                    'data': {
                        'message': '🎉 CONCEPT MASTERED! 🏆',
                        'badge': 'Concept Master',
                        'celebration': True
                    },
                    'reward': 50,
                    'next_state': {**state, 'isInAdaptiveMode': False}
                }
        
        # Normal mode - just move to next
        return {
            'action': ActionType.NEXT_QUESTION,
            'data': {'message': 'Correct! 🎯'},
            'reward': 10,
            'next_state': state
        }
    
    async def _handle_wrong(
        self,
        student_id: int,
        question_id: int,
        selected_answer: int,
        state: Dict
    ) -> Dict:
        """Handle wrong answer logic"""
        
        # Update state
        state['consecutiveWrong'] = state.get('consecutiveWrong', 0) + 1
        state['consecutiveCorrect'] = 0
        
        question_data = state.get('currentQuestion', {})
        
        # First wrong attempt in normal mode
        if state['consecutiveWrong'] == 1 and not state.get('isInAdaptiveMode'):
            # Generate explanation
            explanation = await self.gemini.generate_explanation(
                question=question_data.get('question', ''),
                correct_answer=self._get_correct_answer_text(question_data),
                student_answer=question_data['options'][selected_answer]['text'],
                class_level=state.get('classLevel', 1),
                concept_tags=question_data.get('conceptTags', []),
                attempt_number=1
            )
            
            return {
                'action': ActionType.SHOW_EXPLANATION,
                'data': {
                    'explanation': explanation,
                    'offerPractice': True
                },
                'reward': -5,
                'next_state': state
            }
        
        # In adaptive mode - struggling
        if state.get('isInAdaptiveMode'):
            if state['consecutiveWrong'] == 1:
                # First failure in adaptive mode - try explaining again
                explanation = await self.gemini.generate_explanation(
                    question=question_data.get('question', ''),
                    correct_answer=self._get_correct_answer_text(question_data),
                    student_answer=question_data['options'][selected_answer]['text'],
                    class_level=state.get('classLevel', 1),
                    concept_tags=question_data.get('conceptTags', []),
                    attempt_number=2  # Simpler explanation
                )
                
                return {
                    'action': ActionType.SHOW_EXPLANATION,
                    'data': {
                        'explanation': explanation,
                        'offerPractice': False  # Don't offer practice again
                    },
                    'reward': -3,
                    'next_state': state
                }
            else:
                # Failed twice - mark for review and move on
                await self._mark_for_review(student_id, question_data.get('conceptTags', []))
                
                return {
                    'action': ActionType.MARK_FOR_REVIEW,
                    'data': {
                        'message': 'We\'ll practice this more later! 📝',
                        'moveToNext': True
                    },
                    'reward': -10,
                    'next_state': {**state, 'isInAdaptiveMode': False}
                }
        
        # Multiple failures - something went wrong
        return {
            'action': ActionType.OFFER_HINT,
            'data': {'message': 'Need a hint? 💡'},
            'reward': -5,
            'next_state': state
        }
    
    def _get_correct_answer_text(self, question_data: Dict) -> str:
        """Extract correct answer text from question"""
        for option in question_data.get('options', []):
            if option.get('correct'):
                return option.get('text', '')
        return ''
    
    async def _update_mastery(
        self,
        student_id: int,
        concept_tags: List[str],
        level: MasteryLevel
    ):
        """Update concept mastery in database"""
        for concept in concept_tags:
            # Update or insert mastery record
            await self.db.execute(
                """
                INSERT INTO concept_mastery (student_id, concept_tag, mastery_level)
                VALUES ($1, $2, $3)
                ON CONFLICT (student_id, concept_tag)
                DO UPDATE SET mastery_level = $3, updated_at = NOW()
                """,
                student_id, concept, level.value
            )
    
    async def _mark_for_review(
        self,
        student_id: int,
        concept_tags: List[str]
    ):
        """Mark concepts for future review"""
        for concept in concept_tags:
            await self.db.execute(
                """
                UPDATE concept_mastery
                SET next_review_date = NOW() + INTERVAL '1 day'
                WHERE student_id = $1 AND concept_tag = $2
                """,
                student_id, concept
            )
```

**Tasks for Day 5-7:**
- [ ] Implement AdaptiveEngine class
- [ ] Create state management logic
- [ ] Add mastery tracking
- [ ] Test decision tree
- [ ] Write unit tests

---

## **PHASE 2: Frontend Integration (Week 2)**

### **Day 1-2: API Service Layer**

```typescript
// client/src/services/api/learningApi.ts

import axios from 'axios';

const API_URL = import.meta.env.VITE_API_URL || 'http://localhost:8000';

export interface ProcessAnswerRequest {
  studentId: number;
  questionId: number;
  selectedAnswer: number;
  isCorrect: boolean;
  currentState: any;
}

export interface ProcessAnswerResponse {
  action: string;
  data: any;
  reward: number;
  nextState: any;
}

export const learningApi = {
  async processAnswer(request: ProcessAnswerRequest): Promise<ProcessAnswerResponse> {
    const response = await axios.post(`${API_URL}/api/learning/process-answer`, request);
    return response.data;
  },
  
  async generatePracticeQuestion(
    questionId: number,
    difficulty: 'easy' | 'medium' | 'hard',
    classLevel: number
  ) {
    const response = await axios.post(`${API_URL}/api/learning/generate-question`, {
      question_id: questionId,
      difficulty,
      class_level: classLevel
    });
    return response.data;
  }
};
```

### **Day 3-7: State Management & UI**

Using React Context + Hooks:

```typescript
// client/src/contexts/AdaptiveLearningContext.tsx

import { createContext, useContext, useState, ReactNode } from 'react';

interface AdaptiveLearningState {
  isInAdaptiveMode: boolean;
  currentDifficulty: 'easy' | 'medium' | 'hard';
  consecutiveCorrect: number;
  consecutiveWrong: number;
  conceptTags: string[];
  // ... other state
}

const AdaptiveLearningContext = createContext<any>(null);

export const useAdaptiveLearning = () => {
  const context = useContext(AdaptiveLearningContext);
  if (!context) throw new Error('Must be used within provider');
  return context;
};

export const AdaptiveLearningProvider = ({ children }: { children: ReactNode }) => {
  const [state, setState] = useState<AdaptiveLearningState>({
    isInAdaptiveMode: false,
    currentDifficulty: 'easy',
    consecutiveCorrect: 0,
    consecutiveWrong: 0,
    conceptTags: []
  });
  
  const processAnswer = async (questionId: number, selectedAnswer: number, isCorrect: boolean) => {
    const response = await learningApi.processAnswer({
      studentId: student.id,
      questionId,
      selectedAnswer,
      isCorrect,
      currentState: state
    });
    
    // Handle different actions
    switch (response.action) {
      case 'SHOW_EXPLANATION':
        // Show explanation modal
        break;
      case 'GENERATE_MEDIUM':
        // Generate and show medium question
        break;
      // ... handle all action types
    }
    
    setState(response.nextState);
    return response;
  };
  
  return (
    <AdaptiveLearningContext.Provider value={{ state, processAnswer }}>
      {children}
    </AdaptiveLearningContext.Provider>
  );
};
```

---

## **PHASE 3-5: See continuation in implementation...**

**Tasks:**
- [ ] Complete frontend state management
- [ ] Build UI components
- [ ] Integrate with backend
- [ ] Test end-to-end
- [ ] Deploy and monitor

---

## ✅ **SUMMARY: Technical Approach**

1. **Rule-Based Decision Engine** (not full RL)
2. **AI-Powered Content Generation** (Gemini for explanations/questions)
3. **State Management** (Track student progress and mastery)
4. **Adaptive Difficulty** (Algorithm-based, not ML-based)
5. **Hybrid System** (Rules + AI = Best results)

**This is MORE practical and effective than full RL for educational use cases!**

Would you like me to continue with the detailed implementation of any specific phase?
