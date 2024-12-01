/**
 * reportWebVitals
 *
 * This function measures and reports web vitals performance metrics for the application.
 * It uses the `web-vitals` library to gather metrics and calls the provided callback function
 * (`onPerfEntry`) with the results. These metrics help assess user experience and application performance.
 *
 * Web Vitals Metrics:
 * - CLS (Cumulative Layout Shift): Measures visual stability.
 * - FID (First Input Delay): Measures interactivity.
 * - FCP (First Contentful Paint): Measures the time to render the first piece of content.
 * - LCP (Largest Contentful Paint): Measures loading performance.
 * - TTFB (Time to First Byte): Measures server response time.
 *
 * @param {Function} onPerfEntry - Callback function to handle performance metric entries.
 *                                It will be called with the performance data for each metric.
 */
const reportWebVitals = (onPerfEntry) => {
  if (onPerfEntry && onPerfEntry instanceof Function) {
    import('web-vitals').then(({ getCLS, getFID, getFCP, getLCP, getTTFB }) => {
      getCLS(onPerfEntry); // Report Cumulative Layout Shift
      getFID(onPerfEntry); // Report First Input Delay
      getFCP(onPerfEntry); // Report First Contentful Paint
      getLCP(onPerfEntry); // Report Largest Contentful Paint
      getTTFB(onPerfEntry); // Report Time to First Byte
    });
  }
};

export default reportWebVitals;
