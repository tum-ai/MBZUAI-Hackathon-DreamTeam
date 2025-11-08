import { Routes, Route } from 'react-router-dom'
import CreateProject from '../screens/CreateProject'
import TemplateSelection from '../screens/TemplateSelection'
import CanvasEditor from '../screens/CanvasEditor'

function AppRouter() {
  return (
    <Routes>
      <Route path="/" element={<CreateProject />} />
      <Route path="/templates" element={<TemplateSelection />} />
      <Route path="/editor/:projectId?" element={<CanvasEditor />} />
    </Routes>
  )
}

export default AppRouter

