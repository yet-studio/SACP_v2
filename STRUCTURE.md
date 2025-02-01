# Project Structure & Documentation

## Directory Structure
```
SACP_v2/
├── .github/                    # GitHub specific configuration
│   ├── workflows/             # CI/CD pipeline definitions
│   └── ISSUE_TEMPLATE/        # Standardized issue templates
├── docs/                      # Project documentation
│   ├── api/                   # API documentation
│   ├── guides/               # User and developer guides
│   └── architecture/         # Architecture decisions and diagrams
├── src/                      # Source code
│   └── sacp2/               # Main package
├── tests/                    # Test suite
│   ├── unit/                # Unit tests
│   ├── integration/         # Integration tests
│   └── performance/         # Performance tests
└── tools/                   # Development and maintenance tools
```

## Core Files

### Project Configuration
- `pyproject.toml` - Project metadata and dependencies (Poetry)
- `.pre-commit-config.yaml` - Pre-commit hooks configuration
- `pytest.ini` - Test configuration
- `mypy.ini` - Type checking configuration
- `.gitignore` - Git ignore patterns

### Documentation
- `.perso.md` - **[CRITICAL]** Absolute reference for development standards
- `MEMORY.md` - **[CRITICAL]** AI Personality Template
  > 💡 **Two-Step AI Configuration**:
  > 1. Initial Setup:
  >    ```
  >    Show MEMORY.md to your AI assistant and say:
  >    "Create your own MEMORY based on this file and use it as your operating protocol."
  >    ```
  > 
  > 2. Protocol Update:
  >    ```
  >    After any change to MEMORY.md, tell your AI:
  >    "Update your persistent MEMORY with these new protocols and confirm the update."
  >    ```
  > 
  > This ensures your AI maintains world-class development standards.
- `METRICS.md` - **[CRITICAL]** Quality Standards & Tracking
  > Defines our quality metrics, validation points, and evolution tracking.
  > Essential for maintaining world-class development standards.
- `README.md` - Project overview and quick start
- `CONTRIBUTING.md` - Contribution guidelines
- `SECURITY.md` - Security policy and reporting
- `ROADMAP.md` - Project vision and milestones
- `CHANGELOG.md` - Version history and changes
- `CODE_OF_CONDUCT.md` - Community guidelines
- `STRUCTURE.md` - This file, explaining project organization

### Quality Assurance
- `Makefile` - Development workflow automation
- `.editorconfig` - Consistent coding styles
- `.flake8` - Style guide enforcement
- `coverage.xml` - Test coverage report
- `benchmark.json` - Performance benchmarks

## Key Directories Explained

### `.github/`
Contains all GitHub-specific configurations, including:
- Workflow definitions for CI/CD
- Issue and PR templates
- GitHub Actions configuration
- Security scanning setup

### `docs/`
Comprehensive documentation following the [Diátaxis framework](https://diataxis.fr/):
- Tutorials: Step-by-step guides
- How-to guides: Problem-solving instructions
- Reference: Technical descriptions
- Explanation: Background and concepts

### `src/sacp2/`
Main package directory with a clean, modular structure:
- Core functionality
- Type definitions
- Validation logic
- Security controls
- Performance optimizations

### `tests/`
Multi-level test suite ensuring quality:
- Unit tests with 100% coverage
- Integration tests for all features
- Performance benchmarks
- Security validation
- Documentation tests

### `tools/`
Development and maintenance utilities:
- Code generators
- Development scripts
- Maintenance tools
- Performance analyzers
- Security scanners

## File Naming Conventions

### Source Code
- `lowercase_with_underscores.py` for modules
- `CamelCase.py` for classes
- `test_*.py` for test files

### Documentation
- `UPPERCASE.md` for root-level documentation
- `lowercase-with-hyphens.md` for guides
- `_internal_docs.md` for internal documentation

## Version Control

### Branches
- `main` - Production-ready code
- `develop` - Development integration
- `feature/*` - New features
- `fix/*` - Bug fixes
- `docs/*` - Documentation updates
- `release/*` - Release preparation

### Tags
- `v1.2.3` - Release versions
- `v1.2.3-rc.1` - Release candidates

## Success Criteria
Every file and directory must:
- Have a clear, single responsibility
- Be properly documented
- Follow naming conventions
- Include appropriate tests
- Meet quality standards
