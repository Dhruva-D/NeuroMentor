import { useState, useEffect } from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import { Card } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { getQuizSet } from '@/data/quizData';
import { useStudent } from '@/contexts/StudentContext';
import { Timer, Trophy } from 'lucide-react';
import Mascot from '@/components/Mascot';
import Confetti from '@/components/Confetti';
import Breadcrumb from '@/components/Breadcrumb';
import { Progress } from '@/components/ui/progress';

const Quiz = () => {
  const { chapterId, quizSetId } = useParams<{ chapterId: string; quizSetId: string }>();
  const navigate = useNavigate();
  const { student, completeTopicHandler, addStars } = useStudent();
  
  const quizSet = getQuizSet(chapterId || '', quizSetId || '', student.class);
  const questions = quizSet?.questions || [];
  
  const [currentQuestion, setCurrentQuestion] = useState(0);
  const [selectedAnswer, setSelectedAnswer] = useState<number | null>(null);
  const [isCorrect, setIsCorrect] = useState<boolean | null>(null);
  const [score, setScore] = useState(0);
  const [timeLeft, setTimeLeft] = useState(30);
  const [showResult, setShowResult] = useState(false);
  const [showConfetti, setShowConfetti] = useState(false);
  const [encouragingMsg, setEncouragingMsg] = useState('');
  const [mascotMood, setMascotMood] = useState<'idle' | 'happy' | 'thinking' | 'celebrating' | 'encouraging'>('thinking');

  useEffect(() => {
    if (timeLeft > 0 && selectedAnswer === null) {
      const timer = setTimeout(() => setTimeLeft(timeLeft - 1), 1000);
      return () => clearTimeout(timer);
    } else if (timeLeft === 0 && selectedAnswer === null) {
      handleTimeout();
    }
  }, [timeLeft, selectedAnswer]);

  const handleTimeout = () => {
    setIsCorrect(false);
    setTimeout(() => handleNext(), 2000);
  };

  const handleAnswerClick = (index: number) => {
    // Allow clicking different answer if previous was wrong
    if (selectedAnswer !== null && isCorrect === true) return;
    
    setSelectedAnswer(index);
    const correct = questions[currentQuestion].options[index].correct;
    setIsCorrect(correct);
    
    if (correct) {
      setScore(score + 1);
      addStars(10);
      setShowConfetti(true);
      setMascotMood('happy');
      setEncouragingMsg('');
      setTimeout(() => setShowConfetti(false), 1500);
    } else {
      setMascotMood('encouraging');
      setEncouragingMsg("Almost there! Try again 🦉");
    }
  };

  const handleNext = () => {
    if (currentQuestion < questions.length - 1) {
      setCurrentQuestion(currentQuestion + 1);
      setSelectedAnswer(null);
      setIsCorrect(null);
      setTimeLeft(30);
      setMascotMood('thinking');
      setEncouragingMsg('');
    } else {
      setShowResult(true);
      setMascotMood('celebrating');
      setShowConfetti(true);
      if (chapterId) {
        completeTopicHandler(chapterId);
      }
    }
  };

  if (showResult) {
    return (
      <div className="min-h-screen flex items-center justify-center p-6">
        <Card className="p-12 max-w-2xl w-full text-center space-y-8 gradient-card border-2 border-white/50 animate-bounce-in">
          <Trophy className="w-24 h-24 mx-auto text-secondary" />
          <h1 className="text-5xl font-bold text-foreground">Amazing Job! 🎉</h1>
          <div className="text-6xl">{score === questions.length ? '🏆' : '⭐'}</div>
          <p className="text-3xl text-foreground">
            You scored {score} out of {questions.length}!
          </p>
          <div className="flex gap-4 justify-center">
            <Button
              size="lg"
              onClick={() => navigate('/rewards')}
              className="gradient-button text-white px-8 py-6 rounded-2xl text-lg hover:scale-105 transition-transform"
            >
              View Rewards
            </Button>
            <Button
              size="lg"
              variant="outline"
              onClick={() => navigate('/dashboard')}
              className="px-8 py-6 rounded-2xl text-lg hover:scale-105 transition-transform"
            >
              Back to Dashboard
            </Button>
          </div>
        </Card>
      </div>
    );
  }

  if (!quizSet || questions.length === 0) {
    return (
      <div className="min-h-screen flex items-center justify-center">
        <p className="text-2xl">Quiz not found!</p>
      </div>
    );
  }

  const question = questions[currentQuestion];
  const subject = chapterId?.includes('math') ? 'math' : 'science';
  const subjectName = subject === 'math' ? 'Math Island' : 'Science Island';
  const quizName = quizSet.name;

  return (
    <div className="min-h-screen p-4 md:p-6 bg-gradient-to-br from-[#C8E4F9] to-[#E0F2FF]">
      <Confetti trigger={showConfetti} />
      <div className="max-w-4xl mx-auto space-y-6">
        <Breadcrumb items={[
          { label: 'Dashboard', path: '/dashboard' },
          { label: subjectName, path: `/topics/${subject}` },
          { label: quizName, path: '' }
        ]} />

        {/* Header with Back Button and Star Progress */}
        <div className="flex items-center justify-between">
          <button 
            onClick={() => navigate('/dashboard')}
            className="flex items-center gap-2 px-4 py-2 bg-white rounded-xl shadow-md hover:shadow-lg transition-all"
          >
            <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M15 19l-7-7 7-7" />
            </svg>
            <span className="font-semibold text-gray-700">Back</span>
          </button>
          
          <div className="flex items-center gap-2 px-5 py-2 bg-white rounded-xl shadow-md">
            <span className="text-yellow-500 text-xl">⭐</span>
            <span className="text-xl font-bold text-gray-700">{score}/{questions.length}</span>
          </div>
        </div>

        {/* Subject Title and Progress */}
        <div className="space-y-3">
          <div className="flex items-center justify-between">
            <h1 className="text-2xl font-bold text-gray-800">
              {quizName}
            </h1>
            <span className="text-lg font-semibold text-[#5B9FD8]">
              Question {currentQuestion + 1}/{questions.length}
            </span>
          </div>
          <div className="w-full bg-white/50 rounded-full h-3 overflow-hidden">
            <div 
              className="h-full bg-gradient-to-r from-[#5B9FD8] to-[#4A8BC2] transition-all duration-500 ease-out rounded-full"
              style={{ width: `${((currentQuestion + 1) / questions.length) * 100}%` }}
            />
          </div>
        </div>

        {/* Timer */}
        <div className="flex items-center justify-center">
          <div className={`flex items-center gap-3 px-8 py-4 bg-white rounded-2xl shadow-lg transition-all duration-300 ${
            timeLeft < 5 ? 'animate-pulse ring-4 ring-red-300' : timeLeft < 10 ? 'ring-2 ring-orange-300' : ''
          }`}>
            <Timer className={`w-7 h-7 ${
              timeLeft < 5 ? 'text-red-500' : timeLeft < 10 ? 'text-orange-500' : 'text-[#5B9FD8]'
            }`} />
            <span className={`text-4xl font-bold ${
              timeLeft < 5 ? 'text-red-500' : timeLeft < 10 ? 'text-orange-500' : 'text-[#5B9FD8]'
            }`}>
              {timeLeft}s
            </span>
          </div>
        </div>

        {/* Question Card */}
        <Card className="p-8 md:p-12 bg-white border-0 shadow-2xl rounded-3xl">
          <div className="flex items-start gap-4 mb-8">
            <div className="text-5xl flex-shrink-0">🤖</div>
            <h2 className="text-2xl md:text-3xl font-bold text-gray-800 leading-tight pt-2">
              {question.question}
            </h2>
          </div>

          {/* Answer Options */}
          <div className="grid grid-cols-1 md:grid-cols-2 gap-4 md:gap-6">
            {question.options.map((option, index) => {
              const isSelected = selectedAnswer === index;
              const isCorrectOption = option.correct;
              const showAsCorrect = selectedAnswer !== null && isCorrectOption && !isCorrect;
              
              let buttonStyles = 'bg-[#E8EDF5] hover:bg-[#DDE5F0] border-2 border-transparent';
              
              if (isSelected) {
                if (isCorrect) {
                  buttonStyles = 'bg-[#8DD4B8] border-2 border-[#8DD4B8] quiz-correct-answer';
                } else {
                  buttonStyles = 'bg-[#FFB3C1] border-2 border-[#FF8FA0] quiz-wrong-answer';
                }
              } else if (showAsCorrect) {
                buttonStyles = 'bg-[#8DD4B8]/50 border-2 border-[#8DD4B8]';
              }

              return (
                <button
                  key={index}
                  onClick={() => handleAnswerClick(index)}
                  disabled={selectedAnswer !== null && isCorrect === true}
                  className={`p-6 md:p-8 rounded-2xl transition-all duration-300 hover:scale-105 hover:shadow-xl disabled:hover:scale-100 ${buttonStyles}`}
                >
                  <div className="text-center space-y-2">
                    {option.emoji && <div className="text-4xl md:text-5xl mb-2">{option.emoji}</div>}
                    <div className="text-xl md:text-2xl font-bold text-gray-800">{option.text}</div>
                  </div>
                </button>
              );
            })}
          </div>

          {/* Encouraging Message */}
          {!isCorrect && selectedAnswer !== null && (
            <div className="mt-8 animate-fade-in">
              <div className="p-6 bg-gradient-to-r from-purple-100 to-pink-100 border-2 border-purple-200 rounded-2xl shadow-lg">
                <p className="text-center text-xl font-bold text-purple-800">{encouragingMsg}</p>
                <p className="text-center text-sm text-purple-600 mt-2">Click another answer to try again!</p>
              </div>
            </div>
          )}
        </Card>

        {/* Next Button */}
        {selectedAnswer !== null && isCorrect && (
          <div className="text-center animate-fade-in">
            <Button
              size="lg"
              onClick={handleNext}
              className="bg-gradient-to-r from-[#5B9FD8] to-[#4A8BC2] text-white px-12 py-6 rounded-2xl text-xl font-bold hover:scale-110 transition-transform shadow-xl hover:shadow-2xl"
            >
              {currentQuestion < questions.length - 1 ? 'Next Question →' : 'See Results 🎉'}
            </Button>
          </div>
        )}

        <Mascot mood={mascotMood} showMessage={!isCorrect && selectedAnswer !== null} customMessage={encouragingMsg} />
      </div>
    </div>
  );
};

export default Quiz;
