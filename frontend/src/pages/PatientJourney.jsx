import { useState, useEffect } from 'react';
import { api } from '../api/analyticsApi';
import ChartCard from '../components/ChartCard';
import FiltersBar, { DEFAULTS } from '../components/FiltersBar';
import { LoadingState, ErrorState } from '../components/LoadingState';

export default function PatientJourney() {
  const [filters, setFilters] = useState(DEFAULTS);
  const [data, setData]       = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError]     = useState(null);

  useEffect(() => {
    setLoading(true); setError(null);
    api.patientJourney(filters)
      .then(setData).catch(e => setError(e.message)).finally(() => setLoading(false));
  }, [filters]);

  const maxPatients = data?.stages?.[0]?.patients ?? 1;

  return (
    <div>
      <div className="page-header">
        <h2>Patient Journey</h2>
        <p>Understand where patients progress or drop off across the treatment journey.</p>
      </div>

      <FiltersBar filters={filters} setFilters={setFilters} />

      {loading && <LoadingState />}
      {!loading && error && <ErrorState message={error} />}

      {!loading && !error && data && (
        <>
          {/* Biggest drop-off highlight */}
          {data.biggest_dropoff && (
            <div className="highlight-card">
              <h3>⚠ Largest Drop-off Identified</h3>
              <p>The biggest loss of patients occurs at the <strong>&quot;{data.biggest_dropoff.stage}&quot;</strong> stage.</p>
              <div className="highlight-stats">
                <div className="highlight-stat">
                  <div className="hs-label">Patients Lost</div>
                  <div className="hs-val">{data.biggest_dropoff.dropoff_pct}%</div>
                </div>
                <div className="highlight-stat">
                  <div className="hs-label">Patients at Stage</div>
                  <div className="hs-val">{data.biggest_dropoff.patients?.toLocaleString()}</div>
                </div>
              </div>
            </div>
          )}

          {/* Funnel visualization */}
          <ChartCard title="Patient Journey Funnel">
            <div className="funnel-grid">
              <div className="funnel-row header">
                <span>Stage</span>
                <span>% of All Patients</span>
                <span style={{ textAlign: 'right' }}>Patients</span>
                <span style={{ textAlign: 'right' }}>Drop-off</span>
              </div>
              {data.stages.map((s, i) => {
                const isBig = s.stage === data.biggest_dropoff?.stage;
                return (
                  <div key={s.stage} className={`funnel-row ${isBig ? 'biggest-drop' : ''}`}>
                    <span className="funnel-stage-name">
                      {isBig ? '🔴 ' : `${i + 1}. `}{s.stage}
                    </span>
                    <div className="funnel-bar-wrap">
                      <div
                        className={`funnel-bar ${isBig ? 'drop' : ''}`}
                        style={{ width: `${(s.patients / maxPatients) * 100}%` }}
                      />
                    </div>
                    <span className="funnel-num">{s.patients.toLocaleString()}</span>
                    <span className="funnel-pct" style={{ color: s.dropoff_pct > 0 ? '#dc2626' : '#64748b' }}>
                      {i === 0 ? '—' : `-${s.dropoff_pct}%`}
                    </span>
                  </div>
                );
              })}
            </div>
          </ChartCard>

          {/* Table */}
          <ChartCard title="Stage-by-Stage Detail">
            <div className="table-wrap">
              <table>
                <thead>
                  <tr>
                    <th>Stage</th>
                    <th>Patients</th>
                    <th>% of Diagnosed</th>
                    <th>Drop-off %</th>
                    <th>Status</th>
                  </tr>
                </thead>
                <tbody>
                  {data.stages.map((s, i) => {
                    const isBig = s.stage === data.biggest_dropoff?.stage;
                    return (
                      <tr key={s.stage}>
                        <td style={{ fontWeight: 600 }}>{s.stage}</td>
                        <td>{s.patients.toLocaleString()}</td>
                        <td>{s.conversion_pct}%</td>
                        <td style={{ color: s.dropoff_pct > 40 ? '#dc2626' : 'inherit', fontWeight: s.dropoff_pct > 40 ? 700 : 400 }}>
                          {i === 0 ? '—' : `-${s.dropoff_pct}%`}
                        </td>
                        <td>
                          {isBig
                            ? <span className="badge badge-red">Biggest Drop-off</span>
                            : s.dropoff_pct > 40
                              ? <span className="badge badge-amber">High Loss</span>
                              : <span className="badge badge-green">OK</span>
                          }
                        </td>
                      </tr>
                    );
                  })}
                </tbody>
              </table>
            </div>
          </ChartCard>

          {/* Interpretation */}
          <div className="card">
            <div className="card-title">Business Interpretation</div>
            <div className="insights-grid">
              <div className="insight-card">
                <h4>📌 Where to Focus</h4>
                <p>The <strong>&quot;{data.biggest_dropoff?.stage}&quot;</strong> stage has the highest drop-off.
                Targeted interventions at this step could have the largest impact on overall adoption.</p>
              </div>
              <div className="insight-card">
                <h4>📊 Overall Completion</h4>
                <p>Only <strong>{data.stages[data.stages.length - 1]?.conversion_pct}%</strong> of
                diagnosed patients complete the entire journey through follow-up.</p>
              </div>
              <div className="insight-card">
                <h4>💡 Key Implication</h4>
                <p>Even patients who start treatment often do not continue — continuation and
                follow-up rates need dedicated patient support programmes.</p>
              </div>
            </div>
          </div>
        </>
      )}
    </div>
  );
}
