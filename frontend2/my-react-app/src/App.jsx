import './App.css'
import Login from './Login.jsx'
import MainPage from './MainPage.jsx';
import { BrowserRouter as Router, Routes, Route } from 'react-router-dom';
function App() {
  return (
<Router>
      <div className="app">
        <Routes>
          {/* Start at the Login page */}
          <Route path="/" element={<Login />} />
          
          {/* Navigate to the Main page */}
          <Route path="/main" element={<MainPage />} />
        </Routes>
      </div>
    </Router>
  );
}

export default App;