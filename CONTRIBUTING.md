# Contributing to FabManager Data Analyzer

Thank you for your interest in contributing to FabManager-Data-Analyzer! We welcome contributions from the community.

## 🤝 How to Contribute

### Reporting Bugs

If you find a bug, please create an issue on GitHub with:
- A clear, descriptive title
- Steps to reproduce the issue
- Expected behavior vs actual behavior
- Your environment (OS, Python version, browser if using JupyterLite)
- Error messages or screenshots if applicable

### Suggesting Enhancements

We're open to new ideas! When suggesting an enhancement:
- Use a clear, descriptive title
- Provide a detailed description of the proposed feature
- Explain why this enhancement would be useful
- Include examples of how it would work

### Pull Requests

1. **Fork the repository** and create your branch from `main`
2. **Install development dependencies**: `pip install -e ".[dev]"`
3. **Make your changes** following our code guidelines
4. **Add tests** if you're adding new functionality, examples work as well
5. **Run the test suite**: `pytest`
6. **Format your code**: `black src/ tests/` and `isort src/ tests/`
7. **Check code style**: `flake8 src/ tests/`
8. **Type check**: `mypy src/`
9. **Update documentation** if needed (README.md, examples)
10. **Commit your changes** with clear, descriptive commit messages
11. **Push to your fork** and submit a pull request to the `main` branch
12. **Describe your changes** in the pull request description, referencing any related issues

## 📝 Code Guidelines

### Code Style

- **Python Version**: Write code compatible with Python 3.8+
- **Formatting**: Use [Black](https://github.com/psf/black) with default settings (88 character line length)
- **Import Sorting**: Use [isort](https://pycqa.github.io/isort/) with Black profile
- **Linting**: Follow [flake8](https://flake8.pycqa.org/) guidelines
- **Type Hints**: Add type hints where appropriate; check with [mypy](https://mypy.readthedocs.io/)

### Code Organization

- **Module Structure**: Place new modules in `src/fabmanager_data_analyzer_zumat/`
- **Examples**: Add usage examples to the `examples/` directory
- **Tests**: Add tests to the `tests/` directory with `test_` prefix
- **Documentation**: Include docstrings for all public functions, classes, and methods

### Writing Good Code

- Write clear, self-documenting code with meaningful variable and function names
- Keep functions focused on a single responsibility
- Add comments for complex logic or non-obvious decisions
- Follow existing patterns in the codebase
- Ensure your code works with the FabManager API structure

## 🔍 Areas for Contribution

Check them in the readme file. Moreover, other contributions are welcome!

## 🐛 Bug Fixes

When fixing bugs:

1. **Verify the bug** - Reproduce the issue to understand it fully
2. **Check existing issues** - See if someone else has reported it
3. **Create a test** - Write a test that fails due to the bug
4. **Fix the bug** - Make the minimal changes needed to fix the issue
5. **Verify the fix** - Ensure your test now passes and no other tests break
6. **Document the fix** - Explain what caused the bug and how you fixed it in your PR

For critical bugs affecting many users, please label your issue/PR as "bug" and "priority".

## 📋 Checklist for Pull Requests

Before submitting your pull request, ensure:

- [ ] Code follows the project's style guidelines (Black, isort, flake8)
- [ ] All tests pass (`pytest`)
- [ ] Type checking passes (`mypy src/`)
- [ ] New code has appropriate test coverage
- [ ] Documentation is updated (README.md, docstrings, examples if applicable)
- [ ] Commit messages are clear and descriptive
- [ ] The PR description explains what changes were made and why
- [ ] Any new dependencies are justified and added to `pyproject.toml`
- [ ] Code is compatible with Python 3.8+
- [ ] You've tested the code with actual FabManager API responses (if applicable)
- [ ] Examples are provided for new features (in the `examples/` directory)
- [ ] Breaking changes are clearly documented and justified
- [ ] **You've added yourself to the authors list** in `citation.cff` (for significant contributions)

## 👥 Adding Yourself as an Author

If you're making a significant contribution (new features, major bug fixes, or substantial improvements), please add yourself to the authors list:

1. Open the `citation.cff` file
2. Add your information to the `authors` section following the existing format:
   ```yaml
   - family-names: "YourLastName"
     given-names: "YourFirstName"
     email: "your.email@example.com"
     orcid: "https://orcid.org/0000-0000-0000-0000"  # Optional
   ```
3. Include this change in your pull request

This helps us properly acknowledge all contributors to the project!

## ❓ Questions?

If you have questions about contributing:
- Open an issue with the "question" label
- Check existing issues for similar questions
- Review the README.md for project context

## 📜 Code of Conduct

### Our Standards

- Be respectful and inclusive
- Welcome newcomers and beginners
- Accept constructive criticism gracefully
- Focus on what's best for the community
- Show empathy towards others

### Unacceptable Behavior

- Harassment or discrimination of any kind
- Trolling or insulting comments
- Publishing others' private information
- Any conduct that would be inappropriate in a professional setting

## 📄 License

By contributing, you agree that your contributions will be licensed under the same license as the project.

## 🙏 Thank You!

Your contributions help make FabManager-Data-Analyzer better for everyone. We appreciate your time and effort!
