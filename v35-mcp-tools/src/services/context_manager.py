#!/usr/bin/env python3
"""
Trinitas v3.5 MCP Tools - Advanced Context Management System
Manages context persistence, session management, and cross-persona context synchronization
"""

import json
import hashlib
import asyncio
from typing import Dict, List, Optional, Any, Union
from dataclasses import dataclass, field, asdict
from datetime import datetime, timedelta
from enum import Enum
import logging
import os
import pickle
from pathlib import Path

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class ContextType(str, Enum):
    """Types of context data"""
    TASK = "task"
    RESULT = "result"
    ERROR = "error"
    CONVERSATION = "conversation"
    WORKFLOW = "workflow"
    PERSONA_STATE = "persona_state"
    SESSION_META = "session_meta"
    CUSTOM = "custom"


@dataclass
class ContextFrame:
    """Individual context frame"""
    id: str
    type: ContextType
    content: Dict[str, Any]
    persona: Optional[str] = None
    timestamp: datetime = field(default_factory=datetime.now)
    ttl: Optional[int] = None  # Time to live in seconds
    parent_id: Optional[str] = None
    metadata: Dict[str, Any] = field(default_factory=dict)
    
    def is_expired(self) -> bool:
        """Check if context frame has expired"""
        if self.ttl is None:
            return False
        expiry = self.timestamp + timedelta(seconds=self.ttl)
        return datetime.now() > expiry
    
    def to_dict(self) -> Dict:
        """Convert to dictionary"""
        return {
            "id": self.id,
            "type": self.type.value,
            "content": self.content,
            "persona": self.persona,
            "timestamp": self.timestamp.isoformat(),
            "ttl": self.ttl,
            "parent_id": self.parent_id,
            "metadata": self.metadata
        }


@dataclass
class Session:
    """User session with context history"""
    id: str
    created_at: datetime = field(default_factory=datetime.now)
    last_accessed: datetime = field(default_factory=datetime.now)
    context_frames: List[ContextFrame] = field(default_factory=list)
    active_workflow: Optional[str] = None
    persona_states: Dict[str, Dict] = field(default_factory=dict)
    metadata: Dict[str, Any] = field(default_factory=dict)
    
    def add_frame(self, frame: ContextFrame):
        """Add context frame to session"""
        self.context_frames.append(frame)
        self.last_accessed = datetime.now()
        
        # Prune expired frames
        self.context_frames = [
            f for f in self.context_frames
            if not f.is_expired()
        ]
    
    def get_recent_frames(
        self,
        limit: int = 10,
        type_filter: Optional[ContextType] = None,
        persona_filter: Optional[str] = None
    ) -> List[ContextFrame]:
        """Get recent context frames with optional filters"""
        frames = self.context_frames
        
        if type_filter:
            frames = [f for f in frames if f.type == type_filter]
        
        if persona_filter:
            frames = [f for f in frames if f.persona == persona_filter]
        
        # Sort by timestamp descending
        frames.sort(key=lambda f: f.timestamp, reverse=True)
        
        return frames[:limit]
    
    def get_context_summary(self) -> Dict[str, Any]:
        """Get summary of session context"""
        return {
            "session_id": self.id,
            "created_at": self.created_at.isoformat(),
            "last_accessed": self.last_accessed.isoformat(),
            "frame_count": len(self.context_frames),
            "active_workflow": self.active_workflow,
            "personas_used": list(set(
                f.persona for f in self.context_frames if f.persona
            )),
            "context_types": list(set(
                f.type.value for f in self.context_frames
            ))
        }


class AdvancedContextManager:
    """
    Advanced context management for Trinitas MCP Tools
    Handles session persistence, context synchronization, and intelligent retrieval
    """
    
    def __init__(self, persistence_dir: Optional[str] = None):
        """
        Initialize context manager
        
        Args:
            persistence_dir: Directory for persistent storage
        """
        self.sessions: Dict[str, Session] = {}
        self.active_session_id: Optional[str] = None
        
        # Setup persistence
        if persistence_dir:
            self.persistence_dir = Path(persistence_dir)
            self.persistence_dir.mkdir(parents=True, exist_ok=True)
        else:
            self.persistence_dir = Path.home() / ".trinitas" / "context"
            self.persistence_dir.mkdir(parents=True, exist_ok=True)
        
        # Context transformation rules for cross-persona sync
        self.transformation_rules = self._init_transformation_rules()
        
        # Load existing sessions
        self._load_sessions()
        
        logger.info(f"Context Manager initialized with persistence at {self.persistence_dir}")
    
    def _init_transformation_rules(self) -> Dict:
        """Initialize context transformation rules between personas"""
        return {
            ("springfield", "krukai"): {
                "focus": "strategic_to_technical",
                "preserve": ["requirements", "constraints"],
                "transform": {
                    "architecture": "implementation_details",
                    "roadmap": "technical_milestones"
                }
            },
            ("krukai", "vector"): {
                "focus": "technical_to_security",
                "preserve": ["implementation", "algorithms"],
                "transform": {
                    "endpoints": "attack_surface",
                    "dependencies": "vulnerability_vectors"
                }
            },
            ("springfield", "groza"): {
                "focus": "strategic_to_tactical",
                "language_shift": "japanese_to_english",
                "preserve": ["objectives", "timeline"],
                "transform": {
                    "long_term_plan": "mission_objectives",
                    "team_structure": "squad_composition"
                }
            },
            ("groza", "littara"): {
                "focus": "tactical_to_implementation",
                "preserve": ["mission_objectives"],
                "transform": {
                    "tactical_plan": "implementation_steps",
                    "deployment_strategy": "code_structure"
                }
            }
        }
    
    # Session Management
    
    def create_session(self, session_id: Optional[str] = None) -> str:
        """
        Create new session
        
        Args:
            session_id: Optional custom session ID
            
        Returns:
            Session ID
        """
        if not session_id:
            session_id = self._generate_session_id()
        
        session = Session(id=session_id)
        self.sessions[session_id] = session
        self.active_session_id = session_id
        
        # Persist session
        self._save_session(session)
        
        logger.info(f"Created new session: {session_id}")
        return session_id
    
    def switch_session(self, session_id: str) -> bool:
        """
        Switch to different session
        
        Args:
            session_id: Session to switch to
            
        Returns:
            Success status
        """
        if session_id in self.sessions:
            self.active_session_id = session_id
            logger.info(f"Switched to session: {session_id}")
            return True
        
        # Try to load from disk
        session = self._load_session(session_id)
        if session:
            self.sessions[session_id] = session
            self.active_session_id = session_id
            logger.info(f"Loaded and switched to session: {session_id}")
            return True
        
        logger.warning(f"Session not found: {session_id}")
        return False
    
    def get_current_session(self) -> Optional[Session]:
        """Get current active session"""
        if not self.active_session_id:
            self.create_session()
        
        return self.sessions.get(self.active_session_id)
    
    # Context Storage and Retrieval
    
    def add_context(
        self,
        content: Dict[str, Any],
        context_type: ContextType = ContextType.TASK,
        persona: Optional[str] = None,
        ttl: Optional[int] = None,
        parent_id: Optional[str] = None,
        session_id: Optional[str] = None
    ) -> str:
        """
        Add context to current or specified session
        
        Args:
            content: Context content
            context_type: Type of context
            persona: Associated persona
            ttl: Time to live in seconds
            parent_id: Parent context ID
            session_id: Optional specific session ID
            
        Returns:
            Context frame ID
        """
        # Use provided session_id or get current session
        if session_id:
            session = self.sessions.get(session_id)
            if not session:
                logger.warning(f"Session {session_id} not found")
                return None
        else:
            session = self.get_current_session()
            if not session:
                session = self.sessions[self.create_session()]
        
        # Generate frame ID
        frame_id = self._generate_frame_id(content)
        
        # Create context frame
        frame = ContextFrame(
            id=frame_id,
            type=context_type,
            content=content,
            persona=persona,
            ttl=ttl,
            parent_id=parent_id
        )
        
        # Add to session
        session.add_frame(frame)
        
        # Persist session
        self._save_session(session)
        
        logger.debug(f"Added context frame {frame_id} to session {session.id}")
        return frame_id
    
    def get_context(
        self,
        frame_id: Optional[str] = None,
        limit: int = 10,
        type_filter: Optional[ContextType] = None,
        persona_filter: Optional[str] = None
    ) -> Union[ContextFrame, List[ContextFrame], None]:
        """
        Get context from current session
        
        Args:
            frame_id: Specific frame ID to retrieve
            limit: Number of frames to retrieve
            type_filter: Filter by context type
            persona_filter: Filter by persona
            
        Returns:
            Context frame(s) or None
        """
        session = self.get_current_session()
        if not session:
            return None
        
        if frame_id:
            # Get specific frame
            for frame in session.context_frames:
                if frame.id == frame_id:
                    return frame
            return None
        else:
            # Get recent frames with filters
            return session.get_recent_frames(
                limit=limit,
                type_filter=type_filter,
                persona_filter=persona_filter
            )
    
    # Cross-Persona Context Synchronization
    
    async def sync_context_between_personas(
        self,
        from_persona: str,
        to_persona: str,
        context: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Synchronize context between personas with transformation
        
        Args:
            from_persona: Source persona
            to_persona: Target persona
            context: Context to sync
            
        Returns:
            Transformed context
        """
        # Get transformation rules
        rules = self.transformation_rules.get((from_persona, to_persona), {})
        
        transformed_context = {}
        
        # Preserve specified fields
        if "preserve" in rules:
            for field in rules["preserve"]:
                if field in context:
                    transformed_context[field] = context[field]
        
        # Transform specified fields
        if "transform" in rules:
            for old_key, new_key in rules["transform"].items():
                if old_key in context:
                    transformed_context[new_key] = context[old_key]
        
        # Handle language shift
        if "language_shift" in rules:
            transformed_context["_language_shift"] = rules["language_shift"]
        
        # Add transformation metadata
        transformed_context["_transformed_from"] = from_persona
        transformed_context["_transformed_to"] = to_persona
        transformed_context["_transformation_time"] = datetime.now().isoformat()
        
        # Store both original and transformed contexts
        self.add_context(
            context,
            ContextType.PERSONA_STATE,
            persona=from_persona
        )
        
        self.add_context(
            transformed_context,
            ContextType.PERSONA_STATE,
            persona=to_persona
        )
        
        return transformed_context
    
    # Workflow Context Management
    
    def start_workflow(self, workflow_name: str, parameters: Dict[str, Any]) -> str:
        """
        Start workflow and track context
        
        Args:
            workflow_name: Name of workflow
            parameters: Workflow parameters
            
        Returns:
            Workflow ID
        """
        session = self.get_current_session()
        if not session:
            session = self.sessions[self.create_session()]
        
        workflow_id = f"workflow_{datetime.now().timestamp()}"
        
        session.active_workflow = workflow_id
        
        # Store workflow context
        self.add_context(
            {
                "workflow_name": workflow_name,
                "workflow_id": workflow_id,
                "parameters": parameters,
                "status": "started"
            },
            ContextType.WORKFLOW
        )
        
        logger.info(f"Started workflow {workflow_id}: {workflow_name}")
        return workflow_id
    
    def complete_workflow(self, workflow_id: str, results: Dict[str, Any]):
        """
        Complete workflow and store results
        
        Args:
            workflow_id: Workflow ID
            results: Workflow results
        """
        session = self.get_current_session()
        if session and session.active_workflow == workflow_id:
            session.active_workflow = None
            
            # Store completion context
            self.add_context(
                {
                    "workflow_id": workflow_id,
                    "status": "completed",
                    "results": results
                },
                ContextType.WORKFLOW
            )
            
            logger.info(f"Completed workflow {workflow_id}")
    
    # Intelligent Context Retrieval
    
    def get_relevant_context(
        self,
        query: str,
        max_results: int = 5
    ) -> List[ContextFrame]:
        """
        Get relevant context based on query
        
        Args:
            query: Search query
            max_results: Maximum results to return
            
        Returns:
            Relevant context frames
        """
        session = self.get_current_session()
        if not session:
            return []
        
        query_lower = query.lower()
        scored_frames = []
        
        for frame in session.context_frames:
            score = 0
            
            # Check content
            content_str = json.dumps(frame.content).lower()
            if query_lower in content_str:
                score += 10
            
            # Check metadata
            metadata_str = json.dumps(frame.metadata).lower()
            if query_lower in metadata_str:
                score += 5
            
            # Boost recent frames
            age = (datetime.now() - frame.timestamp).total_seconds()
            if age < 300:  # Last 5 minutes
                score += 3
            elif age < 3600:  # Last hour
                score += 1
            
            if score > 0:
                scored_frames.append((score, frame))
        
        # Sort by score descending
        scored_frames.sort(key=lambda x: x[0], reverse=True)
        
        return [frame for _, frame in scored_frames[:max_results]]
    
    # Persistence
    
    def _save_session(self, session: Session):
        """Save session to disk"""
        try:
            session_file = self.persistence_dir / f"{session.id}.session"
            with open(session_file, 'wb') as f:
                pickle.dump(session, f)
            logger.debug(f"Saved session {session.id} to disk")
        except Exception as e:
            logger.error(f"Failed to save session: {e}")
    
    def _load_session(self, session_id: str) -> Optional[Session]:
        """Load session from disk"""
        try:
            session_file = self.persistence_dir / f"{session_id}.session"
            if session_file.exists():
                with open(session_file, 'rb') as f:
                    session = pickle.load(f)
                logger.debug(f"Loaded session {session_id} from disk")
                return session
        except Exception as e:
            logger.error(f"Failed to load session: {e}")
        return None
    
    def _load_sessions(self):
        """Load all sessions from disk"""
        try:
            for session_file in self.persistence_dir.glob("*.session"):
                session_id = session_file.stem
                session = self._load_session(session_id)
                if session:
                    self.sessions[session_id] = session
            logger.info(f"Loaded {len(self.sessions)} sessions from disk")
        except Exception as e:
            logger.error(f"Failed to load sessions: {e}")
    
    # Utility methods
    
    def _generate_session_id(self) -> str:
        """Generate unique session ID"""
        return f"session_{datetime.now().strftime('%Y%m%d_%H%M%S')}_{os.urandom(4).hex()}"
    
    def _generate_frame_id(self, content: Dict[str, Any]) -> str:
        """Generate unique frame ID"""
        content_str = json.dumps(content, sort_keys=True)
        hash_obj = hashlib.sha256(content_str.encode())
        return f"frame_{hash_obj.hexdigest()[:12]}_{datetime.now().timestamp()}"
    
    def get_statistics(self) -> Dict[str, Any]:
        """Get context manager statistics"""
        total_frames = sum(len(s.context_frames) for s in self.sessions.values())
        
        return {
            "total_sessions": len(self.sessions),
            "active_session": self.active_session_id,
            "total_context_frames": total_frames,
            "persistence_dir": str(self.persistence_dir),
            "sessions": {
                sid: session.get_context_summary()
                for sid, session in self.sessions.items()
            }
        }
    
    async def set_context(self, key: str, value: Any, scope: str = "session", session_id: Optional[str] = None):
        """Set context value"""
        if scope == "session" and session_id:
            if session_id not in self.sessions:
                logger.warning(f"Session {session_id} not found")
                return
            
            # Add as a context frame
            frame_id = self.add_context(
                {key: value},
                ContextType.CUSTOM,
                session_id=session_id
            )
            return frame_id
        elif scope in self.persona_contexts:
            # Persona-specific context
            self.add_context(
                {key: value},
                ContextType.PERSONA_STATE,
                persona=scope,
                session_id=session_id
            )
        else:
            # Global context
            frame_id = self.add_context(
                {key: value},
                ContextType.CUSTOM
            )
            return frame_id
    
    async def get_context(self, key: str, scope: str = "session", session_id: Optional[str] = None) -> Any:
        """Get context value"""
        if scope == "session" and session_id:
            if session_id not in self.sessions:
                return None
            
            session = self.sessions[session_id]
            # Search through context frames
            for frame in reversed(session.context_frames):
                if key in frame.content:
                    return frame.content[key]
            return None
        elif scope in self.persona_contexts:
            # Persona-specific context
            if self.active_session_id:
                session = self.sessions.get(self.active_session_id)
                if session:
                    for frame in reversed(session.context_frames):
                        if frame.persona == scope and key in frame.content:
                            return frame.content[key]
            return None
        else:
            # Global context search
            if self.active_session_id:
                session = self.sessions.get(self.active_session_id)
                if session:
                    for frame in reversed(session.context_frames):
                        if key in frame.content:
                            return frame.content[key]
            return None
    
    async def update_session_context(self, session_id: str, updates: Dict[str, Any]):
        """Update session context with new values"""
        if session_id not in self.sessions:
            logger.warning(f"Session {session_id} not found")
            return
        
        # Add updates as new context frame
        frame_id = self.add_context(
            updates,
            ContextType.CUSTOM,
            session_id=session_id
        )
        return frame_id
    
    async def get_session_context(self, session_id: str) -> Dict[str, Any]:
        """Get all context for a session"""
        if session_id not in self.sessions:
            return {}
        
        session = self.sessions[session_id]
        context = {}
        
        # Merge all context frames
        for frame in session.context_frames:
            context.update(frame.content)
        
        return context
    
    async def get_session_info(self, session_id: str) -> Dict[str, Any]:
        """Get information about a session"""
        if session_id not in self.sessions:
            return {}
        
        session = self.sessions[session_id]
        workflows = await self.get_workflow_history(session_id)
        
        return {
            "id": session.id,
            "created_at": session.created_at.isoformat(),
            "updated_at": session.updated_at.isoformat(),
            "context": await self.get_session_context(session_id),
            "workflows": workflows,
            "frame_count": len(session.context_frames)
        }
    
    async def get_performance_stats(self, session_id: str) -> Dict[str, Any]:
        """Get performance statistics for a session"""
        if session_id not in self.sessions:
            return {}
        
        session = self.sessions[session_id]
        
        # Count operations by type
        context_ops = sum(1 for f in session.context_frames if f.context_type == ContextType.CUSTOM)
        persona_ops = sum(1 for f in session.context_frames if f.context_type == ContextType.PERSONA_STATE)
        workflow_ops = sum(1 for f in session.context_frames if f.context_type == ContextType.WORKFLOW)
        
        return {
            "session_id": session_id,
            "total_operations": len(session.context_frames),
            "context_operations": context_ops,
            "persona_operations": persona_ops,
            "workflow_operations": workflow_ops,
            "session_duration": (datetime.now() - session.created_at).total_seconds(),
            "last_updated": session.updated_at.isoformat()
        }
    
    def cleanup_expired_contexts(self):
        """Clean up expired context frames from all sessions"""
        cleaned = 0
        for session in self.sessions.values():
            original_count = len(session.context_frames)
            session.context_frames = [
                f for f in session.context_frames
                if not f.is_expired()
            ]
            cleaned += original_count - len(session.context_frames)
            
            if original_count != len(session.context_frames):
                self._save_session(session)
        
        if cleaned > 0:
            logger.info(f"Cleaned up {cleaned} expired context frames")
    
    async def track_workflow(self, session_id: str, template_name: str, 
                           context: Dict[str, Any], result: Dict[str, Any]):
        """Track workflow execution in session"""
        if session_id not in self.sessions:
            logger.warning(f"Session {session_id} not found")
            return
        
        workflow_record = {
            "template": template_name,
            "context": context,
            "result": result,
            "timestamp": datetime.now().isoformat()
        }
        
        # Store as context frame
        frame_id = self.add_context(
            {"workflow": workflow_record},
            ContextType.WORKFLOW,
            session_id=session_id
        )
        
        logger.info(f"Tracked workflow {template_name} in session {session_id}")
        return frame_id
    
    async def get_workflow_history(self, session_id: str) -> List[Dict[str, Any]]:
        """Get workflow execution history for a session"""
        if session_id not in self.sessions:
            return []
        
        session = self.sessions[session_id]
        workflows = []
        
        for frame in session.context_frames:
            if frame.type == ContextType.WORKFLOW:
                workflow_data = frame.content.get("workflow", {})
                workflows.append(workflow_data)
        
        return workflows
    
    async def save_session(self, session_id: str):
        """Public method to save session to disk"""
        if session_id in self.sessions:
            self._save_session(self.sessions[session_id])
    
    async def load_session(self, session_id: str):
        """Public method to load session from disk"""
        session = self._load_session(session_id)
        if session:
            self.sessions[session_id] = session
            return True
        return False


# Global context manager instance
context_manager = AdvancedContextManager()


if __name__ == "__main__":
    # Test context manager
    async def test():
        print("Testing Advanced Context Manager")
        print("=" * 60)
        
        # Create session
        session_id = context_manager.create_session()
        print(f"Created session: {session_id}")
        
        # Add contexts
        frame1 = context_manager.add_context(
            {"task": "Design system"},
            ContextType.TASK,
            persona="springfield",
            ttl=3600
        )
        print(f"Added frame: {frame1}")
        
        # Sync between personas
        transformed = await context_manager.sync_context_between_personas(
            "springfield",
            "krukai",
            {"architecture": "microservices", "requirements": "scalable"}
        )
        print(f"Transformed context: {transformed}")
        
        # Get relevant context
        relevant = context_manager.get_relevant_context("architecture")
        print(f"Found {len(relevant)} relevant contexts")
        
        # Get statistics
        stats = context_manager.get_statistics()
        print(f"\nStatistics:")
        print(json.dumps(stats, indent=2, default=str))
    
    asyncio.run(test())