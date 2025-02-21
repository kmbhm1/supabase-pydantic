# CHANGELOG


## v0.17.2 (2025-02-21)

### Bug Fixes

- **types**: Generate correct types for ONE_TO_ONE relationships
  ([#66](https://github.com/kmbhm1/supabase-pydantic/pull/66),
  [`e889eb3`](https://github.com/kmbhm1/supabase-pydantic/commit/e889eb36cd2ed0b4c78f490c92db15c085defec1))

* fix: Debug logging * feat(marshalers): improve foreign key analysis and cross-schema handling

- Add comprehensive test suite for add_foreign_key_info_to_table_details - Enhance debug logging
  with guidance for cross-schema references - Keep foreign keys even when target table is in another
  schema - Ensure proper relationship type detection for Pydantic model generation

This improves support for cross-schema relationships (e.g., public.users -> auth.users) while
  maintaining correct type generation in Pydantic models.


## v0.17.1 (2025-02-21)

### Bug Fixes

- **models**: Correct foreign key relationship types and field names
  ([#65](https://github.com/kmbhm1/supabase-pydantic/pull/65),
  [`368b557`](https://github.com/kmbhm1/supabase-pydantic/commit/368b557013363dc3b91485b7086872e09adecec4))

Generate appropriate types for relationship fields based on cardinality: - ONE_TO_ONE -> single
  instance (Type | None) - ONE_TO_MANY -> list of instances (list[Type] | None) - MANY_TO_MANY ->
  list of instances (list[Type] | None)

This fixes issues where: - All relationships were incorrectly generated as lists - Field names were
  incorrectly using 'ids' suffix - Multiple fields had naming collisions - Referenced table names
  were inconsistently included

refactor: consolidate tooling and improve logging - Replace isort with ruff for import sorting -
  Enhance CLI logging with proper configuration - Improve Makefile documentation and organization


## v0.17.0 (2025-02-16)

### Features

- Differentiate between insert, update, and select models
  ([#63](https://github.com/kmbhm1/supabase-pydantic/pull/63),
  [`372aaad`](https://github.com/kmbhm1/supabase-pydantic/commit/372aaad7c6cd2d736ee227347cf20ed8e08b6c91))

* refactor(pydantic): improve foreign key and relationship field generation

- Keep original column names for foreign keys (e.g., author_id: User) - Use inflection library for
  proper pluralization in many relationships - Fix handling of tables with relationships but no
  foreign keys - Add comprehensive tests for pluralization cases

This change ensures more accurate model generation that better reflects the database schema while
  maintaining proper type hints based on relationship types (ONE_TO_ONE, ONE_TO_MANY, MANY_TO_MANY).

* style: organize imports and format code

- Sort and group imports according to PEP8 - Remove unused imports - Fix line spacing and
  indentation

* fix(sqlalchemy): standardize newline formatting in model generation

- Remove extra newline after __tablename__ in write_docs method - Adjust newlines between sections
  in model output: - Single newline after __tablename__ - Single newline between columns - Single
  newline before section headers - Double newline between classes - Update test assertions to match
  new formatting

* test(cli): fix schema handling in CLI test cases

- Add proper schema parameter to CLI command invocations - Fix mock table dictionary and jobs
  configuration - Improve test coverage for empty schema scenarios - Simplify test setup by removing
  redundant configurations

* fix: line length error

* fix(deps): correct supabase package name in pre-commit config

* style: break long line in sqlalchemy writer

* fix(writers): use RelationshipInfo objects for relationships

* feat(models): add Insert and Update model variants

- Add Insert and Update model variants for each table with appropriate field optionality - Add
  --no-crud-models flag to disable generation of Insert/Update models - Add smoke-test target to
  Makefile for quick testing

Changes: - Add is_identity and related properties to ColumnInfo for tracking auto-generated columns
  - Update SQL query to fetch identity_generation information - Enhance WriterClassType enum with
  INSERT and UPDATE types - Group field property comments in Insert models for better readability -
  Add ruff check --fix to remove unused imports in generated files

This change makes it easier to use the generated models in CRUD operations by: 1. Making
  auto-generated fields optional in Insert models 2. Making all fields optional in Update models 3.
  Adding clear documentation about field properties

* feat(models): generate specialized Insert and Update Pydantic models

- Add Insert models that make auto-generated fields optional (e.g., IDs, timestamps) - Add Update
  models that make all fields optional for partial updates - Add generate_crud_models flag to
  FileWriterFactory for controlling model generation - Improve docstrings to clarify model
  generation behavior

Resolves issue with Insert/Update model generation to match TypeScript behavior

* docs: Update mkdocs with new example illustrating Insert and Update generators


## v0.16.0 (2025-02-16)

### Features

- Foreign key fields should be single instances, not lists in generated Pydantic models
  ([#62](https://github.com/kmbhm1/supabase-pydantic/pull/62),
  [`1484841`](https://github.com/kmbhm1/supabase-pydantic/commit/14848413ec23813c11ff719ac2aea1a3c947b191))

* refactor(pydantic): improve foreign key and relationship field generation

- Keep original column names for foreign keys (e.g., author_id: User) - Use inflection library for
  proper pluralization in many relationships - Fix handling of tables with relationships but no
  foreign keys - Add comprehensive tests for pluralization cases

This change ensures more accurate model generation that better reflects the database schema while
  maintaining proper type hints based on relationship types (ONE_TO_ONE, ONE_TO_MANY, MANY_TO_MANY).

* style: organize imports and format code

- Sort and group imports according to PEP8 - Remove unused imports - Fix line spacing and
  indentation

* fix(sqlalchemy): standardize newline formatting in model generation

- Remove extra newline after __tablename__ in write_docs method - Adjust newlines between sections
  in model output: - Single newline after __tablename__ - Single newline between columns - Single
  newline before section headers - Double newline between classes - Update test assertions to match
  new formatting

* test(cli): fix schema handling in CLI test cases

- Add proper schema parameter to CLI command invocations - Fix mock table dictionary and jobs
  configuration - Improve test coverage for empty schema scenarios - Simplify test setup by removing
  redundant configurations

* fix: line length error

* fix(deps): correct supabase package name in pre-commit config

* style: break long line in sqlalchemy writer

* fix(writers): use RelationshipInfo objects for relationships


## v0.15.6 (2025-01-28)

### Refactoring

- **pydantic**: Migrate from constr to Annotated[str, StringConstraints]
  ([#59](https://github.com/kmbhm1/supabase-pydantic/pull/59),
  [`031a53e`](https://github.com/kmbhm1/supabase-pydantic/commit/031a53e8d2b78f2f3de64d49fddf50712c501aa2))


## v0.15.5 (2025-01-27)

### Bug Fixes

- Move ruff to dev dependencies ([#58](https://github.com/kmbhm1/supabase-pydantic/pull/58),
  [`824c74b`](https://github.com/kmbhm1/supabase-pydantic/commit/824c74b6d4cbbec3b9815b25d38d434258a7040e))


## v0.15.4 (2025-01-27)

### Chores

- Correct ruff dependency ([#57](https://github.com/kmbhm1/supabase-pydantic/pull/57),
  [`3454a4e`](https://github.com/kmbhm1/supabase-pydantic/commit/3454a4e7fe7e1635f9bb943d92a85194a2004810))


## v0.15.3 (2025-01-16)

### Chores

- Upgrade package dependencies ([#54](https://github.com/kmbhm1/supabase-pydantic/pull/54),
  [`4b3efe2`](https://github.com/kmbhm1/supabase-pydantic/commit/4b3efe260eb4e381bde8b2adde107be238f3ef60))


## v0.15.2 (2024-12-24)

### Bug Fixes

- Upgrade jinja to 3.1.5 ([#53](https://github.com/kmbhm1/supabase-pydantic/pull/53),
  [`183812e`](https://github.com/kmbhm1/supabase-pydantic/commit/183812e031b89a1be6f85edd57a895a9530bae6d))


## v0.15.1 (2024-12-15)

### Documentation

- Correct typo on README ([#52](https://github.com/kmbhm1/supabase-pydantic/pull/52),
  [`4bef3ac`](https://github.com/kmbhm1/supabase-pydantic/commit/4bef3ac441e7e0ee59df1ed3815a4d33d4624e6d))


## v0.15.0 (2024-12-14)

### Features

- Support pulling from schemas other than public
  ([#51](https://github.com/kmbhm1/supabase-pydantic/pull/51),
  [`64031d7`](https://github.com/kmbhm1/supabase-pydantic/commit/64031d77e49f4b2e56d9995aa78251bb419c5623))

* feat: expand generating capabilities to non-public schemas


## v0.14.6 (2024-10-30)

### Bug Fixes

- Correct import for datetime (dot) datetime, time, and date
  ([#49](https://github.com/kmbhm1/supabase-pydantic/pull/49),
  [`9f72bcd`](https://github.com/kmbhm1/supabase-pydantic/commit/9f72bcd8cf0aa78c113bd7c042747b3ea0d2fcca))


## v0.14.5 (2024-08-23)

### Bug Fixes

- Remove out of scope code ([#47](https://github.com/kmbhm1/supabase-pydantic/pull/47),
  [`1454654`](https://github.com/kmbhm1/supabase-pydantic/commit/1454654f921663ab12a4f19cc67c1932324efaec))


## v0.14.4 (2024-08-22)

### Refactoring

- Update dependencies and dev status ([#46](https://github.com/kmbhm1/supabase-pydantic/pull/46),
  [`6f16225`](https://github.com/kmbhm1/supabase-pydantic/commit/6f16225b35cc0d8d611756e249a1d5e7fbd7c29c))

* refactor: update dependencies and dev status * refactor: update poetry.lock


## v0.14.3 (2024-08-15)

### Documentation

- Update SQL example ([#45](https://github.com/kmbhm1/supabase-pydantic/pull/45),
  [`5f8f84f`](https://github.com/kmbhm1/supabase-pydantic/commit/5f8f84ffdab21911725a4bdd632da7647b4e2eba))


## v0.14.2 (2024-08-15)

### Bug Fixes

- Refine how dates are organized within a given row for a table
  ([#44](https://github.com/kmbhm1/supabase-pydantic/pull/44),
  [`72927e7`](https://github.com/kmbhm1/supabase-pydantic/commit/72927e76dff853c13df7f6828006bd6890fc210d))


## v0.14.1 (2024-08-14)

### Bug Fixes

- Refine fake data generator ([#43](https://github.com/kmbhm1/supabase-pydantic/pull/43),
  [`873a4d6`](https://github.com/kmbhm1/supabase-pydantic/commit/873a4d651bae12a06ce6de163760471742d4c074))


## v0.14.0 (2024-08-13)

### Features

- Add seed data generator for models ([#42](https://github.com/kmbhm1/supabase-pydantic/pull/42),
  [`cd7c97b`](https://github.com/kmbhm1/supabase-pydantic/commit/cd7c97bcee6d52d0bbdb36b8c58ceb45e0131707))

* feat: add poc of seed data generator * chore: add poc file for relationship viz generators and
  other functions * feat: fix fake data formatting for final sql file * test: corrected existing
  tests for fake data generator * test: add tests for new fake generation methods * feat: add
  seed.sql generator for models * ci: exclude poc folder fo checking


## v0.13.1 (2024-08-06)

### Documentation

- Update conda install instructions ([#41](https://github.com/kmbhm1/supabase-pydantic/pull/41),
  [`8846811`](https://github.com/kmbhm1/supabase-pydantic/commit/884681173067f45444eb366086d0ebc0efee65f5))

- Update README ([#40](https://github.com/kmbhm1/supabase-pydantic/pull/40),
  [`2487307`](https://github.com/kmbhm1/supabase-pydantic/commit/2487307896bcace748d75b0c6635c179e45dfdf5))


## v0.13.0 (2024-08-05)

### Features

- Update version logic to dts and latest schema
  ([#39](https://github.com/kmbhm1/supabase-pydantic/pull/39),
  [`06193cb`](https://github.com/kmbhm1/supabase-pydantic/commit/06193cb0b8c7d9bd599f5e8198912e64a0499836))

* feat: add ability to inherit from all-null parent classes in pydantic fastapi models * feat:
  change versioning to datetime


## v0.12.0 (2024-08-05)

### Features

- Add ability to inherit from all-null parent classes in pydantic fastapi models
  ([#38](https://github.com/kmbhm1/supabase-pydantic/pull/38),
  [`6c6c673`](https://github.com/kmbhm1/supabase-pydantic/commit/6c6c67320b701c3208775a620f2fc46a89d65380))


## v0.11.0 (2024-08-04)

### Documentation

- Correct linkedin url ([#36](https://github.com/kmbhm1/supabase-pydantic/pull/36),
  [`d55991d`](https://github.com/kmbhm1/supabase-pydantic/commit/d55991dd4fe6cc48e65a9e3d63783e4e8313181f))

### Features

- Add db-url connector ([#37](https://github.com/kmbhm1/supabase-pydantic/pull/37),
  [`42fe787`](https://github.com/kmbhm1/supabase-pydantic/commit/42fe787628ba802f398bae94b41006b7db6c7918))

* feat: add db-url connector


## v0.10.0 (2024-08-01)

### Documentation

- Rm invalid refs ([#33](https://github.com/kmbhm1/supabase-pydantic/pull/33),
  [`e8c8717`](https://github.com/kmbhm1/supabase-pydantic/commit/e8c87177979b2b6300cbbf326f0cdb1add10e1d9))

- Update light mode styling and code block in example
  ([#34](https://github.com/kmbhm1/supabase-pydantic/pull/34),
  [`0e0b160`](https://github.com/kmbhm1/supabase-pydantic/commit/0e0b1609595ee7a33e18f00e1064d0dafe109bf7))

### Features

- Update sqlalchemy writer for v2 ([#35](https://github.com/kmbhm1/supabase-pydantic/pull/35),
  [`1c5b9a5`](https://github.com/kmbhm1/supabase-pydantic/commit/1c5b9a519a0211e1d1bcf674f51504ff7f044995))

- feat: ref https://docs.sqlalchemy.org/en/20/orm/declarative_tables.html


## v0.9.0 (2024-07-31)

### Features

- Add homepage ([#32](https://github.com/kmbhm1/supabase-pydantic/pull/32),
  [`6407452`](https://github.com/kmbhm1/supabase-pydantic/commit/6407452d68ed6c4e7e4f5228996fba783bd31feb))

* chore: add homepage * docs: update README


## v0.8.4 (2024-07-31)

### Bug Fixes

- Rm reference to mkdocs-click ([#31](https://github.com/kmbhm1/supabase-pydantic/pull/31),
  [`4ae71f2`](https://github.com/kmbhm1/supabase-pydantic/commit/4ae71f26fbfd0dafe58bd107fc5a7f17449a3afd))


## v0.8.3 (2024-07-31)

### Bug Fixes

- Remove mkdocs-click ([#30](https://github.com/kmbhm1/supabase-pydantic/pull/30),
  [`79f6783`](https://github.com/kmbhm1/supabase-pydantic/commit/79f678328db072b4a9c7e9a645349f5eeed8e288))


## v0.8.2 (2024-07-31)

### Bug Fixes

- Mkdocs deploy 2 ([#29](https://github.com/kmbhm1/supabase-pydantic/pull/29),
  [`4aaf224`](https://github.com/kmbhm1/supabase-pydantic/commit/4aaf2246f659d2dfbcdb4c5bee7e100910ec4950))


## v0.8.1 (2024-07-31)

### Bug Fixes

- Mkdocs deploy ([#28](https://github.com/kmbhm1/supabase-pydantic/pull/28),
  [`27dd29c`](https://github.com/kmbhm1/supabase-pydantic/commit/27dd29cbeecb27e2b3960b8d2de245b7e1f579a5))


## v0.8.0 (2024-07-31)

### Continuous Integration

- Fix codecov upload ([#26](https://github.com/kmbhm1/supabase-pydantic/pull/26),
  [`e4551e8`](https://github.com/kmbhm1/supabase-pydantic/commit/e4551e84636dd680df1a1608370bcebcfafd4b11))

### Features

- Add github pages site with mkdocs ([#27](https://github.com/kmbhm1/supabase-pydantic/pull/27),
  [`ee9eba7`](https://github.com/kmbhm1/supabase-pydantic/commit/ee9eba7e549bc35684eaf6ba4daf1d6489611cc8))

* feat(docs): add mkdocs * feat(docs): add basic nav structure and starter docs * feat(docs):
  integrate reading from root changelog * feat(docs): add purpose statement * chore: update poetry
  lock * feat(docs): add automatic cli docs, updates for code blocks * feat(local-option): enable
  automatic env variables for local connections * feat(docs): add logo and new styling to light/dark
  * feat(docs): completed getting started section * feat(docs): complete examples and API *
  feat(docs): styling changes and add mkdocs deploy action * test: fix clean_directories test


## v0.7.0 (2024-07-29)

### Features

- Add full coverage testing, testing coverage checking, and coverage reporting
  ([#25](https://github.com/kmbhm1/supabase-pydantic/pull/25),
  [`f84dd83`](https://github.com/kmbhm1/supabase-pydantic/commit/f84dd8381a187d1035df89a158af05400d2e6336))

* test: update db tests and cleanup * test: update sorting tests * test: update util tests * test:
  update coverage passing * test: update writer abc, factories, and util tests * test: add
  marshalers tests * test: add pydantic writers tests * test: clean pydantic writers tests * test:
  add sqlalchemy writer tests * test: add cli tests * feat: add full coverage testing and code
  coverage reporting * chore: fix mypy issues * chore: remove incorrect test


## v0.6.2 (2024-07-27)

### Bug Fixes

- Poetry script entry fn ([#24](https://github.com/kmbhm1/supabase-pydantic/pull/24),
  [`06ff101`](https://github.com/kmbhm1/supabase-pydantic/commit/06ff1018cc71df054a867f5eef7aed859b5384fc))


## v0.6.1 (2024-07-26)

### Bug Fixes

- Correct overwrite logic ([#23](https://github.com/kmbhm1/supabase-pydantic/pull/23),
  [`70a02d7`](https://github.com/kmbhm1/supabase-pydantic/commit/70a02d718f5c752cc302504ca57fa69b3231f8df))

* fix: correct overwrite logic * docs: update README with new cli args


## v0.6.0 (2024-07-26)

### Documentation

- Community guidelines ([#20](https://github.com/kmbhm1/supabase-pydantic/pull/20),
  [`865ecf2`](https://github.com/kmbhm1/supabase-pydantic/commit/865ecf292dda8a89eab64489396eaed09f250121))

* docs: add CODE_OF_CONDUCT.md * docs: add SUPPORT.md * docs: add SECURITY.md (#17) * docs: add bug
  report and feature request templates (#18) * chore: remove .vscode * docs: add CODEOWNERS * docs:
  add FUNDING.yml (#19) * docs: add CONTRIBUTING.md

- Fix broken links ([#21](https://github.com/kmbhm1/supabase-pydantic/pull/21),
  [`be69b73`](https://github.com/kmbhm1/supabase-pydantic/commit/be69b732743c2db75a7f7aa88b2d954006feb037))

### Features

- Convert writers to Abstract Base Class and reformate CLI with args like supabase-cli gen function
  ([#22](https://github.com/kmbhm1/supabase-pydantic/pull/22),
  [`d23b88d`](https://github.com/kmbhm1/supabase-pydantic/commit/d23b88d29be7497c7cc5e67e4fc4615f22605537))

* feat(cli-refine-1): move utility functions and add example args for revised cli, like supabase cli
  generate cmd * feat(writer-abc): starter for abc's for new writer classes * feat(writer-abc): add
  methods to abcs and factories for writers * feat(writer-abc): implement pydantic fastapi writer
  from abc * feat(writer-abc): pre-commit updates * feat(writer-abc): updates for jsonapi pydantic
  writer * feat(writer-abc): updates for fastapi sqlalchemy writer * feat(writer-abc): updates for
  jsonapi sqlalchemy writer * feat(writer-abc): rm original writer.py * feat(writer-abc): add ruff
  formatting step for generated files * feat(cli-refine-1): convert cli to be like supabase cli gen
  fn * test: temporary update threshold for failing coverge * chore: change lint and type checking
  in action to verbose


## v0.5.0 (2024-07-21)

### Features

- **pre-commit**: Add pre commits, linting, formatting, pyrpoject.toml config, and tests
  ([#16](https://github.com/kmbhm1/supabase-pydantic/pull/16),
  [`6b686e8`](https://github.com/kmbhm1/supabase-pydantic/commit/6b686e86ce699e0ae5c4a9014a971b30d7bc01a1))

* docs: update pyproject and docs * style: import sorting * style: ruff format * feat(pre-commit):
  add pre-commit and commitizen * feat(pre-commit): add lint checking with ruff to github action,
  correct linting errors * feat(pre-commit): integrate mypy * feat: add toml configuration * fix:
  compensate for array notation in type maps * feat: add testing * feat(pre-commit): missing types
  for toml * feat(pre-commit): fix coverage run in action * feat(pre-commit): fix pytest coverage
  test and check in action * feat(pre-commit): fix test and coverage * feat(pre-commit): re-add
  verbose with testing step in action * feat(pre-commit): remove uneccessary step for reporting


## v0.4.0 (2024-07-19)

### Features

- **add-writer**: Cleanup ([#15](https://github.com/kmbhm1/supabase-pydantic/pull/15),
  [`5d80031`](https://github.com/kmbhm1/supabase-pydantic/commit/5d80031e916e6b62689282dc5da3acad96ae63ef))


## v0.3.0 (2024-07-19)

### Features

- **add-writer**: Updates to rerun pipeline
  ([#14](https://github.com/kmbhm1/supabase-pydantic/pull/14),
  [`c7be9e5`](https://github.com/kmbhm1/supabase-pydantic/commit/c7be9e5a4970ed3f669078cf67d2b648700b5099))


## v0.2.1 (2024-07-12)

### Bug Fixes

- **cicd**: Change strategy for poetry install
  ([#12](https://github.com/kmbhm1/supabase-pydantic/pull/12),
  [`825c4e2`](https://github.com/kmbhm1/supabase-pydantic/commit/825c4e2551d8d5f5d51e83e0e1e9c977b50f5219))

- **cicd**: Change version of python semantic release
  ([#11](https://github.com/kmbhm1/supabase-pydantic/pull/11),
  [`1a0ef1c`](https://github.com/kmbhm1/supabase-pydantic/commit/1a0ef1c075e9d6c3a393a079c03682828e821ee1))

- **cicd**: Fix wrong version pointer and add build command
  ([#10](https://github.com/kmbhm1/supabase-pydantic/pull/10),
  [`ded4864`](https://github.com/kmbhm1/supabase-pydantic/commit/ded486454834ca0811c03dae3c9333e1e4713a6d))


## v0.2.0 (2024-07-12)

### Bug Fixes

- **cicd**: Add github app for bypass ([#8](https://github.com/kmbhm1/supabase-pydantic/pull/8),
  [`127b52e`](https://github.com/kmbhm1/supabase-pydantic/commit/127b52ec7bd84d8ade10dc617a3e077d0371006e))

- **cicd**: Fix pipeline for deploy and cleanup
  ([`10f240b`](https://github.com/kmbhm1/supabase-pydantic/commit/10f240b16e9d280e63fcf2f06c2ca7ef8b601102))

- **cicd**: Fix pipeline for deploy and cleanup, part 2
  ([`40096e3`](https://github.com/kmbhm1/supabase-pydantic/commit/40096e3c09d5b4b341970b0c39104b05d6f6d725))

- **cicd**: Test-pr ([#9](https://github.com/kmbhm1/supabase-pydantic/pull/9),
  [`d410d2f`](https://github.com/kmbhm1/supabase-pydantic/commit/d410d2f59c1fba0ca3d879a8749dbfd7e1819627))

- **cicd**: Testing PR and pipeline deploy
  ([#7](https://github.com/kmbhm1/supabase-pydantic/pull/7),
  [`1c75c55`](https://github.com/kmbhm1/supabase-pydantic/commit/1c75c5542d4a8186d61c8791084d14825bc7d3d7))

- **missing-build-step**: Add missing build step to action
  ([#5](https://github.com/kmbhm1/supabase-pydantic/pull/5),
  [`9b122ae`](https://github.com/kmbhm1/supabase-pydantic/commit/9b122ae7f127465539c17b1b10d2bc65b3bd6146))

- **missing-dist**: Adding dist_path to semantic_release config
  ([#3](https://github.com/kmbhm1/supabase-pydantic/pull/3),
  [`ea3f5d4`](https://github.com/kmbhm1/supabase-pydantic/commit/ea3f5d43424ff621108c4507d1b22672cbcef81a))

- **pipeline-build**: Add missing poetry build command
  ([#4](https://github.com/kmbhm1/supabase-pydantic/pull/4),
  [`5a845e8`](https://github.com/kmbhm1/supabase-pydantic/commit/5a845e8579127911a10c6598d5a12b19016a8157))

- **vscode-dir**: Remove .vscode tracking ([#2](https://github.com/kmbhm1/supabase-pydantic/pull/2),
  [`eed989b`](https://github.com/kmbhm1/supabase-pydantic/commit/eed989b39fa7448de60ee84c3dc8e8da544f22c0))

### Features

- **deploy-prod**: Add publish to pypi step
  ([#6](https://github.com/kmbhm1/supabase-pydantic/pull/6),
  [`cac019e`](https://github.com/kmbhm1/supabase-pydantic/commit/cac019eeb58e60197777c7872d0848e124d9187a))


## v0.1.0 (2024-07-09)
