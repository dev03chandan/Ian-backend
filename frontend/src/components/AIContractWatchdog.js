// src/components/AIContractWatchdog.js
import React, { useState } from "react";
import MarkdownDisplay from "./MarkdownDisplay";

const AIContractWatchdog = () => {
  // Store the files (including the file object) and analysis output
  const [files, setFiles] = useState([]);
  const [analysisResult, setAnalysisResult] = useState("");

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
      // Append the file with key "file" (make sure your FastAPI endpoint accepts this key)
      formData.append("file", fileItem.file);

      // POST the file to your FastAPI /analyze_contract endpoint
      fetch("http://localhost:8000/analyze_contract/", {
        method: "POST",
        body: formData,
      })
        .then((response) => {
          console.log("Raw response:", response); // <-- Step 1
          return response.json();
        })
        .then((data) => {
          console.log("Parsed JSON:", data); // <-- Step 2
          setAnalysisResult(data.analysis);
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
