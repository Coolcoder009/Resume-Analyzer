import React, { useState } from 'react';
import { Upload, FileText, Briefcase, ArrowRight, CheckCircle, AlertTriangle, TrendingUp, Award } from 'lucide-react';

interface MatchResult {
  score: number;
  strengths: string[];
  improvements: {
    category: string;
    suggestions: string[];
  }[];
  keywords: {
    matched: string[];
    missing: string[];
  };
}

function App() {
  const [step, setStep] = useState<'upload' | 'processing' | 'results'>('upload');
  const [resume, setResume] = useState<File | null>(null);
  const [jobDescription, setJobDescription] = useState('');
  const [results, setResults] = useState<MatchResult | null>(null);
  const [dragActive, setDragActive] = useState(false);

  const handleFileDrop = (e: React.DragEvent<HTMLDivElement>) => {
    e.preventDefault();
    setDragActive(false);
    const files = e.dataTransfer.files;
    if (files.length > 0) {
      setResume(files[0]);
    }
  };

  const handleFileSelect = (e: React.ChangeEvent<HTMLInputElement>) => {
    const files = e.target.files;
    if (files && files.length > 0) {
      setResume(files[0]);
    }
  };

  const processMatch = async () => {
  if (!resume || !jobDescription.trim()) return;

  setStep('processing');

  const formData = new FormData();
  formData.append('file', resume);
  formData.append('job_description', jobDescription);

  try {
    const response = await fetch('http://localhost:8001/analyze', {
      method: 'POST',
      body: formData,
    });

    if (!response.ok) {
      throw new Error(`Server responded with ${response.status}`);
    }

    const data = await response.json();

    // Format backend response into MatchResult structure
    const formattedResults: MatchResult = {
      score: data.score,
      strengths: data.strengths,
      keywords: {
        matched: data.keyword_analysis?.matched_keywords || [],
        missing: data.keyword_analysis?.missing_keywords || [],
      },
      improvements: Object.entries(data.improvement_suggestions || {}).map(
        ([category, suggestions]) => ({
          category,
          suggestions,
        })
      ),
    };

    setResults(formattedResults);
    setStep('results');
  } catch (error) {
    console.error('Error analyzing resume match:', error);
    alert('Failed to analyze resume. Please check your file and try again.');
    setStep('upload');
  }
};


  const resetProcess = () => {
    setStep('upload');
    setResume(null);
    setJobDescription('');
    setResults(null);
  };

  if (step === 'upload') {
    return (
      <div className="app">
        <div className="container">
          {/* Header */}
          <div className="header">
            <div className="header-title">
              <div className="header-icon">
                <TrendingUp size={32} />
              </div>
              <h1>Resume Matcher</h1>
            </div>
            <p>
              Upload your resume and paste a job description to get an instant compatibility score and personalized improvement suggestions.
            </p>
          </div>

          <div className="upload-grid">
            {/* Resume Upload */}
            <div className="card">
              <div className="card-header">
                <FileText size={24} />
                <h2>Upload Resume</h2>
              </div>
              
              <div
                className={`file-upload ${dragActive ? 'drag-active' : ''} ${resume ? 'has-file' : ''}`}
                onDragEnter={(e) => { e.preventDefault(); setDragActive(true); }}
                onDragLeave={(e) => { e.preventDefault(); setDragActive(false); }}
                onDragOver={(e) => e.preventDefault()}
                onDrop={handleFileDrop}
              >
                {resume ? (
                  <div className="file-upload-content">
                    <CheckCircle size={48} />
                    <h3>{resume.name}</h3>
                    <p>Resume uploaded successfully!</p>
                  </div>
                ) : (
                  <div className="file-upload-content">
                    <Upload size={48} />
                    <div>
                      <h3>Drag and drop your resume here</h3>
                      <p>Supported formats: PDF, DOC, DOCX</p>
                      <label className="file-button">
                        <Upload size={16} />
                        Choose File
                        <input
                          type="file"
                          className="file-input"
                          accept=".pdf,.doc,.docx"
                          onChange={handleFileSelect}
                        />
                      </label>
                    </div>
                  </div>
                )}
              </div>
            </div>

            {/* Job Description */}
            <div className="card">
              <div className="card-header">
                <Briefcase size={24} />
                <h2>Job Description</h2>
              </div>
              
              <textarea
                className="textarea"
                placeholder="Paste the complete job description here. Include requirements, responsibilities, and preferred qualifications for the best analysis..."
                value={jobDescription}
                onChange={(e) => setJobDescription(e.target.value)}
              />
              
              {jobDescription.length > 0 && (
                <div className="char-count">
                  {jobDescription.length} characters • {Math.ceil(jobDescription.split(' ').length)} words
                </div>
              )}
            </div>
          </div>

          {/* Process Button */}
          <div className="process-button-container">
            <button
              onClick={processMatch}
              disabled={!resume || !jobDescription.trim()}
              className="process-button"
            >
              Analyze Match
              <ArrowRight size={20} />
            </button>
          </div>
        </div>
      </div>
    );
  }

  if (step === 'processing') {
    return (
      <div className="app">
        <div className="processing-screen">
          <div className="processing-content">
            <div className="spinner-container">
              <div className="spinner"></div>
              <div className="spinner-icon">
                <TrendingUp size={48} />
              </div>
            </div>
            
            <h2>Analyzing Your Match</h2>
            <p>
              Our AI is comparing your resume against the job requirements and generating personalized recommendations.
            </p>
            
            <div className="processing-steps">
              <div className="processing-step">
                <div className="step-dot"></div>
                Extracting key information from your resume...
              </div>
              <div className="processing-step">
                <div className="step-dot"></div>
                Analyzing job requirements and skills...
              </div>
              <div className="processing-step">
                <div className="step-dot"></div>
                Generating improvement suggestions...
              </div>
            </div>
          </div>
        </div>
      </div>
    );
  }

  if (step === 'results' && results) {
    const circumference = 2 * Math.PI * 15.9155;
    const strokeDasharray = `${(results.score / 100) * circumference} ${circumference}`;

    return (
      <div className="app">
        <div className="results-container">
          {/* Header */}
          <div className="results-header">
            <h1>Your Match Results</h1>
            <p>Here's how well your resume matches the job requirements</p>
          </div>

          {/* Match Score */}
          <div className="score-card">
            <div className="score-circle">
              <svg viewBox="0 0 36 36">
                <path
                  className="score-circle-bg"
                  d="M18 2.0845 a 15.9155 15.9155 0 0 1 0 31.831 a 15.9155 15.9155 0 0 1 0 -31.831"
                />
                <path
                  className="score-circle-progress"
                  strokeDasharray={strokeDasharray}
                  d="M18 2.0845 a 15.9155 15.9155 0 0 1 0 31.831 a 15.9155 15.9155 0 0 1 0 -31.831"
                />
              </svg>
              <div className="score-text">{results.score}%</div>
            </div>
            <h3>Match Score</h3>
            <p>
              {results.score >= 80 ? 'Excellent match!' : results.score >= 60 ? 'Good match with room for improvement' : 'Consider significant improvements'}
            </p>
          </div>

          <div className="results-grid">
            {/* Strengths */}
            <div className="card">
              <div className="card-header">
                <CheckCircle size={24} />
                <h2>Your Strengths</h2>
              </div>
              
              <div className="strengths-list">
                {results.strengths.map((strength, index) => (
                  <div key={index} className="strength-item">
                    <CheckCircle size={20} />
                    <p>{strength}</p>
                  </div>
                ))}
              </div>
            </div>

            {/* Keywords Analysis */}
            <div className="card">
              <div className="card-header">
                <Award size={24} />
                <h2>Keywords Analysis</h2>
              </div>
              
              <div className="keywords-section keywords-matched">
                <h4>
                  <CheckCircle size={16} />
                  Matched Keywords ({results.keywords.matched.length})
                </h4>
                <div className="keywords-list">
                  {results.keywords.matched.map((keyword, index) => (
                    <span key={index} className="keyword-tag keyword-matched">
                      {keyword}
                    </span>
                  ))}
                </div>
              </div>
              
              <div className="keywords-section keywords-missing">
                <h4>
                  <AlertTriangle size={16} />
                  Missing Keywords ({results.keywords.missing.length})
                </h4>
                <div className="keywords-list">
                  {results.keywords.missing.map((keyword, index) => (
                    <span key={index} className="keyword-tag keyword-missing">
                      {keyword}
                    </span>
                  ))}
                </div>
              </div>
            </div>
          </div>

          {/* Improvement Suggestions */}
          <div className="card">
            <div className="card-header">
              <TrendingUp size={24} />
              <h2>Improvement Suggestions</h2>
            </div>
            
            <div className="improvements-grid">
              {results.improvements.map((category, index) => (
                <div key={index} className="improvement-category">
                  <div className="improvement-header">
                    <div className="improvement-number">
                      <span>{index + 1}</span>
                    </div>
                    <h4>{category.category}</h4>
                  </div>
                  <ul className="improvement-list">
                    {category.suggestions.map((suggestion, suggestionIndex) => (
                      <li key={suggestionIndex} className="improvement-item">
                        <ArrowRight size={16} />
                        <span>{suggestion}</span>
                      </li>
                    ))}
                  </ul>
                </div>
              ))}
            </div>
          </div>

          {/* Action Buttons */}
          <div className="action-buttons">
            <button onClick={resetProcess} className="button-secondary">
              Try Another Match
            </button>
            <button className="button-primary">
              Download Report
            </button>
          </div>
        </div>
      </div>
    );
  }

  return null;
}

export default App;