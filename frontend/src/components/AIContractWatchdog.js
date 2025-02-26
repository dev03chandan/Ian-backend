// src/components/AIContractWatchdog.js
import React, { useState } from "react";
import MarkdownDisplay from "./MarkdownDisplay";
import { useAuth } from '../context/AuthContext';
import { useNavigate } from 'react-router-dom';

const AIContractWatchdog = () => {
  // Store the files (including the file object) and analysis output
  const [files, setFiles] = useState([]);
  const [analysisResult, setAnalysisResult] = useState("");
  const { token } = useAuth();
  const navigate = useNavigate();

  // Update the state to include the actual file objects
  const handleFileChange = (e) => {
    const selectedFiles = Array.from(e.target.files);
    const newFiles = selectedFiles.map((file) => ({
      file, // store the file object for later upload
      name: file.name,
      size: file.size,
      progress: 0,
    }));
    setFiles((prevFiles) => [...prevFiles, ...newFiles]);
  };

  const handleUpload = () => {
    files.forEach((fileItem, index) => {
      const formData = new FormData();
      formData.append("file", fileItem.file);
  
      fetch("http://localhost:8000/analyze_contract/", {
        method: "POST",
        headers: {
          'Authorization': `Bearer ${token}`
        },
        body: formData,
      })
        .then(response => {
          if (!response.ok) {
            if (response.status === 401) {
              // Handle unauthorized access
              navigate('/login');
              return;
            }
            throw new Error('Network response was not ok');
          }
          return response.json(); // Only call this once
        })
        .then((data) => { // Use the parsed data directly
          console.log("Parsed JSON:", data); // <-- Step 1
          setAnalysisResult(data.analysis); // Assuming the response contains an analysis field
        })
        .catch((error) => {
          console.error("Error:", error);
        });
  
      // Simulate upload progress (this is just for UI feedback)
      const intervalId = setInterval(() => {
        setFiles((prevFiles) => {
          const updatedFiles = [...prevFiles];
          if (updatedFiles[index].progress < 100) {
            updatedFiles[index].progress += 5;
          } else {
            clearInterval(intervalId);
          }
          return updatedFiles;
        });
      }, 500);
    });
  };

  return (
    <div style={styles.container}>
      <h1 style={styles.title}>AI Contract Watchdog</h1>
      <p style={styles.description}>
        AI Contract Watchdog instantly scans government contracts to detect
        violations, identify risks, and highlight compliance gaps.
      </p>

      <div style={styles.uploadBox}>
        <label
          htmlFor="contractFileInput"
          style={{
            display: "inline-block",
            padding: "8px 16px",
            backgroundColor: "#007bff",
            color: "#fff",
            borderRadius: "4px",
            cursor: "pointer",
          }}
        >
          Browse...
        </label>
        <input
          id="contractFileInput"
          type="file"
          multiple
          accept=".pdf,.docx"
          style={{ display: "none" }}
          onChange={handleFileChange}
        />
        <p>Or drop files here</p>
      </div>

      <div style={styles.fileList}>
        {files.map((file, index) => (
          <div key={index} style={styles.fileItem}>
            <p>
              {file.name} ({(file.size / 1024).toFixed(2)} KB)
            </p>
            <div style={styles.progressBarContainer}>
              <div
                style={{
                  ...styles.progressBar,
                  width: `${file.progress}%`,
                }}
              />
            </div>
            <span>{file.progress}%</span>
          </div>
        ))}
      </div>

      <button style={styles.uploadButton} onClick={handleUpload}>
        Upload
      </button>

      {/* Display the analysis result if available */}
      {analysisResult && (
        <MarkdownDisplay analysisText={analysisResult} />
      )}
    </div>
  );
};

// Inline styles for the component
const styles = {
  container: {
    maxWidth: "600px",
    margin: "0 auto",
    padding: "20px",
    fontFamily: "sans-serif",
  },
  title: {
    textAlign: "center",
    marginBottom: "1rem",
  },
  description: {
    marginBottom: "2rem",
  },
  uploadBox: {
    border: "2px dashed #ccc",
    padding: "1rem",
    textAlign: "center",
    marginBottom: "1rem",
    borderRadius: "8px",
  },
  fileList: {
    marginBottom: "1rem",
  },
  fileItem: {
    marginBottom: "8px",
  },
  progressBarContainer: {
    backgroundColor: "#eee",
    height: "10px",
    borderRadius: "5px",
    overflow: "hidden",
    width: "70%",
    display: "inline-block",
    marginRight: "1rem",
    verticalAlign: "middle",
  },
  progressBar: {
    backgroundColor: "#007bff",
    height: "100%",
  },
  uploadButton: {
    padding: "10px 16px",
    backgroundColor: "#28a745",
    color: "#fff",
    cursor: "pointer",
    borderRadius: "4px",
    border: "none",
  },
  resultContainer: {
    marginTop: "2rem",
    backgroundColor: "#f9f9f9",
    padding: "1rem",
    borderRadius: "8px",
  },
};

export default AIContractWatchdog;
