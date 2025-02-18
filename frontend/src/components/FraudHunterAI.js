// src/components/FraudHunterAI.js
import React, { useState } from "react";

const FraudHunterAI = () => {
  const [files, setFiles] = useState([]);
  const [parsedInvoices, setParsedInvoices] = useState([]);
  const [analysisReport, setAnalysisReport] = useState([]);

  const handleFileChange = (e) => {
    const selectedFiles = Array.from(e.target.files);
    const newFiles = selectedFiles.map((file) => ({
      file,
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

      fetch("http://localhost:8000/upload-csv-invoices/", {
        method: "POST",
        body: formData,
      })
        .then((response) => response.json())
        .then((data) => {
          console.log("Backend response:", data);

          // Update parsed invoices and analysis
          setParsedInvoices(data.parsed_invoices || []);
          setAnalysisReport(data.analysis_report || []);

          // Set progress to 100% once done
          setFiles((prevFiles) => {
            const updated = [...prevFiles];
            updated[index].progress = 100;
            return updated;
          });
        })
        .catch((error) => {
          console.error("Error uploading file:", error);
        });

      // Simulate a progress bar for demonstration
      const intervalId = setInterval(() => {
        setFiles((prevFiles) => {
          const updated = [...prevFiles];
          if (updated[index].progress < 100) {
            updated[index].progress += 5;
          } else {
            clearInterval(intervalId);
          }
          return updated;
        });
      }, 500);
    });
  };

  return (
    <div style={styles.container}>
      <h1 style={styles.title}>Fraud Hunter AI</h1>
      <p style={styles.description}>
        Analyzes invoices and payments to detect fraud, uncover financial
        discrepancies, and flag suspicious transactions in real time. Using
        cutting-edge AI, it prevents duplicate billing, overpricing, and vendor
        fraud—protecting your finances before losses occur.
      </p>

      <div style={styles.uploadBox}>
        <label
          htmlFor="fileInput"
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
          id="fileInput"
          type="file"
          multiple
          accept=".csv"
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

      {/* Display the parsed invoices in a table */}
      <ParsedInvoices invoices={parsedInvoices} />

      {/* Display the analysis report in card-style blocks */}
      <AnalysisReport report={analysisReport} />
    </div>
  );
};

export default FraudHunterAI;

/**
 * A table for parsed invoices.
 */
function ParsedInvoices({ invoices }) {
  if (!invoices || invoices.length === 0) return null;

  return (
    <div style={{ marginTop: "2rem" }}>
      <h2>Parsed Invoices</h2>
      <table style={styles.table}>
        <thead>
          <tr>
            <th style={styles.th}>Invoice ID</th>
            <th style={styles.th}>Vendor</th>
            <th style={styles.th}>Amount</th>
            <th style={styles.th}>Payment Routing</th>
            <th style={styles.th}>Invoice Date</th>
            <th style={styles.th}>Description</th>
          </tr>
        </thead>
        <tbody>
          {invoices.map((inv, idx) => (
            <tr key={idx}>
              <td style={styles.td}>{inv.invoice_id}</td>
              <td style={styles.td}>{inv.vendor}</td>
              <td style={styles.td}>{inv.amount}</td>
              <td style={styles.td}>{inv.payment_routing}</td>
              <td style={styles.td}>{inv.invoice_date}</td>
              <td style={styles.td}>{inv.description}</td>
            </tr>
          ))}
        </tbody>
      </table>
    </div>
  );
}

/**
 * A card-based layout for the analysis report array.
 */
function AnalysisReport({ report }) {
  if (!report || report.length === 0) return null;

  return (
    <div style={{ marginTop: "2rem" }}>
      <h2>Analysis Report</h2>
      {report.map((item, idx) => (
        <div key={idx} style={styles.card}>
          {/* Header row: invoice + risk level */}
          <div style={styles.cardHeader}>
            <div style={styles.invoiceId}>{item.invoice_id}</div>
            <div style={{ ...styles.riskLevel, ...getRiskLevelStyle(item.risk_level) }}>
              {item.risk_level}
            </div>
          </div>

          <div style={styles.cardBody}>
            <p>
              <strong>Risk Score:</strong> {item.risk_score}
            </p>
            <p>
              <strong>Final Recommendation:</strong> {item.final_recommendation}
            </p>

            {item.issues && item.issues.length > 0 && (
              <div style={{ marginTop: "1rem" }}>
                <strong>Issues:</strong>
                <ul style={{ paddingLeft: "1.2rem", marginTop: "0.5rem" }}>
                  {item.issues.map((issue, i) => (
                    <li key={i} style={{ marginBottom: "0.5rem" }}>
                      <p style={{ margin: 0 }}>
                        <strong>{issue.issue}</strong>
                      </p>
                      <p style={{ margin: 0 }}>
                        <strong>Severity:</strong> {issue.severity}
                      </p>
                      <p style={{ margin: 0 }}>
                        <strong>Risk Increase:</strong> {issue.risk_increase}
                      </p>
                      <p style={{ margin: 0 }}>
                        <strong>Recommended Action:</strong> {issue.recommended_action}
                      </p>
                    </li>
                  ))}
                </ul>
              </div>
            )}
          </div>
        </div>
      ))}
    </div>
  );
}

/**
 * Helper to conditionally style the risk level text color.
 */
function getRiskLevelStyle(riskLevel) {
  if (riskLevel.includes("Safe")) {
    return { color: "green" };
  } else if (riskLevel.includes("Fraud")) {
    return { color: "red" };
  } else if (riskLevel.includes("Suspicious")) {
    return { color: "orange" };
  }
  return { color: "#333" };
}

// Inline styles
const styles = {
  container: {
    maxWidth: "800px",
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
    textAlign: "center",
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

  // Table styles for parsed invoices
  table: {
    borderCollapse: "collapse",
    width: "100%",
    marginTop: "1rem",
  },
  th: {
    border: "1px solid #ddd",
    padding: "8px",
    backgroundColor: "#f2f2f2",
    textAlign: "left",
  },
  td: {
    border: "1px solid #ddd",
    padding: "8px",
  },

  // Card styles for analysis report
  card: {
    backgroundColor: "#fff",
    border: "1px solid #ddd",
    borderRadius: "8px",
    padding: "1rem",
    marginBottom: "1rem",
    boxShadow: "0 2px 4px rgba(0,0,0,0.1)",
  },
  cardHeader: {
    display: "flex",
    justifyContent: "space-between",
    alignItems: "baseline",
    marginBottom: "0.5rem",
  },
  invoiceId: {
    fontWeight: "bold",
    fontSize: "1.1rem",
  },
  riskLevel: {
    fontWeight: "bold",
  },
  cardBody: {
    marginTop: "0.5rem",
  },
};
