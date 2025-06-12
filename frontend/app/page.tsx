"use client";

import { useState } from "react";
import axios from "axios";
import { Document, Page } from "react-pdf";
import "react-pdf/dist/esm/Page/AnnotationLayer.css";

export default function Home() {
  const [file, setFile] = useState<File | null>(null);
  const [pdfUrl, setPdfUrl] = useState<string | null>(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const handleFileChange = (event: React.ChangeEvent<HTMLInputElement>) => {
    const selectedFile = event.target.files?.[0];
    if (selectedFile && selectedFile.type === "application/vnd.openxmlformats-officedocument.wordprocessingml.document") {
      setFile(selectedFile);
      setError(null);
    } else {
      setError("Please upload a valid .docx file.");
    }
  };

  const uploadWithRetry = async (retries: number = 3): Promise<void> => {
    if (!file) {
      setError("No file selected.");
      return;
    }

    setLoading(true);
    setError(null);

    const formData = new FormData();
    formData.append("file", file);

    for (let attempt = 1; attempt <= retries; attempt++) {
      try {
        const response = await axios.post("http://localhost:8000/generate_document", formData, {
          headers: { "Content-Type": "multipart/form-data" },
        });
        setPdfUrl(response.data.pdf_url);
        return;
      } catch (err) {
        if (attempt === retries) {
          setError("Failed to generate PDF after multiple attempts. Please try again later.");
        }
      }
    }

    setLoading(false);
  };

  const handleUpload = () => {
    uploadWithRetry();
  };

  return (
    <div className="min-h-screen flex flex-col items-center justify-center p-8">
      <h1 className="text-2xl font-bold mb-4">Tech Marketing Collateral Production</h1>
      <div className="w-full max-w-md">
        <input
          type="file"
          accept=".docx"
          onChange={handleFileChange}
          className="block w-full text-sm text-gray-500 file:mr-4 file:py-2 file:px-4 file:rounded-full file:border-0 file:text-sm file:font-semibold file:bg-blue-50 file:text-blue-700 hover:file:bg-blue-100"
        />
        {error && <p className="text-red-500 text-sm mt-2">{error}</p>}
        <button
          onClick={handleUpload}
          disabled={loading}
          className="mt-4 w-full bg-blue-500 text-white py-2 px-4 rounded hover:bg-blue-600 disabled:bg-gray-400"
        >
          {loading ? "Uploading..." : "Generate PDF"}
        </button>
      </div>

      {pdfUrl && (
        <div className="mt-8 w-full max-w-2xl">
          <h2 className="text-lg font-semibold mb-4">PDF Preview</h2>
          <div className="border p-4">
            <Document file={pdfUrl}>
              <Page pageNumber={1} />
            </Document>
          </div>
          <a
            href={pdfUrl}
            download
            className="mt-4 inline-block bg-green-500 text-white py-2 px-4 rounded hover:bg-green-600"
          >
            Download PDF
          </a>
        </div>
      )}
    </div>
  );
}
