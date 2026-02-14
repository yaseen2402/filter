import fs from 'fs';
import path from 'path';
import { fileURLToPath } from 'url';
import pdfParse from 'pdf-parse';

const __filename = fileURLToPath(import.meta.url);
const __dirname = path.dirname(__filename);

async function extractResumeData(pdfPath, username) {
  try {
    // Read PDF file
    const dataBuffer = fs.readFileSync(pdfPath);
    const data = await pdfParse(dataBuffer);
    
    // Extract text content
    const text = data.text;
    
    // Basic parsing (you can enhance this with more sophisticated parsing)
    const resumeData = {
      username: username,
      extractedText: text,
      extractedAt: new Date().toISOString(),
      // Basic pattern matching for common resume fields
      email: extractEmail(text),
      phone: extractPhone(text),
      skills: extractSkills(text),
      education: extractEducation(text),
      experience: extractExperience(text)
    };
    
    // Create user directory
    const userDir = path.join(__dirname, '..', 'data', username);
    if (!fs.existsSync(userDir)) {
      fs.mkdirSync(userDir, { recursive: true });
    }
    
    // Save JSON
    const jsonPath = path.join(userDir, 'resume.json');
    fs.writeFileSync(jsonPath, JSON.stringify(resumeData, null, 2));
    
    console.log(`✓ Resume data extracted and saved to ${jsonPath}`);
    return resumeData;
    
  } catch (error) {
    console.error('Error extracting resume:', error);
    throw error;
  }
}

function extractEmail(text) {
  const emailRegex = /[\w.-]+@[\w.-]+\.\w+/g;
  const matches = text.match(emailRegex);
  return matches ? matches[0] : null;
}

function extractPhone(text) {
  const phoneRegex = /(\+?\d{1,3}[-.\s]?)?\(?\d{3}\)?[-.\s]?\d{3}[-.\s]?\d{4}/g;
  const matches = text.match(phoneRegex);
  return matches ? matches[0] : null;
}

function extractSkills(text) {
  // Common tech skills keywords
  const skillKeywords = [
    'JavaScript', 'Python', 'Java', 'C\\+\\+', 'React', 'Node.js', 
    'TypeScript', 'SQL', 'MongoDB', 'AWS', 'Docker', 'Kubernetes',
    'Git', 'HTML', 'CSS', 'Angular', 'Vue', 'Django', 'Flask'
  ];
  
  const foundSkills = [];
  skillKeywords.forEach(skill => {
    const regex = new RegExp(skill, 'gi');
    if (regex.test(text)) {
      foundSkills.push(skill);
    }
  });
  
  return foundSkills;
}

function extractEducation(text) {
  const educationKeywords = ['Bachelor', 'Master', 'PhD', 'University', 'College', 'Degree'];
  const lines = text.split('\n');
  const educationLines = [];
  
  lines.forEach(line => {
    if (educationKeywords.some(keyword => line.includes(keyword))) {
      educationLines.push(line.trim());
    }
  });
  
  return educationLines;
}

function extractExperience(text) {
  const experienceKeywords = ['Experience', 'Work History', 'Employment'];
  const lines = text.split('\n');
  const experienceLines = [];
  let capturing = false;
  
  lines.forEach(line => {
    if (experienceKeywords.some(keyword => line.includes(keyword))) {
      capturing = true;
    }
    if (capturing && line.trim()) {
      experienceLines.push(line.trim());
    }
  });
  
  return experienceLines;
}

// CLI usage
if (process.argv.length < 4) {
  console.log('Usage: node extractResume.js <pdf-path> <username>');
  console.log('Example: node extractResume.js ./resume.pdf john_doe');
  process.exit(1);
}

const pdfPath = process.argv[2];
const username = process.argv[3];

extractResumeData(pdfPath, username)
  .then(() => console.log('Done!'))
  .catch(err => {
    console.error('Failed:', err.message);
    process.exit(1);
  });

export { extractResumeData };
