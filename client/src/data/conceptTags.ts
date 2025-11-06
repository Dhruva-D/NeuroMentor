/**
 * Concept Tags Helper
 * Maps chapters to their concept tags for AI learning
 */

export const CONCEPT_TAGS: Record<string, string[]> = {
  // Class 1 Math
  'class1-math-shapes': ['shapes', 'geometry', 'visual-recognition'],
  'class1-math-numbers': ['counting', 'numbers', 'basic-math'],
  
  // Class 1 Science
  'class1-science-living': ['classification', 'observation', 'living-things'],
  'class1-science-body': ['anatomy', 'body', 'health'],
  
  // Class 2 Math
  'class2-math-numbers-100': ['counting', 'numbers', 'place-value'],
  'class2-math-addition': ['addition', 'subtraction', 'arithmetic'],
  
  // Class 2 Science
  'class2-science-plants': ['plants', 'nature', 'observation'],
  'class2-science-animals': ['animals', 'habitats', 'classification'],
  
  // Class 3 Math
  'class3-math-multiplication': ['multiplication', 'tables', 'arithmetic'],
  'class3-math-division': ['division', 'arithmetic', 'problem-solving'],
  
  // Class 3 Science
  'class3-science-water': ['water', 'states-of-matter', 'science'],
  'class3-science-air': ['air', 'atmosphere', 'science'],
};

export function getConceptTags(chapterId: string): string[] {
  return CONCEPT_TAGS[chapterId] || ['general-knowledge'];
}
