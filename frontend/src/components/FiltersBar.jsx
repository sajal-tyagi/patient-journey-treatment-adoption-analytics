import { useState, useEffect } from 'react';
import { api } from '../api/analyticsApi';

const DEFAULTS = { region: 'All', gender: 'All', age_group: 'All', insurance: 'All', severity: 'All' };

export default function FiltersBar({ filters, setFilters }) {
  const [options, setOptions] = useState(null);

  useEffect(() => {
    api.filterOptions().then(setOptions).catch(() => {});
  }, []);

  if (!options) return null;

  const set = (key, val) => setFilters(prev => ({ ...prev, [key]: val }));
  const reset = () => setFilters(DEFAULTS);
  const isActive = Object.values(filters).some(v => v !== 'All');

  const sel = (key, label, opts) => (
    <label key={key} style={{ display: 'flex', alignItems: 'center', gap: '.4rem' }}>
      <span className="filter-label">{label}</span>
      <select className="filter-select" value={filters[key]} onChange={e => set(key, e.target.value)}>
        {opts.map(o => <option key={o} value={o}>{o}</option>)}
      </select>
    </label>
  );

  return (
    <div className="filters-bar">
      {sel('region',    'Region',    options.regions)}
      {sel('gender',    'Gender',    options.genders)}
      {sel('age_group', 'Age Group', options.age_groups)}
      {sel('insurance', 'Insurance', options.insurances)}
      {sel('severity',  'Severity',  options.severities)}
      {isActive && (
        <button className="filter-reset" onClick={reset}>✕ Reset filters</button>
      )}
    </div>
  );
}

export { DEFAULTS };
