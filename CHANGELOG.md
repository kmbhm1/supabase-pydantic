# CHANGELOG

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
