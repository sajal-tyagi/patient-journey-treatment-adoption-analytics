import { useState, useEffect } from 'react';
import { api } from '../api/analyticsApi';
import ChartCard from '../components/ChartCard';
import FiltersBar, { DEFAULTS } from '../components/FiltersBar';
import { LoadingState, ErrorState } from '../components/LoadingState';
import {
  BarChart, Bar, XAxis, YAxis, CartesianGrid, Tooltip,
  ResponsiveContainer, Cell
} from 'recharts';

const COLORS = ['#2563eb','#0891b2','#059669','#d97706','#dc2626','#7c3aed'];

function segBadge(seg) {
  if (seg.includes('High-Need') && seg.includes('High-Ability')) return 'badge-green';
  if (seg.includes('High-Need') && seg.includes('Low-Ability'))  return 'badge-red';
  if (seg.includes('High-Need'))                                  return 'badge-blue';
  if (seg.includes('Low-Ability'))                                return 'badge-amber';
  return 'badge-blue';
}

export default function Segments() {
  const [filters, setFilters] = useState(DEFAULTS);
  const [data, setData]       = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError]     = useState(null);

  useEffect(() => {
    setLoading(true); setError(null);
    api.segments(filters)
      .then(setData).catch(e => setError(e.message)).finally(() => setLoading(false));
  }, [filters]);

  const segs = data?.segments ?? [];

  return (
    <div>
      <div className="page-header">
        <h2>Patient Segments</h2>
        <p>Patients segmented by clinical need and financial ability to identify priority groups.</p>
      </div>

      <FiltersBar filters={filters} setFilters={setFilters} />

      {loading && <LoadingState />}
      {!loading && error && <ErrorState message={error} />}

      {!loading && !error && segs.length > 0 && (
        <>
          <div className="charts-grid-2">
            <ChartCard title="Segment Size (Total Patients)">
              <ResponsiveContainer width="100%" height={250}>
                <BarChart data={segs} layout="vertical" margin={{ left: 10 }}>
                  <CartesianGrid strokeDasharray="3 3" horizontal={false} />
                  <XAxis type="number" tick={{ fontSize: 10 }} />
                  <YAxis type="category" dataKey="segment" tick={{ fontSize: 9 }} width={140} />
                  <Tooltip formatter={v=>[v.toLocaleString(),'Patients']} />
                  <Bar dataKey="total" radius={[0,4,4,0]}>
                    {segs.map((_,i)=><Cell key={i} fill={COLORS[i%COLORS.length]}/>)}
                  </Bar>
                </BarChart>
              </ResponsiveContainer>
            </ChartCard>

            <ChartCard title="Adoption Rate by Segment">
              <ResponsiveContainer width="100%" height={250}>
                <BarChart data={segs} layout="vertical" margin={{ left: 10 }}>
                  <CartesianGrid strokeDasharray="3 3" horizontal={false} />
                  <XAxis type="number" domain={[0,100]} tickFormatter={v=>`${v}%`} tick={{ fontSize: 10 }} />
                  <YAxis type="category" dataKey="segment" tick={{ fontSize: 9 }} width={140} />
                  <Tooltip formatter={v=>[`${v}%`,'Adoption Rate']} />
                  <Bar dataKey="adoption_rate" radius={[0,4,4,0]}>
                    {segs.map((_,i)=><Cell key={i} fill={COLORS[i%COLORS.length]}/>)}
                  </Bar>
                </BarChart>
              </ResponsiveContainer>
            </ChartCard>
          </div>

          {/* Table */}
          <ChartCard title="Segment Summary Table">
            <div className="table-wrap">
              <table>
                <thead>
                  <tr>
                    <th>Segment</th>
                    <th>Total Patients</th>
                    <th>Adopted</th>
                    <th>Untreated</th>
                    <th>Adoption Rate</th>
                    <th>Continuation Rate</th>
                    <th>Priority</th>
                  </tr>
                </thead>
                <tbody>
                  {segs.map(s => (
                    <tr key={s.segment}>
                      <td style={{ fontWeight: 600 }}>{s.segment}</td>
                      <td>{s.total.toLocaleString()}</td>
                      <td>{s.adopted.toLocaleString()}</td>
                      <td>{s.untreated.toLocaleString()}</td>
                      <td>
                        <strong>{s.adoption_rate}%</strong>
                        <div style={{ background: '#e2e8f0', borderRadius: 99, height: 4, marginTop: 4 }}>
                          <div style={{ background: '#2563eb', borderRadius: 99, height: 4, width: `${s.adoption_rate}%` }} />
                        </div>
                      </td>
                      <td>{s.continuation_rate != null ? `${s.continuation_rate}%` : '—'}</td>
                      <td><span className={`badge ${segBadge(s.segment)}`}>
                        {s.segment.includes('High-Need') && s.segment.includes('High-Ability') ? 'Priority' :
                         s.segment.includes('High-Need') && s.segment.includes('Low-Ability')  ? 'Support Needed' :
                         s.segment.includes('High-Need')                                        ? 'Moderate' : 'Standard'}
                      </span></td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          </ChartCard>

          {/* Interpretation */}
          <div className="card">
            <div className="card-title">Business Interpretation</div>
            <div className="insights-grid">
              {segs.filter(s=>s.segment.includes('High-Need')&&s.segment.includes('High-Ability')).map(s=>(
                <div className="insight-card" key={s.segment}>
                  <h4>✅ High-Need / High-Ability</h4>
                  <p>Highest adoption at <strong>{s.adoption_rate}%</strong>. These patients have
                  both the clinical need and financial ability. Physician engagement is the key lever.</p>
                </div>
              ))}
              {segs.filter(s=>s.segment.includes('High-Need')&&s.segment.includes('Low-Ability')).map(s=>(
                <div className="insight-card" key={s.segment}>
                  <h4>⚠ High-Need / Low-Ability</h4>
                  <p>Only <strong>{s.adoption_rate}%</strong> adoption despite high clinical need.
                  <strong> {s.untreated.toLocaleString()}</strong> untreated patients need affordability support.</p>
                </div>
              ))}
              {segs.filter(s=>s.segment.includes('Low-Need')&&s.segment.includes('Low-Ability')).map(s=>(
                <div className="insight-card" key={s.segment}>
                  <h4>📉 Low-Need / Low-Ability</h4>
                  <p>Lowest adoption at <strong>{s.adoption_rate}%</strong>. Lower clinical urgency
                  combined with financial barriers results in the lowest treatment rates.</p>
                </div>
              ))}
            </div>
          </div>
        </>
      )}
    </div>
  );
}
