'use client';

import React, { useEffect } from 'react';

export default function DocsPage() {
  useEffect(() => {
    // Redirect cleanly to the standalone Swagger UI
    window.location.replace('/docs/index.html');
  }, []);

  return (
    <div style={{
      display: 'flex',
      flexDirection: 'column',
      alignItems: 'center',
      justifyContent: 'center',
      minHeight: '100vh',
      fontFamily: '-apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif',
      background: '#F5F1E8',
      color: '#263C32',
      textAlign: 'center',
      padding: '2rem'
    }}>
      <h1 style={{ fontSize: '1.5rem', fontWeight: 700, marginBottom: '0.75rem' }}>
        Loading API Swagger Documentation...
      </h1>
      <p style={{ color: '#829184', marginBottom: '1.5rem' }}>
        Connecting to the interactive OpenAPI documentation.
      </p>
      <a
        href="/docs/index.html"
        style={{
          display: 'inline-block',
          padding: '0.6rem 1.25rem',
          backgroundColor: '#263C32',
          color: '#FFFFFF',
          textDecoration: 'none',
          borderRadius: '4px',
          fontWeight: 600
        }}
      >
        Click here if not redirected automatically →
      </a>
    </div>
  );
}
