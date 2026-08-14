import SimulationPage from './pages/SimulationPage';
import SimulationHistory from './components/SimulationHistory';
import AuthGate from './components/AuthGate';
import AdminPanel from './components/AdminPanel';

function App() {
  return <AuthGate><div className="app-shell"><aside className="sidebar"><div className="brand-mark"><span>◈</span><div><strong>FocusGroup</strong><small>AI Research Studio</small></div></div><nav><a className="nav-item nav-item--active" href="#simulation"><span>✦</span> 새 시뮬레이션</a><a className="nav-item" href="#history"><span>◷</span> 시뮬레이션 이력</a><a className="nav-item" href="#insights"><span>◌</span> 인사이트</a><a className="nav-item" href="#admin"><span>▦</span> 관리자 대시보드</a></nav><div className="sidebar-footer"><span className="online-dot" /> AI 엔진 연결됨</div></aside><div className="app-content"><header className="topbar"><div><span className="breadcrumb">Workspace /</span><strong>AI Simulation Focus Group</strong></div><div className="topbar-status"><span className="online-dot" /> Live workspace</div></header><div id="simulation"><SimulationPage /></div><main className="container" id="history"><SimulationHistory /><div id="admin"><AdminPanel /></div></main></div></div></AuthGate>;
}

export default App;
