import { useNavigate } from 'react-router-dom';
import { Card } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { Progress } from '@/components/ui/progress';
import { useStudent } from '@/contexts/StudentContext';
import { subjects } from '@/data/mockData';
import { Trophy, Star, Flame, Settings } from 'lucide-react';
import Mascot from '@/components/Mascot';
import FloatingShapes from '@/components/FloatingShapes';
import ThemeToggle from '@/components/ThemeToggle';

const Dashboard = () => {
  const navigate = useNavigate();
  const { student } = useStudent();
  
  const progressPercentage = Math.min((student.completedTopics.length / 8) * 100, 100);

  return (
    <div className="min-h-screen p-6 md:p-12 relative">
      <ThemeToggle />
      <FloatingShapes />
      <div className="max-w-6xl mx-auto space-y-8 relative z-10">
        {/* Top Bar */}
        <div className="flex items-center justify-between bg-card/80 backdrop-blur-sm p-6 rounded-3xl shadow-lg">
          <div className="flex items-center gap-4">
            <div className="w-16 h-16 rounded-full bg-gradient-to-br from-primary to-accent flex items-center justify-center text-3xl shadow-lg">
              👦
            </div>
            <div>
              <h2 className="text-2xl font-bold text-foreground">Hello, {student.name}! 👋</h2>
              <p className="text-foreground/70">Class {student.class}</p>
            </div>
          </div>
           {/* Quick Stats */}
        <div className="flex flex-wrap gap-4">
          <Card className="px-6 py-3 bg-gradient-to-r from-destructive/20 to-destructive/10 border-destructive/30 hover:scale-105 transition-transform">
            <div className="flex items-center gap-2">
             
              <span className="font-bold text-foreground">🔥 3 days streak!</span>
            </div>
          </Card>
          <Card className="px-6 py-3 bg-gradient-to-r from-accent/20 to-accent/10 border-accent/30 hover:scale-105 transition-transform">
            <div className="flex items-center gap-2">
              <Trophy className="w-5 h-5 text-accent" />
              <span className="font-bold text-foreground">{student.completedTopics.length} topics completed</span>
            </div>
          </Card>
        </div>
          <div className="flex items-center gap-6">
            <div className="flex items-center gap-2">
              <Star className="w-6 h-6 text-secondary fill-secondary" />
              <span className="text-2xl font-bold text-foreground">{student.stars}</span>
            </div>
            <div className="flex items-center gap-2">
              <Trophy className="w-6 h-6 text-supporting-orange" />
              <span className="text-2xl font-bold text-foreground">{student.badges.length}</span>
            </div>
            <Button
              onClick={() => navigate('/settings')}
              variant="outline"
              size="icon"
              className="rounded-full w-12 h-12 hover:bg-primary/10 hover:scale-110 transition-all"
            >
              <Settings className="w-5 h-5" />
            </Button>
          </div>
        </div>

        {/* Progress Section */}
        <Card className="p-8 bg-white/80 backdrop-blur-sm shadow-2xl border-2 border-primary/20">
          <div className="space-y-6">
            <div className="flex items-center justify-between">
              <h3 className="text-2xl font-bold text-foreground">Your Learning Journey 🚀</h3>
              <span className="text-2xl font-bold text-primary">{Math.round(progressPercentage)}%</span>
            </div>
            
            <Progress value={progressPercentage} className="h-4 rounded-full" />  
    
          </div>
        </Card>

       


        {/* Subject Cards Grid */}
        <div className="grid md:grid-cols-2 gap-8">
          {subjects.map((subject, index) => {
            const subjectTopicCount = subject.id === 'math' ? 4 : 4;
            const completedCount = student.completedTopics.filter(t => 
              subject.id === 'math' 
                ? ['counting', 'addition', 'subtraction', 'shapes'].includes(t)
                : ['plants', 'animals', 'weather', 'human-body'].includes(t)
            ).length;
            const subjectProgress = (completedCount / subjectTopicCount) * 100;

            return (
              <Card
                key={subject.id}
                className={`p-8 cursor-pointer transition-all duration-300 hover:scale-105 hover:shadow-2xl hover:-translate-y-1 border-2 border-white/50 animate-fade-in ${
                  subject.id === 'math' 
                    ? 'bg-gradient-to-br from-blue-400/20 to-green-400/20 hover:from-blue-400/30 hover:to-green-400/30' 
                    : 'bg-gradient-to-br from-purple-400/20 to-yellow-400/20 hover:from-purple-400/30 hover:to-yellow-400/30'
                }`}
                style={{ animationDelay: `${index * 0.1}s` }}
                onClick={() => navigate(`/topics/${subject.id}`)}
              >
                <div className="space-y-6">
                  <div className="text-8xl text-center">{subject.icon}</div>
                  <div className="text-center space-y-2">
                    <h3 className="text-3xl font-bold text-foreground">{subject.name}</h3>
                    <p className="text-lg text-foreground/70">{subject.description}</p>
                  </div>
                  <div className="space-y-2">
                    <div className="flex justify-between text-sm text-foreground/70">
                      <span>{completedCount} of {subjectTopicCount} topics</span>
                      <span>{Math.round(subjectProgress)}%</span>
                    </div>
                    <Progress value={subjectProgress} className="h-2" />
                  </div>
                  <Button 
                    className="w-full gradient-button text-white text-lg py-6 rounded-2xl hover:scale-105 transition-transform shadow-lg"
                  >
                    Start Learning
                  </Button>
                </div>
              </Card>
            );
          })}
        </div>
        
        {/* Recent Activity */}
        {student.completedTopics.length > 0 && (
          <Card className="p-6 bg-white/80 backdrop-blur-sm shadow-lg border-2 border-primary/10">
            <h3 className="text-2xl font-bold text-foreground mb-4">🌟 Your Recent Adventures</h3>
            <div className="space-y-3">
              {student.completedTopics.slice(-3).reverse().map((topic, index) => (
                <div
                  key={topic}
                  className="flex items-center justify-between p-4 bg-gradient-to-r from-primary/10 to-accent/10 rounded-xl hover:scale-102 transition-transform"
                >
                  <div className="flex items-center gap-3">
                    <div className="text-3xl">
                      {topic === 'counting' ? '🔢' : topic === 'addition' ? '➕' : topic === 'plants' ? '🌱' : '📚'}
                    </div>
                    <div>
                      <p className="font-semibold text-foreground capitalize">{topic.replace('-', ' ')}</p>
                      <p className="text-sm text-foreground/60">Completed recently</p>
                    </div>
                  </div>
                  <div className="flex items-center gap-2">
                    <Star className="w-5 h-5 text-secondary fill-secondary" />
                    <span className="font-bold text-foreground">+10</span>
                  </div>
                </div>
              ))}
            </div>
          </Card>
        )}

        <Mascot mood="idle" />
      </div>
    </div>
  );
};

export default Dashboard;
