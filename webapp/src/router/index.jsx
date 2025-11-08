import { Routes, Route } from 'react-router-dom'
import CreateProject from '../screens/CreateProject'
import TemplateSelection from '../screens/TemplateSelection'

function AppRouter() {
  return (
    <Routes>
      <Route path="/" element={<CreateProject />} />
      <Route path="/templates" element={<TemplateSelection />} />
    </Routes>
  )
}

export default AppRouter

