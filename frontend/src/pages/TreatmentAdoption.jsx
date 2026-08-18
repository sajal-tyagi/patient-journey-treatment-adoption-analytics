import { useState, useEffect } from 'react';
import { api } from '../api/analyticsApi';
import ChartCard from '../components/ChartCard';
import KPICard from '../components/KPICard';
import FiltersBar, { DEFAULTS } from '../components/FiltersBar';
import { LoadingState, ErrorState } from '../components/LoadingState';
import {
  BarChart, Bar, XAxis, YAxis, CartesianGrid, Tooltip,
  ResponsiveContainer, Cell, ReferenceLine
} from 'recharts';

const COLORS = ['#2563eb','#0891b2','#059669','#d97706','#dc2626'];
const SEV_ORDER = ['Mild','Moderate','Severe'];
const AGE_ORDER = ['18-30','31-45','46-60','61+'];

export default function TreatmentAdoption() {
  const [filters, setFilters] = useState(DEFAULTS);
  const [data, setData]       = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError]     = useState(null);

  useEffect(() => {
    setLoading(true); setError(null);
    api.adoption(filters)
      .then(setData).catch(e => setError(e.message)).finally(() => setLoading(false));
  }, [filters]);

  const ordered = (arr, key, order) =>
    order ? order.map(o => arr.find(r => r.category === o)).filter(Boolean) : arr;

  const SimpleBar = ({ data: d, title }) => (
    <ChartCard title={title}>
      <ResponsiveContainer width="100%" height={220}>
        <BarChart data={d} margin={{ left: 0 }}>
          <CartesianGrid strokeDasharray="3 3" vertical={false} />
          <XAxis dataKey="category" tick={{ fontSize: 11 }} />
          <YAxis domain={[0, 100]} tickFormatter={v => `${v}%`} tick={{ fontSize: 11 }} />
          <Tooltip formatter={v => [`${v}%`, 'Adoption Rate']}
                   labelFormatter={l => `Category: ${l}`} />
          {data?.overall_rate && <ReferenceLine y={data.overall_rate} stroke="#94a3b8" strokeDasharray="4 4"
            label={{ value: `Avg ${data.overall_rate}%`, position: 'insideTopRight', fontSize: 10, fill: '#94a3b8' }} />}
          <Bar dataKey="rate_pct" radius={[4,4,0,0]}>
            {d.map((_, i) => <Cell key={i} fill={COLORS[i % COLORS.length]} />)}
          </Bar>
        </BarChart>
      </ResponsiveContainer>
    </ChartCard>
  );

  return (
    <div>
      <div className="page-header">
        <h2>Treatment Adoption</h2>
        <p>Compare adoption rates across patient dimensions to identify barriers and opportunities.</p>
      </div>

      <FiltersBar filters={filters} setFilters={setFilters} />

      {loading && <LoadingState />}
      {!loading && error && <ErrorState message={error} />}

      {!loading && !error && data && (
        <>
          <div className="kpi-grid" style={{ marginBottom: '1.5rem' }}>
            <KPICard label="Overall Adoption Rate" value={`${data.overall_rate}%`}
              sub="% of patients who started treatment" color="blue" />
          </div>

          <div className="charts-grid-2">
            {data.by_insurance && <SimpleBar data={data.by_insurance} title="Adoption by Insurance Status" />}
            {data.by_severity  && <SimpleBar data={ordered(data.by_severity, 'category', SEV_ORDER)} title="Adoption by Disease Severity" />}
          </div>

          <div className="charts-grid-2">
            {data.by_age_group && <SimpleBar data={ordered(data.by_age_group, 'category', AGE_ORDER)} title="Adoption by Age Group" />}
            {data.by_region    && <SimpleBar data={data.by_region} title="Adoption by Region" />}
          </div>

          <div className="charts-grid-2">
            {data.by_recommendation && (
              <ChartCard title="Physician Recommendation vs Adoption">
                <ResponsiveContainer width="100%" height={220}>
                  <BarChart data={data.by_recommendation}>
                    <CartesianGrid strokeDasharray="3 3" vertical={false} />
                    <XAxis dataKey="category" tick={{ fontSize: 11 }} />
                    <YAxis domain={[0,100]} tickFormatter={v=>`${v}%`} tick={{ fontSize: 11 }} />
                    <Tooltip formatter={v=>[`${v}%`,'Adoption Rate']} />
                    <Bar dataKey="rate_pct" radius={[4,4,0,0]}>
                      <Cell fill="#059669" />
                      <Cell fill="#dc2626" />
                    </Bar>
                  </BarChart>
                </ResponsiveContainer>
              </ChartCard>
            )}
            {data.by_cost_band && (
              <SimpleBar
                data={['Low (<$15k)','Medium ($15-35k)','High ($35-60k)','Very High (>$60k)']
                  .map(o => data.by_cost_band.find(r => r.category === o)).filter(Boolean)}
                title="Adoption by Treatment Cost Band"
              />
            )}
          </div>

          {/* Key Insights */}
          <div className="card">
            <div className="card-title">Key Adoption Insights</div>
            <div className="insights-grid">
              {data.by_recommendation && (() => {
                const rec   = data.by_recommendation.find(r => r.category === 'Recommended');
                const noRec = data.by_recommendation.find(r => r.category === 'Not Recommended');
                return rec && noRec ? (
                  <div className="insight-card">
                    <h4>👨‍⚕️ Recommendation Effect</h4>
                    <p>Physician recommendation is associated with <strong>{rec.rate_pct}%</strong> adoption
                    vs. <strong>{noRec.rate_pct}%</strong> without. A difference of <strong>{(rec.rate_pct - noRec.rate_pct).toFixed(1)} pp</strong>.</p>
                  </div>
                ) : null;
              })()}
              {data.by_insurance && (() => {
                const ins = data.by_insurance.find(r=>r.category==='Insured');
                const uni = data.by_insurance.find(r=>r.category==='Uninsured');
                return ins && uni ? (
                  <div className="insight-card">
                    <h4>💳 Insurance Gap</h4>
                    <p>Uninsured patients adopt at only <strong>{uni.rate_pct}%</strong> vs.
                    <strong> {ins.rate_pct}%</strong> for insured. A gap of <strong>{(ins.rate_pct - uni.rate_pct).toFixed(1)} pp</strong>.</p>
                  </div>
                ) : null;
              })()}
              {data.by_severity && (() => {
                const sev  = data.by_severity.find(r=>r.category==='Severe');
                const mild = data.by_severity.find(r=>r.category==='Mild');
                return sev && mild ? (
                  <div className="insight-card">
                    <h4>🏥 Severity Effect</h4>
                    <p>Severe patients adopt at <strong>{sev.rate_pct}%</strong> vs.
                    <strong> {mild.rate_pct}%</strong> for mild — urgency drives adoption.</p>
                  </div>
                ) : null;
              })()}
              {data.by_cost_band && (() => {
                const low  = data.by_cost_band.find(r=>r.category==='Low (<$15k)');
                const high = data.by_cost_band.find(r=>r.category?.includes('Very High'));
                return low && high ? (
                  <div className="insight-card">
                    <h4>💰 Cost Barrier</h4>
                    <p>Very high cost patients adopt at only <strong>{high.rate_pct}%</strong> vs.
                    <strong> {low.rate_pct}%</strong> for low cost — cost is a significant barrier.</p>
                  </div>
                ) : null;
              })()}
            </div>
          </div>
        </>
      )}
    </div>
  );
}
