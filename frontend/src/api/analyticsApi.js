/**
 * analyticsApi.js
 * Central API client. All fetch calls go through here.
 */

const BASE = '/api';

async function get(path, params = {}) {
  const url = new URL(BASE + path, window.location.origin);
  Object.entries(params).forEach(([k, v]) => {
    if (v && v !== 'All') url.searchParams.append(k, v);
  });
  const res = await fetch(url.toString());
  if (!res.ok) {
    const err = await res.json().catch(() => ({ detail: res.statusText }));
    throw new Error(err.detail || 'API error');
  }
  return res.json();
}

export const api = {
  health:          ()       => get('/health'),
  filterOptions:   ()       => get('/filters/options'),
  overview:        (f = {}) => get('/overview',          toParams(f)),
  patientJourney:  (f = {}) => get('/patient-journey',   toParams(f)),
  adoption:        (f = {}) => get('/adoption',          toParams(f)),
  segments:        (f = {}) => get('/segments',          toParams(f)),
  marketOpp:       ()       => get('/market-opportunity'),
  modelInsights:   ()       => get('/model-insights'),
};

function toParams({ region, gender, age_group, insurance, severity }) {
  return { region, gender, age_group, insurance, severity };
}
