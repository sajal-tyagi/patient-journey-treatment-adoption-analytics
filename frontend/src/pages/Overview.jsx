import { useState, useEffect } from 'react';
import { api } from '../api/analyticsApi';
import KPICard from '../components/KPICard';
import ChartCard from '../components/ChartCard';
import FiltersBar, { DEFAULTS } from '../components/FiltersBar';
import { LoadingState, ErrorState } from '../components/LoadingState';
import {
  BarChart, Bar, XAxis, YAxis, CartesianGrid, Tooltip,
  ResponsiveContainer, Cell
} from 'recharts';

const COLORS = ['#2563eb', '#0891b2', '#059669', '#d97706', '#dc2626'];

export default function Overview() {
  const [filters, setFilters] = useState(DEFAULTS);
  const [data, setData]       = useState(null);
  const [journey, setJourney] = useState(null);
  const [adoption, setAdoption] = useState(null);
  const [market, setMarket]   = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError]     = useState(null);

  useEffect(() => {
    setLoading(true); setError(null);
    Promise.all([
      api.overview(filters),
      api.patientJourney(filters),
      api.adoption(filters),
      api.marketOpp(),
    ])
      .then(([ov, jn, ad, mk]) => { setData(ov); setJourney(jn); setAdoption(ad); setMarket(mk); })
      .catch(e => setError(e.message))
      .finally(() => setLoading(false));
  }, [filters]);

  const fmt  = n => n?.toLocaleString() ?? '—';
  const pct  = n => n != null ? `${n}%` : '—';

  return (
    <div>
      <div className="page-header">
        <h2>Patient Journey &amp; Treatment Adoption Analytics</h2>
        <p>Turning patient data into actionable business insights — Therapy X · NovaCure Pharmaceuticals</p>
      </div>

      <FiltersBar filters={filters} setFilters={setFilters} />

      {loading && <LoadingState />}
      {!loading && error && <ErrorState message={error} />}

      {!loading && !error && data && (
        <>
          {/* KPIs */}
          <div className="kpi-grid">
            <KPICard label="Total Patients"      value={fmt(data.total_patients)}    sub="In dataset" />
            <KPICard label="Adoption Rate"        value={pct(data.adoption_rate)}      sub="Started treatment" color="green" />
            <KPICard label="Continuation Rate"    value={pct(data.continuation_rate)} sub="Continued after starting" color="cyan" />
            <KPICard label="Untreated Patients"   value={fmt(data.untreated_patients)} sub="Never started" color="amber" />
            <KPICard label="Top Opportunity"      value={data.top_opportunity_region}  sub={`${fmt(data.top_opportunity_untreated)} untreated`} color="red" />
          </div>

          {/* Journey mini-funnel */}
          {journey && (
            <div className="section">
              <div className="section-title">Patient Journey — Stage Overview</div>
              <ChartCard>
                <div className="funnel-grid">
                  <div className="funnel-row header">
                    <span>Stage</span><span>Progress</span><span style={{textAlign:'right'}}>Patients</span><span style={{textAlign:'right'}}>Conv. %</span>
                  </div>
                  {journey.stages.map((s, i) => (
                    <div
                      key={s.stage}
                      className={`funnel-row ${s.stage === journey.biggest_dropoff?.stage ? 'biggest-drop' : ''}`}
                    >
                      <span className="funnel-stage-name">{s.stage}</span>
                      <div className="funnel-bar-wrap">
                        <div
                          className="funnel-bar"
                          style={{ width: `${s.conversion_pct}%` }}
                        />
                      </div>
                      <span className="funnel-num">{s.patients.toLocaleString()}</span>
                      <span className="funnel-pct">{s.conversion_pct}%</span>
                    </div>
                  ))}
                </div>
                {journey.biggest_dropoff && (
                  <p style={{ marginTop: '1rem', fontSize: '.82rem', color: '#dc2626', fontWeight: 600 }}>
                    ⚠ Biggest drop-off at &quot;{journey.biggest_dropoff.stage}&quot; — {journey.biggest_dropoff.dropoff_pct}% of patients lost here
                  </p>
                )}
              </ChartCard>
            </div>
          )}

          {/* Adoption charts */}
          {adoption && (
            <div className="section">
              <div className="section-title">Treatment Adoption</div>
              <div className="charts-grid-2">
                <ChartCard title="Adoption Rate by Region">
                  <ResponsiveContainer width="100%" height={220}>
                    <BarChart data={adoption.by_region} layout="vertical" margin={{ left: 10 }}>
                      <CartesianGrid strokeDasharray="3 3" horizontal={false} />
                      <XAxis type="number" domain={[0, 100]} tickFormatter={v => `${v}%`} tick={{ fontSize: 11 }} />
                      <YAxis type="category" dataKey="category" tick={{ fontSize: 11 }} width={80} />
                      <Tooltip formatter={v => [`${v}%`, 'Adoption Rate']} />
                      <Bar dataKey="rate_pct" radius={[0,4,4,0]}>
                        {adoption.by_region.map((_, i) => <Cell key={i} fill={COLORS[i % COLORS.length]} />)}
                      </Bar>
                    </BarChart>
                  </ResponsiveContainer>
                </ChartCard>

                <ChartCard title="Adoption Rate by Insurance Status">
                  <ResponsiveContainer width="100%" height={220}>
                    <BarChart data={adoption.by_insurance} margin={{ left: 10 }}>
                      <CartesianGrid strokeDasharray="3 3" vertical={false} />
                      <XAxis dataKey="category" tick={{ fontSize: 11 }} />
                      <YAxis domain={[0, 100]} tickFormatter={v => `${v}%`} tick={{ fontSize: 11 }} />
                      <Tooltip formatter={v => [`${v}%`, 'Adoption Rate']} />
                      <Bar dataKey="rate_pct" radius={[4,4,0,0]}>
                        {adoption.by_insurance.map((_, i) => <Cell key={i} fill={COLORS[i]} />)}
                      </Bar>
                    </BarChart>
                  </ResponsiveContainer>
                </ChartCard>
              </div>
            </div>
          )}

          {/* Market Opportunity */}
          {market && (
            <div className="section">
              <div className="section-title">Market Opportunity</div>
              <ChartCard title="Untreated Patients by Region">
                <ResponsiveContainer width="100%" height={200}>
                  <BarChart data={[...market.regions].sort((a,b) => b.untreated_patients - a.untreated_patients)}>
                    <CartesianGrid strokeDasharray="3 3" vertical={false} />
                    <XAxis dataKey="region" tick={{ fontSize: 11 }} />
                    <YAxis tick={{ fontSize: 11 }} />
                    <Tooltip formatter={v => [v.toLocaleString(), 'Untreated Patients']} />
                    <Bar dataKey="untreated_patients" radius={[4,4,0,0]}>
                      {market.regions.map((_, i) => <Cell key={i} fill={COLORS[i % COLORS.length]} />)}
                    </Bar>
                  </BarChart>
                </ResponsiveContainer>
              </ChartCard>
            </div>
          )}

          {/* Dynamic insights */}
          {data && adoption && (
            <div className="section">
              <div className="section-title">Key Business Insights</div>
              <div className="insights-grid">
                <div className="insight-card">
                  <h4>📉 Adoption Gap</h4>
                  <p>Only <strong>{pct(data.adoption_rate)}</strong> of patients start Therapy X,
                  leaving <strong>{fmt(data.untreated_patients)}</strong> untreated patients.</p>
                </div>
                {adoption.by_recommendation && (() => {
                  const rec = adoption.by_recommendation.find(r => r.category === 'Recommended');
                  const noRec = adoption.by_recommendation.find(r => r.category === 'Not Recommended');
                  return rec && noRec ? (
                    <div className="insight-card">
                      <h4>👨‍⚕️ Physician Impact</h4>
                      <p>Physician recommendation is associated with <strong>{pct(rec.rate_pct)}</strong> adoption
                      vs. <strong>{pct(noRec.rate_pct)}</strong> without — a {(rec.rate_pct - noRec.rate_pct).toFixed(1)} pp gap.</p>
                    </div>
                  ) : null;
                })()}
                {adoption.by_insurance && (() => {
                  const ins = adoption.by_insurance.find(r => r.category === 'Insured');
                  const uni = adoption.by_insurance.find(r => r.category === 'Uninsured');
                  return ins && uni ? (
                    <div className="insight-card">
                      <h4>🏥 Insurance Barrier</h4>
                      <p>Insured patients adopt at <strong>{pct(ins.rate_pct)}</strong> vs.
                      only <strong>{pct(uni.rate_pct)}</strong> for uninsured — cost is a major barrier.</p>
                    </div>
                  ) : null;
                })()}
                {market && (
                  <div className="insight-card">
                    <h4>🗺️ Top Market</h4>
                    <p><strong>{market.top_region}</strong> has the highest opportunity score with
                    {' '}<strong>{fmt(market.regions.find(r=>r.region===market.top_region)?.untreated_patients)}</strong> untreated patients.</p>
                  </div>
                )}
              </div>
            </div>
          )}
        </>
      )}
    </div>
  );
}
