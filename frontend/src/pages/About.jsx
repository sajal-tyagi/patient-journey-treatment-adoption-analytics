const TECH = ['Python','Pandas','NumPy','Scikit-learn','FastAPI','Uvicorn',
              'React','Vite','JavaScript','Recharts','SQL','Power BI'];

const WORKFLOW = [
  { step: '1', label: 'Patient Data',        desc: 'Synthetic CSV dataset (25,000 patients)' },
  { step: '2', label: 'Python Analytics',    desc: 'Data cleaning, EDA, segmentation, modelling' },
  { step: '3', label: 'Results & Charts',    desc: 'CSV result tables + PNG charts' },
  { step: '4', label: 'FastAPI Backend',     desc: 'REST API endpoints serving JSON' },
  { step: '5', label: 'React Frontend',      desc: 'Interactive dashboard consuming the API' },
  { step: '6', label: 'Interactive Dashboard', desc: 'Visual analytics accessible via browser' },
];

export default function About() {
  return (
    <div>
      <div className="page-header">
        <h2>About This Project</h2>
        <p>Patient Journey &amp; Treatment Adoption Analytics — an end-to-end portfolio project.</p>
      </div>

      <div className="about-section">
        <div className="card">
          <div className="card-title">Project Overview</div>
          <p>
            This project analyses a synthetic dataset of <strong>25,000 patients</strong> to understand
            why patients do or do not start <strong>Therapy X</strong> — a fictional treatment by
            fictional company <strong>NovaCure Pharmaceuticals</strong>. The project covers the complete
            analytics lifecycle from data generation to an interactive web dashboard.
          </p>
        </div>
      </div>

      <div className="about-section">
        <div className="card">
          <div className="card-title">Business Problem</div>
          <p>
            Despite Therapy X being available, only <strong>43.3%</strong> of diagnosed patients ever
            start treatment. The company needs to understand:
          </p>
          <ul style={{ marginTop: '.6rem' }}>
            <li>Where patients drop off in the treatment journey</li>
            <li>Which patient groups have higher or lower adoption</li>
            <li>What factors are most associated with treatment initiation</li>
            <li>Which regions have the highest untreated patient populations</li>
            <li>What the company should prioritise to improve adoption</li>
          </ul>
        </div>
      </div>

      <div className="about-section">
        <div className="card">
          <div className="card-title">Full-Stack Architecture</div>
          <div style={{ display: 'flex', flexWrap: 'wrap', alignItems: 'center', gap: '.5rem', padding: '.5rem 0' }}>
            {WORKFLOW.map((w, i) => (
              <div key={w.step} style={{ display: 'flex', alignItems: 'center', gap: '.5rem' }}>
                <div style={{
                  background: '#dbeafe', border: '1px solid #93c5fd',
                  borderRadius: 8, padding: '.5rem .85rem', minWidth: 120, textAlign: 'center'
                }}>
                  <div style={{ fontSize: '.65rem', color: '#1d4ed8', fontWeight: 700, textTransform: 'uppercase' }}>
                    Step {w.step}
                  </div>
                  <div style={{ fontSize: '.82rem', fontWeight: 600, color: '#1e3a8a' }}>{w.label}</div>
                  <div style={{ fontSize: '.7rem', color: '#3b82f6', marginTop: 2 }}>{w.desc}</div>
                </div>
                {i < WORKFLOW.length - 1 && (
                  <span style={{ color: '#93c5fd', fontSize: '1.2rem', fontWeight: 700 }}>→</span>
                )}
              </div>
            ))}
          </div>
        </div>
      </div>

      <div className="about-section">
        <div className="card">
          <div className="card-title">Technology Stack</div>
          <div className="tech-tags">
            {TECH.map(t => <span key={t} className="tech-tag">{t}</span>)}
          </div>
        </div>
      </div>

      <div className="about-section">
        <div className="card">
          <div className="card-title">Analytical Approach</div>
          <ul>
            <li><strong>Patient Journey:</strong> Funnel analysis from diagnosis to follow-up</li>
            <li><strong>Segmentation:</strong> Rule-based segments by clinical need × financial ability</li>
            <li><strong>Adoption Analysis:</strong> Group comparisons across 7 dimensions</li>
            <li><strong>Logistic Regression:</strong> Identifies factors associated with treatment initiation</li>
            <li><strong>Market Opportunity:</strong> Composite score from untreated volume + adoption gap</li>
            <li><strong>SQL:</strong> 20 business queries for additional analytical depth</li>
          </ul>
        </div>
      </div>

      <div className="disclaimer-box">
        <strong>⚠ Synthetic Data Disclaimer</strong><br /><br />
        This project uses synthetic data created for analytical and educational purposes only.
        It does not represent real patients, real clinical outcomes, medical advice, or actual
        pharmaceutical market data. All company names, drug names, and patient data are entirely
        fictional. Any resemblance to real persons, companies, or clinical situations is purely
        coincidental. This project is a portfolio demonstration and should not be used to inform
        real clinical or business decisions.
      </div>
    </div>
  );
}
