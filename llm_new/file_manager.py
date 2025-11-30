"""
File Manager for managing Vue files in session projects.
Handles creating/editing pages, components, and router updates.
"""
import re
import logging
import aiofiles
from pathlib import Path
from typing import Optional, List
from llm_new.session_manager import SessionManager

logger = logging.getLogger(__name__)


class FileManager:
    """
    Manages Vue file operations for session projects.
    Writes .vue files and triggers Vite HMR automatically.
    """
    
    def __init__(self, session_manager: SessionManager):
        self.session_manager = session_manager
    
    async def write_view(self, session_id: str, page_name: str, vue_code: str):
        """
        Write or update a view page file.
        
        Args:
            session_id: Session identifier
            page_name: Name of the page (e.g., "Home", "Pricing")
            vue_code: Complete Vue SFC code
        """
        session = self.session_manager.get_session(session_id)
        if not session:
            raise ValueError(f"Session {session_id} not found")
        
        # Sanitize page name (PascalCase)
        safe_name = page_name.replace(' ', '').replace('-', '').capitalize()
        filename = f"{safe_name}.vue"
        
        # Write to views directory
        file_path = session.project_path / "src" / "views" / filename
        file_path.parent.mkdir(parents=True, exist_ok=True)
        
        async with aiofiles.open(file_path, 'w', encoding='utf-8') as f:
            await f.write(vue_code)
        
        # Track file creation
        relative_path = str(file_path.relative_to(session.project_path))
        if relative_path not in session.files_created:
            session.files_created.append(relative_path)
        
        logger.info(f"[FileManager] Wrote view: {filename} for session {session_id}")
        
        # Vite HMR will automatically reload!
        return file_path
    
    async def read_view(self, session_id: str, page_name: str) -> Optional[str]:
        """Read content of a view page"""
        session = self.session_manager.get_session(session_id)
        if not session:
            return None
        
        safe_name = page_name.replace(' ', '').replace('-', '').capitalize()
        file_path = session.project_path / "src" / "views" / f"{safe_name}.vue"
        
        if not file_path.exists():
            return None
        
        async with aiofiles.open(file_path, 'r', encoding='utf-8') as f:
            return await f.read()
    
    async def create_new_page(
        self,
        session_id: str,
        page_name: str,
        vue_code: str
    ):
        """
        Create a brand new page: view file + router entry + nav links.
        
        Args:
            session_id: Session identifier
            page_name: Name of page (e.g., "About")
            vue_code: Complete Vue SFC for the page
        """
        logger.info(f"[FileManager] Creating new page: {page_name} for session {session_id}")
        
        # Step 1: Write view file
        await self.write_view(session_id, page_name, vue_code)
        
        # Step 2: Add route to router
        await self.add_route_to_router(session_id, page_name)
        
        # Step 3: Add nav links to existing pages
        await self.add_nav_link_to_pages(session_id, page_name)
        
        # Track page creation
        session = self.session_manager.get_session(session_id)
        if page_name not in session.pages_created:
            session.pages_created.append(page_name)
        
        logger.info(f"[FileManager] Page '{page_name}' created successfully")
    
    async def add_route_to_router(self, session_id: str, page_name: str):
        """
        Add a new route to router/index.js
        """
        session = self.session_manager.get_session(session_id)
        router_path = session.project_path / "src" / "router" / "index.js"
        
        # Read current router
        async with aiofiles.open(router_path, 'r', encoding='utf-8') as f:
            router_content = await f.read()
        
        # Generate import and route
        safe_name = page_name.replace(' ', '').replace('-', '').capitalize()
        path = f"/{page_name.lower().replace(' ', '-')}"
        
        import_line = f"import {safe_name} from '../views/{safe_name}.vue'"
        route_entry = f"""  {{
    path: '{path}',
    name: '{safe_name}',
    component: {safe_name}
  }}"""
        
        # Add import after existing imports
        import_section_end = router_content.rfind("from '../views/")
        if import_section_end != -1:
            # Find end of that line
            line_end = router_content.find('\n', import_section_end)
            router_content = (
                router_content[:line_end + 1] +
                import_line + '\n' +
                router_content[line_end + 1:]
            )
        
        # Add route to routes array (before closing bracket)
        routes_end = router_content.rfind(']')
        if routes_end != -1:
            # Add comma if there are existing routes
            router_content = (
                router_content[:routes_end].rstrip() + ',\n' +
                route_entry + '\n' +
                router_content[routes_end:]
            )
        
        # Write updated router
        async with aiofiles.open(router_path, 'w', encoding='utf-8') as f:
            await f.write(router_content)
        
        logger.info(f"[FileManager] Added route '{path}' to router")
    
    async def add_nav_link_to_pages(self, session_id: str, page_name: str):
        """
        Add navigation link to all existing pages
        """
        session = self.session_manager.get_session(session_id)
        views_dir = session.project_path / "src" / "views"
        
        safe_name = page_name.replace(' ', '').replace('-', '').capitalize()
        path = f"/{page_name.lower().replace(' ', '-')}"
        
        # Process each view file
        for view_file in views_dir.glob("*.vue"):
            if view_file.stem == safe_name:
                continue  # Skip the newly created page
            
            async with aiofiles.open(view_file, 'r', encoding='utf-8') as f:
                content = await f.read()
            
            # Find nav section and add link
            # Look for router-link pattern
            nav_link = f'<router-link to="{path}" class="text-gray-400 hover:text-white transition">{page_name}</router-link>'
            
            # Insert before the "Get Started" button or closing </div>
            pattern = r'(<router-link[^>]*>Pricing</router-link>\s*</div>)'
            
            if re.search(pattern, content):
                replacement = f'{nav_link}\n          </div>'
                content = re.sub(
                    r'(</router-link>\s*)(</div>\s*<button)',
                    f'\\1\n          {nav_link}\n          \\2',
                    content,
                    count=1
                )
            
            async with aiofiles.open(view_file, 'w', encoding='utf-8') as f:
                await f.write(content)
        
        logger.info(f"[FileManager] Added nav links for '{page_name}'")
    
    async def write_component(self, session_id: str, component_name: str, vue_code: str):
        """
        Write a reusable component to components/ directory
        """
        session = self.session_manager.get_session(session_id)
        if not session:
            raise ValueError(f"Session {session_id} not found")
        
        safe_name = component_name.replace(' ', '').replace('-', '').capitalize()
        filename = f"{safe_name}.vue"
        
        file_path = session.project_path / "src" / "components" / filename
        file_path.parent.mkdir(parents=True, exist_ok=True)
        
        async with aiofiles.open(file_path, 'w', encoding='utf-8') as f:
            await f.write(vue_code)
        
        relative_path = str(file_path.relative_to(session.project_path))
        if relative_path not in session.files_created:
            session.files_created.append(relative_path)
        
        logger.info(f"[FileManager] Wrote component: {filename}")
        return file_path
    
    async def list_pages(self, session_id: str) -> List[str]:
        """List all pages in a session"""
        session = self.session_manager.get_session(session_id)
        if not session:
            return []
        
        return session.pages_created
    
    async def delete_page(self, session_id: str, page_name: str):
        """Delete a page (view file, router entry, nav links)"""
        session = self.session_manager.get_session(session_id)
        if not session:
            raise ValueError(f"Session {session_id} not found")
        
        safe_name = page_name.replace(' ', '').replace('-', '').capitalize()
        
        # Delete view file
        view_path = session.project_path / "src" / "views" / f"{safe_name}.vue"
        if view_path.exists():
            view_path.unlink()
        
        # Remove from router (simplified - would need proper parsing)
        # Remove from pages_created
        if page_name in session.pages_created:
            session.pages_created.remove(page_name)
        
        logger.info(f"[FileManager] Deleted page: {page_name}")
