import { useState, useEffect } from 'react';
import { api } from '../api/analyticsApi';
import ChartCard from '../components/ChartCard';
import KPICard from '../components/KPICard';
import { LoadingState, ErrorState } from '../components/LoadingState';
import {
  BarChart, Bar, XAxis, YAxis, CartesianGrid, Tooltip,
  ResponsiveContainer, Cell, ReferenceLine
} from 'recharts';

export default function ModelInsights() {
  const [data, setData]       = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError]     = useState(null);

  useEffect(() => {
    api.modelInsights().then(setData).catch(e=>setError(e.message)).finally(()=>setLoading(false));
  }, []);

  const m = data?.metrics ?? {};

  return (
    <div>
      <div className="page-header">
        <h2>Treatment Adoption Model</h2>
        <p>
          We used a simple Logistic Regression model to identify factors <em>associated with</em> treatment adoption.
          This is for pattern discovery, not clinical prediction.
        </p>
      </div>

      {loading && <LoadingState />}
      {!loading && error && <ErrorState message={error} />}

      {!loading && !error && data && (
        <>
          {/* Metrics KPIs */}
          <div className="kpi-grid">
            <KPICard label="ROC-AUC"   value={m['ROC-AUC']}  sub="Discrimination ability" color="blue"  />
            <KPICard label="Accuracy"  value={m['Accuracy']}  sub="Overall correct"        color="green" />
            <KPICard label="Precision" value={m['Precision']} sub="Of predicted adopters"  color="cyan"  />
            <KPICard label="Recall"    value={m['Recall']}    sub="Actual adopters found"  color="amber" />
            <KPICard label="F1 Score"  value={m['F1 Score']}  sub="Precision-recall balance" />
          </div>

          {/* Coefficients chart */}
          {data.coefficients?.length > 0 && (
            <ChartCard title="Factors Associated with Treatment Adoption (Logistic Regression Coefficients)">
              <p style={{ fontSize: '.8rem', color: '#64748b', marginBottom: '1rem' }}>
                Positive = more associated with starting treatment · Negative = less associated
              </p>
              <ResponsiveContainer width="100%" height={340}>
                <BarChart
                  data={data.coefficients}
                  layout="vertical"
                  margin={{ left: 10, right: 40 }}
                >
                  <CartesianGrid strokeDasharray="3 3" horizontal={false} />
                  <XAxis type="number" tick={{ fontSize: 10 }}
                    label={{ value: 'Coefficient (standardised)', position: 'insideBottom', offset: -2, fontSize: 10 }} />
                  <YAxis type="category" dataKey="feature" tick={{ fontSize: 11 }} width={160} />
                  <Tooltip formatter={v=>[v.toFixed(4),'Coefficient']} />
                  <ReferenceLine x={0} stroke="#94a3b8" strokeWidth={1.5} />
                  <Bar dataKey="coefficient" radius={[0,4,4,0]}>
                    {data.coefficients.map((d,i)=>(
                      <Cell key={i} fill={d.coefficient >= 0 ? '#2563eb' : '#dc2626'} />
                    ))}
                  </Bar>
                </BarChart>
              </ResponsiveContainer>
            </ChartCard>
          )}

          {/* Model explanation */}
          <div className="card">
            <div className="card-title">How to Interpret This Model</div>
            <div className="insights-grid">
              <div className="insight-card">
                <h4>📊 What is Logistic Regression?</h4>
                <p>A simple statistical model that estimates the probability of a yes/no outcome —
                here, whether a patient starts treatment. Each factor gets a weight (coefficient).</p>
              </div>
              <div className="insight-card">
                <h4>➕ Positive Coefficients</h4>
                <p>Factors like <strong>Physician Recommendation</strong> and <strong>Insurance</strong> have
                positive coefficients — patients with these factors are more likely to start treatment.</p>
              </div>
              <div className="insight-card">
                <h4>➖ Negative Coefficients</h4>
                <p>Factors like <strong>Side Effect Concern</strong> have negative coefficients —
                higher concern is associated with lower probability of starting treatment.</p>
              </div>
              <div className="insight-card">
                <h4>⚠ Important Caveat</h4>
                <p>{data.note}</p>
              </div>
            </div>
          </div>

          <div className="disclaimer-box" style={{ marginTop: '1rem' }}>
            <strong>Model Disclaimer:</strong> This model is trained on synthetic data for educational
            purposes only. The ROC-AUC of {m['ROC-AUC']} indicates the model is better than random
            guessing, but not sufficient for real clinical use. All findings are associative, not causal.
          </div>
        </>
      )}
    </div>
  );
}
