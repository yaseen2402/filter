// Browser-based PDF parsing utility
export async function parsePDF(file: File) {
  try {
    const arrayBuffer = await file.arrayBuffer();
    const uint8Array = new Uint8Array(arrayBuffer);
    
    // Use pdf.js for browser-based parsing
    const pdfjsLib = await import('pdfjs-dist');
    
    // Set worker - use jsdelivr CDN
    pdfjsLib.GlobalWorkerOptions.workerSrc = `https://cdn.jsdelivr.net/npm/pdfjs-dist@${pdfjsLib.version}/build/pdf.worker.min.mjs`;
    
    const pdf = await pdfjsLib.getDocument(uint8Array).promise;
    
    let fullText = '';
    
    // Extract text from all pages
    for (let i = 1; i <= pdf.numPages; i++) {
      const page = await pdf.getPage(i);
      const textContent = await page.getTextContent();
      const pageText = textContent.items
        .map((item: any) => item.str)
        .join(' ');
      fullText += pageText + '\n';
    }
    
    return fullText;
  } catch (error) {
    console.error('Error parsing PDF:', error);
    throw error;
  }
}

export function extractEmail(text: string): string | null {
  const emailRegex = /[\w.-]+@[\w.-]+\.\w+/g;
  const matches = text.match(emailRegex);
  return matches ? matches[0] : null;
}

export function extractPhone(text: string): string | null {
  const phoneRegex = /(\+?\d{1,3}[-.\s]?)?\(?\d{3}\)?[-.\s]?\d{3}[-.\s]?\d{4}/g;
  const matches = text.match(phoneRegex);
  return matches ? matches[0] : null;
}

export function extractSkills(text: string): string[] {
  const skillKeywords = [
    'JavaScript', 'Python', 'Java', 'C\\+\\+', 'React', 'Node.js',
    'TypeScript', 'SQL', 'MongoDB', 'AWS', 'Docker', 'Kubernetes',
    'Git', 'HTML', 'CSS', 'Angular', 'Vue', 'Django', 'Flask',
    'PostgreSQL', 'Redis', 'GraphQL', 'REST', 'API', 'Microservices'
  ];
  
  const foundSkills: string[] = [];
  skillKeywords.forEach(skill => {
    const regex = new RegExp(skill, 'gi');
    if (regex.test(text)) {
      foundSkills.push(skill);
    }
  });
  
  return [...new Set(foundSkills)]; // Remove duplicates
}

export function extractEducation(text: string): string[] {
  const educationKeywords = ['Bachelor', 'Master', 'PhD', 'University', 'College', 'Degree', 'B.S.', 'M.S.', 'B.A.', 'M.A.'];
  const lines = text.split('\n');
  const educationLines: string[] = [];
  
  lines.forEach(line => {
    if (educationKeywords.some(keyword => line.includes(keyword))) {
      const trimmed = line.trim();
      if (trimmed) educationLines.push(trimmed);
    }
  });
  
  return educationLines;
}

export function extractExperience(text: string): string[] {
  const experienceKeywords = ['Experience', 'Work History', 'Employment', 'Engineer', 'Developer', 'Manager'];
  const lines = text.split('\n');
  const experienceLines: string[] = [];
  
  lines.forEach(line => {
    if (experienceKeywords.some(keyword => line.includes(keyword))) {
      const trimmed = line.trim();
      if (trimmed) experienceLines.push(trimmed);
    }
  });
  
  return experienceLines;
}

export interface ResumeData {
  filename: string;
  extractedText: string;
  extractedAt: string;
  email: string | null;
  phone: string | null;
  skills: string[];
  education: string[];
  experience: string[];
}

export async function extractResumeData(file: File): Promise<ResumeData> {
  const text = await parsePDF(file);
  
  return {
    filename: file.name,
    extractedText: text,
    extractedAt: new Date().toISOString(),
    email: extractEmail(text),
    phone: extractPhone(text),
    skills: extractSkills(text),
    education: extractEducation(text),
    experience: extractExperience(text)
  };
}
