import { createContext, useContext, useState, ReactNode } from 'react';

interface StudentProgress {
  name: string;
  class: number;
  completedTopics: string[];
  stars: number;
  badges: string[];
  currentSubject?: string;
}

interface StudentContextType {
  student: StudentProgress;
  updateProgress: (updates: Partial<StudentProgress>) => void;
  completeTopicHandler: (topic: string) => void;
  addStars: (count: number) => void;
  addBadge: (badge: string) => void;
}

const StudentContext = createContext<StudentContextType | undefined>(undefined);

export const StudentProvider = ({ children }: { children: ReactNode }) => {
  const [student, setStudent] = useState<StudentProgress>({
    name: 'Alex',
    class: 2,
    completedTopics: ['counting', 'plants'],
    stars: 50,
    badges: ['number-ninja', 'plant-expert'],
  });

  const updateProgress = (updates: Partial<StudentProgress>) => {
    setStudent(prev => ({ ...prev, ...updates }));
  };

  const completeTopicHandler = (topic: string) => {
    setStudent(prev => ({
      ...prev,
      completedTopics: [...new Set([...prev.completedTopics, topic])],
    }));
  };

  const addStars = (count: number) => {
    setStudent(prev => ({ ...prev, stars: prev.stars + count }));
  };

  const addBadge = (badge: string) => {
    setStudent(prev => ({
      ...prev,
      badges: [...new Set([...prev.badges, badge])],
    }));
  };

  return (
    <StudentContext.Provider value={{ student, updateProgress, completeTopicHandler, addStars, addBadge }}>
      {children}
    </StudentContext.Provider>
  );
};

export const useStudent = () => {
  const context = useContext(StudentContext);
  if (!context) throw new Error('useStudent must be used within StudentProvider');
  return context;
};
