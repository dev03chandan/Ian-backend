// src/components/ComplianceReport.js

import React from "react";

const ComplianceReport = () => {
  return (
    <div style={styles.container}>
      <h1 style={styles.title}>ZeroRedTape AI Compliance Report</h1>

      <div style={styles.reportSection}>
        <h2>Contract Name: Lunar Cargo Transport Project</h2>
        <p>Uploaded Date: 2025-03-10</p>
        <p>Contractor: SpaceY Aerospace</p>
        <p>Contract Value: $1.2 Billion</p>
        <p>Contract Type: Defense &amp; Space Transportation</p>
        <p>Regulatory Framework: FAR, DFARS, NASA Procurement Policies</p>
      </div>

      <div style={styles.violationsSection}>
        <h2 style={{ color: "red" }}>Major Compliance Violations Detected:</h2>
        <ul>
          <li>
            <strong>Unauthorized Subcontracting:</strong> SpaceY subcontracted
            key components to an unverified foreign supplier, violating ITAR
            export control laws.
          </li>
          <li>
            <strong>Mispricing Alert:</strong> SpaceY charged $9,800 per unit
            for a standard aerospace part listed at $3,200 on GSA Advantage.
          </li>
        </ul>
      </div>
    </div>
  );
};

export default ComplianceReport;

// Optional inline styles for demonstration
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
  reportSection: {
    backgroundColor: "#f8f8f8",
    padding: "1rem",
    borderRadius: "8px",
    marginBottom: "1rem",
  },
  violationsSection: {
    backgroundColor: "#fff0f0",
    padding: "1rem",
    borderRadius: "8px",
  },
};
