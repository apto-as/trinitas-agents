# Changelog

## [3.5.0] - 2025-08-26

### Phase 3 Implementation Complete

#### Added
- **Hybrid Memory System**: Redis + ChromaDB + SQLite intelligent routing
- **AI-Driven Memory Management**:
  - Automatic importance scoring with 5 feature extractors
  - Predictive caching with pattern learning
  - Anomaly detection for unusual memory patterns
- **Persona-Specific Embeddings**:
  - Custom vocabulary and weights per persona
  - Japanese/English bilingual support
  - Adaptive embedding refinement
- **Web Visualization Dashboard**:
  - Overview statistics and metrics
  - Knowledge graph visualization
  - Timeline view of memories
  - 3D space exploration
  - Analytics and insights
- **New Personas**:
  - Bellona (Tactical Coordinator) - Real-time operations management
  - Seshat (Knowledge Architect) - Documentation and knowledge management

#### Changed
- Upgraded from 3-persona to 5-persona system
- Enhanced memory backend with hybrid storage
- Improved UV package manager support
- Updated all documentation to reflect Phase 3 features
- Refactored persona definitions to use mythology names as default

#### Fixed
- Missing Bellona and Seshat agent files
- Incomplete dependencies in pyproject.toml
- Documentation inconsistencies
- README files missing Phase 3 features

#### Migration Notes
- Run migration scripts in trinitas-mcp/migrations/ for existing data
- Update environment variables for memory backend configuration
- Docker compose available for Redis deployment

### Phase 4 Status
- Quantum computing features postponed until suitable architecture available
- Focus shifted to production optimization and stability

## [3.4.0] - Previous Release
- Initial v35 implementation
- MCP tools integration
- Local LLM support
- Basic memory system