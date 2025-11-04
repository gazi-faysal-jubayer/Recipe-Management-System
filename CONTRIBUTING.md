# Contributing to Recipe Management System

Thank you for your interest in contributing! This document provides guidelines for contributing to the project.

## Getting Started

1. Fork the repository
2. Clone your fork: `git clone https://github.com/your-username/recipe-management-system.git`
3. Create a branch: `git checkout -b feature/your-feature-name`
4. Make your changes
5. Test thoroughly
6. Commit with clear messages
7. Push and create a Pull Request

## Development Setup

Follow the [SETUP.md](docs/SETUP.md) guide to set up your development environment.

## Code Style

### Python (Backend)
- Follow PEP 8
- Use type hints where possible
- Maximum line length: 120 characters
- Use docstrings for functions/classes
- Run linter: `flake8 apps/`
- Format code: `black apps/`

### TypeScript (Frontend)
- Follow TypeScript best practices
- Use functional components
- Proper type definitions
- Run linter: `npm run lint`
- Format code: `npm run format`

## Commit Messages

Format: `type(scope): description`

Types:
- `feat`: New feature
- `fix`: Bug fix
- `docs`: Documentation
- `style`: Formatting
- `refactor`: Code restructuring
- `test`: Adding tests
- `chore`: Maintenance

Examples:
- `feat(recipes): add batch import functionality`
- `fix(auth): resolve token refresh issue`
- `docs(api): update authentication endpoints`

## Pull Request Process

1. Update documentation if needed
2. Add tests for new features
3. Ensure all tests pass
4. Update CHANGELOG.md
5. Request review from maintainers
6. Address review feedback
7. Wait for approval and merge

## Testing

### Required Tests
- Unit tests for new functions
- Integration tests for API endpoints
- Frontend component tests
- E2E tests for critical flows

### Running Tests

```bash
# Backend
cd backend
pytest

# Frontend
cd frontend
npm test
```

## Documentation

Update relevant documentation:
- README.md for user-facing changes
- API_DOCUMENTATION.md for API changes
- ARCHITECTURE.md for structural changes
- Code comments for complex logic

## Issue Reporting

### Bug Reports

Include:
- Clear description
- Steps to reproduce
- Expected vs actual behavior
- Screenshots/logs
- Environment details

### Feature Requests

Include:
- Use case description
- Proposed solution
- Alternative solutions considered
- Additional context

## Code Review

Reviews focus on:
- Code quality and readability
- Test coverage
- Performance implications
- Security considerations
- Documentation completeness

## Questions?

- Open a GitHub Discussion
- Ask in Pull Request comments
- Review existing documentation

Thank you for contributing! 🎉
