import { useState } from 'react';
import Sidebar from './components/Sidebar';
import Overview from './pages/Overview';
import PatientJourney from './pages/PatientJourney';
import TreatmentAdoption from './pages/TreatmentAdoption';
import Segments from './pages/Segments';
import MarketOpportunity from './pages/MarketOpportunity';
import ModelInsights from './pages/ModelInsights';
import About from './pages/About';

const PAGES = {
  overview: Overview,
  journey:  PatientJourney,
  adoption: TreatmentAdoption,
  segments: Segments,
  market:   MarketOpportunity,
  model:    ModelInsights,
  about:    About,
};

export default function App() {
  const [page, setPage] = useState('overview');
  const Page = PAGES[page] ?? Overview;

  return (
    <div className="app-shell">
      <Sidebar page={page} setPage={setPage} />
      <main className="main-content">
        <Page />
      </main>
    </div>
  );
}
