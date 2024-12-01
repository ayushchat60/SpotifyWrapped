import React from 'react';
import ReactDOM from 'react-dom/client';
import App from './App';
import './index.css';
import reportWebVitals from './reportWebVitals';

/**
 * Index.js
 *
 * The entry point of the React application. This file sets up the root React component (`App`) 
 * and renders it into the DOM. It also includes functionality to measure web vitals 
 * for performance monitoring.
 *
 * Features:
 * - Renders the `App` component inside the root element in the HTML.
 * - Wraps the app in `React.StrictMode` for highlighting potential issues in development mode.
 * - Calls `reportWebVitals` to optionally log or send performance metrics.
 */

// Create a root React element using React 18's new root API
const root = ReactDOM.createRoot(document.getElementById('root'));

// Render the App component into the root element
root.render(
  <React.StrictMode>
    <App />
  </React.StrictMode>
);

// Measure performance
// Pass a function (e.g., console.log) to log results, or send them to an analytics endpoint.
// Learn more: https://bit.ly/CRA-vitals
reportWebVitals();
