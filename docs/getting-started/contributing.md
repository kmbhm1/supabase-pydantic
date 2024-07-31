# Contributing

We welcome contributions and volunteers for the project! Please read the following guidelines before contributing.

## Issues

Questions, bug reports, and feature requests are welcome as [discussions or issues](https://github.com/kmbhm1/supabase-pydantic/issues/new/choose). Please search the existing issues before opening a new one. **To report a security vulneratbility, please see the [security policy](./security.md).**

To help us resolve your issue, please provide the following information:

- **Expected behavior:** A clear and concise description of what you expected to happen.
- **Actual behavior:** A clear and concise description of what actually happened.
- **Steps to reproduce:** How can we reproduce the issue?
- **Environment:** Include relevant details like the operating system, Python version, and any other relevant information.

## Pull Requests

We welcome pull requests for bug fixes, new features, and improvements. We aim to provide feedback regularly and will review your pull request as soon as possible. :tada:

Unless your change is not trivial, please [create an issue](https://github.com/kmbhm1/supabase-pydantic/issues/new/choose) before submitting a pull request. This will allow us to discuss the change and ensure it aligns with the project goals.

### Prerequisites

You will need the following to start developing:

- Python 3.10+
- [virtualenv](https://virtualenv.pypa.io/en/latest/), [poetry](https://python-poetry.org/), or [pipenv](https://pipenv.pypa.io/en/latest/) for the development environment.
- [git](https://git-scm.com/) for version control.
- [make](https://www.gnu.org/software/make/) for running the Makefile commands.

### Installation & Setup

Fork the [repository](https://github.com/kmbhm1/supabase-pydantic) on GitHub and clone your fork locally. Then, install the dependencies:

``` bash
# Clone your fork and cd into the repo directory
git clone git@github.com:<your username>/supabase-pydantic.git
cd supabase-pydantic

# Install the dependencies
# e.g., using poetry
poetry install

# Setup pre-commit
make pre-commit-setup
```

### Checkout a New Branch

Create a new branch for your changes:

``` bash
# Create a new branch
git checkout -b my-new-feature
```

### Run Tests, Linting, Formatting, Type checking, & Pre-Commit Hooks

Before submitting a pull request, ensure that the tests pass, the code is formatted correctly, and the code passes the linting and type checking checks:

``` bash
# Run tests
make test

# Run linting & formatting
make lint
make format
make check-types

# Run pre-commit hooks
make pre-commit
```

### Build Documentation

If you make changes to the documentation, you can build the documentation locally:

``` bash
# Build the documentation
make serve-docs
```

### Commit and Push your Changes

Commit your changes, push to your forked repository, and create a pull request:

Please follow the pull request template and fill in as much information as possible. Link to any relevant issues and include a description of your changes.

When your pull request is ready for review, add a comment with the message "please review" and we'll take a look as soon as we can.

## Code Style & Conventions

### Documentation Style

Documentation is written in format and follows the [Markdown Style Guide](https://www.cirosantilli.com/markdown-style-guide/). Please ensure that the documentation is clear, concise, and easy to read. API documentation is generated using [mkdocs](https://www.mkdocs.org/) & [mkdocstrings](https://mkdocstrings.github.io/). We follow [google-style](https://google.github.io/styleguide/pyguide.html) docstrings.

### Code Documentation

Please ensure that the code is well-documented and easy to understand when contributing. The following should be documented using proper docstrings:

- Modules
- Class Definitions
- Function Definitions
- Module-level Variables

`supabase-pydantic` uses [Google-style docstrings](https://google.github.io/styleguide/pyguide.html#38-comments-and-docstrings) according to [PEP 257](https://www.python.org/dev/peps/pep-0257/). Please see the [example](https://sphinxcontrib-napoleon.readthedocs.io/en/latest/example_google.html) for more information.

Class attributes and function arguments should be documented in the style of "name: description" & include an annotated type and return type when applicable. Feel free to include example code in docstrings. 
