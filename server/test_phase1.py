"""
Test script for Phase 1 implementation
Tests Gemini API integration and adaptive engine
"""

import asyncio
import sys
import os

# Add parent directory to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from services.gemini_service import gemini_service
from services.adaptive_engine import AdaptiveEngine


async def test_gemini_explanation():
    """Test explanation generation"""
    print("\n" + "="*60)
    print("TEST 1: Generating AI Explanation")
    print("="*60)
    
    try:
        explanation = await gemini_service.generate_explanation(
            question="What shape is a ball? ⚽",
            correct_answer="Circle",
            student_answer="Square",
            class_level=1,
            concept_tags=["shapes", "geometry"],
            attempt_number=1
        )
        
        print("\n✅ Explanation generated successfully!")
        print(f"\n📝 Encouragement: {explanation['encouragement']}")
        print(f"📚 Explanation: {explanation['explanation']}")
        print(f"🌟 Example: {explanation['example']}")
        print(f"💡 Tip: {explanation['tip']}")
        
        return True
        
    except Exception as e:
        print(f"\n❌ Error: {e}")
        return False


async def test_gemini_question_generation():
    """Test question generation"""
    print("\n" + "="*60)
    print("TEST 2: Generating Similar Question")
    print("="*60)
    
    try:
        question = await gemini_service.generate_similar_question(
            original_question="How many corners does a triangle have? 🔺",
            correct_answer="3 corners",
            concept_tags=["shapes", "counting"],
            difficulty="easy",
            class_level=1
        )
        
        print("\n✅ Question generated successfully!")
        print(f"\n❓ Question: {question['question']}")
        print(f"📊 Difficulty: {question['difficulty']}")
        print("\n📝 Options:")
        for i, opt in enumerate(question['options'], 1):
            mark = "✓" if opt['correct'] else " "
            print(f"   [{mark}] {i}. {opt.get('emoji', '')} {opt['text']}")
        print(f"\n💬 Explanation: {question['explanation']}")
        
        return True
        
    except Exception as e:
        print(f"\n❌ Error: {e}")
        return False


async def test_adaptive_engine():
    """Test adaptive engine decision making"""
    print("\n" + "="*60)
    print("TEST 3: Testing Adaptive Engine")
    print("="*60)
    
    try:
        engine = AdaptiveEngine(gemini_service)
        
        # Test scenario: Student gets answer wrong
        question_data = {
            'id': 1,
            'question': 'What color is the sky? 🌤️',
            'options': [
                {'text': 'Blue', 'correct': True},
                {'text': 'Green', 'correct': False},
                {'text': 'Red', 'correct': False},
                {'text': 'Yellow', 'correct': False}
            ],
            'conceptTags': ['colors', 'nature']
        }
        
        state = {
            'classLevel': 1,
            'consecutiveCorrect': 0,
            'consecutiveWrong': 0,
            'isInAdaptiveMode': False,
            'recentPerformance': []
        }
        
        print("\n📋 Scenario: Student selects WRONG answer (Green)")
        
        result = await engine.process_answer(
            student_id=1,
            question_id=1,
            selected_answer=1,  # Green (wrong)
            is_correct=False,
            state=state,
            question_data=question_data
        )
        
        print(f"\n✅ Engine decision: {result['action']}")
        print(f"💬 Message: {result['data'].get('message', 'N/A')}")
        print(f"🏆 Reward: {result['reward']}")
        
        if 'explanation' in result['data']:
            exp = result['data']['explanation']
            print(f"\n📝 AI Explanation provided:")
            print(f"   Encouragement: {exp.get('encouragement', 'N/A')}")
        
        return True
        
    except Exception as e:
        print(f"\n❌ Error: {e}")
        import traceback
        traceback.print_exc()
        return False


async def test_adaptive_progression():
    """Test adaptive difficulty progression"""
    print("\n" + "="*60)
    print("TEST 4: Testing Difficulty Progression (Easy → Medium → Hard)")
    print("="*60)
    
    try:
        engine = AdaptiveEngine(gemini_service)
        
        question_data = {
            'id': 2,
            'question': 'Generated easy question',
            'options': [
                {'text': 'Correct', 'correct': True},
                {'text': 'Wrong 1', 'correct': False},
                {'text': 'Wrong 2', 'correct': False},
                {'text': 'Wrong 3', 'correct': False}
            ],
            'conceptTags': ['addition']
        }
        
        # Test Easy → Medium progression
        state_easy = {
            'classLevel': 1,
            'isInAdaptiveMode': True,
            'currentDifficulty': 'easy',
            'consecutiveCorrect': 0,
            'consecutiveWrong': 0,
            'recentPerformance': []
        }
        
        print("\n📊 Testing: Easy question answered CORRECTLY")
        result_easy = await engine.process_answer(
            student_id=1,
            question_id=2,
            selected_answer=0,  # Correct
            is_correct=True,
            state=state_easy,
            question_data=question_data
        )
        
        print(f"✅ Action: {result_easy['action']}")
        print(f"💬 Message: {result_easy['data'].get('message', 'N/A')}")
        print(f"📈 Next Difficulty: {result_easy['nextState'].get('currentDifficulty', 'N/A')}")
        
        # Test Medium → Hard progression
        state_medium = {
            'classLevel': 1,
            'isInAdaptiveMode': True,
            'currentDifficulty': 'medium',
            'consecutiveCorrect': 1,
            'consecutiveWrong': 0,
            'recentPerformance': [True]
        }
        
        print("\n📊 Testing: Medium question answered CORRECTLY")
        result_medium = await engine.process_answer(
            student_id=1,
            question_id=3,
            selected_answer=0,  # Correct
            is_correct=True,
            state=state_medium,
            question_data=question_data
        )
        
        print(f"✅ Action: {result_medium['action']}")
        print(f"💬 Message: {result_medium['data'].get('message', 'N/A')}")
        print(f"📈 Next Difficulty: {result_medium['nextState'].get('currentDifficulty', 'N/A')}")
        
        # Test Hard → MASTERED
        state_hard = {
            'classLevel': 1,
            'isInAdaptiveMode': True,
            'currentDifficulty': 'hard',
            'consecutiveCorrect': 2,
            'consecutiveWrong': 0,
            'recentPerformance': [True, True]
        }
        
        print("\n📊 Testing: Hard question answered CORRECTLY")
        result_hard = await engine.process_answer(
            student_id=1,
            question_id=4,
            selected_answer=0,  # Correct
            is_correct=True,
            state=state_hard,
            question_data=question_data
        )
        
        print(f"✅ Action: {result_hard['action']}")
        print(f"💬 Message: {result_hard['data'].get('message', 'N/A')}")
        print(f"🏆 Badge: {result_hard['data'].get('badge', 'N/A')}")
        print(f"⭐ Stars: {result_hard['data'].get('stars', 'N/A')}")
        
        return True
        
    except Exception as e:
        print(f"\n❌ Error: {e}")
        import traceback
        traceback.print_exc()
        return False


async def main():
    """Run all tests"""
    print("\n" + "="*60)
    print("🚀 PHASE 1 IMPLEMENTATION TESTS")
    print("="*60)
    print("\nTesting Gemini API integration and Adaptive Engine...")
    
    results = []
    
    # Test 1: Explanation generation
    results.append(await test_gemini_explanation())
    await asyncio.sleep(2)  # Rate limiting
    
    # Test 2: Question generation
    results.append(await test_gemini_question_generation())
    await asyncio.sleep(2)
    
    # Test 3: Adaptive engine basic
    results.append(await test_adaptive_engine())
    await asyncio.sleep(1)
    
    # Test 4: Adaptive progression
    results.append(await test_adaptive_progression())
    
    # Summary
    print("\n" + "="*60)
    print("📊 TEST SUMMARY")
    print("="*60)
    
    total = len(results)
    passed = sum(results)
    
    print(f"\nTotal Tests: {total}")
    print(f"✅ Passed: {passed}")
    print(f"❌ Failed: {total - passed}")
    
    if passed == total:
        print("\n🎉 ALL TESTS PASSED! Phase 1 implementation successful!")
    else:
        print(f"\n⚠️ {total - passed} test(s) failed. Check errors above.")
    
    print("\n" + "="*60)


if __name__ == "__main__":
    asyncio.run(main())
