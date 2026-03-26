# Contributing to Hunter

Thank you for your interest in contributing to Hunter! This document provides guidelines for contributing.

## 🚀 Quick Start

1. Fork the repository
2. Clone your fork: `git clone https://github.com/yourusername/hunter.git`
3. Install in development mode: `pip install -e ".[dev]"`
4. Create a branch: `git checkout -b feature/your-feature`
5. Make changes and commit
6. Push and create a Pull Request

## 📋 Development Setup

```bash
# Clone the repo
git clone https://github.com/yourusername/hunter.git
cd hunter

# Create virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install in editable mode with dev dependencies
pip install -e ".[dev]"

# Install pre-commit hooks
pre-commit install
```

## 🧪 Testing

```bash
# Run all tests
pytest

# Run with coverage
pytest --cov=hunter

# Run specific test file
pytest tests/test_config.py
```

## 📝 Code Style

We use:
- **Black** for code formatting
- **Ruff** for linting
- **MyPy** for type checking

```bash
# Format code
black hunter/

# Run linter
ruff check hunter/

# Type check
mypy hunter/

# Run all checks
pre-commit run --all-files
```

## 🎯 Contribution Areas

### High Priority
- [ ] Data source integrations (Birdeye, Helius)
- [ ] Strategy detection algorithms
- [ ] Risk assessment engine
- [ ] Paper trading system
- [ ] Backtesting framework

### Medium Priority
- [ ] Additional ecosystem support (SUI, BASE)
- [ ] More strategy types
- [ ] Performance analytics
- [ ] Documentation improvements

### Nice to Have
- [ ] Web dashboard
- [ ] Discord bot integration
- [ ] Mobile app
- [ ] Advanced ML models

## 🐛 Reporting Bugs

When reporting bugs, please include:
1. Hunter version (`hunter --version`)
2. Python version
3. Operating system
4. Steps to reproduce
5. Expected vs actual behavior
6. Error logs (if any)

## 💡 Suggesting Features

We welcome feature suggestions! Please:
1. Check if already requested in Issues
2. Describe the use case clearly
3. Explain why it benefits Hunter
4. Consider implementation complexity

## 🏗️ Architecture Decisions

Before making major architectural changes:
1. Open an Issue to discuss
2. Explain the problem and proposed solution
3. Consider impact on existing code
4. Get approval from maintainers

## 📚 Adding Documentation

- Docstrings: Google style
- README updates for user-facing changes
- Architecture docs for design changes
- Examples for complex features

## 🧠 Design Patterns

When implementing features, consider the 21 Agentic Design Patterns:
- Does this need Prompt Chaining?
- Can we use Parallelization?
- Is Reflection appropriate?
- Should we use Multi-Agent approach?

## 💝 Donations

If you contribute significantly, you're eligible for donation sharing! See README for donation wallet addresses.

## ❓ Questions?

- Open a Discussion for general questions
- Join our Telegram community
- Email: hunter@example.com

## 📝 License

By contributing, you agree that your contributions will be licensed under the MIT License.

---

**Thank you for making Hunter better! 🎯**
