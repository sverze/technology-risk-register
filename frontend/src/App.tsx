import { BrowserRouter as Router, Routes, Route } from 'react-router-dom';
import { MainLayout } from '@/layouts/MainLayout';
import { Dashboard } from '@/pages/Dashboard';
import { RiskList } from '@/pages/RiskList';
import { AddRisk } from '@/pages/AddRisk';

function App() {
  return (
    <Router>
      <MainLayout>
        <Routes>
          <Route path="/" element={<Dashboard />} />
          <Route path="/risks" element={<RiskList />} />
          <Route path="/risks/new" element={<AddRisk />} />
        </Routes>
      </MainLayout>
    </Router>
  );
}

export default App
