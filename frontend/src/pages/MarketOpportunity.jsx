import { useState, useEffect } from 'react';
import { api } from '../api/analyticsApi';
import ChartCard from '../components/ChartCard';
import { LoadingState, ErrorState } from '../components/LoadingState';
import {
  BarChart, Bar, XAxis, YAxis, CartesianGrid, Tooltip,
  ResponsiveContainer, Cell
} from 'recharts';

const COLORS = ['#dc2626','#d97706','#2563eb','#0891b2','#059669'];

export default function MarketOpportunity() {
  const [data, setData]     = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError]   = useState(null);

  useEffect(() => {
    api.marketOpp().then(setData).catch(e=>setError(e.message)).finally(()=>setLoading(false));
  }, []);

  const top = data?.regions?.[0];
  const sorted = data ? [...data.regions].sort((a,b)=>b.opportunity_score - a.opportunity_score) : [];

  return (
    <div>
      <div className="page-header">
        <h2>Market Opportunity</h2>
        <p>Identify regions where patient need and adoption gaps indicate the greatest commercial potential.</p>
      </div>

      {loading && <LoadingState />}
      {!loading && error && <ErrorState message={error} />}

      {!loading && !error && data && (
        <>
          {/* Top opportunity card */}
          {top && (
            <div className="highlight-card" style={{ marginBottom: '1.5rem' }}>
              <h3>🏆 Highest Opportunity Region: {top.region}</h3>
              <p>This region has the highest combination of untreated patient volume and adoption gap.</p>
              <div className="highlight-stats">
                <div className="highlight-stat">
                  <div className="hs-label">Untreated Patients</div>
                  <div className="hs-val">{top.untreated_patients.toLocaleString()}</div>
                </div>
                <div className="highlight-stat">
                  <div className="hs-label">Adoption Rate</div>
                  <div className="hs-val">{top.adoption_rate}%</div>
                </div>
                <div className="highlight-stat">
                  <div className="hs-label">Adoption Gap</div>
                  <div className="hs-val">{top.adoption_gap}%</div>
                </div>
                <div className="highlight-stat">
                  <div className="hs-label">Opportunity Score</div>
                  <div className="hs-val">{top.opportunity_score}</div>
                </div>
              </div>
            </div>
          )}

          <div className="charts-grid-2">
            <ChartCard title="Opportunity Score by Region (Higher = More Opportunity)">
              <ResponsiveContainer width="100%" height={250}>
                <BarChart data={sorted}>
                  <CartesianGrid strokeDasharray="3 3" vertical={false} />
                  <XAxis dataKey="region" tick={{ fontSize: 11 }} />
                  <YAxis domain={[0,1]} tick={{ fontSize: 11 }} />
                  <Tooltip formatter={v=>[v.toFixed(4),'Opportunity Score']} />
                  <Bar dataKey="opportunity_score" radius={[4,4,0,0]}>
                    {sorted.map((_,i)=><Cell key={i} fill={COLORS[i%COLORS.length]}/>)}
                  </Bar>
                </BarChart>
              </ResponsiveContainer>
            </ChartCard>

            <ChartCard title="Untreated Patients by Region">
              <ResponsiveContainer width="100%" height={250}>
                <BarChart data={[...data.regions].sort((a,b)=>b.untreated_patients-a.untreated_patients)}>
                  <CartesianGrid strokeDasharray="3 3" vertical={false} />
                  <XAxis dataKey="region" tick={{ fontSize: 11 }} />
                  <YAxis tick={{ fontSize: 11 }} />
                  <Tooltip formatter={v=>[v.toLocaleString(),'Untreated Patients']} />
                  <Bar dataKey="untreated_patients" radius={[4,4,0,0]}>
                    {data.regions.map((_,i)=><Cell key={i} fill={COLORS[i%COLORS.length]}/>)}
                  </Bar>
                </BarChart>
              </ResponsiveContainer>
            </ChartCard>
          </div>

          <ChartCard title="Adoption Gap by Region (% of patients not yet treated)">
            <ResponsiveContainer width="100%" height={200}>
              <BarChart data={[...data.regions].sort((a,b)=>b.adoption_gap - a.adoption_gap)}>
                <CartesianGrid strokeDasharray="3 3" vertical={false} />
                <XAxis dataKey="region" tick={{ fontSize: 11 }} />
                <YAxis domain={[0,100]} tickFormatter={v=>`${v}%`} tick={{ fontSize: 11 }} />
                <Tooltip formatter={v=>[`${v}%`,'Adoption Gap']} />
                <Bar dataKey="adoption_gap" radius={[4,4,0,0]}>
                  {data.regions.map((_,i)=><Cell key={i} fill={COLORS[i%COLORS.length]}/>)}
                </Bar>
              </BarChart>
            </ResponsiveContainer>
          </ChartCard>

          {/* Table */}
          <ChartCard title="Regional Market Opportunity Summary">
            <div className="table-wrap">
              <table>
                <thead>
                  <tr>
                    <th>Rank</th><th>Region</th><th>Total Patients</th>
                    <th>Treated</th><th>Untreated</th>
                    <th>Adoption %</th><th>Gap %</th><th>Opp. Score</th>
                  </tr>
                </thead>
                <tbody>
                  {sorted.map((r,i)=>(
                    <tr key={r.region}>
                      <td><strong>#{i+1}</strong></td>
                      <td style={{fontWeight:600}}>{r.region}</td>
                      <td>{r.total_patients.toLocaleString()}</td>
                      <td>{r.treated_patients.toLocaleString()}</td>
                      <td>{r.untreated_patients.toLocaleString()}</td>
                      <td>{r.adoption_rate}%</td>
                      <td>{r.adoption_gap}%</td>
                      <td>
                        <span className={`badge ${i===0?'badge-red':i===1?'badge-amber':'badge-blue'}`}>
                          {r.opportunity_score.toFixed(3)}
                        </span>
                      </td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          </ChartCard>
        </>
      )}
    </div>
  );
}
