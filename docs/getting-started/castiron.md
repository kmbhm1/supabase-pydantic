# supabase-pydantic and castiron

!!! info "Project status (August 2026)"
    supabase-pydantic is in **maintenance mode**. Bug fixes and dependency updates
    continue, nothing is being removed, and no end-of-life date has been set. New feature
    work has moved to [castiron](https://github.com/kmbhm1/castiron), its successor.

This page exists so you can decide, with accurate information, whether castiron is worth
your attention yet. For a good number of projects the honest answer today is *not yet* —
castiron is `0.1.0` and pre-alpha, and supabase-pydantic still does several things it
cannot.

## What castiron is

castiron is a schema→typed-code compiler for Python, by the same author, and it carries
supabase-pydantic's schema-fidelity engine onto a source-agnostic architecture: pluggable
**sources** parse a schema into one formalized **Schema IR**, and pluggable **emitters**
turn that IR into typed code.

The practical difference today is where the schema comes from. supabase-pydantic
introspects a live database over a connection. castiron's first source reads the OpenAPI
document that PostgREST publishes at a Supabase project's API root — one authenticated
HTTP request, no driver, no connection string:

```bash
pip install cast-iron

export CASTIRON_KEY='eyJhbGciOi...'
castiron gen --from https://abcdefgh.supabase.co --emit pydantic
```

The distribution on PyPI is `cast-iron`, hyphenated, because PyPI does not allow
`castiron` as a distribution name. The command you run and the package you import are
`castiron`, unhyphenated.

## What ships today

castiron `0.1.0` is one command (`gen`), one source (OpenAPI/PostgREST), and one emitter
(Pydantic v2). Its API and its generated output may change between releases.

| Capability | supabase-pydantic | castiron 0.1.0 |
| --- | --- | --- |
| Pydantic v2 models — Row, Insert, Update, enums, foreign-key relationships | yes | yes |
| Generation with no database connection, from a Supabase URL or a saved OpenAPI file | no | yes |
| SQLAlchemy models (`--type sqlalchemy`) | yes | planned, not shipped |
| Live Postgres connection (`--local`, `--db-url`) | yes | planned, not shipped |
| MySQL (`--db-type mysql`) | yes | not available |
| Faker seed data (`--seed`) | yes | not available |
| A `check` mode that fails CI on schema drift | no | planned, not shipped |

"Planned" is castiron's own word for these, from
[What works today](https://kmbhm1.github.io/castiron/#what-works-today); no dates are
attached to any of them.

## What the OpenAPI source cannot see

Reading an API description instead of a database catalogue has a real cost, and it is the
thing most likely to matter to you. PostgREST's OpenAPI document does not encode unique or
check constraints, identity/generated columns, exact integer widths below `bigint`, or
function return types — so castiron cannot see them either. It does not guess at them; it
documents the gap and warns when one of these limits is about to change your output.

castiron's
[What the OpenAPI source can and cannot see](https://kmbhm1.github.io/castiron/sources/openapi/)
covers this in full. Read it before you trust a generated constraint.

## Should you move yet?

**Stay with supabase-pydantic** if you generate SQLAlchemy models or Faker seed data, read
from MySQL, read from a Postgres database that is not fronted by PostgREST, or depend on
schema facts that only a live catalogue carries.

**castiron may be worth a look** if you generate Pydantic v2 models from a Supabase
project and you would like that generation to run in CI without database credentials —
keeping in mind that it is pre-alpha.

Either way, you do not have to decide now. supabase-pydantic keeps working, and fixes keep
landing.

## There is no automated migration

castiron is a separate tool with its own CLI, its own configuration (a `[tool.castiron]`
table in your `pyproject.toml`), and its own generated output. Nothing converts a
supabase-pydantic setup into a castiron one, and the generated files are not drop-in
identical. To evaluate it, install it alongside supabase-pydantic, generate into a
separate directory, and compare the results against what you have.

## Where to look

- [castiron documentation](https://kmbhm1.github.io/castiron/)
- [castiron quickstart](https://kmbhm1.github.io/castiron/getting-started/quickstart/)
- [castiron CLI reference](https://kmbhm1.github.io/castiron/reference/cli/)
- [castiron repository and issues](https://github.com/kmbhm1/castiron)

Issues with supabase-pydantic itself still belong
[here](https://github.com/kmbhm1/supabase-pydantic/issues/new/choose) — see
[Getting help](getting-help.md).
