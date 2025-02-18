import React from "react";
import ReactMarkdown from "react-markdown";
import remarkGfm from "remark-gfm";

function MarkdownDisplay({ analysisText }) {
  return (
    <div style={styles.container}>
      <ReactMarkdown remarkPlugins={[remarkGfm]}>
        {analysisText}
      </ReactMarkdown>
    </div>
  );
}

const styles = {
  container: {
    backgroundColor: "#f9f9f9",
    padding: "1.5rem",
    borderRadius: "8px",
    lineHeight: 1.6,
    fontFamily: "sans-serif",
    color: "#333",
    boxShadow: "0 2px 8px rgba(0, 0, 0, 0.1)",
    maxWidth: "800px",
    margin: "1rem auto",
  },
};

export default MarkdownDisplay;
