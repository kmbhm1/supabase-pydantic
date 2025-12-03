# CHANGELOG

## v0.26.3 (2025-12-03)

### Fix

* fix: dependabot alert (#120) ([`42c8e26`](https://github.com/kmbhm1/supabase-pydantic/commit/42c8e260d93f5fc8b4b15e25d3f01023c0bfff42))

## v0.26.2 (2025-10-17)

### Fix

* fix: semantic release build cmd (#119) ([`e94c34a`](https://github.com/kmbhm1/supabase-pydantic/commit/e94c34a955598ffdd4aa830f07e46c7df9ddb0c9))

* fix: python build command in semantic release (#118) ([`5066162`](https://github.com/kmbhm1/supabase-pydantic/commit/5066162de0a9f66ca76693c1fca876de5e0c1183))

* fix: incorrect table child table types and singularize bug &amp; semantic versioning errors (#117)

* fix: singularization and incorrect collection checking

* test: update tests

* chore: update changelog

* fix: update semantic release configuration to resolve changelog generation ([`d4f8489`](https://github.com/kmbhm1/supabase-pydantic/commit/d4f8489dc6003392c355e5a337f5fd4d6b009db7))

## v0.26.1 (2025-09-29)

### Fix

* fix: extend JSON field types to support list[dict] and list[Any] variants (#115) ([`f64d600`](https://github.com/kmbhm1/supabase-pydantic/commit/f64d600f956525ce5b20f1485d4e44eb32bffbbc))

## v0.26.0 (2025-09-26)

### Feature

* feat: add ability to singularize class names (#113)

* feat: add option to singularize class names

* docs: add guide for using singular class names

* test: add singular_names flag support to gen command tests

* feat: pass singular_names parameter to writer instances for consistent naming; add integration tests

* fix: pass singular_names to base writer to ensure consistent class naming

* test: add support for --no-crud-models flag in singular names test

* test: fix for tox

* test: remove test for later ([`73cd6cf`](https://github.com/kmbhm1/supabase-pydantic/commit/73cd6cf600bd2e4eb49929b1346cfd096a1e80eb))

## v0.25.7 (2025-09-24)

### Fix

* fix: modify enum type generation and views in schema marshaling to be namespace independent (#111)

* fix: modify enum type generation and views in schema marshaling to be namespace independent

* docs: add changelog entries for v0.25.0 through v0.25.6 releases

* fix: inverted flag logic ([`1b25af7`](https://github.com/kmbhm1/supabase-pydantic/commit/1b25af78b9e1e0c1a20619d0df520ab58917ba41))

## v0.25.6 (2025-09-18)

### Documentation

* docs: add PyPI monthly downloads badge to README (#109) ([`81f910a`](https://github.com/kmbhm1/supabase-pydantic/commit/81f910a82e3cfd73ecec099fa5c2faec5ba88af1))

## v0.25.5 (2025-09-18)

### Fix

* fix: add missing decimal import for numeric and float types in SQLAlchemy type maps (#108) ([`34cc805`](https://github.com/kmbhm1/supabase-pydantic/commit/34cc8058bc5a5f59abc192444cd1f3c7b53778bc))

## v0.25.4 (2025-09-18)

### Fix

* fix: update datetime type references to use fully qualified paths (#107) ([`ab87c48`](https://github.com/kmbhm1/supabase-pydantic/commit/ab87c48adc08ede9d7aa278f8f71ce039ef98e86))

## v0.25.3 (2025-09-17)

### Fix

* fix: add proper datetime imports and handle timezone columns in SQLAlchemy schema generation (#106) ([`a99c5f1`](https://github.com/kmbhm1/supabase-pydantic/commit/a99c5f11295dd75bf8e1c9b520e7dd055914adb1))

## v0.25.2 (2025-09-16)

### Fix

* fix(types): add missing imports for array element types (#104) ([`fce553c`](https://github.com/kmbhm1/supabase-pydantic/commit/fce553c749b20cc7f09dec2e8af7a4040faacec2))

## v0.25.1 (2025-09-14)

### Fix

* fix: enhance enum handling and naming (#103)

* fix: enhance enum handling and logging for PostgreSQL array types

* fix: improve error handling and logging in ruff formatting process

* fix: add support for column comments in MySQL schema marshaler

* fix: correct warning message in ruff formatting test ([`1a1fbaa`](https://github.com/kmbhm1/supabase-pydantic/commit/1a1fbaa174bec5672ca8fda37665818b62abfa04))

## v0.25.0 (2025-09-14)

### Feature

* feat: add descriptions to Pydantic field types and future support Python 3.14 (#102)

* feat: added support for getting column description from postgres and mysql

* refactor: add Python 3.14 support, fix tests, update CHANGELOG

* fix: escape quotes in column description to prevent syntax errors

* test: add unit test for column descriptions in Pydantic fields with escaping

---------

Co-authored-by: Adrián Gallego Castellanos &lt;kugoad@gmail.com&gt; ([`f9c7b20`](https://github.com/kmbhm1/supabase-pydantic/commit/f9c7b20faa7aecb08953d6c6005aae48b5c7f6c1))

## v0.24.2 (2025-08-26)

### Chore

* chore: align mysql-connector for conda (#100) ([`846449e`](https://github.com/kmbhm1/supabase-pydantic/commit/846449e99655ff4a4af348e0d3d32d5421cc7f7a))

## v0.24.1 (2025-08-26)

### Documentation

* docs: update README (#99) ([`143964e`](https://github.com/kmbhm1/supabase-pydantic/commit/143964eab1e36af0ae458e1a0b94ecf459e39417))

## v0.24.0 (2025-08-26)

### Feature

* feat: add mysql support (#98)

* chore: housekeeping

* feat: add types-pymysql

* feat: implement database, connector, and marshaling abstraction with PostgreSQL, working version

* refactor: reorganize postgres-specific code into dedicated drivers directory

* feat: first working version of mysql connector

* refactor: correct python typing for mysql generation

* chore: mypy cleanup

* chore: mypy fixes

* test: correct test startup errors

* test: fix failing tests

* test: add new tests for increased coverage

* test: increase coverage to above threshold

* test: finalize testing

* refactor: improve logging

* chore: correct type issue

* refactor: resolution of connection parameters

* fix: misleading warning messages

* test: fix tests

* fix: incorrect mapping by database type

* fix: issue-84

* refactor: log time fmt

* docs: update docs

* feat: add vulture

* docs: cleanup

* docs: fix link

* chore: vulture changes

* refactor: ignore whitelist ([`0a27a58`](https://github.com/kmbhm1/supabase-pydantic/commit/0a27a58f00d47d890b9a0d7c27451082d64daee0))

## v0.23.0 (2025-08-18)

### Feature

* feat: add sqlalchemy generator (#96)

* feat: implement sqlalchemy writer

* chore: add explicit type hints to variables and fix string quote consistency

* test: update sqlalchemy writer tests to match new class docs and nullable columns

* docs: add SQLAlchemy ORM model generation with Insert/Update variants ([`b3cafa5`](https://github.com/kmbhm1/supabase-pydantic/commit/b3cafa59d895536ba58ff6219ab532a041138fd2))

## v0.22.3 (2025-08-18)

### Ci

* ci: update test coverage on failure (#94)

* refactor: README downloads to pepy

* ci: enhance test coverage reporting with XML output and test results upload

* fix: wrong codecov impl ([`c5c76a2`](https://github.com/kmbhm1/supabase-pydantic/commit/c5c76a2190cdc16f9b40bbd136a48cda6d5b0075))

### Documentation

* docs: update CHANGELOG.md with missing entries through v0.22.2 (#95) ([`65dcc00`](https://github.com/kmbhm1/supabase-pydantic/commit/65dcc00c08d75e3ae02475911118adaab0a77068))

## v0.22.2 (2025-08-18)

### Fix

* fix: remove mkdocs-click (#93) ([`f4d246b`](https://github.com/kmbhm1/supabase-pydantic/commit/f4d246ba5c24c25cd73bd1546a06b18b35966ac8))

## v0.22.1 (2025-08-18)

### Fix

* fix: fix failing ci deployment (#92) ([`511ddf3`](https://github.com/kmbhm1/supabase-pydantic/commit/511ddf3c552c67b7895b7a1cd2b9419b2819d508))

## v0.22.0 (2025-08-18)

### Feature

* feat: restructure project organization and enhance logging (#91)

* feat: initialize src project structure with core modules

* refactor: reorganize utility functions into separate modules for better organization

* refactor: reorganize constants into new src modules

* refactor: reorganize dataclasses into src modules

* refactor: reorganize json into src modules

* refactor: reorganize exceptions into src modules

* refactor: reorganize faker to src module

* refactor: reorganize db into src module

* refactor: reorganize sorting into src module

* refactor: reorganize marshalers into src module

* refactor: reorganize writers abstract classes and util into src module

* refactor: reorganize sqlalchemy and pydantic writers into src module

* refactor: reorganize factories into src module

* refactor: reorganize remaining files into src module

* fix: import errors for working version

* chore: remove original supabase_pydantic parent folder

* chore: correct pre-commit errors

* test: correct import errors

* test: corrected all patch path errors and other changes from src reorganization

* feat: replace logging with loguru

* fix: type check

* chore: linting and reorganization changes; addition for __str__ methods for testing

* refactor: reorganize test files into modular directory structure

* refactor: remove previous tests

* refactor: add new and reorganized tests

* test: fix tox missing yaml issue

* fix: lint error and missing yaml types

* chore: add .DS_Store to gitignore

* ci: add code coverage reporting and improve CI/CD workflow structure ([`f04d154`](https://github.com/kmbhm1/supabase-pydantic/commit/f04d15425be8b9a9dbea1962396a52c1f2477aa6))

## v0.21.0 (2025-08-10)

### Feature

* feat: add option to disable Pydantic&#39;s model_ prefix protection (#90)

* feat: add option to disable Pydantic&#39;s model_ prefix protection

* chore: formatting

* test: add test coverage for enum array column type handling and processing ([`a1aadd2`](https://github.com/kmbhm1/supabase-pydantic/commit/a1aadd23caf3a2669ea0c4a47abff0007ac942fa))

## v0.20.0 (2025-07-30)

### Feature

* feat: improve array type handling in Pydantic models (#88)

* feat: add support for array types in Pydantic model generation

* test: consolidate array type handling tests and add enum array support

* chore: revert changes from first commit

* refactor: add udt_name to GET_ALL_PUBLIC_TABLES_AND_COLUMNS

* feat: add support for enum arrays in Pydantic model generation

* chore: missing import

* feat: add support for PostgreSQL array types with proper Pydantic list typing ([`7e0c0b9`](https://github.com/kmbhm1/supabase-pydantic/commit/7e0c0b9e5dbae18dadb3a44e8a405d4867fdc37c))

## v0.19.8 (2025-07-30)

### Fix

* fix: add common business terms to reserved column name exceptions (#87)

* feat: add &#39;credits&#39; as reserved column name exception

* feat: add more business term exceptions to reserved column name check ([`da4be98`](https://github.com/kmbhm1/supabase-pydantic/commit/da4be98ab7b11f5e8a204211a1072eba8de547e9))

## v0.19.7 (2025-06-19)

### Fix

* fix: upgrade urllib3 from 2.3.0 to 2.5.0 (#83) ([`79c9c0c`](https://github.com/kmbhm1/supabase-pydantic/commit/79c9c0ca5877da644dcac90d03b39951f4e48cbc))

## v0.19.6 (2025-06-13)

### Fix

* fix: update requests to &gt;=2.32.4 to address security vulnerability (#82)

- Addresses Dependabot alert #7 regarding .netrc credentials leak via malicious URLs
- Explicitly pin requests to secure version to ensure all transitive dependencies use the patched version
- CVE reference: https://seclists.org/fulldisclosure/2025/Jun/2 ([`5c77f85`](https://github.com/kmbhm1/supabase-pydantic/commit/5c77f85055ca5233a74499ffbf04377d31adc1b6))

## v0.19.5 (2025-06-03)

### Fix

* fix(print): fix keyerror on printing (#80)

* fix(print): fix keyerror on printing

Fix keyerror when attempting to print an error regarding
the key not being found in the given tables dict.

- Note: this also allows the program to continue
execution when the specified table key is not in the
dict of tables for the given schema. Not sure if this is
the original intent

* fix: lint and typing errors on pr-80

---------

Co-authored-by: KB &lt;kmbhm1@gmail.com&gt; ([`3cfe73a`](https://github.com/kmbhm1/supabase-pydantic/commit/3cfe73a7e5408d3218c1faace39f86b3eb4b8c8b))

## v0.19.4 (2025-05-22)

### Fix

* fix: incorrect tox placement in pyproject.toml (#79) ([`5036905`](https://github.com/kmbhm1/supabase-pydantic/commit/50369058913bfca1973a62b04020316396ae8948))

## v0.19.3 (2025-05-22)

### Fix

* fix: Build step in release (#78) ([`a5d729d`](https://github.com/kmbhm1/supabase-pydantic/commit/a5d729d63de03d8aacc3f6b4a928426a23ff824b))

## v0.19.2 (2025-05-22)

### Fix

* fix(gen): Gracefully handle missing ruff during code generation (#77)

* fix(gen): Gracefully handle missing ruff during code generation

The [format_with_ruff](cci:1://file:///Users/godel/Projects/personal/supabase-pydantic/supabase_pydantic/util/sorting.py:18:0-38:83) utility now catches `FileNotFoundError` if the
ruff executable is not found in the environment. Instead of crashing,
it prints a warning and skips the formatting step.

This allows the `sb-pydantic gen` command to complete successfully
even when ruff (a dev dependency) is not installed, improving
robustness for users who install supabase-pydantic as a library.

* refactor: Add RuffNotFoundError for catching in parent

* fix(cli): resolve configuration loading and CLI test failures

- Improve configuration loading to locate pyproject.toml in parent directories
- Modify option defaults to avoid Click initialization errors
- Fix clean command to handle configuration properly
- Ensure CLI returns expected exit codes when invoked without commands
- Restore expected output messages for test compatibility ([`cec7784`](https://github.com/kmbhm1/supabase-pydantic/commit/cec7784d07bce5884d3f7330f886a0c2100113cf))

## v0.19.1 (2025-04-30)

### Fix

* fix: Upgrade version of tox (#76) ([`8f9d8be`](https://github.com/kmbhm1/supabase-pydantic/commit/8f9d8be2e7af701c19d6b9a950926907c7c3040d))

## v0.19.0 (2025-04-30)

### Feature

* feat(cicd): integrate tox for py3.{10,11,12,13} validation in cicd (#75)

* refactor: rm .python-version

* chore: Remove poc

* feat: Integrate tox for multiple Python versions

* feat(cicd): Add tox action(s) for testing with multiple versions

* fix: Potential fix for code scanning alert no. 6: Workflow does not contain permissions

Co-authored-by: Copilot Autofix powered by AI &lt;62310815+github-advanced-security[bot]@users.noreply.github.com&gt;
Signed-off-by: kmbhm1 &lt;kmbhm1@gmail.com&gt;

* fix: Failing dependency install

* fix: Remove dev dependency installation from multi-version tests

* fix: Quotes in pip instal

* chore: Update poetry lock

---------

Signed-off-by: kmbhm1 &lt;kmbhm1@gmail.com&gt;
Co-authored-by: Copilot Autofix powered by AI &lt;62310815+github-advanced-security[bot]@users.noreply.github.com&gt; ([`efe0c88`](https://github.com/kmbhm1/supabase-pydantic/commit/efe0c885392bf201f08b6b310a8750dd5104e40f))

## v0.18.3 (2025-04-28)

### Fix

* fix(security): limit GitHub Actions workflow permissions (#74)

Adds explicit read-only permissions to the build job in python-publish.yml
to follow least privilege principle and address GitHub security alert. ([`7465830`](https://github.com/kmbhm1/supabase-pydantic/commit/7465830f027236aaa9dd116f45074073b1c822bc))

## v0.18.2 (2025-04-28)

### Fix

* fix: bug Annotated imported incorrectly (#73)

* fix: Incorrect Annotated addition
* test: Add test for condition ([`41f911c`](https://github.com/kmbhm1/supabase-pydantic/commit/41f911c13d5a0da1c7f58c14b0a2d0be33724550))

## v0.18.1 (2025-04-19)

### Documentation

* docs: Update copyright (#71) ([`345df88`](https://github.com/kmbhm1/supabase-pydantic/commit/345df88c2ad0b495e920aee8174231a2741ab3ae))

## v0.18.0 (2025-04-17)

### Feature

* feat: Add enum types for BaseModels (#70)

* feat: Add enum types for BaseModels
* feat: Add --no-enums cli argument
* feat: Add enum example article
* test: Add testing for enum generation
* refactor: typing issues
* fix: Type check error ([`b4c060e`](https://github.com/kmbhm1/supabase-pydantic/commit/b4c060e84f5c6858502acb71189a58118a571d80))

## v0.17.4 (2025-03-15)

### Fix

* fix(deps): update Jinja2 to ^3.1.6 to resolve security vulnerabilities (#68) ([`7a263bc`](https://github.com/kmbhm1/supabase-pydantic/commit/7a263bc64e70b6579bdb4ab05279d484ee78006f))

## v0.17.3 (2025-03-07)

### Fix

* fix: update Jinja2 to ^3.1.6 to address security vulnerability (#67) ([`add28df`](https://github.com/kmbhm1/supabase-pydantic/commit/add28dfabd57e3a8c2d26e1eaf78a3b5740e9c84))

## v0.17.2 (2025-02-21)

### Fix

* fix(types): generate correct types for ONE_TO_ONE relationships (#66)

* fix: Debug logging
* feat(marshalers): improve foreign key analysis and cross-schema handling

- Add comprehensive test suite for add_foreign_key_info_to_table_details
- Enhance debug logging with guidance for cross-schema references
- Keep foreign keys even when target table is in another schema
- Ensure proper relationship type detection for Pydantic model generation

This improves support for cross-schema relationships (e.g., public.users -&gt; auth.users)
while maintaining correct type generation in Pydantic models. ([`e889eb3`](https://github.com/kmbhm1/supabase-pydantic/commit/e889eb36cd2ed0b4c78f490c92db15c085defec1))

## v0.17.1 (2025-02-21)

### Fix

* fix(models): correct foreign key relationship types and field names (#65)

Generate appropriate types for relationship fields based on cardinality:
- ONE_TO_ONE -&gt; single instance (Type | None)
- ONE_TO_MANY -&gt; list of instances (list[Type] | None)
- MANY_TO_MANY -&gt; list of instances (list[Type] | None)

This fixes issues where:
- All relationships were incorrectly generated as lists
- Field names were incorrectly using &#39;ids&#39; suffix
- Multiple fields had naming collisions
- Referenced table names were inconsistently included

refactor: consolidate tooling and improve logging
- Replace isort with ruff for import sorting
- Enhance CLI logging with proper configuration
- Improve Makefile documentation and organization ([`368b557`](https://github.com/kmbhm1/supabase-pydantic/commit/368b557013363dc3b91485b7086872e09adecec4))

## v0.17.0 (2025-02-16)

### Feature

* feat: differentiate between insert, update, and select models (#63)

* refactor(pydantic): improve foreign key and relationship field generation

- Keep original column names for foreign keys (e.g., author_id: User)
- Use inflection library for proper pluralization in many relationships
- Fix handling of tables with relationships but no foreign keys
- Add comprehensive tests for pluralization cases

This change ensures more accurate model generation that better reflects
the database schema while maintaining proper type hints based on
relationship types (ONE_TO_ONE, ONE_TO_MANY, MANY_TO_MANY).

* style: organize imports and format code

- Sort and group imports according to PEP8
- Remove unused imports
- Fix line spacing and indentation

* fix(sqlalchemy): standardize newline formatting in model generation

- Remove extra newline after __tablename__ in write_docs method
- Adjust newlines between sections in model output:
  - Single newline after __tablename__
  - Single newline between columns
  - Single newline before section headers
  - Double newline between classes
- Update test assertions to match new formatting

* test(cli): fix schema handling in CLI test cases

- Add proper schema parameter to CLI command invocations
- Fix mock table dictionary and jobs configuration
- Improve test coverage for empty schema scenarios
- Simplify test setup by removing redundant configurations

* fix: line length error

* fix(deps): correct supabase package name in pre-commit config

* style: break long line in sqlalchemy writer

* fix(writers): use RelationshipInfo objects for relationships

* feat(models): add Insert and Update model variants

- Add Insert and Update model variants for each table with appropriate field optionality
- Add --no-crud-models flag to disable generation of Insert/Update models
- Add smoke-test target to Makefile for quick testing

Changes:
- Add is_identity and related properties to ColumnInfo for tracking auto-generated columns
- Update SQL query to fetch identity_generation information
- Enhance WriterClassType enum with INSERT and UPDATE types
- Group field property comments in Insert models for better readability
- Add ruff check --fix to remove unused imports in generated files

This change makes it easier to use the generated models in CRUD operations by:
1. Making auto-generated fields optional in Insert models
2. Making all fields optional in Update models
3. Adding clear documentation about field properties

* feat(models): generate specialized Insert and Update Pydantic models

- Add Insert models that make auto-generated fields optional (e.g., IDs, timestamps)
- Add Update models that make all fields optional for partial updates
- Add generate_crud_models flag to FileWriterFactory for controlling model generation
- Improve docstrings to clarify model generation behavior

Resolves issue with Insert/Update model generation to match TypeScript behavior

* docs: Update mkdocs with new example illustrating Insert and Update generators ([`372aaad`](https://github.com/kmbhm1/supabase-pydantic/commit/372aaad7c6cd2d736ee227347cf20ed8e08b6c91))

## v0.16.0 (2025-02-16)

### Feature

* feat: foreign key fields should be single instances, not lists in generated Pydantic models (#62)

* refactor(pydantic): improve foreign key and relationship field generation

- Keep original column names for foreign keys (e.g., author_id: User)
- Use inflection library for proper pluralization in many relationships
- Fix handling of tables with relationships but no foreign keys
- Add comprehensive tests for pluralization cases

This change ensures more accurate model generation that better reflects
the database schema while maintaining proper type hints based on
relationship types (ONE_TO_ONE, ONE_TO_MANY, MANY_TO_MANY).

* style: organize imports and format code

- Sort and group imports according to PEP8
- Remove unused imports
- Fix line spacing and indentation

* fix(sqlalchemy): standardize newline formatting in model generation

- Remove extra newline after __tablename__ in write_docs method
- Adjust newlines between sections in model output:
  - Single newline after __tablename__
  - Single newline between columns
  - Single newline before section headers
  - Double newline between classes
- Update test assertions to match new formatting

* test(cli): fix schema handling in CLI test cases

- Add proper schema parameter to CLI command invocations
- Fix mock table dictionary and jobs configuration
- Improve test coverage for empty schema scenarios
- Simplify test setup by removing redundant configurations

* fix: line length error

* fix(deps): correct supabase package name in pre-commit config

* style: break long line in sqlalchemy writer

* fix(writers): use RelationshipInfo objects for relationships ([`1484841`](https://github.com/kmbhm1/supabase-pydantic/commit/14848413ec23813c11ff719ac2aea1a3c947b191))

## v0.15.6 (2025-01-28)

### Refactor

* refactor(pydantic): migrate from constr to Annotated[str, StringConstraints] (#59) ([`031a53e`](https://github.com/kmbhm1/supabase-pydantic/commit/031a53e8d2b78f2f3de64d49fddf50712c501aa2))

## v0.15.5 (2025-01-27)

### Fix

* fix: move ruff to dev dependencies (#58) ([`824c74b`](https://github.com/kmbhm1/supabase-pydantic/commit/824c74b6d4cbbec3b9815b25d38d434258a7040e))

## v0.15.4 (2025-01-27)

### Chore

* chore: correct ruff dependency (#57) ([`3454a4e`](https://github.com/kmbhm1/supabase-pydantic/commit/3454a4e7fe7e1635f9bb943d92a85194a2004810))

## v0.15.3 (2025-01-16)

### Chore

* chore: upgrade package dependencies (#54) ([`4b3efe2`](https://github.com/kmbhm1/supabase-pydantic/commit/4b3efe260eb4e381bde8b2adde107be238f3ef60))

## v0.15.2 (2024-12-24)

### Fix

* fix: upgrade jinja to 3.1.5 (#53) ([`183812e`](https://github.com/kmbhm1/supabase-pydantic/commit/183812e031b89a1be6f85edd57a895a9530bae6d))

## v0.15.1 (2024-12-15)

### Documentation

* docs: correct typo on README (#52) ([`4bef3ac`](https://github.com/kmbhm1/supabase-pydantic/commit/4bef3ac441e7e0ee59df1ed3815a4d33d4624e6d))

## v0.15.0 (2024-12-14)

### Feature

* feat: support pulling from schemas other than public (#51)

* feat: expand generating capabilities to non-public schemas ([`64031d7`](https://github.com/kmbhm1/supabase-pydantic/commit/64031d77e49f4b2e56d9995aa78251bb419c5623))

## v0.14.6 (2024-10-30)

### Fix

* fix: correct import for datetime (dot) datetime, time, and date (#49) ([`9f72bcd`](https://github.com/kmbhm1/supabase-pydantic/commit/9f72bcd8cf0aa78c113bd7c042747b3ea0d2fcca))

## v0.14.5 (2024-08-23)

### Fix

* fix: remove out of scope code (#47) ([`1454654`](https://github.com/kmbhm1/supabase-pydantic/commit/1454654f921663ab12a4f19cc67c1932324efaec))

## v0.14.4 (2024-08-22)

### Refactor

* refactor: update dependencies and dev status (#46)

* refactor: update dependencies and dev status
* refactor: update poetry.lock ([`6f16225`](https://github.com/kmbhm1/supabase-pydantic/commit/6f16225b35cc0d8d611756e249a1d5e7fbd7c29c))

## v0.14.3 (2024-08-15)

### Documentation

* docs: update SQL example (#45) ([`5f8f84f`](https://github.com/kmbhm1/supabase-pydantic/commit/5f8f84ffdab21911725a4bdd632da7647b4e2eba))

## v0.14.2 (2024-08-15)

### Fix

* fix: refine how dates are organized within a given row for a table (#44) ([`72927e7`](https://github.com/kmbhm1/supabase-pydantic/commit/72927e76dff853c13df7f6828006bd6890fc210d))

## v0.14.1 (2024-08-14)

### Fix

* fix: refine fake data generator (#43) ([`873a4d6`](https://github.com/kmbhm1/supabase-pydantic/commit/873a4d651bae12a06ce6de163760471742d4c074))

## v0.14.0 (2024-08-13)

### Feature

* feat: add seed data generator for models (#42)

* feat: add poc of seed data generator
* chore: add poc file for relationship viz generators and other functions
* feat: fix fake data formatting for final sql file
* test: corrected existing tests for fake data generator
* test: add tests for new fake generation methods
* feat: add seed.sql generator for models
* ci: exclude poc folder fo checking ([`cd7c97b`](https://github.com/kmbhm1/supabase-pydantic/commit/cd7c97bcee6d52d0bbdb36b8c58ceb45e0131707))

## v0.13.1 (2024-08-06)

### Documentation

* docs: update conda install instructions (#41) ([`8846811`](https://github.com/kmbhm1/supabase-pydantic/commit/884681173067f45444eb366086d0ebc0efee65f5))

* docs: update README (#40) ([`2487307`](https://github.com/kmbhm1/supabase-pydantic/commit/2487307896bcace748d75b0c6635c179e45dfdf5))

## v0.13.0 (2024-08-05)

### Feature

* feat: update version logic to dts and latest schema (#39)

* feat: add ability to inherit from all-null parent classes in pydantic fastapi models
* feat: change versioning to datetime ([`06193cb`](https://github.com/kmbhm1/supabase-pydantic/commit/06193cb0b8c7d9bd599f5e8198912e64a0499836))

## v0.12.0 (2024-08-05)

### Feature

* feat: add ability to inherit from all-null parent classes in pydantic fastapi models (#38) ([`6c6c673`](https://github.com/kmbhm1/supabase-pydantic/commit/6c6c67320b701c3208775a620f2fc46a89d65380))

## v0.11.0 (2024-08-04)

### Documentation

* docs: correct linkedin url (#36) ([`d55991d`](https://github.com/kmbhm1/supabase-pydantic/commit/d55991dd4fe6cc48e65a9e3d63783e4e8313181f))

### Feature

* feat: add db-url connector (#37)

* feat: add db-url connector ([`42fe787`](https://github.com/kmbhm1/supabase-pydantic/commit/42fe787628ba802f398bae94b41006b7db6c7918))

## v0.10.0 (2024-08-01)

### Documentation

* docs: update light mode styling and code block in example (#34) ([`0e0b160`](https://github.com/kmbhm1/supabase-pydantic/commit/0e0b1609595ee7a33e18f00e1064d0dafe109bf7))

* docs: rm invalid refs (#33) ([`e8c8717`](https://github.com/kmbhm1/supabase-pydantic/commit/e8c87177979b2b6300cbbf326f0cdb1add10e1d9))

### Feature

* feat: update sqlalchemy writer for v2 (#35)

- feat: ref https://docs.sqlalchemy.org/en/20/orm/declarative_tables.html ([`1c5b9a5`](https://github.com/kmbhm1/supabase-pydantic/commit/1c5b9a519a0211e1d1bcf674f51504ff7f044995))

## v0.9.0 (2024-07-31)

### Feature

* feat: add homepage (#32)

* chore: add homepage
* docs: update README ([`6407452`](https://github.com/kmbhm1/supabase-pydantic/commit/6407452d68ed6c4e7e4f5228996fba783bd31feb))

## v0.8.4 (2024-07-31)

### Fix

* fix: rm reference to mkdocs-click (#31) ([`4ae71f2`](https://github.com/kmbhm1/supabase-pydantic/commit/4ae71f26fbfd0dafe58bd107fc5a7f17449a3afd))

## v0.8.3 (2024-07-31)

### Fix

* fix: remove mkdocs-click (#30) ([`79f6783`](https://github.com/kmbhm1/supabase-pydantic/commit/79f678328db072b4a9c7e9a645349f5eeed8e288))

## v0.8.2 (2024-07-31)

### Fix

* fix: mkdocs deploy 2 (#29) ([`4aaf224`](https://github.com/kmbhm1/supabase-pydantic/commit/4aaf2246f659d2dfbcdb4c5bee7e100910ec4950))

## v0.8.1 (2024-07-31)

### Fix

* fix: mkdocs deploy (#28) ([`27dd29c`](https://github.com/kmbhm1/supabase-pydantic/commit/27dd29cbeecb27e2b3960b8d2de245b7e1f579a5))

## v0.8.0 (2024-07-31)

### Ci

* ci: fix codecov upload (#26) ([`e4551e8`](https://github.com/kmbhm1/supabase-pydantic/commit/e4551e84636dd680df1a1608370bcebcfafd4b11))

### Feature

* feat: add github pages site with mkdocs (#27)

* feat(docs): add mkdocs
* feat(docs): add basic nav structure and starter docs
* feat(docs): integrate reading from root changelog
* feat(docs): add purpose statement
* chore: update poetry lock
* feat(docs): add automatic cli docs, updates for code blocks
* feat(local-option): enable automatic env variables for local connections
* feat(docs): add logo and new styling to light/dark
* feat(docs): completed getting started section
* feat(docs): complete examples and API
* feat(docs): styling changes and add mkdocs deploy action
* test: fix clean_directories test ([`ee9eba7`](https://github.com/kmbhm1/supabase-pydantic/commit/ee9eba7e549bc35684eaf6ba4daf1d6489611cc8))

## v0.7.0 (2024-07-29)

### Feature

* feat: Add full coverage testing, testing coverage checking, and coverage reporting (#25)

* test: update db tests and cleanup
* test: update sorting tests
* test: update util tests
* test: update coverage passing
* test: update writer abc, factories, and util tests
* test: add marshalers tests
* test: add pydantic writers tests
* test: clean pydantic writers tests
* test: add sqlalchemy writer tests
* test: add cli tests
* feat: add full coverage testing and code coverage reporting
* chore: fix mypy issues
* chore: remove incorrect test ([`f84dd83`](https://github.com/kmbhm1/supabase-pydantic/commit/f84dd8381a187d1035df89a158af05400d2e6336))

## v0.6.2 (2024-07-27)

### Fix

* fix: poetry script entry fn (#24) ([`06ff101`](https://github.com/kmbhm1/supabase-pydantic/commit/06ff1018cc71df054a867f5eef7aed859b5384fc))

## v0.6.1 (2024-07-26)

### Fix

* fix: correct overwrite logic (#23)

* fix: correct overwrite logic
* docs: update README with new cli args ([`70a02d7`](https://github.com/kmbhm1/supabase-pydantic/commit/70a02d718f5c752cc302504ca57fa69b3231f8df))

## v0.6.0 (2024-07-26)

### Documentation

* docs: fix broken links (#21) ([`be69b73`](https://github.com/kmbhm1/supabase-pydantic/commit/be69b732743c2db75a7f7aa88b2d954006feb037))

* docs: community guidelines (#20)

* docs: add CODE_OF_CONDUCT.md
* docs: add SUPPORT.md
* docs: add SECURITY.md (#17)
* docs: add bug report and feature request templates (#18)
* chore: remove .vscode
* docs: add CODEOWNERS
* docs: add FUNDING.yml (#19)
* docs: add CONTRIBUTING.md ([`865ecf2`](https://github.com/kmbhm1/supabase-pydantic/commit/865ecf292dda8a89eab64489396eaed09f250121))

### Feature

* feat: Convert writers to Abstract Base Class and reformate CLI with args like supabase-cli gen function (#22)

* feat(cli-refine-1): move utility functions and add example args for revised cli, like supabase cli generate cmd
* feat(writer-abc): starter for abc&#39;s for new writer classes
* feat(writer-abc): add methods to abcs and factories for writers
* feat(writer-abc): implement pydantic fastapi writer from abc
* feat(writer-abc): pre-commit updates
* feat(writer-abc): updates for jsonapi pydantic writer
* feat(writer-abc): updates for fastapi sqlalchemy writer
* feat(writer-abc): updates for jsonapi sqlalchemy writer
* feat(writer-abc): rm original writer.py
* feat(writer-abc): add ruff formatting step for generated files
* feat(cli-refine-1): convert cli to be like supabase cli gen fn
* test: temporary update threshold for failing coverge
* chore: change lint and type checking in action to verbose ([`d23b88d`](https://github.com/kmbhm1/supabase-pydantic/commit/d23b88d29be7497c7cc5e67e4fc4615f22605537))

## v0.5.0 (2024-07-21)

### Feature

* feat(pre-commit): add pre commits, linting, formatting, pyrpoject.toml config, and tests (#16)

* docs: update pyproject and docs
* style: import sorting
* style: ruff format
* feat(pre-commit): add pre-commit and commitizen
* feat(pre-commit): add lint checking with ruff to github action, correct linting errors
* feat(pre-commit): integrate mypy
* feat: add toml configuration
* fix: compensate for array notation in type maps
* feat: add testing
* feat(pre-commit): missing types for toml
* feat(pre-commit): fix coverage run in action
* feat(pre-commit): fix pytest coverage test and check in action
* feat(pre-commit): fix test and coverage
* feat(pre-commit): re-add verbose with testing step in action
* feat(pre-commit): remove uneccessary step for reporting ([`6b686e8`](https://github.com/kmbhm1/supabase-pydantic/commit/6b686e86ce699e0ae5c4a9014a971b30d7bc01a1))

## v0.4.0 (2024-07-19)

### Feature

* feat(add-writer): cleanup (#15) ([`5d80031`](https://github.com/kmbhm1/supabase-pydantic/commit/5d80031e916e6b62689282dc5da3acad96ae63ef))

## v0.3.0 (2024-07-19)

### Feature

* feat(add-writer): updates to rerun pipeline (#14) ([`c7be9e5`](https://github.com/kmbhm1/supabase-pydantic/commit/c7be9e5a4970ed3f669078cf67d2b648700b5099))

### Unknown

* Add writer class and FastAPI-JSONAPI writing (#13)

* feat(add-writer): add first FileWriter and ClassWriter classes
* feat(add-writer): cleanup for writer classes, add sqlalchemy class writing, add nullable base schema, update cli args
* feat(add-writer): integrate fastapi-jsonapi writing into writer classes, add job configuration for cli
* feat(add-writer): update marshalling logic to incorporate foreign relation types, add sqlalchemy jsonapi starter
* feat(add-writer): finalize marshalling logic and writer for relationships
* feat(add-writer): update todo&#39;s ([`caf2b59`](https://github.com/kmbhm1/supabase-pydantic/commit/caf2b59e399f79c11f3ff4359b4739643def498b))

## v0.2.1 (2024-07-12)

### Fix

* fix(cicd): change strategy for poetry install (#12) ([`825c4e2`](https://github.com/kmbhm1/supabase-pydantic/commit/825c4e2551d8d5f5d51e83e0e1e9c977b50f5219))

* fix(cicd): change version of python semantic release (#11) ([`1a0ef1c`](https://github.com/kmbhm1/supabase-pydantic/commit/1a0ef1c075e9d6c3a393a079c03682828e821ee1))

* fix(cicd): fix wrong version pointer and add build command (#10) ([`ded4864`](https://github.com/kmbhm1/supabase-pydantic/commit/ded486454834ca0811c03dae3c9333e1e4713a6d))

## v0.2.0 (2024-07-12)

### Feature

* feat(deploy-prod): add publish to pypi step (#6) ([`cac019e`](https://github.com/kmbhm1/supabase-pydantic/commit/cac019eeb58e60197777c7872d0848e124d9187a))

### Fix

* fix(cicd): test-pr (#9) ([`d410d2f`](https://github.com/kmbhm1/supabase-pydantic/commit/d410d2f59c1fba0ca3d879a8749dbfd7e1819627))

* fix(cicd): add github app for bypass (#8) ([`127b52e`](https://github.com/kmbhm1/supabase-pydantic/commit/127b52ec7bd84d8ade10dc617a3e077d0371006e))

* fix(cicd): testing PR and pipeline deploy (#7) ([`1c75c55`](https://github.com/kmbhm1/supabase-pydantic/commit/1c75c5542d4a8186d61c8791084d14825bc7d3d7))

* fix(cicd): fix pipeline for deploy and cleanup, part 2 ([`40096e3`](https://github.com/kmbhm1/supabase-pydantic/commit/40096e3c09d5b4b341970b0c39104b05d6f6d725))

* fix(cicd): fix pipeline for deploy and cleanup ([`10f240b`](https://github.com/kmbhm1/supabase-pydantic/commit/10f240b16e9d280e63fcf2f06c2ca7ef8b601102))

* fix(missing-build-step): add missing build step to action (#5) ([`9b122ae`](https://github.com/kmbhm1/supabase-pydantic/commit/9b122ae7f127465539c17b1b10d2bc65b3bd6146))

* fix(pipeline-build): add missing poetry build command (#4) ([`5a845e8`](https://github.com/kmbhm1/supabase-pydantic/commit/5a845e8579127911a10c6598d5a12b19016a8157))

* fix(missing-dist): adding dist_path to semantic_release config (#3) ([`ea3f5d4`](https://github.com/kmbhm1/supabase-pydantic/commit/ea3f5d43424ff621108c4507d1b22672cbcef81a))

* fix(vscode-dir): remove .vscode tracking (#2) ([`eed989b`](https://github.com/kmbhm1/supabase-pydantic/commit/eed989b39fa7448de60ee84c3dc8e8da544f22c0))

## v0.1.0 (2024-07-09)

### Unknown

* Initialize project (#1)

* feat(init): add poetry
* feat(init): add example schema query and conn
* feat(init): add utility fns and main runner
* feat(init): update logic for dataclasses
* feat(init): integrate ruff for linting and formatting
* feat(init): clean up imports
* feat(init): add foreign key relationship info
* feat(init): added alias checking and first draft of fake data generation
* feat(init): project reorganization and fixed import issue; some refinement
* feat(init): add writer for fastapi_jsonapi, pydantic
* feat(init): add first part of foreign key and constraint reconciliation process for fastapi
* feat(init): add deploy; minor changes for init prep ([`e926c2b`](https://github.com/kmbhm1/supabase-pydantic/commit/e926c2b62da4c3e803bbc9ef542e28a18da95c31))

* Initial commit ([`a82aacd`](https://github.com/kmbhm1/supabase-pydantic/commit/a82aacd912901c6d563eca7e03e82b3240a1d4e0))
