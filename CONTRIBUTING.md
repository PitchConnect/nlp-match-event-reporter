# Contributing to NLP Match Event Reporter

Thank you for your interest in contributing to the NLP Match Event Reporter! This document provides guidelines and information for contributors.

## 🚀 Getting Started

### Prerequisites

- Python 3.9 or higher
- Docker and Docker Compose
- Git
- A FOGIS account for testing (optional but recommended)

### Development Setup

1. **Fork and clone the repository:**
   ```bash
   git clone https://github.com/your-username/nlp-match-event-reporter.git
   cd nlp-match-event-reporter
   ```

2. **Set up the development environment:**
   ```bash
   ./scripts/setup_dev.sh
   ```

3. **Activate the virtual environment:**
   ```bash
   source venv/bin/activate
   ```

4. **Configure environment variables:**
   ```bash
   cp .env.example .env
   # Edit .env with your configuration
   ```

5. **Run the development server:**
   ```bash
   uvicorn src.nlp_match_event_reporter.main:app --reload
   ```

## 📋 Development Workflow

### Branch Strategy

- `main` - Production-ready code
- `develop` - Integration branch for features
- `feature/*` - Feature development branches
- `bugfix/*` - Bug fix branches
- `hotfix/*` - Critical production fixes

### Making Changes

1. **Create a feature branch:**
   ```bash
   git checkout -b feature/your-feature-name
   ```

2. **Make your changes following our coding standards**

3. **Run tests and linting:**
   ```bash
   pytest tests/
   pre-commit run --all-files
   ```

4. **Commit your changes:**
   ```bash
   git add .
   git commit -m "feat: add your feature description"
   ```

5. **Push and create a pull request:**
   ```bash
   git push origin feature/your-feature-name
   ```

## 🎯 Coding Standards

### Python Code Style

We follow PEP 8 with some modifications:

- **Line length:** 88 characters (Black default)
- **Import sorting:** isort with Black profile
- **Type hints:** Required for all functions and methods
- **Docstrings:** Google style for all public functions and classes

### Code Quality Tools

- **Black:** Code formatting
- **isort:** Import sorting
- **flake8:** Linting
- **mypy:** Type checking
- **bandit:** Security analysis
- **pytest:** Testing

### Pre-commit Hooks

We use pre-commit hooks to ensure code quality:

```bash
pre-commit install
```

This will run automatically before each commit.

## 🧪 Testing

### Running Tests

```bash
# Run all tests
pytest

# Run with coverage
pytest --cov=src/nlp_match_event_reporter

# Run specific test file
pytest tests/unit/test_matches.py

# Run integration tests
pytest tests/integration/
```

### Writing Tests

- **Unit tests:** Test individual functions and classes
- **Integration tests:** Test API endpoints and service interactions
- **Test coverage:** Aim for >90% coverage
- **Test naming:** Use descriptive names that explain what is being tested

Example test structure:
```python
def test_create_event_with_valid_data(client, sample_event_data):
    """Test creating an event with valid data returns success."""
    response = client.post("/api/v1/events/", json=sample_event_data)
    
    assert response.status_code == 200
    data = response.json()
    assert data["event"]["event_type"] == sample_event_data["event_type"]
```

## 📚 Documentation

### API Documentation

- Update `docs/api.md` for API changes
- Use clear examples and descriptions
- Include error scenarios

### Code Documentation

- Add docstrings to all public functions and classes
- Use type hints consistently
- Comment complex logic

### README Updates

- Keep the main README.md up to date
- Update feature lists and installation instructions
- Add new configuration options

## 🐛 Bug Reports

When reporting bugs, please include:

1. **Environment information:**
   - Python version
   - Operating system
   - Docker version (if applicable)

2. **Steps to reproduce:**
   - Clear, numbered steps
   - Expected vs actual behavior
   - Error messages or logs

3. **Additional context:**
   - Screenshots (if applicable)
   - Configuration files (sanitized)
   - Related issues or PRs

## 💡 Feature Requests

For new features:

1. **Check existing issues** to avoid duplicates
2. **Describe the problem** the feature would solve
3. **Propose a solution** with implementation details
4. **Consider alternatives** and their trade-offs

## 🔄 Pull Request Process

### Before Submitting

- [ ] Tests pass locally
- [ ] Code follows style guidelines
- [ ] Documentation is updated
- [ ] Commit messages follow conventional format
- [ ] Branch is up to date with develop

### PR Description Template

```markdown
## Description
Brief description of changes

## Type of Change
- [ ] Bug fix
- [ ] New feature
- [ ] Breaking change
- [ ] Documentation update

## Testing
- [ ] Unit tests added/updated
- [ ] Integration tests added/updated
- [ ] Manual testing completed

## Checklist
- [ ] Code follows style guidelines
- [ ] Self-review completed
- [ ] Documentation updated
- [ ] No breaking changes (or documented)
```

### Review Process

1. **Automated checks** must pass
2. **Code review** by maintainers
3. **Testing** in development environment
4. **Approval** and merge

## 🏗️ Architecture Guidelines

### Microservices Design

- **Single responsibility** for each service
- **Clear API boundaries** between services
- **Containerized deployment** with Docker
- **Health checks** for all services

### Voice Processing

- **Modular design** for different voice engines
- **Error handling** for audio processing failures
- **Resource management** for continuous listening
- **Performance optimization** for real-time processing

### FOGIS Integration

- **Robust error handling** for API failures
- **Retry mechanisms** with exponential backoff
- **Data validation** before sending to FOGIS
- **Sync status tracking** for all events

## 📞 Getting Help

- **GitHub Issues:** For bugs and feature requests
- **GitHub Discussions:** For questions and general discussion
- **Email:** info@pitchconnect.se for private matters

## 📄 License

By contributing, you agree that your contributions will be licensed under the MIT License.

---

Thank you for contributing to the NLP Match Event Reporter! 🎉
