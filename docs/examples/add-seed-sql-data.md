# Create Test Data for your SQL Database

This example demonstrates how to create test data for your SQL database using the `--seed` option when generating Pydantic models with `supabase-pydantic`, a very useful feature when you need to populate your database with test data.

!!! info "Please note ..."

    This is a developing feature :hatching_chick:. It is imperfect, so please report any issues you encounter.

## Prerequisites

You should follow the setup & prerequisites guide in the [Slack Clone example](setup-slack-simple-fastapi.md#setup) to initialize your local Supabase instance.

## Generating Seed Data

To generate seed data, you simply need to append the `--seed` option to the `generate` command. For example, run the following command:

``` bash title="Generate Seed Data"
$ sb-pydantic gen --type pydantic --framework fastapi --local --seed

PostGres connection is open.
PostGres connection is closed.
Generating FastAPI Pydantic models...
FastAPI Pydantic models generated successfully: /path/to/your/project/entities/fastapi/schemas_latest.py
File formatted successfully: /path/to/your/project/entities/fastapi/schemas_latest.py
Generating seed data...
Seed data generated successfully: /path/to/your/project/entities/seed_latest.sql
```

Note that the seed sql file will be generated in the `entities` directory of your project: 

``` sql title="seed_latest.sql"
-- role_permissions
INSERT INTO role_permissions (id, role, permission) VALUES (22070, 'admin', 'channels.delete');
INSERT INTO role_permissions (id, role, permission) VALUES (24280, 'admin', 'messages.delete');
INSERT INTO role_permissions (id, role, permission) VALUES (79303, 'moderator', 'channels.delete');
INSERT INTO role_permissions (id, role, permission) VALUES (45911, 'moderator', 'messages.delete');

-- users
INSERT INTO users (id, username, status) VALUES ('0563f439-85ac-4f5f-8529-13d15558ad13', 'Money head second article. Finally or maybe look hospital.', NULL);
INSERT INTO users (id, username, status) VALUES ('f6fc7cb3-c31a-4712-94cd-75deb4e3cb5d', 'Stock method indeed easy turn time perhaps. Defense certainly senior response major never either.', 'OFFLINE');
INSERT INTO users (id, username, status) VALUES ('17fefd16-8a32-4c16-ab3f-4522ca1ebcf6', 'Score with few list parent realize worker. Number maintain data human weight.', 'OFFLINE');
INSERT INTO users (id, username, status) VALUES ('a46bc01e-8fb2-42af-a24b-08353278ef70', 'Treat peace bank.
Also main push special network on. Water require certain phone where.', 'ONLINE');
INSERT INTO users (id, username, status) VALUES ('b9d91a21-ea71-474d-8bc4-8501acc6f354', 'And talk left. They term doctor certain occur resource green.', NULL);
INSERT INTO users (id, username, status) VALUES ('10e802fd-638f-460f-a7a4-c4bf835aaa31', 'Performance attorney toward more decision benefit consider six. Name standard ground also.', 'ONLINE');
INSERT INTO users (id, username, status) VALUES ('219742c4-8c82-4451-9261-dda2af56a2c5', 'Put child hear nature laugh good. Stock place fill fly.', NULL);
INSERT INTO users (id, username, status) VALUES ('eeb86296-aa6d-4821-83a1-953d8a67e5e6', 'Send agree act price material. Various practice adult read.
Record miss somebody building.', 'OFFLINE');
INSERT INTO users (id, username, status) VALUES ('f59e5ea3-1c9c-4c39-9403-611f7bc54676', NULL, 'OFFLINE');
INSERT INTO users (id, username, status) VALUES ('e41df02e-32ca-4c37-81f4-a049293b74d6', NULL, NULL);
INSERT INTO users (id, username, status) VALUES ('4af2536a-e007-4d6e-9874-6a90b9634f30', 'During open painting. Early industry occur question religious leave.', 'ONLINE');

-- user_roles
INSERT INTO user_roles (id, user_id, role) VALUES (13765, '4af2536a-e007-4d6e-9874-6a90b9634f30', 'admin');
INSERT INTO user_roles (id, user_id, role) VALUES (802, '4af2536a-e007-4d6e-9874-6a90b9634f30', 'moderator');
INSERT INTO user_roles (id, user_id, role) VALUES (1808, 'b9d91a21-ea71-474d-8bc4-8501acc6f354', 'admin');
INSERT INTO user_roles (id, user_id, role) VALUES (25453, '0563f439-85ac-4f5f-8529-13d15558ad13', 'moderator');
INSERT INTO user_roles (id, user_id, role) VALUES (24638, '0563f439-85ac-4f5f-8529-13d15558ad13', 'admin');
INSERT INTO user_roles (id, user_id, role) VALUES (25534, '10e802fd-638f-460f-a7a4-c4bf835aaa31', 'admin');
INSERT INTO user_roles (id, user_id, role) VALUES (31827, 'b9d91a21-ea71-474d-8bc4-8501acc6f354', 'moderator');

-- channels
INSERT INTO channels (id, inserted_at, slug, created_by) VALUES (6898, '1982-12-14 04:16:04.417288', 'Break read bill fly born grow. Resource reality push resource ok energy her.', 'e41df02e-32ca-4c37-81f4-a049293b74d6');
INSERT INTO channels (id, inserted_at, slug, created_by) VALUES (7471, '1989-12-28 07:52:18.344641', 'Physical crime meet lay. Work among food maybe. Grow test toward.', 'b9d91a21-ea71-474d-8bc4-8501acc6f354');
INSERT INTO channels (id, inserted_at, slug, created_by) VALUES (49558, '1993-07-04 02:24:36.230160', 'Than really wide camera he response near. Where present well support.', 'f59e5ea3-1c9c-4c39-9403-611f7bc54676');
INSERT INTO channels (id, inserted_at, slug, created_by) VALUES (86035, '2012-12-27 13:09:55.768500', 'According range song up performance lose. Easy effort new. Hotel call people support.', '10e802fd-638f-460f-a7a4-c4bf835aaa31');
INSERT INTO channels (id, inserted_at, slug, created_by) VALUES (6906, '2002-12-26 09:15:50.034564', 'With early yes. Population air heavy.', '219742c4-8c82-4451-9261-dda2af56a2c5');
INSERT INTO channels (id, inserted_at, slug, created_by) VALUES (45562, '1977-03-05 21:06:47.531894', 'Own baby unit service.
Ok small environmental just nearly yes.', 'f6fc7cb3-c31a-4712-94cd-75deb4e3cb5d');
INSERT INTO channels (id, inserted_at, slug, created_by) VALUES (91872, '2011-12-07 11:30:49.754872', 'Draw movement player teach. Base song experience during note.', 'f59e5ea3-1c9c-4c39-9403-611f7bc54676');
INSERT INTO channels (id, inserted_at, slug, created_by) VALUES (55675, '1974-08-18 05:21:57.427831', 'Mission while few skin claim employee list plan. Account agency do night campaign really rule key.', '4af2536a-e007-4d6e-9874-6a90b9634f30');
INSERT INTO channels (id, inserted_at, slug, created_by) VALUES (81981, '1983-06-20 04:50:58.546525', 'Item long music evidence sing home.
Culture what reason buy black common into.', 'f6fc7cb3-c31a-4712-94cd-75deb4e3cb5d');
INSERT INTO channels (id, inserted_at, slug, created_by) VALUES (54550, '1973-09-28 03:17:09.557882', 'Sport push think city beautiful choice. Cover someone amount open.', 'a46bc01e-8fb2-42af-a24b-08353278ef70');
INSERT INTO channels (id, inserted_at, slug, created_by) VALUES (9773, '2011-11-30 17:43:50.013279', 'Maintain real we outside. Enjoy six watch reflect forget more sing.', '219742c4-8c82-4451-9261-dda2af56a2c5');

-- messages
INSERT INTO messages (id, inserted_at, message, user_id, channel_id) VALUES (68800, '1972-03-17 12:53:27.669385', 'Which environmental expert another. Pass tree list national difficult city beautiful still.', '219742c4-8c82-4451-9261-dda2af56a2c5', 9773);
INSERT INTO messages (id, inserted_at, message, user_id, channel_id) VALUES (61665, '2021-07-03 00:44:22.296232', NULL, '4af2536a-e007-4d6e-9874-6a90b9634f30', 9773);
INSERT INTO messages (id, inserted_at, message, user_id, channel_id) VALUES (621, '1982-01-17 14:14:21.873722', 'Fact soldier employee language budget stop.', '219742c4-8c82-4451-9261-dda2af56a2c5', 91872);
INSERT INTO messages (id, inserted_at, message, user_id, channel_id) VALUES (70354, '2012-06-29 18:49:52.227446', 'Wall six name beyond race. Tell knowledge develop beat check either eye. Half we compare.', 'e41df02e-32ca-4c37-81f4-a049293b74d6', 9773);
INSERT INTO messages (id, inserted_at, message, user_id, channel_id) VALUES (59299, '2000-01-06 03:10:49.377285', 'Behind begin movement final. Serve church beat building visit. Chance quite fast yet.', '10e802fd-638f-460f-a7a4-c4bf835aaa31', 6906);
INSERT INTO messages (id, inserted_at, message, user_id, channel_id) VALUES (26859, '1974-03-14 21:52:02.243613', 'Note approach group up stop. Common early avoid want near.', '0563f439-85ac-4f5f-8529-13d15558ad13', 49558);
```

## Future Improvements

- Add support for more SQL databases.
- Add support for more complex date setting (e.g., created_date vs last_updated).
- Add support for more complex datatypes, for instance recognizing and mimicking emails or usernames.

## Conclusion

You have successfully generated seed data for your SQL database using the `--seed` option with `supabase-pydantic`. This feature is very useful when you need to populate your database with test data or test your application with a large dataset & Pydantic models.

<br><br><br>
