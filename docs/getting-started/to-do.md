# To Do's

- [x] Finalize JsonAPI writers as correct with FastAPI-JSONAPI lib
- [x] README: change Supabase-Pydantic to `supabase-py`; change this description, "A project to translate Supabase schemas into Pydantic models"; add github link
- [x] Add community health guidelines
- [ ] Add better examples and usage in README
- [ ] Add example Makefile command
- [x] Integrate pyproject.toml
- [x] Add linting with ruff and in actions
- [x] Add tests with coverage and in actions
- [x] Add better cli args for sqlalchemy, fastapi and fastapi-json
- [x] Add pre-commit hooks
- [ ] Add compatibility with 3.11 & 3.12
- [ ] Setup issues and wiki pages for github (+ docs site from github?)
- [ ] Integrate mkdocs, mkdocs-material, mkdocstrings, mkdocstrings-python
- [x] Explore security scanners in pipelines
- [ ] Explore SDK integrations, rather than CLI use
- [ ] Test with other conn methods (e.g., supabase secret key)
- [x] Separate nullable and non-nullable columns in models in a better way
- [ ] Acquire test dbs for integration tests
- [x] Finish adding tests for writers and marshalers
- [x] Add uploading of coverage report to codecov or somewhere
- [ ] Add badges to README
- [ ] polymorphism for Writer class; add interfaces?

- [x] Convert Writer to abstract class pattern
- [x] Update CLI with behavior more like supabase-js type gen command
- [ ] Update for [django](https://docs.djangoproject.com/en/5.0/topics/db/models/#automatic-primary-key-fields) model.Model and [update](https://docs.sqlalchemy.org/en/20/tutorial/metadata.html#declaring-mapped-classes) sqlalchemy for Declarative base
- [ ] route generators? [flask](https://www.reddit.com/r/flask/comments/gyf22b/if_you_are_using_flask_you_should_start_using/), django-rest, fastapi, jsonapi, etc.
- [ ] Revisit table relationship logic