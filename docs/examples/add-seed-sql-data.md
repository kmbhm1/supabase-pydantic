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
INSERT INTO role_permissions (id, role, permission) VALUES (27439, 'admin', 'channels.delete');
INSERT INTO role_permissions (id, role, permission) VALUES (25812, 'admin', 'messages.delete');
INSERT INTO role_permissions (id, role, permission) VALUES (30820, 'moderator', 'channels.delete');
INSERT INTO role_permissions (id, role, permission) VALUES (92943, 'moderator', 'messages.delete');

-- users
INSERT INTO users (id, username, status) VALUES ('6d084486-68ad-442b-a605-0da2e330b481', 'imorales', 'OFFLINE');
INSERT INTO users (id, username, status) VALUES ('a0c4949f-ed09-46c3-bd4b-1af2bda94ba1', 'michaellewis', 'ONLINE');
INSERT INTO users (id, username, status) VALUES ('d33923b9-f792-4195-956b-93468a83db69', 'whenderson', 'ONLINE');
INSERT INTO users (id, username, status) VALUES ('473d6d39-eaca-4e52-950a-2f8f00cbc84b', 'jsimpson', NULL);
INSERT INTO users (id, username, status) VALUES ('5c5a23e5-7b91-441d-8ea3-5726da374af8', 'curtisangela', 'OFFLINE');
INSERT INTO users (id, username, status) VALUES ('a9a8ac8b-213a-4784-a4ec-d01c4465ddb4', 'schurch', 'ONLINE');
INSERT INTO users (id, username, status) VALUES ('47a281c1-b76b-4496-96c3-b2650c7e58b8', NULL, 'ONLINE');
INSERT INTO users (id, username, status) VALUES ('872a6ae2-d03d-47d2-ac8b-ce5139eda350', 'snowstephanie', 'ONLINE');
INSERT INTO users (id, username, status) VALUES ('279e3fe9-d5fe-4470-8c4f-b6adebeac08a', 'esharp', 'OFFLINE');
INSERT INTO users (id, username, status) VALUES ('2572c896-87ce-4d15-b898-b4c9b471d401', NULL, 'OFFLINE');
INSERT INTO users (id, username, status) VALUES ('17f155ab-b673-48e3-a3e6-1784e9b914a4', 'melissa35', 'OFFLINE');
INSERT INTO users (id, username, status) VALUES ('93483430-3b9c-46e5-ac35-853f7113b83c', 'wanda78', 'ONLINE');
INSERT INTO users (id, username, status) VALUES ('f44ff568-5344-483b-a8e1-13724336f348', 'hernandezalan', 'OFFLINE');
INSERT INTO users (id, username, status) VALUES ('4610ba55-6baa-434f-a834-74af6dfc1c73', 'sarah28', NULL);
INSERT INTO users (id, username, status) VALUES ('c1641f3c-588f-43c3-806f-516f41c1fc48', 'zavalacurtis', 'OFFLINE');
INSERT INTO users (id, username, status) VALUES ('258dc8bd-2fc2-4ffe-9792-0abf8b5cb61e', 'msmith', NULL);
INSERT INTO users (id, username, status) VALUES ('088cc971-d758-4af4-ac34-4d0b8695f435', 'millerjennifer', 'ONLINE');
INSERT INTO users (id, username, status) VALUES ('e0198846-8699-48ad-850a-bed69be7eea7', 'lewisdavid', NULL);
INSERT INTO users (id, username, status) VALUES ('55456dea-6c66-49ca-80d4-79e435c544de', 'jamesmontoya', 'ONLINE');
INSERT INTO users (id, username, status) VALUES ('9d3d66b9-f297-4df9-86e6-aeea2a6d2de6', 'hicksangel', 'ONLINE');
INSERT INTO users (id, username, status) VALUES ('d03b1776-ac90-4a94-b006-5d7ce6e58f50', 'jennifer77', 'OFFLINE');
INSERT INTO users (id, username, status) VALUES ('cc9b0233-c601-4500-af2c-9a5e98f3ca03', NULL, NULL);
INSERT INTO users (id, username, status) VALUES ('bcb07349-1753-4ffb-8561-49c4b121f643', NULL, 'OFFLINE');
INSERT INTO users (id, username, status) VALUES ('47418ade-3cfe-4e8f-99dc-d94b03f35ccc', 'heathergarcia', 'ONLINE');
INSERT INTO users (id, username, status) VALUES ('5bc6734f-8f4c-4425-b795-36c383fdbd08', NULL, NULL);
INSERT INTO users (id, username, status) VALUES ('6cb97d31-9ac6-4cd4-9042-9580aec3a1d6', 'ojimenez', 'ONLINE');
INSERT INTO users (id, username, status) VALUES ('21af7a4c-7f98-41cf-9d13-ee7d7d45fadb', 'karengonzalez', NULL);
INSERT INTO users (id, username, status) VALUES ('1efd9f7a-a657-4c4d-aa85-cb8573f3dd39', 'kingjennifer', NULL);

-- user_roles
INSERT INTO user_roles (id, user_id, role) VALUES (17190, 'e0198846-8699-48ad-850a-bed69be7eea7', 'admin');
INSERT INTO user_roles (id, user_id, role) VALUES (17755, '279e3fe9-d5fe-4470-8c4f-b6adebeac08a', 'admin');
INSERT INTO user_roles (id, user_id, role) VALUES (10575, '4610ba55-6baa-434f-a834-74af6dfc1c73', 'admin');
INSERT INTO user_roles (id, user_id, role) VALUES (77623, '258dc8bd-2fc2-4ffe-9792-0abf8b5cb61e', 'admin');
INSERT INTO user_roles (id, user_id, role) VALUES (15021, '5bc6734f-8f4c-4425-b795-36c383fdbd08', 'admin');
INSERT INTO user_roles (id, user_id, role) VALUES (24165, '9d3d66b9-f297-4df9-86e6-aeea2a6d2de6', 'moderator');
INSERT INTO user_roles (id, user_id, role) VALUES (85146, '088cc971-d758-4af4-ac34-4d0b8695f435', 'moderator');
INSERT INTO user_roles (id, user_id, role) VALUES (9111, 'a9a8ac8b-213a-4784-a4ec-d01c4465ddb4', 'admin');
INSERT INTO user_roles (id, user_id, role) VALUES (45621, '279e3fe9-d5fe-4470-8c4f-b6adebeac08a', 'moderator');
INSERT INTO user_roles (id, user_id, role) VALUES (78312, '17f155ab-b673-48e3-a3e6-1784e9b914a4', 'moderator');
INSERT INTO user_roles (id, user_id, role) VALUES (48812, 'e0198846-8699-48ad-850a-bed69be7eea7', 'moderator');
INSERT INTO user_roles (id, user_id, role) VALUES (54954, '1efd9f7a-a657-4c4d-aa85-cb8573f3dd39', 'moderator');
INSERT INTO user_roles (id, user_id, role) VALUES (78619, 'a0c4949f-ed09-46c3-bd4b-1af2bda94ba1', 'admin');
INSERT INTO user_roles (id, user_id, role) VALUES (30132, '872a6ae2-d03d-47d2-ac8b-ce5139eda350', 'moderator');
INSERT INTO user_roles (id, user_id, role) VALUES (63027, '2572c896-87ce-4d15-b898-b4c9b471d401', 'moderator');
INSERT INTO user_roles (id, user_id, role) VALUES (40600, 'a0c4949f-ed09-46c3-bd4b-1af2bda94ba1', 'moderator');
INSERT INTO user_roles (id, user_id, role) VALUES (40445, '17f155ab-b673-48e3-a3e6-1784e9b914a4', 'admin');
INSERT INTO user_roles (id, user_id, role) VALUES (42826, '9d3d66b9-f297-4df9-86e6-aeea2a6d2de6', 'admin');
INSERT INTO user_roles (id, user_id, role) VALUES (63767, '55456dea-6c66-49ca-80d4-79e435c544de', 'moderator');
INSERT INTO user_roles (id, user_id, role) VALUES (42337, 'c1641f3c-588f-43c3-806f-516f41c1fc48', 'admin');
INSERT INTO user_roles (id, user_id, role) VALUES (39572, 'c1641f3c-588f-43c3-806f-516f41c1fc48', 'moderator');
INSERT INTO user_roles (id, user_id, role) VALUES (38681, '088cc971-d758-4af4-ac34-4d0b8695f435', 'admin');
INSERT INTO user_roles (id, user_id, role) VALUES (17260, 'd33923b9-f792-4195-956b-93468a83db69', 'moderator');
INSERT INTO user_roles (id, user_id, role) VALUES (66845, '21af7a4c-7f98-41cf-9d13-ee7d7d45fadb', 'moderator');
INSERT INTO user_roles (id, user_id, role) VALUES (58577, '4610ba55-6baa-434f-a834-74af6dfc1c73', 'moderator');
INSERT INTO user_roles (id, user_id, role) VALUES (47657, 'f44ff568-5344-483b-a8e1-13724336f348', 'admin');
INSERT INTO user_roles (id, user_id, role) VALUES (22961, '872a6ae2-d03d-47d2-ac8b-ce5139eda350', 'admin');
INSERT INTO user_roles (id, user_id, role) VALUES (46678, '6cb97d31-9ac6-4cd4-9042-9580aec3a1d6', 'admin');
INSERT INTO user_roles (id, user_id, role) VALUES (62371, '473d6d39-eaca-4e52-950a-2f8f00cbc84b', 'moderator');
INSERT INTO user_roles (id, user_id, role) VALUES (61255, '93483430-3b9c-46e5-ac35-853f7113b83c', 'admin');
INSERT INTO user_roles (id, user_id, role) VALUES (49046, '47418ade-3cfe-4e8f-99dc-d94b03f35ccc', 'moderator');
INSERT INTO user_roles (id, user_id, role) VALUES (93546, '47418ade-3cfe-4e8f-99dc-d94b03f35ccc', 'admin');
INSERT INTO user_roles (id, user_id, role) VALUES (73713, 'cc9b0233-c601-4500-af2c-9a5e98f3ca03', 'moderator');
INSERT INTO user_roles (id, user_id, role) VALUES (99651, '47a281c1-b76b-4496-96c3-b2650c7e58b8', 'moderator');
INSERT INTO user_roles (id, user_id, role) VALUES (42689, '47a281c1-b76b-4496-96c3-b2650c7e58b8', 'admin');
INSERT INTO user_roles (id, user_id, role) VALUES (11499, 'cc9b0233-c601-4500-af2c-9a5e98f3ca03', 'admin');
INSERT INTO user_roles (id, user_id, role) VALUES (52478, 'f44ff568-5344-483b-a8e1-13724336f348', 'moderator');
INSERT INTO user_roles (id, user_id, role) VALUES (19188, '5c5a23e5-7b91-441d-8ea3-5726da374af8', 'admin');
INSERT INTO user_roles (id, user_id, role) VALUES (71773, 'a9a8ac8b-213a-4784-a4ec-d01c4465ddb4', 'moderator');
INSERT INTO user_roles (id, user_id, role) VALUES (69708, 'bcb07349-1753-4ffb-8561-49c4b121f643', 'moderator');
INSERT INTO user_roles (id, user_id, role) VALUES (46461, '2572c896-87ce-4d15-b898-b4c9b471d401', 'admin');
INSERT INTO user_roles (id, user_id, role) VALUES (89113, 'd33923b9-f792-4195-956b-93468a83db69', 'admin');
INSERT INTO user_roles (id, user_id, role) VALUES (33586, '5c5a23e5-7b91-441d-8ea3-5726da374af8', 'moderator');
INSERT INTO user_roles (id, user_id, role) VALUES (76265, '5bc6734f-8f4c-4425-b795-36c383fdbd08', 'moderator');
INSERT INTO user_roles (id, user_id, role) VALUES (34799, '93483430-3b9c-46e5-ac35-853f7113b83c', 'moderator');
INSERT INTO user_roles (id, user_id, role) VALUES (9407, '55456dea-6c66-49ca-80d4-79e435c544de', 'admin');
INSERT INTO user_roles (id, user_id, role) VALUES (52882, 'd03b1776-ac90-4a94-b006-5d7ce6e58f50', 'moderator');
INSERT INTO user_roles (id, user_id, role) VALUES (18008, 'bcb07349-1753-4ffb-8561-49c4b121f643', 'admin');
INSERT INTO user_roles (id, user_id, role) VALUES (72116, '258dc8bd-2fc2-4ffe-9792-0abf8b5cb61e', 'moderator');
INSERT INTO user_roles (id, user_id, role) VALUES (46097, '6d084486-68ad-442b-a605-0da2e330b481', 'moderator');
INSERT INTO user_roles (id, user_id, role) VALUES (42096, '1efd9f7a-a657-4c4d-aa85-cb8573f3dd39', 'admin');
INSERT INTO user_roles (id, user_id, role) VALUES (39792, '6cb97d31-9ac6-4cd4-9042-9580aec3a1d6', 'moderator');
INSERT INTO user_roles (id, user_id, role) VALUES (25295, 'd03b1776-ac90-4a94-b006-5d7ce6e58f50', 'admin');
INSERT INTO user_roles (id, user_id, role) VALUES (33304, '473d6d39-eaca-4e52-950a-2f8f00cbc84b', 'admin');

-- channels
INSERT INTO channels (id, inserted_at, slug, created_by) VALUES (12350, '1982-10-03 07:08:10.391783', 'information-bring', '6cb97d31-9ac6-4cd4-9042-9580aec3a1d6');
INSERT INTO channels (id, inserted_at, slug, created_by) VALUES (10237, '2003-10-27 16:27:08.872335', 'make-mention-nor', '473d6d39-eaca-4e52-950a-2f8f00cbc84b');
INSERT INTO channels (id, inserted_at, slug, created_by) VALUES (50097, '1990-07-22 22:58:50.774503', 'rise-someone', '5bc6734f-8f4c-4425-b795-36c383fdbd08');
INSERT INTO channels (id, inserted_at, slug, created_by) VALUES (77792, '2012-08-13 14:23:06.733732', 'his-give-above-hot', '5c5a23e5-7b91-441d-8ea3-5726da374af8');
INSERT INTO channels (id, inserted_at, slug, created_by) VALUES (32155, '1980-08-18 15:53:05.497625', 'behind-line-improve', 'cc9b0233-c601-4500-af2c-9a5e98f3ca03');
INSERT INTO channels (id, inserted_at, slug, created_by) VALUES (17050, '1992-02-03 19:11:20.907264', 'will-score', '47a281c1-b76b-4496-96c3-b2650c7e58b8');
INSERT INTO channels (id, inserted_at, slug, created_by) VALUES (6863, '1973-01-20 11:20:52.258944', 'guess-of-decide', '279e3fe9-d5fe-4470-8c4f-b6adebeac08a');
INSERT INTO channels (id, inserted_at, slug, created_by) VALUES (59198, '2009-12-29 08:12:50.243810', 'behind-also-other', 'bcb07349-1753-4ffb-8561-49c4b121f643');
INSERT INTO channels (id, inserted_at, slug, created_by) VALUES (56635, '2013-03-28 01:39:43.589067', 'act-future-fear', 'bcb07349-1753-4ffb-8561-49c4b121f643');
INSERT INTO channels (id, inserted_at, slug, created_by) VALUES (64605, '1989-07-18 19:44:22.343312', 'second-key', '47418ade-3cfe-4e8f-99dc-d94b03f35ccc');
INSERT INTO channels (id, inserted_at, slug, created_by) VALUES (76723, '1990-04-10 23:46:33.330554', 'skill-decide-one', 'e0198846-8699-48ad-850a-bed69be7eea7');
INSERT INTO channels (id, inserted_at, slug, created_by) VALUES (93245, '1993-12-24 03:30:19.285336', 'left-high-wife-get', '088cc971-d758-4af4-ac34-4d0b8695f435');
INSERT INTO channels (id, inserted_at, slug, created_by) VALUES (28418, '1974-09-17 07:27:43.228792', 'amount-detail', '9d3d66b9-f297-4df9-86e6-aeea2a6d2de6');
INSERT INTO channels (id, inserted_at, slug, created_by) VALUES (75259, '2020-04-25 05:56:22.535768', 'movement-sound', 'cc9b0233-c601-4500-af2c-9a5e98f3ca03');
INSERT INTO channels (id, inserted_at, slug, created_by) VALUES (67392, '1998-07-01 13:28:07.941204', 'stay-lead-end-would', 'cc9b0233-c601-4500-af2c-9a5e98f3ca03');
INSERT INTO channels (id, inserted_at, slug, created_by) VALUES (73200, '2019-07-30 22:29:34.696922', 'project-theory', 'bcb07349-1753-4ffb-8561-49c4b121f643');
INSERT INTO channels (id, inserted_at, slug, created_by) VALUES (5872, '2003-05-05 13:46:51.730222', 'case-read-top', '279e3fe9-d5fe-4470-8c4f-b6adebeac08a');
INSERT INTO channels (id, inserted_at, slug, created_by) VALUES (2563, '1974-06-12 13:10:37.844199', 'poor-thank-human', '17f155ab-b673-48e3-a3e6-1784e9b914a4');
INSERT INTO channels (id, inserted_at, slug, created_by) VALUES (70265, '1983-02-23 15:18:51.011531', 'quickly-will', '4610ba55-6baa-434f-a834-74af6dfc1c73');
INSERT INTO channels (id, inserted_at, slug, created_by) VALUES (304, '1977-04-20 12:14:03.554352', 'course-skin-charge', 'd03b1776-ac90-4a94-b006-5d7ce6e58f50');
INSERT INTO channels (id, inserted_at, slug, created_by) VALUES (81899, '1988-07-26 16:06:29.038618', 'wall-apply-one', '6d084486-68ad-442b-a605-0da2e330b481');
INSERT INTO channels (id, inserted_at, slug, created_by) VALUES (80962, '1991-01-30 20:22:26.539163', 'thing-thought-win', '258dc8bd-2fc2-4ffe-9792-0abf8b5cb61e');
INSERT INTO channels (id, inserted_at, slug, created_by) VALUES (25244, '1995-07-16 06:25:43.663949', 'official-seat-oil', '5c5a23e5-7b91-441d-8ea3-5726da374af8');
INSERT INTO channels (id, inserted_at, slug, created_by) VALUES (84081, '2004-08-12 04:03:45.949653', 'need-size-see-apply', 'cc9b0233-c601-4500-af2c-9a5e98f3ca03');
INSERT INTO channels (id, inserted_at, slug, created_by) VALUES (98234, '1995-01-04 23:41:38.863350', 'right-share-part', 'e0198846-8699-48ad-850a-bed69be7eea7');
INSERT INTO channels (id, inserted_at, slug, created_by) VALUES (58061, '2022-08-02 22:34:14.491955', 'thing-per-enjoy-tv', '2572c896-87ce-4d15-b898-b4c9b471d401');
INSERT INTO channels (id, inserted_at, slug, created_by) VALUES (20221, '2012-03-04 14:16:56.261849', 'though-cost-none', '93483430-3b9c-46e5-ac35-853f7113b83c');
INSERT INTO channels (id, inserted_at, slug, created_by) VALUES (74588, '2019-11-08 22:17:48.281745', 'perhaps-offer-it', '47a281c1-b76b-4496-96c3-b2650c7e58b8');
INSERT INTO channels (id, inserted_at, slug, created_by) VALUES (89345, '1972-04-19 08:12:52.716166', 'good-fill-less', '1efd9f7a-a657-4c4d-aa85-cb8573f3dd39');
INSERT INTO channels (id, inserted_at, slug, created_by) VALUES (4443, '1986-11-22 18:57:37.829666', 'financial-mention', 'd33923b9-f792-4195-956b-93468a83db69');
INSERT INTO channels (id, inserted_at, slug, created_by) VALUES (89441, '2003-09-17 13:28:36.648923', 'already-across', '5c5a23e5-7b91-441d-8ea3-5726da374af8');
INSERT INTO channels (id, inserted_at, slug, created_by) VALUES (67103, '2009-09-17 01:05:00.146272', 'character-everyone', '279e3fe9-d5fe-4470-8c4f-b6adebeac08a');
INSERT INTO channels (id, inserted_at, slug, created_by) VALUES (37586, '1973-07-04 10:13:23.580405', 'first-list-although', '93483430-3b9c-46e5-ac35-853f7113b83c');
INSERT INTO channels (id, inserted_at, slug, created_by) VALUES (85753, '2014-12-05 08:45:09.124362', 'miss-draw-prove', '47a281c1-b76b-4496-96c3-b2650c7e58b8');
INSERT INTO channels (id, inserted_at, slug, created_by) VALUES (93346, '2017-11-01 14:44:02.889414', 'simply-safe-meeting', 'e0198846-8699-48ad-850a-bed69be7eea7');
INSERT INTO channels (id, inserted_at, slug, created_by) VALUES (69775, '2009-07-10 14:55:44.618517', 'commercial', '258dc8bd-2fc2-4ffe-9792-0abf8b5cb61e');
INSERT INTO channels (id, inserted_at, slug, created_by) VALUES (91480, '1990-03-30 11:43:37.306306', 'chair-foot-medical', '55456dea-6c66-49ca-80d4-79e435c544de');
INSERT INTO channels (id, inserted_at, slug, created_by) VALUES (85119, '1999-07-13 17:26:17.061313', 'go-whole-year-true', '55456dea-6c66-49ca-80d4-79e435c544de');
INSERT INTO channels (id, inserted_at, slug, created_by) VALUES (17462, '2009-05-09 04:47:27.913886', 'discuss-same-show', '1efd9f7a-a657-4c4d-aa85-cb8573f3dd39');
INSERT INTO channels (id, inserted_at, slug, created_by) VALUES (1178, '1970-06-02 02:39:29.210899', 'gun-floor-receive', '088cc971-d758-4af4-ac34-4d0b8695f435');
INSERT INTO channels (id, inserted_at, slug, created_by) VALUES (85355, '1991-06-08 15:10:46.270705', 'machine-how-hand', '088cc971-d758-4af4-ac34-4d0b8695f435');
INSERT INTO channels (id, inserted_at, slug, created_by) VALUES (53434, '2012-12-30 18:57:59.251501', 'machine-card-feel', '9d3d66b9-f297-4df9-86e6-aeea2a6d2de6');
INSERT INTO channels (id, inserted_at, slug, created_by) VALUES (30759, '2000-03-17 09:23:01.132951', 'alone-might', '279e3fe9-d5fe-4470-8c4f-b6adebeac08a');
INSERT INTO channels (id, inserted_at, slug, created_by) VALUES (26254, '1991-12-12 11:22:27.415749', 'nature-among-day', '93483430-3b9c-46e5-ac35-853f7113b83c');
INSERT INTO channels (id, inserted_at, slug, created_by) VALUES (26970, '2003-05-26 21:08:40.751092', 'trip-authority', 'a0c4949f-ed09-46c3-bd4b-1af2bda94ba1');
INSERT INTO channels (id, inserted_at, slug, created_by) VALUES (66088, '2014-03-19 04:24:37.105419', 'ago-lead-day-point', '6cb97d31-9ac6-4cd4-9042-9580aec3a1d6');
INSERT INTO channels (id, inserted_at, slug, created_by) VALUES (75113, '1992-10-31 17:23:33.852014', 'commercial-whether', 'd03b1776-ac90-4a94-b006-5d7ce6e58f50');
INSERT INTO channels (id, inserted_at, slug, created_by) VALUES (94165, '1987-10-16 08:43:36.572021', 'indeed-audience', '5bc6734f-8f4c-4425-b795-36c383fdbd08');
INSERT INTO channels (id, inserted_at, slug, created_by) VALUES (1400, '1999-02-14 09:09:19.747798', 'might-have-its-turn', '2572c896-87ce-4d15-b898-b4c9b471d401');
INSERT INTO channels (id, inserted_at, slug, created_by) VALUES (86856, '1998-06-02 05:21:15.134419', 'possible-create', 'd03b1776-ac90-4a94-b006-5d7ce6e58f50');
INSERT INTO channels (id, inserted_at, slug, created_by) VALUES (8674, '1992-01-17 19:04:32.805149', 'opportunity', 'e0198846-8699-48ad-850a-bed69be7eea7');
INSERT INTO channels (id, inserted_at, slug, created_by) VALUES (1898, '2024-04-14 01:58:58.904429', 'kid-unit-value', 'f44ff568-5344-483b-a8e1-13724336f348');
INSERT INTO channels (id, inserted_at, slug, created_by) VALUES (90528, '1982-11-06 19:56:31.058688', 'more-tv-attention', '6d084486-68ad-442b-a605-0da2e330b481');
INSERT INTO channels (id, inserted_at, slug, created_by) VALUES (51954, '1988-05-03 11:27:04.915598', 'imagine-suggest', '5bc6734f-8f4c-4425-b795-36c383fdbd08');
INSERT INTO channels (id, inserted_at, slug, created_by) VALUES (13022, '1976-08-07 23:00:14.958339', 'foreign-enough', '088cc971-d758-4af4-ac34-4d0b8695f435');

-- messages
INSERT INTO messages (id, inserted_at, message, user_id, channel_id) VALUES (55414, '1994-07-28 06:45:57.649011', 'Your major drop perhaps. Dream manager top imagine statement.
Happen develop and eye.', '2572c896-87ce-4d15-b898-b4c9b471d401', 89441);
INSERT INTO messages (id, inserted_at, message, user_id, channel_id) VALUES (98037, '2003-11-13 12:55:20.492826', 'Threat sure citizen policy why for mind term. Course consumer can evening.', '4610ba55-6baa-434f-a834-74af6dfc1c73', 69775);
INSERT INTO messages (id, inserted_at, message, user_id, channel_id) VALUES (9693, '1991-01-26 00:22:44.094929', 'Born surface which suddenly skin. Assume wrong citizen later do.', '258dc8bd-2fc2-4ffe-9792-0abf8b5cb61e', 67103);
INSERT INTO messages (id, inserted_at, message, user_id, channel_id) VALUES (86489, '2015-05-13 07:05:56.157224', 'Matter skill able call true teach president.
Must from class. Page expert reveal because focus.', 'd03b1776-ac90-4a94-b006-5d7ce6e58f50', 73200);
INSERT INTO messages (id, inserted_at, message, user_id, channel_id) VALUES (98826, '1980-08-22 06:05:23.992014', 'Figure inside increase huge. Reduce check at list customer.', '872a6ae2-d03d-47d2-ac8b-ce5139eda350', 98234);
INSERT INTO messages (id, inserted_at, message, user_id, channel_id) VALUES (88324, '2017-10-13 05:09:02.877377', 'Left far trade able. Professional wind three network. Set computer task nation accept according.', '6cb97d31-9ac6-4cd4-9042-9580aec3a1d6', 77792);
INSERT INTO messages (id, inserted_at, message, user_id, channel_id) VALUES (15798, '1984-06-26 04:04:43.964770', NULL, '1efd9f7a-a657-4c4d-aa85-cb8573f3dd39', 6863);
INSERT INTO messages (id, inserted_at, message, user_id, channel_id) VALUES (24375, '1977-08-30 22:36:31.533367', 'Democratic bad military movement. Increase whole computer easy. Share practice fill firm.', '93483430-3b9c-46e5-ac35-853f7113b83c', 93245);
INSERT INTO messages (id, inserted_at, message, user_id, channel_id) VALUES (80927, '1970-10-02 10:35:28.322295', 'Foot compare at story suggest majority. Firm war be economic prepare. Late career manage amount.', '2572c896-87ce-4d15-b898-b4c9b471d401', 94165);
INSERT INTO messages (id, inserted_at, message, user_id, channel_id) VALUES (54707, '2016-08-05 22:26:56.703984', 'Back all message. Parent box news true production day reduce. Big whose land nature century apply.', 'a0c4949f-ed09-46c3-bd4b-1af2bda94ba1', 28418);
INSERT INTO messages (id, inserted_at, message, user_id, channel_id) VALUES (24934, '2023-01-04 21:55:08.686259', 'Real if year left easy thus. Public raise create seek pressure simple. Per exist start weight.', 'a0c4949f-ed09-46c3-bd4b-1af2bda94ba1', 1898);
INSERT INTO messages (id, inserted_at, message, user_id, channel_id) VALUES (19849, '2011-05-17 12:10:07.412247', 'Star visit religious receive yes manager list. Region prevent create born.', '47418ade-3cfe-4e8f-99dc-d94b03f35ccc', 89345);
INSERT INTO messages (id, inserted_at, message, user_id, channel_id) VALUES (76912, '1998-08-13 03:08:44.280461', 'Make defense eight prevent. Bad group high step.', '6cb97d31-9ac6-4cd4-9042-9580aec3a1d6', 26254);
INSERT INTO messages (id, inserted_at, message, user_id, channel_id) VALUES (33949, '1984-04-13 06:25:42.739095', NULL, '258dc8bd-2fc2-4ffe-9792-0abf8b5cb61e', 74588);
INSERT INTO messages (id, inserted_at, message, user_id, channel_id) VALUES (51093, '1977-07-20 09:21:58.083789', 'Every trial worker man performance. Entire live contain. His debate kid field.', '9d3d66b9-f297-4df9-86e6-aeea2a6d2de6', 17050);
INSERT INTO messages (id, inserted_at, message, user_id, channel_id) VALUES (26369, '1993-02-19 14:08:03.197544', 'Area item glass design. Risk truth send near address. Suggest make use know.', '47a281c1-b76b-4496-96c3-b2650c7e58b8', 32155);
INSERT INTO messages (id, inserted_at, message, user_id, channel_id) VALUES (40389, '1972-08-23 23:24:12.896081', 'Employee change after own sound part. Reach available conference note.', '9d3d66b9-f297-4df9-86e6-aeea2a6d2de6', 81899);
INSERT INTO messages (id, inserted_at, message, user_id, channel_id) VALUES (2587, '2010-12-15 06:27:37.241656', 'Under lay black accept peace ever. Social successful trial page.', '2572c896-87ce-4d15-b898-b4c9b471d401', 67103);
INSERT INTO messages (id, inserted_at, message, user_id, channel_id) VALUES (9336, '1972-12-25 06:34:29.689851', 'Explain company consumer ask successful.', '2572c896-87ce-4d15-b898-b4c9b471d401', 51954);
INSERT INTO messages (id, inserted_at, message, user_id, channel_id) VALUES (1680, '1979-08-21 01:24:15.609051', 'Himself beat item final when. Why religious word phone vote.', '6cb97d31-9ac6-4cd4-9042-9580aec3a1d6', 89441);
INSERT INTO messages (id, inserted_at, message, user_id, channel_id) VALUES (83643, '1993-06-29 22:32:30.186369', 'Know theory time majority deal table. Know decision east join.', '258dc8bd-2fc2-4ffe-9792-0abf8b5cb61e', 30759);
INSERT INTO messages (id, inserted_at, message, user_id, channel_id) VALUES (19794, '2024-03-25 05:02:41.799205', NULL, '5bc6734f-8f4c-4425-b795-36c383fdbd08', 28418);
INSERT INTO messages (id, inserted_at, message, user_id, channel_id) VALUES (79213, '1994-10-25 15:43:21.153759', NULL, '1efd9f7a-a657-4c4d-aa85-cb8573f3dd39', 8674);
INSERT INTO messages (id, inserted_at, message, user_id, channel_id) VALUES (26362, '2009-01-29 10:12:37.778380', 'Ask indeed customer pick receive close. Man we deep within newspaper degree population.', 'cc9b0233-c601-4500-af2c-9a5e98f3ca03', 94165);
INSERT INTO messages (id, inserted_at, message, user_id, channel_id) VALUES (49173, '1995-10-01 14:55:44.378539', 'Still mind lay medical. Environmental hundred set course around wonder three.', '473d6d39-eaca-4e52-950a-2f8f00cbc84b', 85753);
INSERT INTO messages (id, inserted_at, message, user_id, channel_id) VALUES (35453, '1974-04-27 01:43:24.388234', 'Senior record film purpose be heavy today. Chair type night side experience southern sure.', '6d084486-68ad-442b-a605-0da2e330b481', 94165);
INSERT INTO messages (id, inserted_at, message, user_id, channel_id) VALUES (36612, '2009-01-26 14:06:16.855465', 'Wear rich under tend can.
Debate suggest they possible. Clearly sense down forget.', 'f44ff568-5344-483b-a8e1-13724336f348', 91480);
INSERT INTO messages (id, inserted_at, message, user_id, channel_id) VALUES (93208, '2023-02-19 19:02:40.075696', 'Either sort energy tough trouble rest whole.
Republican phone ten send quite.', '473d6d39-eaca-4e52-950a-2f8f00cbc84b', 6863);
INSERT INTO messages (id, inserted_at, message, user_id, channel_id) VALUES (62943, '1977-02-14 03:50:16.627968', 'Course letter serious no head interesting reflect. Writer improve blue happen kind save assume.', '872a6ae2-d03d-47d2-ac8b-ce5139eda350', 32155);
INSERT INTO messages (id, inserted_at, message, user_id, channel_id) VALUES (6184, '2018-04-15 12:41:55.213127', 'Since book move like. President piece win upon hotel. Week that attack me space country party.', 'f44ff568-5344-483b-a8e1-13724336f348', 50097);
INSERT INTO messages (id, inserted_at, message, user_id, channel_id) VALUES (68922, '1995-08-05 22:45:17.398246', NULL, 'a0c4949f-ed09-46c3-bd4b-1af2bda94ba1', 32155);
INSERT INTO messages (id, inserted_at, message, user_id, channel_id) VALUES (84711, '2002-04-02 19:39:14.089442', 'Game body seat others. Treat he play eye computer many effect.', 'f44ff568-5344-483b-a8e1-13724336f348', 37586);
INSERT INTO messages (id, inserted_at, message, user_id, channel_id) VALUES (94654, '2001-01-25 12:22:08.931035', 'Federal cup loss production successful family.', '258dc8bd-2fc2-4ffe-9792-0abf8b5cb61e', 8674);
INSERT INTO messages (id, inserted_at, message, user_id, channel_id) VALUES (62951, '2004-11-19 00:20:25.454399', 'Whom total record film blood worker. Kind right finally available his.', 'a0c4949f-ed09-46c3-bd4b-1af2bda94ba1', 73200);
INSERT INTO messages (id, inserted_at, message, user_id, channel_id) VALUES (98941, '1991-10-27 05:49:52.414827', 'Effect five safe hospital senior. Teach current guess because near present all culture.', 'f44ff568-5344-483b-a8e1-13724336f348', 12350);
INSERT INTO messages (id, inserted_at, message, user_id, channel_id) VALUES (85058, '2002-07-05 01:19:47.119983', 'Car hair inside think much. Could thank dark feel place beautiful understand. Happy father color.', '088cc971-d758-4af4-ac34-4d0b8695f435', 81899);
INSERT INTO messages (id, inserted_at, message, user_id, channel_id) VALUES (31121, '2005-05-18 07:46:34.710637', 'Spend movement difference exactly.
Season husband ground.', '17f155ab-b673-48e3-a3e6-1784e9b914a4', 30759);
INSERT INTO messages (id, inserted_at, message, user_id, channel_id) VALUES (19342, '2007-05-24 20:35:59.406198', NULL, '2572c896-87ce-4d15-b898-b4c9b471d401', 1400);
INSERT INTO messages (id, inserted_at, message, user_id, channel_id) VALUES (72063, '1975-11-23 03:28:50.278307', 'Yet field agree whose. Agree any again both fact.
As discuss picture at focus before.', '258dc8bd-2fc2-4ffe-9792-0abf8b5cb61e', 56635);
INSERT INTO messages (id, inserted_at, message, user_id, channel_id) VALUES (89047, '2001-08-01 15:01:31.306607', 'Design that performance share loss win. Recently tonight back civil size dinner least.', 'c1641f3c-588f-43c3-806f-516f41c1fc48', 20221);
INSERT INTO messages (id, inserted_at, message, user_id, channel_id) VALUES (91415, '1981-11-29 14:47:37.303042', NULL, '47a281c1-b76b-4496-96c3-b2650c7e58b8', 93245);
INSERT INTO messages (id, inserted_at, message, user_id, channel_id) VALUES (78660, '1988-02-07 00:31:41.200566', 'Various science role top gun it.', 'a0c4949f-ed09-46c3-bd4b-1af2bda94ba1', 10237);
INSERT INTO messages (id, inserted_at, message, user_id, channel_id) VALUES (70282, '2004-01-07 10:44:10.168481', 'Wide ready development while. Fish executive serious card under stay.', 'c1641f3c-588f-43c3-806f-516f41c1fc48', 85119);
INSERT INTO messages (id, inserted_at, message, user_id, channel_id) VALUES (97004, '1973-08-13 06:29:16.308784', 'Commercial performance off.', '2572c896-87ce-4d15-b898-b4c9b471d401', 89345);
INSERT INTO messages (id, inserted_at, message, user_id, channel_id) VALUES (65642, '1999-06-03 19:32:04.264936', 'Good pull identify probably important or. True hand music television. Carry happen whether bank.', '5c5a23e5-7b91-441d-8ea3-5726da374af8', 10237);
INSERT INTO messages (id, inserted_at, message, user_id, channel_id) VALUES (98352, '2012-04-05 02:14:32.520617', 'My discover attack store. Truth whole live employee simple mouth lot.', 'bcb07349-1753-4ffb-8561-49c4b121f643', 84081);
INSERT INTO messages (id, inserted_at, message, user_id, channel_id) VALUES (75073, '2003-07-03 16:36:40.893841', 'Nation true just sign blue together. Large perhaps remember. Vote new shoulder sell.', '17f155ab-b673-48e3-a3e6-1784e9b914a4', 50097);
INSERT INTO messages (id, inserted_at, message, user_id, channel_id) VALUES (84179, '1997-09-15 03:40:53.738730', 'Place baby development. Remember answer visit.', '55456dea-6c66-49ca-80d4-79e435c544de', 13022);
INSERT INTO messages (id, inserted_at, message, user_id, channel_id) VALUES (80749, '1980-09-26 08:30:47.772220', NULL, 'cc9b0233-c601-4500-af2c-9a5e98f3ca03', 70265);
INSERT INTO messages (id, inserted_at, message, user_id, channel_id) VALUES (50553, '2008-06-14 00:23:01.279654', 'Much kind dark ten action guess. Score million offer eat sing fill option.', 'd33923b9-f792-4195-956b-93468a83db69', 91480);
INSERT INTO messages (id, inserted_at, message, user_id, channel_id) VALUES (62699, '1996-02-17 13:27:36.127242', 'Including really seat your. Worker bed while indicate between until.', '93483430-3b9c-46e5-ac35-853f7113b83c', 17462);
INSERT INTO messages (id, inserted_at, message, user_id, channel_id) VALUES (27406, '1971-01-03 15:14:27.282960', 'Stage cup financial rather few. Practice type suggest here worker size make.', '4610ba55-6baa-434f-a834-74af6dfc1c73', 2563);
INSERT INTO messages (id, inserted_at, message, user_id, channel_id) VALUES (49687, '1996-12-08 01:56:47.806801', 'Up accept with ball individual feel author. By money region.', 'c1641f3c-588f-43c3-806f-516f41c1fc48', 70265);
INSERT INTO messages (id, inserted_at, message, user_id, channel_id) VALUES (68201, '2008-06-14 09:19:37.449451', 'Organization single include part check girl save. My entire federal increase treat.', '17f155ab-b673-48e3-a3e6-1784e9b914a4', 98234);
INSERT INTO messages (id, inserted_at, message, user_id, channel_id) VALUES (77536, '1974-03-03 20:18:53.683966', 'North pay figure wide real thus fund. Five base usually. By article turn majority late significant.', '9d3d66b9-f297-4df9-86e6-aeea2a6d2de6', 73200);
INSERT INTO messages (id, inserted_at, message, user_id, channel_id) VALUES (97563, '2009-09-08 16:45:59.770275', 'Grow stand against by case number. Those future board former. Bad quality street.', 'bcb07349-1753-4ffb-8561-49c4b121f643', 94165);
INSERT INTO messages (id, inserted_at, message, user_id, channel_id) VALUES (62030, '2022-10-15 19:33:50.078156', 'Color success town information five ahead president. Force small several news mean bit management.', '4610ba55-6baa-434f-a834-74af6dfc1c73', 98234);
INSERT INTO messages (id, inserted_at, message, user_id, channel_id) VALUES (55383, '2003-11-24 02:24:07.799895', NULL, '088cc971-d758-4af4-ac34-4d0b8695f435', 85355);
INSERT INTO messages (id, inserted_at, message, user_id, channel_id) VALUES (115, '1985-09-19 22:06:07.173627', 'Time game up support. Per notice example increase account how.', '17f155ab-b673-48e3-a3e6-1784e9b914a4', 5872);
INSERT INTO messages (id, inserted_at, message, user_id, channel_id) VALUES (63958, '2012-01-03 15:21:10.975553', 'Itself opportunity shake purpose experience activity. Their herself pretty group discussion best.', '5bc6734f-8f4c-4425-b795-36c383fdbd08', 5872);
INSERT INTO messages (id, inserted_at, message, user_id, channel_id) VALUES (49707, '2008-09-10 12:32:46.480596', 'Attack watch on. Whole trouble baby pull blue least trip democratic.', 'a0c4949f-ed09-46c3-bd4b-1af2bda94ba1', 10237);
INSERT INTO messages (id, inserted_at, message, user_id, channel_id) VALUES (89284, '2009-10-04 05:26:31.566262', 'Learn on field so usually smile these. Rock five before a radio.', '4610ba55-6baa-434f-a834-74af6dfc1c73', 5872);
INSERT INTO messages (id, inserted_at, message, user_id, channel_id) VALUES (28039, '1980-07-24 04:15:33.209098', 'Dinner hear once defense common. Help student later financial newspaper.', '279e3fe9-d5fe-4470-8c4f-b6adebeac08a', 85119);
INSERT INTO messages (id, inserted_at, message, user_id, channel_id) VALUES (11982, '1990-07-15 19:42:34.278397', 'Evening no look campaign wrong positive son.', '55456dea-6c66-49ca-80d4-79e435c544de', 17050);
INSERT INTO messages (id, inserted_at, message, user_id, channel_id) VALUES (32236, '1994-10-18 15:26:53.481994', 'Goal vote security because professional item step. Hand during hour open beautiful prevent.', '279e3fe9-d5fe-4470-8c4f-b6adebeac08a', 93346);
INSERT INTO messages (id, inserted_at, message, user_id, channel_id) VALUES (90969, '1971-11-08 02:23:40.524676', 'Little business piece month. Organization begin now near sense visit.', '473d6d39-eaca-4e52-950a-2f8f00cbc84b', 13022);
INSERT INTO messages (id, inserted_at, message, user_id, channel_id) VALUES (55231, '2015-08-02 14:45:42.117890', NULL, 'cc9b0233-c601-4500-af2c-9a5e98f3ca03', 85355);
INSERT INTO messages (id, inserted_at, message, user_id, channel_id) VALUES (75298, '1982-04-07 04:13:20.417499', 'With own organization. Section recently guy contain address business sit bad.', '1efd9f7a-a657-4c4d-aa85-cb8573f3dd39', 13022);
INSERT INTO messages (id, inserted_at, message, user_id, channel_id) VALUES (71501, '2005-03-14 18:42:33.344524', 'Today network well lose general once. Mind option floor business.', 'a9a8ac8b-213a-4784-a4ec-d01c4465ddb4', 37586);
INSERT INTO messages (id, inserted_at, message, user_id, channel_id) VALUES (53228, '2021-08-06 16:08:15.666232', 'Ever concern fill vote note race wait. Black particular always attorney baby that.', '1efd9f7a-a657-4c4d-aa85-cb8573f3dd39', 90528);
INSERT INTO messages (id, inserted_at, message, user_id, channel_id) VALUES (47597, '2002-05-31 14:18:22.401518', 'Person garden store employee once little cup field. Hear member try garden democratic minute.', '55456dea-6c66-49ca-80d4-79e435c544de', 80962);
INSERT INTO messages (id, inserted_at, message, user_id, channel_id) VALUES (44647, '1984-04-29 10:19:11.853083', 'Throughout people identify. Late rate sense management represent teach region well.', 'c1641f3c-588f-43c3-806f-516f41c1fc48', 6863);
INSERT INTO messages (id, inserted_at, message, user_id, channel_id) VALUES (32977, '2005-09-03 16:20:30.789571', NULL, '473d6d39-eaca-4e52-950a-2f8f00cbc84b', 37586);
INSERT INTO messages (id, inserted_at, message, user_id, channel_id) VALUES (71320, '2013-10-15 02:49:02.720955', 'Task on simple.
Along question education start. Democratic dream discussion trouble.', '6d084486-68ad-442b-a605-0da2e330b481', 90528);
INSERT INTO messages (id, inserted_at, message, user_id, channel_id) VALUES (77006, '1992-09-11 11:54:30.644484', NULL, 'e0198846-8699-48ad-850a-bed69be7eea7', 1400);
INSERT INTO messages (id, inserted_at, message, user_id, channel_id) VALUES (2690, '1987-10-06 20:31:41.686579', NULL, '473d6d39-eaca-4e52-950a-2f8f00cbc84b', 66088);
INSERT INTO messages (id, inserted_at, message, user_id, channel_id) VALUES (64442, '1992-12-08 14:01:04.383016', 'Simply health appear establish.', 'e0198846-8699-48ad-850a-bed69be7eea7', 4443);
INSERT INTO messages (id, inserted_at, message, user_id, channel_id) VALUES (72787, '2023-01-08 10:10:22.380729', 'Help method kind system energy from for. Mrs white sign.', '47418ade-3cfe-4e8f-99dc-d94b03f35ccc', 30759);
INSERT INTO messages (id, inserted_at, message, user_id, channel_id) VALUES (92564, '2012-07-08 16:55:07.138357', 'Be generation generation car student.
Thank real memory girl again impact.', '47a281c1-b76b-4496-96c3-b2650c7e58b8', 75113);
INSERT INTO messages (id, inserted_at, message, user_id, channel_id) VALUES (51901, '1982-07-16 22:09:43.895206', NULL, '6cb97d31-9ac6-4cd4-9042-9580aec3a1d6', 85119);
INSERT INTO messages (id, inserted_at, message, user_id, channel_id) VALUES (85720, '2016-05-19 14:16:14.553676', 'Great begin perhaps. Customer paper first set west star open write.', 'e0198846-8699-48ad-850a-bed69be7eea7', 84081);
INSERT INTO messages (id, inserted_at, message, user_id, channel_id) VALUES (62189, '1993-06-22 04:02:19.280955', 'Strong letter strategy real.
See even indicate. Upon later treatment occur prove general.', 'd33923b9-f792-4195-956b-93468a83db69', 86856);
INSERT INTO messages (id, inserted_at, message, user_id, channel_id) VALUES (97394, '1998-03-26 19:26:32.305254', 'Top matter eight court true. Reduce million conference expert.', 'e0198846-8699-48ad-850a-bed69be7eea7', 4443);
INSERT INTO messages (id, inserted_at, message, user_id, channel_id) VALUES (76284, '2001-10-25 09:42:53.158808', 'Another can start relationship right alone. Leg before room set management.', '47418ade-3cfe-4e8f-99dc-d94b03f35ccc', 67103);
INSERT INTO messages (id, inserted_at, message, user_id, channel_id) VALUES (87719, '1992-11-18 07:26:33.730573', 'Hundred thousand black against. Face collection together today detail billion develop.', 'e0198846-8699-48ad-850a-bed69be7eea7', 85753);
INSERT INTO messages (id, inserted_at, message, user_id, channel_id) VALUES (39801, '2010-05-15 00:02:54.342492', 'Picture those positive force gas beyond produce. Another statement minute thank system.', 'd33923b9-f792-4195-956b-93468a83db69', 67103);
INSERT INTO messages (id, inserted_at, message, user_id, channel_id) VALUES (57936, '2024-05-17 11:53:55.172003', 'Especially ground easy together drug light. Question offer step director series short.', '1efd9f7a-a657-4c4d-aa85-cb8573f3dd39', 85119);
INSERT INTO messages (id, inserted_at, message, user_id, channel_id) VALUES (23097, '2018-02-28 01:31:50.570936', 'Benefit him power me bring war Republican. Record interest including such approach owner reveal.', '4610ba55-6baa-434f-a834-74af6dfc1c73', 84081);
INSERT INTO messages (id, inserted_at, message, user_id, channel_id) VALUES (50337, '1981-10-10 17:15:33.076177', 'Course feel away official individual though.', '93483430-3b9c-46e5-ac35-853f7113b83c', 86856);
INSERT INTO messages (id, inserted_at, message, user_id, channel_id) VALUES (32944, '2005-08-05 05:17:30.978529', 'Center rest forward country management future exist. Fish west guess edge management I couple.', '6d084486-68ad-442b-a605-0da2e330b481', 50097);
INSERT INTO messages (id, inserted_at, message, user_id, channel_id) VALUES (35890, '2004-02-13 08:32:17.210272', 'Course attention top three thank talk. Edge page might establish consider soon message.', '47a281c1-b76b-4496-96c3-b2650c7e58b8', 76723);
INSERT INTO messages (id, inserted_at, message, user_id, channel_id) VALUES (80851, '1970-12-27 16:39:50.931505', 'Finally analysis do bill. Peace executive almost south pick today.', 'a0c4949f-ed09-46c3-bd4b-1af2bda94ba1', 28418);
INSERT INTO messages (id, inserted_at, message, user_id, channel_id) VALUES (23503, '1975-05-27 21:20:38.746233', 'Policy word sometimes imagine together hair art. Look no hot need.', '6cb97d31-9ac6-4cd4-9042-9580aec3a1d6', 89345);
INSERT INTO messages (id, inserted_at, message, user_id, channel_id) VALUES (22285, '2014-01-20 19:24:55.874136', NULL, '55456dea-6c66-49ca-80d4-79e435c544de', 8674);
INSERT INTO messages (id, inserted_at, message, user_id, channel_id) VALUES (44845, '1978-11-23 13:58:26.175998', 'Response if office dark nature size.', 'd03b1776-ac90-4a94-b006-5d7ce6e58f50', 66088);
INSERT INTO messages (id, inserted_at, message, user_id, channel_id) VALUES (9813, '2018-10-11 07:39:36.039200', NULL, '47a281c1-b76b-4496-96c3-b2650c7e58b8', 86856);
INSERT INTO messages (id, inserted_at, message, user_id, channel_id) VALUES (79523, '1980-07-28 19:51:43.689913', 'Election character conference go media color. Act Democrat one camera until stand western.', '6cb97d31-9ac6-4cd4-9042-9580aec3a1d6', 1400);
INSERT INTO messages (id, inserted_at, message, user_id, channel_id) VALUES (12503, '2015-02-27 11:36:07.278584', 'A check add ok day of run bad. Leg best film describe sit look.', '279e3fe9-d5fe-4470-8c4f-b6adebeac08a', 1898);
INSERT INTO messages (id, inserted_at, message, user_id, channel_id) VALUES (43152, '2005-06-09 07:42:52.230640', NULL, '55456dea-6c66-49ca-80d4-79e435c544de', 6863);
INSERT INTO messages (id, inserted_at, message, user_id, channel_id) VALUES (14678, '2019-04-26 16:09:18.724589', 'Loss church admit born big contain. Increase challenge cup girl item.', '6d084486-68ad-442b-a605-0da2e330b481', 2563);
INSERT INTO messages (id, inserted_at, message, user_id, channel_id) VALUES (21848, '2000-12-30 11:04:45.858149', 'Anyone skill why hope could. Size threat red general. Those board friend last never.', '473d6d39-eaca-4e52-950a-2f8f00cbc84b', 75113);
INSERT INTO messages (id, inserted_at, message, user_id, channel_id) VALUES (52454, '1972-02-19 14:29:00.974404', 'Outside million let natural. Better however week anyone.
Put various dark office within.', '6d084486-68ad-442b-a605-0da2e330b481', 56635);
INSERT INTO messages (id, inserted_at, message, user_id, channel_id) VALUES (9585, '2007-11-17 17:28:42.577667', 'Once scientist drive listen budget speech company. Forget wear that be game.', '872a6ae2-d03d-47d2-ac8b-ce5139eda350', 1178);
INSERT INTO messages (id, inserted_at, message, user_id, channel_id) VALUES (91939, '2020-12-16 16:53:04.884638', 'Pick ever together computer plant. Herself write cut understand let job.', 'f44ff568-5344-483b-a8e1-13724336f348', 26970);
INSERT INTO messages (id, inserted_at, message, user_id, channel_id) VALUES (91294, '2015-10-08 09:01:57.861394', NULL, '4610ba55-6baa-434f-a834-74af6dfc1c73', 67392);
INSERT INTO messages (id, inserted_at, message, user_id, channel_id) VALUES (8875, '1973-03-03 15:16:09.466462', 'Maybe economy forget group sing director. Need actually best subject will.', 'bcb07349-1753-4ffb-8561-49c4b121f643', 93245);
INSERT INTO messages (id, inserted_at, message, user_id, channel_id) VALUES (39309, '2017-05-07 19:09:13.328597', 'Of structure rise political night. Bed program box. Medical main society capital door rise own.', '93483430-3b9c-46e5-ac35-853f7113b83c', 67103);
INSERT INTO messages (id, inserted_at, message, user_id, channel_id) VALUES (23460, '2014-10-07 23:42:40.472891', 'About public start read black table chair author. Agree born day follow.', 'a0c4949f-ed09-46c3-bd4b-1af2bda94ba1', 89441);
INSERT INTO messages (id, inserted_at, message, user_id, channel_id) VALUES (70949, '2022-12-27 04:46:01.209229', NULL, '17f155ab-b673-48e3-a3e6-1784e9b914a4', 98234);
INSERT INTO messages (id, inserted_at, message, user_id, channel_id) VALUES (70377, '2010-03-02 04:23:52.321469', 'Whose similar fly exactly summer condition itself. Anything financial skill sometimes cup me thing.', '1efd9f7a-a657-4c4d-aa85-cb8573f3dd39', 67103);
INSERT INTO messages (id, inserted_at, message, user_id, channel_id) VALUES (48094, '1994-07-19 16:23:02.837220', 'Weight authority fine side manager some. Rate live situation speech whom dog.', '47a281c1-b76b-4496-96c3-b2650c7e58b8', 84081);
INSERT INTO messages (id, inserted_at, message, user_id, channel_id) VALUES (84586, '2021-07-13 12:13:30.638916', 'Bar on grow other.', 'c1641f3c-588f-43c3-806f-516f41c1fc48', 86856);
INSERT INTO messages (id, inserted_at, message, user_id, channel_id) VALUES (90557, '2004-09-15 22:39:52.387638', 'Argue feel who. Agency back TV carry clear among.
Process play message be name entire.', 'f44ff568-5344-483b-a8e1-13724336f348', 51954);
INSERT INTO messages (id, inserted_at, message, user_id, channel_id) VALUES (56004, '2002-10-09 17:40:55.256576', 'Pass particular why according down others sure work.', 'd03b1776-ac90-4a94-b006-5d7ce6e58f50', 67392);
INSERT INTO messages (id, inserted_at, message, user_id, channel_id) VALUES (83653, '1976-02-08 03:02:33.397224', NULL, '17f155ab-b673-48e3-a3e6-1784e9b914a4', 32155);
INSERT INTO messages (id, inserted_at, message, user_id, channel_id) VALUES (86238, '1996-10-20 04:37:53.782322', 'Hard season commercial. Both subject practice analysis bad.', '258dc8bd-2fc2-4ffe-9792-0abf8b5cb61e', 2563);
INSERT INTO messages (id, inserted_at, message, user_id, channel_id) VALUES (89107, '1979-06-27 08:40:14.427933', 'Shake determine knowledge decide media per.', '2572c896-87ce-4d15-b898-b4c9b471d401', 1898);
INSERT INTO messages (id, inserted_at, message, user_id, channel_id) VALUES (63506, '1996-10-03 17:18:43.238224', 'Land pressure appear current cause suffer many. Sense reality environmental chair dark must.', '21af7a4c-7f98-41cf-9d13-ee7d7d45fadb', 86856);
INSERT INTO messages (id, inserted_at, message, user_id, channel_id) VALUES (39079, '2008-07-16 13:40:05.915581', 'Image fear painting. Good blood course cell knowledge west marriage.', '93483430-3b9c-46e5-ac35-853f7113b83c', 74588);
INSERT INTO messages (id, inserted_at, message, user_id, channel_id) VALUES (66434, '1995-06-07 22:29:57.689117', 'Financial event idea perform total. Character whose beyond.', '9d3d66b9-f297-4df9-86e6-aeea2a6d2de6', 64605);
INSERT INTO messages (id, inserted_at, message, user_id, channel_id) VALUES (75074, '2012-08-26 11:34:39.824133', 'Yet better stock PM option guess. Thing blood send do. Investment character type mind land general.', '872a6ae2-d03d-47d2-ac8b-ce5139eda350', 26254);
INSERT INTO messages (id, inserted_at, message, user_id, channel_id) VALUES (63492, '1974-08-08 18:10:01.456369', 'Least hard cause rich east both. Card serious situation everyone.', 'd33923b9-f792-4195-956b-93468a83db69', 98234);
INSERT INTO messages (id, inserted_at, message, user_id, channel_id) VALUES (28183, '2023-11-16 03:18:08.986042', NULL, 'a0c4949f-ed09-46c3-bd4b-1af2bda94ba1', 85355);
INSERT INTO messages (id, inserted_at, message, user_id, channel_id) VALUES (84910, '1977-12-16 14:41:09.594800', 'Season woman yard writer yet throw once. Able bit police field. Black poor protect garden.', '6d084486-68ad-442b-a605-0da2e330b481', 64605);
INSERT INTO messages (id, inserted_at, message, user_id, channel_id) VALUES (29434, '1988-05-27 08:51:59.595318', 'Recognize each road leave enjoy. Perform participant nor agree standard. Culture gas morning high.', 'a9a8ac8b-213a-4784-a4ec-d01c4465ddb4', 93245);
INSERT INTO messages (id, inserted_at, message, user_id, channel_id) VALUES (32442, '1991-02-27 20:14:56.426540', 'Party table like heavy herself increase audience nor. New shake without hour product.', '5bc6734f-8f4c-4425-b795-36c383fdbd08', 50097);
INSERT INTO messages (id, inserted_at, message, user_id, channel_id) VALUES (50196, '1972-05-22 22:25:58.109160', 'Technology through look usually standard. Reveal herself remain pressure peace early.', '1efd9f7a-a657-4c4d-aa85-cb8573f3dd39', 1898);
INSERT INTO messages (id, inserted_at, message, user_id, channel_id) VALUES (35866, '2016-12-28 23:21:41.448350', 'Real piece likely scene.', 'cc9b0233-c601-4500-af2c-9a5e98f3ca03', 67103);
INSERT INTO messages (id, inserted_at, message, user_id, channel_id) VALUES (82101, '2009-07-25 16:38:20.113558', 'Difference herself citizen price. Forget clear middle.', '47a281c1-b76b-4496-96c3-b2650c7e58b8', 81899);
INSERT INTO messages (id, inserted_at, message, user_id, channel_id) VALUES (70798, '1979-05-20 23:33:47.024771', 'Say despite generation section news. Anything dinner citizen beyond economy identify write.', 'e0198846-8699-48ad-850a-bed69be7eea7', 67392);
INSERT INTO messages (id, inserted_at, message, user_id, channel_id) VALUES (18778, '2011-12-07 14:35:17.610270', 'Protect list star worry. Question set national understand night organization.', '93483430-3b9c-46e5-ac35-853f7113b83c', 56635);
INSERT INTO messages (id, inserted_at, message, user_id, channel_id) VALUES (20042, '1989-12-30 09:49:03.825219', 'Citizen yet fine national magazine church. Contain arrive similar guess book according.', '21af7a4c-7f98-41cf-9d13-ee7d7d45fadb', 13022);
INSERT INTO messages (id, inserted_at, message, user_id, channel_id) VALUES (41750, '2021-08-20 11:32:05.001789', 'Support seat free blue voice visit song. Practice skill tell man line present.', '5bc6734f-8f4c-4425-b795-36c383fdbd08', 28418);
INSERT INTO messages (id, inserted_at, message, user_id, channel_id) VALUES (14018, '2024-04-22 06:42:43.230264', 'Society buy land support bar. Sort simply bed let although event church.', 'a0c4949f-ed09-46c3-bd4b-1af2bda94ba1', 69775);
INSERT INTO messages (id, inserted_at, message, user_id, channel_id) VALUES (53348, '2018-07-09 01:15:39.646677', 'You writer physical maintain. Same TV form both whom government should. Real bill affect paper.', '279e3fe9-d5fe-4470-8c4f-b6adebeac08a', 67392);
INSERT INTO messages (id, inserted_at, message, user_id, channel_id) VALUES (60477, '2014-06-05 02:34:06.055144', NULL, '47a281c1-b76b-4496-96c3-b2650c7e58b8', 85355);
INSERT INTO messages (id, inserted_at, message, user_id, channel_id) VALUES (12201, '1984-06-26 16:28:29.590513', 'Find around without. Market foreign give service manager sport job.', '4610ba55-6baa-434f-a834-74af6dfc1c73', 1400);
INSERT INTO messages (id, inserted_at, message, user_id, channel_id) VALUES (42989, '2001-12-10 13:35:30.822727', 'Thousand collection yet consumer political peace. Couple treat turn something.', '93483430-3b9c-46e5-ac35-853f7113b83c', 17462);
INSERT INTO messages (id, inserted_at, message, user_id, channel_id) VALUES (13409, '2009-06-15 13:32:13.231008', 'Down room want professor benefit field report. Fast hair long how to. Expect stock late.', '5bc6734f-8f4c-4425-b795-36c383fdbd08', 4443);
INSERT INTO messages (id, inserted_at, message, user_id, channel_id) VALUES (73291, '1992-02-18 12:05:36.248340', 'Fight machine office billion drop clear run. Here provide begin. Either chance maybe what do.', '872a6ae2-d03d-47d2-ac8b-ce5139eda350', 81899);
INSERT INTO messages (id, inserted_at, message, user_id, channel_id) VALUES (20864, '2022-05-14 08:13:53.169629', 'Remain series certain list discuss. Produce paper consumer necessary certain.', 'd03b1776-ac90-4a94-b006-5d7ce6e58f50', 67103);
INSERT INTO messages (id, inserted_at, message, user_id, channel_id) VALUES (60331, '1974-06-06 08:25:52.148377', 'Also enter example local together. Big add material consider.', '55456dea-6c66-49ca-80d4-79e435c544de', 93346);
INSERT INTO messages (id, inserted_at, message, user_id, channel_id) VALUES (96392, '1976-09-02 01:01:30.185441', 'Anyone name skin ten half face maybe. Determine clearly evening increase.', 'a9a8ac8b-213a-4784-a4ec-d01c4465ddb4', 20221);
INSERT INTO messages (id, inserted_at, message, user_id, channel_id) VALUES (86234, '2012-09-08 10:05:04.819015', 'Visit carry nation prove office physical. Bill prevent experience school month simply everything.', 'f44ff568-5344-483b-a8e1-13724336f348', 73200);
INSERT INTO messages (id, inserted_at, message, user_id, channel_id) VALUES (31343, '1993-06-17 12:23:28.882461', 'Now state doctor remain involve. Training administration instead perhaps yard professional.', '088cc971-d758-4af4-ac34-4d0b8695f435', 86856);
INSERT INTO messages (id, inserted_at, message, user_id, channel_id) VALUES (20850, '1989-08-30 18:46:15.918240', 'Finish possible beyond third cost. Field owner new crime.', 'e0198846-8699-48ad-850a-bed69be7eea7', 51954);
INSERT INTO messages (id, inserted_at, message, user_id, channel_id) VALUES (93773, '2013-05-24 01:23:18.537287', 'Ability past employee. Change early travel kind particular top I.', '6d084486-68ad-442b-a605-0da2e330b481', 90528);
INSERT INTO messages (id, inserted_at, message, user_id, channel_id) VALUES (72922, '1999-04-28 02:47:30.121399', 'Response professional four he message. Us TV rather store. Moment various vote.', '258dc8bd-2fc2-4ffe-9792-0abf8b5cb61e', 304);
INSERT INTO messages (id, inserted_at, message, user_id, channel_id) VALUES (29251, '2010-01-19 11:53:00.011870', NULL, 'a0c4949f-ed09-46c3-bd4b-1af2bda94ba1', 89345);
INSERT INTO messages (id, inserted_at, message, user_id, channel_id) VALUES (38644, '1993-12-07 20:23:56.775918', 'Between beautiful quickly such. Hour spend look recently better. Although idea church mind.', '55456dea-6c66-49ca-80d4-79e435c544de', 53434);
INSERT INTO messages (id, inserted_at, message, user_id, channel_id) VALUES (67968, '1992-02-16 08:34:55.984708', 'Many bill bit. Traditional rule popular often if positive.', '47a281c1-b76b-4496-96c3-b2650c7e58b8', 5872);
INSERT INTO messages (id, inserted_at, message, user_id, channel_id) VALUES (18975, '1975-02-09 09:02:27.279964', 'Sign throw wonder. Collection camera finish sound necessary.', '872a6ae2-d03d-47d2-ac8b-ce5139eda350', 17050);
INSERT INTO messages (id, inserted_at, message, user_id, channel_id) VALUES (43983, '1979-08-08 02:00:56.486736', 'Another your support many information safe. Action loss floor edge.', '088cc971-d758-4af4-ac34-4d0b8695f435', 77792);
INSERT INTO messages (id, inserted_at, message, user_id, channel_id) VALUES (69080, '2006-02-27 03:29:30.362114', 'Guess bit a event education kid second on. Form professor raise painting.', '4610ba55-6baa-434f-a834-74af6dfc1c73', 98234);
INSERT INTO messages (id, inserted_at, message, user_id, channel_id) VALUES (88632, '2010-12-13 11:17:57.326241', 'Sea citizen recent ahead. Act once ability may hear agent use.', '47a281c1-b76b-4496-96c3-b2650c7e58b8', 51954);
```

## Future Improvements

- Add support for more SQL databases.
- Add support for more complex date setting (e.g., created_date vs last_updated).
- ~~Add support for more complex datatypes, for instance recognizing and mimicking emails or usernames.~~

## Conclusion

You have successfully generated seed data for your SQL database using the `--seed` option with `supabase-pydantic`. This feature is very useful when you need to populate your database with test data or test your application with a large dataset & Pydantic models.

<br><br><br>
