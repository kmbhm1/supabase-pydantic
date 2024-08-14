# CHANGELOG

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
