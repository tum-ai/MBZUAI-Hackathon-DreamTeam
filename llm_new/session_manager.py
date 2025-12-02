"""
Session Manager for Vite project lifecycle.
Manages per-user Vite projects, port allocation, and cleanup.
"""
import asyncio
import shutil
import subprocess
import logging
from dataclasses import dataclass, field
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional, Set
import sys
import os

logger = logging.getLogger(__name__)


@dataclass
class SessionInfo:
    """Information about a user's Vite session"""
    session_id: str
    project_path: Path
    vite_port: int
    vite_process: Optional[subprocess.Popen]
    created_at: datetime
    last_active: datetime
    files_created: List[str] = field(default_factory=list)
    pages_created: List[str] = field(default_factory=list)  # Track created pages


class SessionManager:
    """
    Manages Vite project sessions for concurrent users.
    Each session gets its own Vite project and dev server.
    """
    
    def __init__(
        self,
        base_dir: Path = Path("/tmp/vite-sessions"),
        template_dir: Path = None,
        port_range: tuple = (3000, 4000),
        max_sessions: int = 50
    ):
        self.base_dir = Path(base_dir)
        self.template_dir = template_dir or Path(__file__).parent / "templates" / "vite-vue-base"
        self.port_range = port_range
        self.max_sessions = max_sessions
        
        self.sessions: Dict[str, SessionInfo] = {}
        self.allocated_ports: Set[int] = set()
        
        # Determine npm command based on OS
        self.npm_cmd = "npm.cmd" if sys.platform == "win32" else "npm"
        
        # Create base directory
        self.base_dir.mkdir(parents=True, exist_ok=True)
        
        logger.info(f"[SessionManager] Initialized with base_dir={self.base_dir}, port_range={self.port_range}")
    
    async def create_session(self, session_id: str) -> SessionInfo:
        """
        Create a new Vite project and start dev server.
        
        Args:
            session_id: Unique session identifier
            
        Returns:
            SessionInfo with project details and Vite server info
        """
        if session_id in self.sessions:
            logger.warning(f"[SessionManager] Session {session_id} already exists")
            return self.sessions[session_id]
        
        if len(self.sessions) >= self.max_sessions:
            raise RuntimeError(f"Maximum sessions ({self.max_sessions}) reached")
        
        logger.info(f"[SessionManager] Creating session: {session_id}")
        
        # Create project directory
        project_path = self.base_dir / f"session-{session_id}"
        project_path.mkdir(parents=True, exist_ok=True)
        
        try:
            # Copy template files
            await self._copy_template(project_path)
            
            # Install dependencies
            await self._install_dependencies(project_path)
            
            # Allocate port
            vite_port = self._get_available_port()
            self.allocated_ports.add(vite_port)
            logger.info(f"[SessionManager] Allocated port {vite_port} for session {session_id}")
            
            try:
                # Start Vite dev server
                vite_process = await self._start_vite_server(project_path, vite_port)
                
                # Create session info
                session_info = SessionInfo(
                    session_id=session_id,
                    project_path=project_path,
                    vite_port=vite_port,
                    vite_process=vite_process,
                    created_at=datetime.now(),
                    last_active=datetime.now(),
                    files_created=[],
                    pages_created=["Home", "Features", "Compare", "Pricing"]  # Default pages
                )
                
                self.sessions[session_id] = session_info
                # self.allocated_ports.add(vite_port) # Already added
                
                logger.info(f"[SessionManager] Session {session_id} created on port {vite_port}")
                return session_info
                
            except Exception as e:
                # Release port on failure
                if vite_port in self.allocated_ports:
                    self.allocated_ports.remove(vite_port)
                raise e
            
        except Exception as e:
            logger.error(f"[SessionManager] Failed to create session {session_id}: {e}")
            # Cleanup on failure
            if project_path.exists():
                shutil.rmtree(project_path, ignore_errors=True)
            raise
    
    async def _copy_template(self, dest_path: Path):
        """Copy Vite template to session directory"""
        logger.info(f"[SessionManager] Copying template to {dest_path}")
        
        if not self.template_dir.exists():
            raise FileNotFoundError(f"Template directory not found: {self.template_dir}")
        
        # Copy recursively
        await asyncio.to_thread(
            shutil.copytree,
            self.template_dir,
            dest_path,
            dirs_exist_ok=True,
            ignore=shutil.ignore_patterns('node_modules', 'dist', '.git')
        )
        
        logger.info(f"[SessionManager] Template copied successfully")
    
    async def _install_dependencies(self, project_path: Path):
        """Run npm install in project directory"""
        logger.info(f"[SessionManager] Installing dependencies for {project_path.name}")
        
        process = await asyncio.create_subprocess_exec(
            self.npm_cmd, "install",
            cwd=project_path,
            stdout=asyncio.subprocess.PIPE,
            stderr=asyncio.subprocess.PIPE
        )
        
        stdout, stderr = await process.communicate()
        
        if process.returncode != 0:
            error_msg = stderr.decode()
            logger.error(f"[SessionManager] npm install failed: {error_msg}")
            raise RuntimeError(f"npm install failed: {error_msg}")
        
        logger.info(f"[SessionManager] Dependencies installed successfully")
    
    def _get_available_port(self) -> int:
        """Find an available port in the configured range"""
        for port in range(self.port_range[0], self.port_range[1]):
            if port not in self.allocated_ports:
                # Check if port is actually available
                import socket
                with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
                    try:
                        s.bind(('', port))
                        return port
                    except OSError:
                        continue
        
        raise RuntimeError(f"No available ports in range {self.port_range}")
    
    async def _start_vite_server(self, project_path: Path, port: int) -> subprocess.Popen:
        """Start Vite dev server on specified port"""
        logger.info(f"[SessionManager] Starting Vite server on port {port} for {project_path.name}")
        
        # Set environment variable for port
        env = os.environ.copy()
        env["VITE_PORT"] = str(port)
        
        # Start Vite dev server
        process = subprocess.Popen(
            [self.npm_cmd, "run", "dev", "--", "--port", str(port), "--host", "0.0.0.0"],
            cwd=project_path,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            env=env
        )
        
        # Wait a bit for server to start
        await asyncio.sleep(2)
        
        if process.poll() is not None:
            # Process died
            stdout, stderr = process.communicate()
            error_msg = stderr.decode() if stderr else "No stderr output"
            stdout_msg = stdout.decode() if stdout else "No stdout output"
            logger.error(f"[SessionManager] Vite failed to start. Return code: {process.returncode}")
            logger.error(f"[SessionManager] Vite stdout: {stdout_msg}")
            logger.error(f"[SessionManager] Vite stderr: {error_msg}")
            raise RuntimeError(f"Vite server failed to start on port {port}. Error: {error_msg}")
        
        # Store port in file for reference
        port_file = project_path / ".vite-port"
        port_file.write_text(str(port))
        
        logger.info(f"[SessionManager] Vite server started successfully on port {port}")
        return process
    
    def get_session(self, session_id: str) -> Optional[SessionInfo]:
        """Get session info by ID"""
        return self.sessions.get(session_id)
    
    def session_exists(self, session_id: str) -> bool:
        """Check if session exists"""
        return session_id in self.sessions
    
    def update_activity(self, session_id: str):
        """Update last_active timestamp for session"""
        if session_id in self.sessions:
            self.sessions[session_id].last_active = datetime.now()
            logger.debug(f"[SessionManager] Updated activity for session {session_id}")
    
    async def cleanup_session(self, session_id: str):
        """
        Clean up a session: stop Vite, delete files, release port.
        """
        if session_id not in self.sessions:
            logger.warning(f"[SessionManager] Session {session_id} not found for cleanup")
            return
        
        session = self.sessions[session_id]
        logger.info(f"[SessionManager] Cleaning up session {session_id}")
        
        try:
            # Stop Vite process
            if session.vite_process:
                session.vite_process.terminate()
                try:
                    session.vite_process.wait(timeout=5)
                except subprocess.TimeoutExpired:
                    session.vite_process.kill()
                logger.info(f"[SessionManager] Vite process terminated for {session_id}")
            
            # Delete project directory
            if session.project_path.exists():
                await asyncio.to_thread(shutil.rmtree, session.project_path, ignore_errors=True)
                logger.info(f"[SessionManager] Project directory deleted for {session_id}")
            
            # Release port
            if session.vite_port in self.allocated_ports:
                self.allocated_ports.remove(session.vite_port)
            
            # Remove from sessions dict
            del self.sessions[session_id]
            
            logger.info(f"[SessionManager] Session {session_id} cleaned up successfully")
            
        except Exception as e:
            logger.error(f"[SessionManager] Error cleaning up session {session_id}: {e}")
    
    async def cleanup_inactive_sessions(self, timeout_seconds: int = 300):
        """
        Clean up sessions inactive for longer than timeout.
        
        Args:
            timeout_seconds: Inactivity timeout in seconds (default 5 minutes)
        """
        now = datetime.now()
        inactive_sessions = []
        
        for session_id, session_info in self.sessions.items():
            inactive_time = (now - session_info.last_active).seconds
            if inactive_time > timeout_seconds:
                inactive_sessions.append(session_id)
        
        if inactive_sessions:
            logger.info(f"[SessionManager] Cleaning up {len(inactive_sessions)} inactive sessions")
            for session_id in inactive_sessions:
                await self.cleanup_session(session_id)
        else:
            logger.debug(f"[SessionManager] No inactive sessions to clean up")
    
    def get_session_stats(self) -> dict:
        """Get statistics about current sessions"""
        return {
            "total_sessions": len(self.sessions),
            "max_sessions": self.max_sessions,
            "allocated_ports": len(self.allocated_ports),
            "sessions": [
                {
                    "session_id": s.session_id,
                    "port": s.vite_port,
                    "created_at": s.created_at.isoformat(),
                    "files_created": len(s.files_created),
                    "pages_created": s.pages_created
                }
                for s in self.sessions.values()
            ]
        }
