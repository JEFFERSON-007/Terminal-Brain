# CONTRIBUTING

## Development Setup

```bash
# Clone repository
git clone <repo>
cd "Terminal Brain"

# Create virtual environment
python3 -m venv venv
source venv/bin/activate

# Install with development dependencies
pip install -e ".[dev]"
```

## Code Style

- **Formatting**: Black
- **Linting**: Ruff
- **Type checking**: mypy

```bash
# Format code
black terminalbrain/

# Lint
ruff check terminalbrain/

# Type check
mypy terminalbrain/
```

## Testing

```bash
# Run all tests
pytest tests/

# Run specific test file
pytest tests/test_core.py -v

# Run with coverage
pytest --cov=terminalbrain tests/
```

## Documentation

- Update README.md for user-facing changes
- Update docs/ARCHITECTURE.md for system changes
- Update docs/API.md for API changes
- Add docstrings to all functions

## Commit Messages

Follow conventional commits:

```
feat: Add command prediction feature
fix: Correct history analyzer bug
docs: Update API documentation
test: Add tests for ranking engine
refactor: Restructure core modules
```

## Pull Request Process

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit changes (`git commit -m 'feat: add amazing feature'`)
4. Push to branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

## Reporting Issues

- Use GitHub Issues
- Provide clear reproduction steps
- Include version and OS information
- Attach relevant logs or screenshots

## Feature Requests

- Discuss large features in Issues first
- Explain use case and benefits
- Consider implementation complexity

## Code Review Guidelines

- Reviews should be constructive and helpful
- Approve when meets project standards
- Request changes for improvements
- Resolve conversations before merging

## Release Process

1. Update version in `__init__.py`
2. Update CHANGELOG.md
3. Create release on GitHub
4. Publish to PyPI

## License

All contributions are under MIT License.
