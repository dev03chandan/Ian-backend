import React, { useEffect, useState } from "react";
import { useAuth } from "../context/AuthContext";
import { Link } from "react-router-dom";
import "../styles/Dashboard.css";

const Dashboard = () => {
  const [documents, setDocuments] = useState([]);
  const { token } = useAuth();

  useEffect(() => {
    const fetchDocuments = async () => {
      try {
        const response = await fetch("http://localhost:8000/documents/my-documents", {
          method: "GET",
          headers: {
            "Authorization": `Bearer ${token}`,
            "Accept": "application/json"
          }
        });

        if (!response.ok) {
          throw new Error("Failed to fetch documents");
        }

        const data = await response.json();
        setDocuments(data);
      } catch (error) {
        console.error("Error fetching documents:", error);
      }
    };

    fetchDocuments();
  }, [token]);

  const renderRiskLevel = (riskLevel) => {
    const riskColors = {
      "Low": "green",
      "Medium": "orange",
      "High": "red",
      "Critical": "darkred",
      "Pending": "gray",
      "Flagged": "purple"
    };
    return <span style={{ color: riskColors[riskLevel] || "black" }}>{riskLevel}</span>;
  };

  return (
    <div className="dashboard-container">
      <h1>Dashboard</h1>
      <p>
        Instantly track contract compliance and financial fraud risks in real-time.
        Stay ahead of violations, prevent fraud, and take action before it's too late.
      </p>
      
      <table className="dashboard-table">
        <thead>
          <tr>
            <th>#</th>
            <th>Document Name</th>
            <th>Uploaded Date</th>
            <th>Document Type</th>
            <th>Status</th>
            <th>Risk Level</th>
            <th>Actions</th>
          </tr>
        </thead>
        <tbody>
          {documents.map((doc, index) => (
            <tr key={doc.id}>
              <td>{index + 1}</td>
              <td>{doc.document_name}</td>
              <td>{new Date(doc.upload_date).toLocaleDateString()}</td>
              <td>{doc.document_type}</td>
              <td>{doc.status}</td>
              <td>{renderRiskLevel(doc.risk_level)}</td>
              <td>
                <Link to={`/view-report/${doc.id}`} className="action-button view">
                  View Report
                </Link>
                <button 
                  className="action-button download"
                  onClick={() => window.open(`/download/${doc.id}`, '_blank')}
                >
                  Download
                </button>
                {doc.status === "flagged" && (
                  <button 
                    className="action-button action"
                    onClick={() => alert('Take appropriate action!')}
                  >
                    Take Action
                  </button>
                )}
              </td>
            </tr>
          ))}
        </tbody>
      </table>
    </div>
  );
};

export default Dashboard;
