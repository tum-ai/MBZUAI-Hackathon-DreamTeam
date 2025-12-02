import { Routes, Route } from 'react-router-dom'
import CreateProject from '../screens/CreateProject'
import TemplateSelection from '../screens/TemplateSelection'
import Workspace from '../screens/Workspace'

function AppRouter() {
  return (
    <Routes>
      <Route path="/" element={<CreateProject />} />
      <Route path="/templates" element={<TemplateSelection />} />
      <Route path="/workspace" element={<Workspace />} />
    </Routes>
  )
}

export default AppRouter

