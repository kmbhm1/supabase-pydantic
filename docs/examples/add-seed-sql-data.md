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

2023-07-15 10:25:18 - INFO - PostGres connection is open.
2023-07-15 10:25:19 - INFO - PostGres connection is closed.
2023-07-15 10:25:19 - INFO - Generating FastAPI Pydantic models...
2023-07-15 10:25:22 - INFO - FastAPI Pydantic models generated successfully: /path/to/your/project/entities/fastapi/schemas_latest.py
2023-07-15 10:25:22 - INFO - File formatted successfully: /path/to/your/project/entities/fastapi/schemas_latest.py
2023-07-15 10:25:22 - INFO - Generating seed data...
2023-07-15 10:25:24 - INFO - Seed data generated successfully: /path/to/your/project/entities/seed_latest.sql
```

Note that the seed sql file will be generated in the `entities` directory of your project: 

``` sql title="seed_latest.sql"
-- role_permissions
INSERT INTO role_permissions (id, role, permission) VALUES (87803, 'admin', 'channels.delete');
INSERT INTO role_permissions (id, role, permission) VALUES (31084, 'admin', 'messages.delete');
INSERT INTO role_permissions (id, role, permission) VALUES (33762, 'moderator', 'channels.delete');
INSERT INTO role_permissions (id, role, permission) VALUES (48955, 'moderator', 'messages.delete');

-- users
INSERT INTO users (id, username, status) VALUES ('525116b8-901b-4828-be03-c44bb3de3b3b', 'hdavis', 'ONLINE');
INSERT INTO users (id, username, status) VALUES ('a2fbe746-3bce-4e28-bce6-305775398857', 'carolyn24', NULL);
INSERT INTO users (id, username, status) VALUES ('28959251-33ed-4bb4-8da7-6903704348f3', 'wthompson', 'OFFLINE');
INSERT INTO users (id, username, status) VALUES ('deeae4e6-1fc3-40ed-9966-30bebaddeb5a', 'kim76', 'ONLINE');
INSERT INTO users (id, username, status) VALUES ('33c6593e-8697-4a67-b729-455cbc0d498b', 'rwise', 'ONLINE');
INSERT INTO users (id, username, status) VALUES ('90a76966-ecb9-4114-af3b-f23471ba5616', 'daniel17', NULL);
INSERT INTO users (id, username, status) VALUES ('1471c3bc-dc10-4d91-9918-271e6ffcf32a', 'mcdowelljohn', NULL);
INSERT INTO users (id, username, status) VALUES ('30d3098d-a436-443b-a4fc-2529e74a0fa9', 'debra45', 'OFFLINE');
INSERT INTO users (id, username, status) VALUES ('00f2e429-83dc-4052-8643-e0c4d931bab2', 'phopkins', 'ONLINE');
INSERT INTO users (id, username, status) VALUES ('22b3bfaf-f35c-4e40-90cf-87805c4a3c2d', 'brittanyhart', 'OFFLINE');
INSERT INTO users (id, username, status) VALUES ('8da77568-8b83-4d70-b872-a4d5472fa0c0', 'kayla82', 'OFFLINE');
INSERT INTO users (id, username, status) VALUES ('6a731db3-a36d-4d47-983c-04c97b91630b', 'lle', 'ONLINE');
INSERT INTO users (id, username, status) VALUES ('55020e0b-5c4e-40f9-942c-0b44529043a6', 'justinmills', 'OFFLINE');
INSERT INTO users (id, username, status) VALUES ('3ac52e44-f864-423d-81fa-4c092d06369c', 'dallen', 'ONLINE');
INSERT INTO users (id, username, status) VALUES ('379b0a29-14af-4779-90ed-6c97e9d9d92d', 'jenniferhughes', 'OFFLINE');
INSERT INTO users (id, username, status) VALUES ('194ab5d9-1fd0-4ba2-83c9-eb920a47f84b', 'jenniferstewart', 'OFFLINE');
INSERT INTO users (id, username, status) VALUES ('448a00d4-b5ae-4d52-9a17-6bc0407ddae4', 'christopher98', 'ONLINE');
INSERT INTO users (id, username, status) VALUES ('56a00eec-628a-465d-a5c0-5a9562cdbbf8', 'mark68', 'ONLINE');
INSERT INTO users (id, username, status) VALUES ('44ddfeaf-bee9-48b7-a554-ef09082f4088', 'gibsongary', NULL);
INSERT INTO users (id, username, status) VALUES ('ef61ef82-53f4-41ea-94e7-ad67f6379b91', 'nortoncrystal', NULL);
INSERT INTO users (id, username, status) VALUES ('6d074ed9-cfa9-4bbc-9be8-14ad71bb1330', 'pmccarthy', 'ONLINE');
INSERT INTO users (id, username, status) VALUES ('fd26ba43-dbba-4c33-9b7d-262f91e8b7a0', 'benjamin81', 'ONLINE');
INSERT INTO users (id, username, status) VALUES ('616d31dc-139f-44a6-b200-3a4ffd79834f', 'daniel42', 'ONLINE');
INSERT INTO users (id, username, status) VALUES ('4f0085e7-155b-4d46-9451-28e5e62ceb7e', 'jaredgay', NULL);
INSERT INTO users (id, username, status) VALUES ('222dc7aa-7f87-408c-b8e4-9c237d44fb5b', 'vturner', 'OFFLINE');
INSERT INTO users (id, username, status) VALUES ('b1bba5eb-2e94-4bac-9e8e-251b13c13ad3', NULL, 'OFFLINE');
INSERT INTO users (id, username, status) VALUES ('50e2395d-31c4-4b13-ac82-1963b7ec3e8a', 'crystal35', 'ONLINE');
INSERT INTO users (id, username, status) VALUES ('00891d6f-be15-40ea-96b5-b8035d6164e7', 'jennifer17', NULL);
INSERT INTO users (id, username, status) VALUES ('97fdb7cc-4cbb-42ab-b0ad-4dabd22aca31', 'thomasmunoz', 'ONLINE');
INSERT INTO users (id, username, status) VALUES ('ec1c09f2-9b79-48f9-b838-df6db4ec88f0', NULL, 'ONLINE');
INSERT INTO users (id, username, status) VALUES ('146a1828-e631-49f6-98f1-42d222b7931f', 'montgomeryjessica', 'OFFLINE');
INSERT INTO users (id, username, status) VALUES ('efe27982-b5c2-46fc-b287-8c61729e8a1c', 'jamesduran', 'OFFLINE');
INSERT INTO users (id, username, status) VALUES ('b9d94cba-bde5-41bc-a634-720d65c23cfb', 'earl09', 'ONLINE');
INSERT INTO users (id, username, status) VALUES ('291ecf4e-53e6-4227-80e3-7904e0f23368', 'valencialawrence', 'ONLINE');
INSERT INTO users (id, username, status) VALUES ('bfde79a0-19e4-42a6-93f0-aa33b5d0b16f', 'jason76', 'ONLINE');
INSERT INTO users (id, username, status) VALUES ('7836b471-3efd-4ccd-a61d-9de717a0051f', NULL, 'OFFLINE');

-- user_roles
INSERT INTO user_roles (id, user_id, role) VALUES (83319, '33c6593e-8697-4a67-b729-455cbc0d498b', 'moderator');
INSERT INTO user_roles (id, user_id, role) VALUES (33898, '90a76966-ecb9-4114-af3b-f23471ba5616', 'moderator');
INSERT INTO user_roles (id, user_id, role) VALUES (85861, 'a2fbe746-3bce-4e28-bce6-305775398857', 'admin');
INSERT INTO user_roles (id, user_id, role) VALUES (10985, 'ef61ef82-53f4-41ea-94e7-ad67f6379b91', 'admin');
INSERT INTO user_roles (id, user_id, role) VALUES (82816, 'b1bba5eb-2e94-4bac-9e8e-251b13c13ad3', 'moderator');
INSERT INTO user_roles (id, user_id, role) VALUES (74426, 'b9d94cba-bde5-41bc-a634-720d65c23cfb', 'moderator');
INSERT INTO user_roles (id, user_id, role) VALUES (75966, 'ec1c09f2-9b79-48f9-b838-df6db4ec88f0', 'moderator');
INSERT INTO user_roles (id, user_id, role) VALUES (84609, 'fd26ba43-dbba-4c33-9b7d-262f91e8b7a0', 'moderator');
INSERT INTO user_roles (id, user_id, role) VALUES (50910, '4f0085e7-155b-4d46-9451-28e5e62ceb7e', 'admin');
INSERT INTO user_roles (id, user_id, role) VALUES (37486, 'efe27982-b5c2-46fc-b287-8c61729e8a1c', 'admin');
INSERT INTO user_roles (id, user_id, role) VALUES (47221, '6a731db3-a36d-4d47-983c-04c97b91630b', 'moderator');
INSERT INTO user_roles (id, user_id, role) VALUES (78989, '22b3bfaf-f35c-4e40-90cf-87805c4a3c2d', 'admin');
INSERT INTO user_roles (id, user_id, role) VALUES (95616, '4f0085e7-155b-4d46-9451-28e5e62ceb7e', 'moderator');
INSERT INTO user_roles (id, user_id, role) VALUES (26133, '146a1828-e631-49f6-98f1-42d222b7931f', 'admin');
INSERT INTO user_roles (id, user_id, role) VALUES (74435, '55020e0b-5c4e-40f9-942c-0b44529043a6', 'admin');
INSERT INTO user_roles (id, user_id, role) VALUES (43973, 'efe27982-b5c2-46fc-b287-8c61729e8a1c', 'moderator');
INSERT INTO user_roles (id, user_id, role) VALUES (20909, '33c6593e-8697-4a67-b729-455cbc0d498b', 'admin');

-- channels
INSERT INTO channels (id, inserted_at, slug, created_by) VALUES (73167, '2020-05-19 19:56:22.739152', 'congress-glass-or', 'efe27982-b5c2-46fc-b287-8c61729e8a1c');
INSERT INTO channels (id, inserted_at, slug, created_by) VALUES (59035, '2020-07-21 12:59:46.688203', 'strong-yes-garden', '30d3098d-a436-443b-a4fc-2529e74a0fa9');
INSERT INTO channels (id, inserted_at, slug, created_by) VALUES (57011, '2024-03-05 13:59:28.859460', 'tax-yes-try', '3ac52e44-f864-423d-81fa-4c092d06369c');
INSERT INTO channels (id, inserted_at, slug, created_by) VALUES (56051, '2022-01-17 12:16:38.051458', 'hit-discover', 'a2fbe746-3bce-4e28-bce6-305775398857');
INSERT INTO channels (id, inserted_at, slug, created_by) VALUES (24499, '2022-07-22 05:04:16.900182', 'return-arrive-rock', '22b3bfaf-f35c-4e40-90cf-87805c4a3c2d');
INSERT INTO channels (id, inserted_at, slug, created_by) VALUES (62758, '2021-12-10 05:16:23.680029', 'which-apply-voice', '7836b471-3efd-4ccd-a61d-9de717a0051f');
INSERT INTO channels (id, inserted_at, slug, created_by) VALUES (82233, '2023-11-09 00:27:22.705116', 'thought-put-reduce', 'efe27982-b5c2-46fc-b287-8c61729e8a1c');
INSERT INTO channels (id, inserted_at, slug, created_by) VALUES (76493, '2022-05-24 13:11:22.534508', 'cost-young-upon', '4f0085e7-155b-4d46-9451-28e5e62ceb7e');
INSERT INTO channels (id, inserted_at, slug, created_by) VALUES (93212, '2023-07-09 12:11:52.868773', 'shake-experience', '6d074ed9-cfa9-4bbc-9be8-14ad71bb1330');
INSERT INTO channels (id, inserted_at, slug, created_by) VALUES (64604, '2020-05-18 14:38:50.692194', 'pick-sure-hard-room', '6a731db3-a36d-4d47-983c-04c97b91630b');
INSERT INTO channels (id, inserted_at, slug, created_by) VALUES (38704, '2019-12-15 04:05:28.598066', 'college-enough-cup', 'b1bba5eb-2e94-4bac-9e8e-251b13c13ad3');
INSERT INTO channels (id, inserted_at, slug, created_by) VALUES (91106, '2021-07-27 09:20:08.928559', 'total-example-call', '33c6593e-8697-4a67-b729-455cbc0d498b');
INSERT INTO channels (id, inserted_at, slug, created_by) VALUES (7055, '2023-09-30 02:58:06.518260', 'however-scientist', 'bfde79a0-19e4-42a6-93f0-aa33b5d0b16f');
INSERT INTO channels (id, inserted_at, slug, created_by) VALUES (61443, '2024-03-13 13:13:17.621869', 'doctor-avoid-cell', '146a1828-e631-49f6-98f1-42d222b7931f');
INSERT INTO channels (id, inserted_at, slug, created_by) VALUES (26048, '2022-07-31 14:10:03.903888', 'play-physical-glass', '50e2395d-31c4-4b13-ac82-1963b7ec3e8a');
INSERT INTO channels (id, inserted_at, slug, created_by) VALUES (37632, '2020-01-11 22:53:32.668729', 'film-why-foot-five', 'deeae4e6-1fc3-40ed-9966-30bebaddeb5a');
INSERT INTO channels (id, inserted_at, slug, created_by) VALUES (79473, '2022-09-08 23:58:29.804262', 'series-attack-no', 'efe27982-b5c2-46fc-b287-8c61729e8a1c');
INSERT INTO channels (id, inserted_at, slug, created_by) VALUES (95748, '2019-08-28 23:07:41.358693', 'particularly', '33c6593e-8697-4a67-b729-455cbc0d498b');
INSERT INTO channels (id, inserted_at, slug, created_by) VALUES (32984, '2020-05-02 03:44:17.576074', 'social-rock-admit', '30d3098d-a436-443b-a4fc-2529e74a0fa9');
INSERT INTO channels (id, inserted_at, slug, created_by) VALUES (44763, '2022-03-02 10:58:30.600494', 'majority-point-best', 'ef61ef82-53f4-41ea-94e7-ad67f6379b91');
INSERT INTO channels (id, inserted_at, slug, created_by) VALUES (87801, '2019-12-06 10:13:13.380238', 'shake-fall-go', 'fd26ba43-dbba-4c33-9b7d-262f91e8b7a0');
INSERT INTO channels (id, inserted_at, slug, created_by) VALUES (26463, '2019-12-31 04:55:28.614491', 'fact-son-think', '3ac52e44-f864-423d-81fa-4c092d06369c');
INSERT INTO channels (id, inserted_at, slug, created_by) VALUES (51366, '2020-07-22 22:34:00.752688', 'practice-capital', '30d3098d-a436-443b-a4fc-2529e74a0fa9');
INSERT INTO channels (id, inserted_at, slug, created_by) VALUES (88239, '2023-01-29 16:35:12.975673', 'perhaps-education', '50e2395d-31c4-4b13-ac82-1963b7ec3e8a');
INSERT INTO channels (id, inserted_at, slug, created_by) VALUES (93630, '2023-12-04 10:53:05.602732', 'meet-performance', '222dc7aa-7f87-408c-b8e4-9c237d44fb5b');
INSERT INTO channels (id, inserted_at, slug, created_by) VALUES (67309, '2019-10-13 01:28:18.688679', 'environment-hot', '616d31dc-139f-44a6-b200-3a4ffd79834f');
INSERT INTO channels (id, inserted_at, slug, created_by) VALUES (27378, '2022-09-21 00:20:24.387332', 'pass-choose-will', '28959251-33ed-4bb4-8da7-6903704348f3');
INSERT INTO channels (id, inserted_at, slug, created_by) VALUES (325, '2020-10-11 20:18:53.040586', 'leave-allow-others', 'a2fbe746-3bce-4e28-bce6-305775398857');
INSERT INTO channels (id, inserted_at, slug, created_by) VALUES (36861, '2021-11-21 13:28:56.636748', 'become-today', 'ec1c09f2-9b79-48f9-b838-df6db4ec88f0');
INSERT INTO channels (id, inserted_at, slug, created_by) VALUES (88947, '2024-05-12 00:35:22.301089', 'note-meeting-bar', 'efe27982-b5c2-46fc-b287-8c61729e8a1c');
INSERT INTO channels (id, inserted_at, slug, created_by) VALUES (39505, '2023-12-15 06:31:34.955745', 'idea-teacher-would', '8da77568-8b83-4d70-b872-a4d5472fa0c0');
INSERT INTO channels (id, inserted_at, slug, created_by) VALUES (23239, '2020-03-13 05:28:38.338495', 'history-big-station', '7836b471-3efd-4ccd-a61d-9de717a0051f');
INSERT INTO channels (id, inserted_at, slug, created_by) VALUES (66980, '2020-06-23 00:54:48.738734', 'first-more-baby', '00891d6f-be15-40ea-96b5-b8035d6164e7');
INSERT INTO channels (id, inserted_at, slug, created_by) VALUES (89498, '2023-12-14 23:39:12.696564', 'onto-now-his-nor', '379b0a29-14af-4779-90ed-6c97e9d9d92d');
INSERT INTO channels (id, inserted_at, slug, created_by) VALUES (71298, '2022-03-31 09:30:28.774492', 'world-near-visit', 'deeae4e6-1fc3-40ed-9966-30bebaddeb5a');
INSERT INTO channels (id, inserted_at, slug, created_by) VALUES (56167, '2020-08-20 23:47:05.461635', 'miss-five-lay-never', '448a00d4-b5ae-4d52-9a17-6bc0407ddae4');
INSERT INTO channels (id, inserted_at, slug, created_by) VALUES (10276, '2023-12-03 09:45:20.970217', 'report-attack-right', '55020e0b-5c4e-40f9-942c-0b44529043a6');
INSERT INTO channels (id, inserted_at, slug, created_by) VALUES (45941, '2021-11-28 16:19:35.948412', 'whatever-which', '222dc7aa-7f87-408c-b8e4-9c237d44fb5b');
INSERT INTO channels (id, inserted_at, slug, created_by) VALUES (72582, '2020-05-22 23:31:16.312553', 'rich-wind-lot-that', 'fd26ba43-dbba-4c33-9b7d-262f91e8b7a0');
INSERT INTO channels (id, inserted_at, slug, created_by) VALUES (52450, '2022-02-25 01:57:50.751057', 'head-executive', '525116b8-901b-4828-be03-c44bb3de3b3b');
INSERT INTO channels (id, inserted_at, slug, created_by) VALUES (189, '2022-11-02 09:33:50.948655', 'operation-health', 'ef61ef82-53f4-41ea-94e7-ad67f6379b91');
INSERT INTO channels (id, inserted_at, slug, created_by) VALUES (51664, '2020-11-29 22:52:51.897747', 'deal-same-according', '379b0a29-14af-4779-90ed-6c97e9d9d92d');
INSERT INTO channels (id, inserted_at, slug, created_by) VALUES (13325, '2020-12-30 01:01:50.271950', 'summer-field', 'efe27982-b5c2-46fc-b287-8c61729e8a1c');
INSERT INTO channels (id, inserted_at, slug, created_by) VALUES (91537, '2023-02-10 06:17:01.907602', 'one-woman-animal', '30d3098d-a436-443b-a4fc-2529e74a0fa9');
INSERT INTO channels (id, inserted_at, slug, created_by) VALUES (30391, '2022-01-24 08:07:56.246516', 'state-job-course', '50e2395d-31c4-4b13-ac82-1963b7ec3e8a');
INSERT INTO channels (id, inserted_at, slug, created_by) VALUES (6035, '2020-05-29 22:45:14.954044', 'thought-arrive', 'ef61ef82-53f4-41ea-94e7-ad67f6379b91');
INSERT INTO channels (id, inserted_at, slug, created_by) VALUES (20063, '2020-09-24 07:11:44.431197', 'leader-mrs-figure', 'ef61ef82-53f4-41ea-94e7-ad67f6379b91');
INSERT INTO channels (id, inserted_at, slug, created_by) VALUES (71838, '2020-09-27 21:08:25.259468', 'return-arm-several', '90a76966-ecb9-4114-af3b-f23471ba5616');
INSERT INTO channels (id, inserted_at, slug, created_by) VALUES (30163, '2024-06-16 04:52:18.677314', 'natural-left-story', 'ec1c09f2-9b79-48f9-b838-df6db4ec88f0');
INSERT INTO channels (id, inserted_at, slug, created_by) VALUES (27128, '2021-11-07 23:05:34.459393', 'organization-than', '448a00d4-b5ae-4d52-9a17-6bc0407ddae4');
INSERT INTO channels (id, inserted_at, slug, created_by) VALUES (44185, '2021-07-23 04:34:19.933307', 'industry-leader', '97fdb7cc-4cbb-42ab-b0ad-4dabd22aca31');
INSERT INTO channels (id, inserted_at, slug, created_by) VALUES (93337, '2021-09-01 17:43:30.562810', 'wall-sound-but-note', '6a731db3-a36d-4d47-983c-04c97b91630b');
INSERT INTO channels (id, inserted_at, slug, created_by) VALUES (56533, '2020-06-12 06:12:05.934041', 'play-under-practice', 'ec1c09f2-9b79-48f9-b838-df6db4ec88f0');
INSERT INTO channels (id, inserted_at, slug, created_by) VALUES (86588, '2023-10-06 19:01:07.180291', 'wall-suggest-turn', '8da77568-8b83-4d70-b872-a4d5472fa0c0');
INSERT INTO channels (id, inserted_at, slug, created_by) VALUES (60327, '2022-10-24 01:56:44.013445', 'tend-build-simple', 'b9d94cba-bde5-41bc-a634-720d65c23cfb');
INSERT INTO channels (id, inserted_at, slug, created_by) VALUES (52745, '2021-12-17 07:32:59.019277', 'unit-painting-our', '30d3098d-a436-443b-a4fc-2529e74a0fa9');
INSERT INTO channels (id, inserted_at, slug, created_by) VALUES (68649, '2024-04-04 12:14:02.987468', 'politics-middle', '55020e0b-5c4e-40f9-942c-0b44529043a6');
INSERT INTO channels (id, inserted_at, slug, created_by) VALUES (93207, '2023-07-15 06:50:06.450265', 'only-worry-positive', '00891d6f-be15-40ea-96b5-b8035d6164e7');
INSERT INTO channels (id, inserted_at, slug, created_by) VALUES (85531, '2022-09-18 06:45:13.687391', 'spend-score-perform', '4f0085e7-155b-4d46-9451-28e5e62ceb7e');
INSERT INTO channels (id, inserted_at, slug, created_by) VALUES (89718, '2022-09-19 03:04:53.394402', 'pick-understand', '194ab5d9-1fd0-4ba2-83c9-eb920a47f84b');
INSERT INTO channels (id, inserted_at, slug, created_by) VALUES (24669, '2021-07-17 03:29:02.985954', 'impact-offer', 'efe27982-b5c2-46fc-b287-8c61729e8a1c');
INSERT INTO channels (id, inserted_at, slug, created_by) VALUES (87023, '2019-12-16 22:20:34.613300', 'after-then-within', '7836b471-3efd-4ccd-a61d-9de717a0051f');
INSERT INTO channels (id, inserted_at, slug, created_by) VALUES (22166, '2021-11-14 15:21:49.144113', 'election-better', 'fd26ba43-dbba-4c33-9b7d-262f91e8b7a0');
INSERT INTO channels (id, inserted_at, slug, created_by) VALUES (82868, '2023-09-21 00:34:23.777594', 'offer-trial', '8da77568-8b83-4d70-b872-a4d5472fa0c0');
INSERT INTO channels (id, inserted_at, slug, created_by) VALUES (16571, '2022-01-21 16:10:42.260021', 'dream-wear-finally', 'ec1c09f2-9b79-48f9-b838-df6db4ec88f0');
INSERT INTO channels (id, inserted_at, slug, created_by) VALUES (28400, '2023-07-10 15:26:59.785436', 'remember-among-kind', 'a2fbe746-3bce-4e28-bce6-305775398857');
INSERT INTO channels (id, inserted_at, slug, created_by) VALUES (29889, '2021-07-03 05:31:43.548479', 'traditional-choice', '222dc7aa-7f87-408c-b8e4-9c237d44fb5b');
INSERT INTO channels (id, inserted_at, slug, created_by) VALUES (17512, '2023-05-05 16:35:13.471517', 'modern-office-some', 'ec1c09f2-9b79-48f9-b838-df6db4ec88f0');
INSERT INTO channels (id, inserted_at, slug, created_by) VALUES (51035, '2019-12-18 03:26:45.038981', 'could-reality-miss', '379b0a29-14af-4779-90ed-6c97e9d9d92d');
INSERT INTO channels (id, inserted_at, slug, created_by) VALUES (59627, '2023-01-04 20:46:57.295161', 'accept-marriage', '6d074ed9-cfa9-4bbc-9be8-14ad71bb1330');
INSERT INTO channels (id, inserted_at, slug, created_by) VALUES (30149, '2019-12-03 13:19:18.953340', 'east-movie-between', '3ac52e44-f864-423d-81fa-4c092d06369c');
INSERT INTO channels (id, inserted_at, slug, created_by) VALUES (12409, '2021-11-07 16:17:18.083127', 'price-wish-fact', '4f0085e7-155b-4d46-9451-28e5e62ceb7e');
INSERT INTO channels (id, inserted_at, slug, created_by) VALUES (35432, '2024-06-14 02:09:44.794580', 'less-serve', '1471c3bc-dc10-4d91-9918-271e6ffcf32a');
INSERT INTO channels (id, inserted_at, slug, created_by) VALUES (68566, '2021-09-11 19:52:45.272986', 'stage-eat-east', '1471c3bc-dc10-4d91-9918-271e6ffcf32a');
INSERT INTO channels (id, inserted_at, slug, created_by) VALUES (62611, '2021-05-14 20:57:16.836321', 'music-not-kid', '56a00eec-628a-465d-a5c0-5a9562cdbbf8');
INSERT INTO channels (id, inserted_at, slug, created_by) VALUES (25532, '2024-02-24 06:44:10.990147', 'issue-ten', 'bfde79a0-19e4-42a6-93f0-aa33b5d0b16f');
INSERT INTO channels (id, inserted_at, slug, created_by) VALUES (93875, '2021-08-18 16:25:41.962306', 'only-for-raise-name', '7836b471-3efd-4ccd-a61d-9de717a0051f');
INSERT INTO channels (id, inserted_at, slug, created_by) VALUES (43742, '2020-12-31 10:37:34.457135', 'describe-return', '6a731db3-a36d-4d47-983c-04c97b91630b');
INSERT INTO channels (id, inserted_at, slug, created_by) VALUES (82869, '2019-11-24 05:42:17.307144', 'coach-manage-here', 'a2fbe746-3bce-4e28-bce6-305775398857');
INSERT INTO channels (id, inserted_at, slug, created_by) VALUES (53550, '2020-10-19 19:42:46.511516', 'worker-police-along', '55020e0b-5c4e-40f9-942c-0b44529043a6');
INSERT INTO channels (id, inserted_at, slug, created_by) VALUES (68085, '2019-10-17 10:36:50.744514', 'true-everyone-land', '55020e0b-5c4e-40f9-942c-0b44529043a6');
INSERT INTO channels (id, inserted_at, slug, created_by) VALUES (61914, '2024-03-31 05:14:58.057353', 'election-beat-good', '8da77568-8b83-4d70-b872-a4d5472fa0c0');
INSERT INTO channels (id, inserted_at, slug, created_by) VALUES (28392, '2021-01-14 22:46:26.919398', 'offer-throw-occur', '194ab5d9-1fd0-4ba2-83c9-eb920a47f84b');
INSERT INTO channels (id, inserted_at, slug, created_by) VALUES (44458, '2020-09-03 06:53:39.310147', 'late-forward-firm', '00f2e429-83dc-4052-8643-e0c4d931bab2');
INSERT INTO channels (id, inserted_at, slug, created_by) VALUES (98176, '2023-07-13 00:01:15.441537', 'morning-chair', '6a731db3-a36d-4d47-983c-04c97b91630b');
INSERT INTO channels (id, inserted_at, slug, created_by) VALUES (19763, '2022-05-02 14:53:30.866564', 'best-green-town', '22b3bfaf-f35c-4e40-90cf-87805c4a3c2d');
INSERT INTO channels (id, inserted_at, slug, created_by) VALUES (36219, '2020-11-27 22:53:28.104114', 'daughter-modern', 'ef61ef82-53f4-41ea-94e7-ad67f6379b91');
INSERT INTO channels (id, inserted_at, slug, created_by) VALUES (31071, '2022-03-14 18:36:44.059751', 'believe-large', 'deeae4e6-1fc3-40ed-9966-30bebaddeb5a');
INSERT INTO channels (id, inserted_at, slug, created_by) VALUES (410, '2023-03-26 21:07:08.952724', 'season-happen', 'fd26ba43-dbba-4c33-9b7d-262f91e8b7a0');
INSERT INTO channels (id, inserted_at, slug, created_by) VALUES (77734, '2022-04-11 06:18:47.817735', 'move-these-blood', 'b9d94cba-bde5-41bc-a634-720d65c23cfb');
INSERT INTO channels (id, inserted_at, slug, created_by) VALUES (14244, '2023-03-10 01:54:51.800683', 'congress-during', 'b1bba5eb-2e94-4bac-9e8e-251b13c13ad3');
INSERT INTO channels (id, inserted_at, slug, created_by) VALUES (20824, '2020-03-06 10:48:39.335374', 'society-image', '525116b8-901b-4828-be03-c44bb3de3b3b');
INSERT INTO channels (id, inserted_at, slug, created_by) VALUES (90103, '2020-12-03 15:28:03.753493', 'beyond-than-support', '28959251-33ed-4bb4-8da7-6903704348f3');
INSERT INTO channels (id, inserted_at, slug, created_by) VALUES (99108, '2022-09-06 19:36:13.763351', 'we-teacher-he', '222dc7aa-7f87-408c-b8e4-9c237d44fb5b');
INSERT INTO channels (id, inserted_at, slug, created_by) VALUES (67523, '2022-05-11 18:28:19.590147', 'national-assume', '28959251-33ed-4bb4-8da7-6903704348f3');
INSERT INTO channels (id, inserted_at, slug, created_by) VALUES (81395, '2020-08-14 14:51:08.888472', 'effect-however', '379b0a29-14af-4779-90ed-6c97e9d9d92d');
INSERT INTO channels (id, inserted_at, slug, created_by) VALUES (92250, '2022-11-23 00:10:14.013508', 'president-professor', '379b0a29-14af-4779-90ed-6c97e9d9d92d');
INSERT INTO channels (id, inserted_at, slug, created_by) VALUES (86781, '2020-04-06 05:16:35.671224', 'stuff-much-action', '525116b8-901b-4828-be03-c44bb3de3b3b');
INSERT INTO channels (id, inserted_at, slug, created_by) VALUES (28447, '2023-12-16 15:34:19.859106', 'morning-increase', 'deeae4e6-1fc3-40ed-9966-30bebaddeb5a');
INSERT INTO channels (id, inserted_at, slug, created_by) VALUES (14588, '2022-04-29 13:21:14.385175', 'kitchen-beyond', '33c6593e-8697-4a67-b729-455cbc0d498b');
INSERT INTO channels (id, inserted_at, slug, created_by) VALUES (27285, '2020-01-26 21:01:33.279949', 'use-two-around-key', 'b1bba5eb-2e94-4bac-9e8e-251b13c13ad3');
INSERT INTO channels (id, inserted_at, slug, created_by) VALUES (47791, '2021-05-19 00:19:29.767325', 'i-cause-myself', '291ecf4e-53e6-4227-80e3-7904e0f23368');
INSERT INTO channels (id, inserted_at, slug, created_by) VALUES (24272, '2023-08-23 01:31:23.997519', 'decide-store-above', 'b1bba5eb-2e94-4bac-9e8e-251b13c13ad3');
INSERT INTO channels (id, inserted_at, slug, created_by) VALUES (67312, '2021-11-26 16:59:11.131843', 'sister-star', '1471c3bc-dc10-4d91-9918-271e6ffcf32a');
INSERT INTO channels (id, inserted_at, slug, created_by) VALUES (2834, '2022-05-28 09:17:42.976684', 'subject-stuff-left', '448a00d4-b5ae-4d52-9a17-6bc0407ddae4');
INSERT INTO channels (id, inserted_at, slug, created_by) VALUES (10416, '2019-09-14 22:58:57.562240', 'inside-town', '4f0085e7-155b-4d46-9451-28e5e62ceb7e');
INSERT INTO channels (id, inserted_at, slug, created_by) VALUES (86312, '2020-03-24 01:24:00.963407', 'hot-mr-standard', '56a00eec-628a-465d-a5c0-5a9562cdbbf8');
INSERT INTO channels (id, inserted_at, slug, created_by) VALUES (32283, '2023-03-23 00:40:12.516776', 'enter-capital-good', '616d31dc-139f-44a6-b200-3a4ffd79834f');
INSERT INTO channels (id, inserted_at, slug, created_by) VALUES (50581, '2021-04-13 02:30:24.165179', 'great-deep-give', '7836b471-3efd-4ccd-a61d-9de717a0051f');
INSERT INTO channels (id, inserted_at, slug, created_by) VALUES (35873, '2024-01-22 23:04:29.293683', 'media-minute-page', '44ddfeaf-bee9-48b7-a554-ef09082f4088');
INSERT INTO channels (id, inserted_at, slug, created_by) VALUES (54165, '2024-01-18 11:28:57.551250', 'project-social-data', '00f2e429-83dc-4052-8643-e0c4d931bab2');
INSERT INTO channels (id, inserted_at, slug, created_by) VALUES (99123, '2022-01-18 18:07:24.079151', 'million-pretty', '97fdb7cc-4cbb-42ab-b0ad-4dabd22aca31');
INSERT INTO channels (id, inserted_at, slug, created_by) VALUES (39593, '2022-10-16 13:32:15.357604', 'young-before-pull', '448a00d4-b5ae-4d52-9a17-6bc0407ddae4');
INSERT INTO channels (id, inserted_at, slug, created_by) VALUES (42470, '2023-12-15 15:36:07.126564', 'wife-hour-three', 'b1bba5eb-2e94-4bac-9e8e-251b13c13ad3');
INSERT INTO channels (id, inserted_at, slug, created_by) VALUES (85094, '2022-05-05 01:37:16.843638', 'what-economic-treat', '194ab5d9-1fd0-4ba2-83c9-eb920a47f84b');
INSERT INTO channels (id, inserted_at, slug, created_by) VALUES (90768, '2020-01-15 13:51:39.705106', 'indeed-black', '4f0085e7-155b-4d46-9451-28e5e62ceb7e');

-- messages
INSERT INTO messages (id, inserted_at, message, user_id, channel_id) VALUES (94829, '2021-11-18 13:04:06.597713', 'President not defense song drive. Total American significant out Republican share thus gas.', '00891d6f-be15-40ea-96b5-b8035d6164e7', 19763);
INSERT INTO messages (id, inserted_at, message, user_id, channel_id) VALUES (62458, '2022-08-23 00:33:17.215169', 'Agree every rich together.', '8da77568-8b83-4d70-b872-a4d5472fa0c0', 30391);
INSERT INTO messages (id, inserted_at, message, user_id, channel_id) VALUES (62048, '2024-05-22 10:33:44.088109', 'Tax deep know well.
Offer by box necessary increase continue push.', '4f0085e7-155b-4d46-9451-28e5e62ceb7e', 93875);
INSERT INTO messages (id, inserted_at, message, user_id, channel_id) VALUES (34834, '2021-12-13 12:23:09.500900', NULL, '90a76966-ecb9-4114-af3b-f23471ba5616', 27285);
INSERT INTO messages (id, inserted_at, message, user_id, channel_id) VALUES (50407, '2023-08-07 14:17:15.536419', 'Food tell six beautiful. Meeting hot travel set see. Improve here approach today girl use book.', 'b1bba5eb-2e94-4bac-9e8e-251b13c13ad3', 28400);
INSERT INTO messages (id, inserted_at, message, user_id, channel_id) VALUES (18740, '2021-07-16 21:37:58.483578', 'Reason each home church beat major. Power ask large this respond central.', '222dc7aa-7f87-408c-b8e4-9c237d44fb5b', 44763);
INSERT INTO messages (id, inserted_at, message, user_id, channel_id) VALUES (69265, '2019-08-27 02:46:14.472327', NULL, '56a00eec-628a-465d-a5c0-5a9562cdbbf8', 28400);
INSERT INTO messages (id, inserted_at, message, user_id, channel_id) VALUES (88099, '2021-02-16 16:55:41.204674', 'Add wrong sing able we follow. Save style cup foreign. Current like any.', '33c6593e-8697-4a67-b729-455cbc0d498b', 35432);
INSERT INTO messages (id, inserted_at, message, user_id, channel_id) VALUES (55517, '2022-04-25 05:19:38.712064', 'Take stage son build Republican despite.', '448a00d4-b5ae-4d52-9a17-6bc0407ddae4', 56533);
INSERT INTO messages (id, inserted_at, message, user_id, channel_id) VALUES (76685, '2021-12-12 02:16:43.536780', 'Former remain concern fish hear choice often. Minute year TV short year receive.', '56a00eec-628a-465d-a5c0-5a9562cdbbf8', 20824);
INSERT INTO messages (id, inserted_at, message, user_id, channel_id) VALUES (88942, '2020-11-02 00:43:04.648724', 'Machine break president sit. How ask decision audience these office yard special.', 'ef61ef82-53f4-41ea-94e7-ad67f6379b91', 90103);
INSERT INTO messages (id, inserted_at, message, user_id, channel_id) VALUES (15040, '2020-10-19 04:37:21.574757', 'Method kitchen three floor increase. Trouble law finally school economy.', '448a00d4-b5ae-4d52-9a17-6bc0407ddae4', 51664);
INSERT INTO messages (id, inserted_at, message, user_id, channel_id) VALUES (87093, '2021-02-05 21:04:10.161199', 'Set television skin remain window for before. Manage reflect various treatment.', 'deeae4e6-1fc3-40ed-9966-30bebaddeb5a', 62758);
INSERT INTO messages (id, inserted_at, message, user_id, channel_id) VALUES (4529, '2023-09-11 22:51:51.721073', 'Gun company build also fear. Boy weight institution scene party article film fall.', 'bfde79a0-19e4-42a6-93f0-aa33b5d0b16f', 29889);
INSERT INTO messages (id, inserted_at, message, user_id, channel_id) VALUES (48614, '2021-06-23 02:55:00.286303', 'Likely collection ago throw group eat. Show say free window reason large.', '379b0a29-14af-4779-90ed-6c97e9d9d92d', 44763);
INSERT INTO messages (id, inserted_at, message, user_id, channel_id) VALUES (45510, '2021-03-22 05:35:26.874110', NULL, '3ac52e44-f864-423d-81fa-4c092d06369c', 61443);
INSERT INTO messages (id, inserted_at, message, user_id, channel_id) VALUES (41375, '2021-02-04 09:04:51.698930', 'Every find lot something make. Chance Congress state use popular.', '7836b471-3efd-4ccd-a61d-9de717a0051f', 68085);
INSERT INTO messages (id, inserted_at, message, user_id, channel_id) VALUES (43201, '2024-04-26 16:55:19.388476', 'Sign important sell staff day. Main here standard weight. Their use nature model.', '194ab5d9-1fd0-4ba2-83c9-eb920a47f84b', 16571);
INSERT INTO messages (id, inserted_at, message, user_id, channel_id) VALUES (14305, '2022-09-26 15:48:24.874145', 'Father executive media since. Approach while than hear teacher. Center off main possible prove.', '30d3098d-a436-443b-a4fc-2529e74a0fa9', 90768);
INSERT INTO messages (id, inserted_at, message, user_id, channel_id) VALUES (41065, '2022-06-21 21:43:41.518341', 'Expert despite region college wall include. Experience apply nor stand risk.', '56a00eec-628a-465d-a5c0-5a9562cdbbf8', 23239);
INSERT INTO messages (id, inserted_at, message, user_id, channel_id) VALUES (74148, '2020-01-10 12:16:15.430840', 'Ready happy hair purpose hand represent. Lay blood high give huge position.', '194ab5d9-1fd0-4ba2-83c9-eb920a47f84b', 14588);
INSERT INTO messages (id, inserted_at, message, user_id, channel_id) VALUES (79178, '2021-07-24 09:12:08.450179', 'Him ever player themselves special agent letter yet. Yourself trouble peace over though.', 'b1bba5eb-2e94-4bac-9e8e-251b13c13ad3', 36219);
INSERT INTO messages (id, inserted_at, message, user_id, channel_id) VALUES (84849, '2020-06-12 08:29:55.520926', 'Perhaps from marriage who finally. Policy ground which impact catch.', '525116b8-901b-4828-be03-c44bb3de3b3b', 92250);
INSERT INTO messages (id, inserted_at, message, user_id, channel_id) VALUES (22983, '2020-12-10 08:06:53.142072', 'Quickly five figure example natural same. Very open human without fear. Fish worry sea prepare.', '28959251-33ed-4bb4-8da7-6903704348f3', 39593);
INSERT INTO messages (id, inserted_at, message, user_id, channel_id) VALUES (20195, '2021-04-25 01:02:29.267352', 'Call than southern base. Dinner crime positive throughout look north. Social again theory director.', 'deeae4e6-1fc3-40ed-9966-30bebaddeb5a', 71838);
INSERT INTO messages (id, inserted_at, message, user_id, channel_id) VALUES (32111, '2021-11-30 12:38:18.374103', 'Case author ever between necessary. Direction fund total Congress until policy stop economy.', 'deeae4e6-1fc3-40ed-9966-30bebaddeb5a', 99123);
INSERT INTO messages (id, inserted_at, message, user_id, channel_id) VALUES (58071, '2023-03-22 00:50:48.148502', 'Glass pull collection. Organization and do development south require light.', '4f0085e7-155b-4d46-9451-28e5e62ceb7e', 77734);
INSERT INTO messages (id, inserted_at, message, user_id, channel_id) VALUES (27386, '2020-05-29 05:52:53.740390', 'Food a business. College school ground approach election. Well statement high actually.', '56a00eec-628a-465d-a5c0-5a9562cdbbf8', 14244);
INSERT INTO messages (id, inserted_at, message, user_id, channel_id) VALUES (4135, '2021-12-28 18:06:39.722119', 'Around sure try interesting expect reduce adult. Plan price hair movie determine crime.', 'deeae4e6-1fc3-40ed-9966-30bebaddeb5a', 26463);
INSERT INTO messages (id, inserted_at, message, user_id, channel_id) VALUES (5891, '2021-01-09 23:55:07.136522', 'When yourself lawyer current sort task. Western happy whether account. Treatment old music cold.', '3ac52e44-f864-423d-81fa-4c092d06369c', 12409);
INSERT INTO messages (id, inserted_at, message, user_id, channel_id) VALUES (35179, '2021-10-13 15:46:37.447123', 'Capital eight during begin pick thousand read. Four necessary film the.', '222dc7aa-7f87-408c-b8e4-9c237d44fb5b', 12409);
INSERT INTO messages (id, inserted_at, message, user_id, channel_id) VALUES (5306, '2021-04-01 12:15:32.205757', 'Wife recently generation produce heart.', '33c6593e-8697-4a67-b729-455cbc0d498b', 93207);
INSERT INTO messages (id, inserted_at, message, user_id, channel_id) VALUES (59160, '2023-02-14 15:43:50.376787', 'Little hot exist design. Provide choice born.', 'b1bba5eb-2e94-4bac-9e8e-251b13c13ad3', 89498);
INSERT INTO messages (id, inserted_at, message, user_id, channel_id) VALUES (19237, '2022-01-22 00:50:53.240448', 'Yeah newspaper meeting plan. Set half describe. Become court table.', '8da77568-8b83-4d70-b872-a4d5472fa0c0', 90103);
INSERT INTO messages (id, inserted_at, message, user_id, channel_id) VALUES (60640, '2022-04-29 13:45:54.910076', 'Job tonight at color light statement. Defense imagine material meet reflect.', '8da77568-8b83-4d70-b872-a4d5472fa0c0', 66980);
INSERT INTO messages (id, inserted_at, message, user_id, channel_id) VALUES (65030, '2020-05-15 15:17:33.631718', 'Manage off poor. Include suggest mention top. Rise everybody candidate local.', '448a00d4-b5ae-4d52-9a17-6bc0407ddae4', 93630);
INSERT INTO messages (id, inserted_at, message, user_id, channel_id) VALUES (72790, '2021-02-27 00:21:40.595679', 'Letter expert let tree environmental huge land avoid.
Movie summer near attack next.', '448a00d4-b5ae-4d52-9a17-6bc0407ddae4', 82869);
INSERT INTO messages (id, inserted_at, message, user_id, channel_id) VALUES (63137, '2019-09-22 04:34:35.341990', NULL, 'ef61ef82-53f4-41ea-94e7-ad67f6379b91', 62758);
INSERT INTO messages (id, inserted_at, message, user_id, channel_id) VALUES (24400, '2022-08-14 03:45:10.347726', 'Key coach cut partner. Most free across notice skin. Common stand painting simple.', '6a731db3-a36d-4d47-983c-04c97b91630b', 86312);
INSERT INTO messages (id, inserted_at, message, user_id, channel_id) VALUES (7024, '2023-08-23 13:34:22.749739', 'Color hard end result suggest. Newspaper free born begin.', '194ab5d9-1fd0-4ba2-83c9-eb920a47f84b', 93212);
INSERT INTO messages (id, inserted_at, message, user_id, channel_id) VALUES (37547, '2021-08-01 19:19:22.498216', 'Ok range help accept American. Challenge standard produce property range song.', '55020e0b-5c4e-40f9-942c-0b44529043a6', 95748);
INSERT INTO messages (id, inserted_at, message, user_id, channel_id) VALUES (48129, '2022-10-06 02:50:57.050759', 'Interest start pretty day shoulder in market. Foot these modern protect including forget garden.', '55020e0b-5c4e-40f9-942c-0b44529043a6', 38704);
INSERT INTO messages (id, inserted_at, message, user_id, channel_id) VALUES (78395, '2022-02-18 07:22:15.841797', 'Mother lot choice study it. Have prepare stay clear black choose truth close.', '50e2395d-31c4-4b13-ac82-1963b7ec3e8a', 73167);
INSERT INTO messages (id, inserted_at, message, user_id, channel_id) VALUES (67978, '2023-07-19 02:21:10.810202', 'Animal quickly understand section research issue. Smile bill different as project more.', '146a1828-e631-49f6-98f1-42d222b7931f', 73167);
INSERT INTO messages (id, inserted_at, message, user_id, channel_id) VALUES (92790, '2023-06-04 10:33:16.189443', 'Medical party partner easy. Better type service serious.', '30d3098d-a436-443b-a4fc-2529e74a0fa9', 24272);
INSERT INTO messages (id, inserted_at, message, user_id, channel_id) VALUES (24246, '2020-02-29 16:17:02.803081', 'Firm ask example guy goal degree. Tax class her section each star may job.', 'efe27982-b5c2-46fc-b287-8c61729e8a1c', 13325);
INSERT INTO messages (id, inserted_at, message, user_id, channel_id) VALUES (95540, '2022-07-31 22:16:49.164415', 'Down once really. Sense recognize voice concern.', '56a00eec-628a-465d-a5c0-5a9562cdbbf8', 44763);
INSERT INTO messages (id, inserted_at, message, user_id, channel_id) VALUES (54228, '2022-06-21 19:21:01.503431', NULL, '50e2395d-31c4-4b13-ac82-1963b7ec3e8a', 10416);
INSERT INTO messages (id, inserted_at, message, user_id, channel_id) VALUES (4327, '2020-05-07 05:43:01.645906', NULL, '30d3098d-a436-443b-a4fc-2529e74a0fa9', 30163);
INSERT INTO messages (id, inserted_at, message, user_id, channel_id) VALUES (99849, '2021-10-05 21:43:20.571702', 'List debate war instead. Father prove certain past.
Necessary knowledge bring so despite dog.', 'a2fbe746-3bce-4e28-bce6-305775398857', 35873);
INSERT INTO messages (id, inserted_at, message, user_id, channel_id) VALUES (57113, '2020-10-21 07:12:50.011332', 'Between smile better magazine. Style interesting man up majority soldier owner.', '146a1828-e631-49f6-98f1-42d222b7931f', 24499);
INSERT INTO messages (id, inserted_at, message, user_id, channel_id) VALUES (83726, '2020-12-20 20:59:06.544979', 'Himself particular specific. Nearly you authority poor. Water build participant behind.', 'efe27982-b5c2-46fc-b287-8c61729e8a1c', 56533);
INSERT INTO messages (id, inserted_at, message, user_id, channel_id) VALUES (76688, '2022-11-23 08:27:22.880867', NULL, 'deeae4e6-1fc3-40ed-9966-30bebaddeb5a', 92250);
INSERT INTO messages (id, inserted_at, message, user_id, channel_id) VALUES (16261, '2020-10-21 08:59:09.636557', 'Manager why company say. Theory rich up play nation later. Run full economy might job.', '379b0a29-14af-4779-90ed-6c97e9d9d92d', 26048);
INSERT INTO messages (id, inserted_at, message, user_id, channel_id) VALUES (90156, '2024-03-05 02:03:14.205370', NULL, '616d31dc-139f-44a6-b200-3a4ffd79834f', 67312);
INSERT INTO messages (id, inserted_at, message, user_id, channel_id) VALUES (16093, '2022-06-25 05:45:18.031076', 'Much Democrat night modern. Would audience weight begin save family. Bring close reduce help.', 'ec1c09f2-9b79-48f9-b838-df6db4ec88f0', 24272);
INSERT INTO messages (id, inserted_at, message, user_id, channel_id) VALUES (56701, '2022-09-16 18:58:36.301702', 'Sometimes apply foot spend organization pretty. Never woman yard now ask.', '33c6593e-8697-4a67-b729-455cbc0d498b', 86312);
INSERT INTO messages (id, inserted_at, message, user_id, channel_id) VALUES (85764, '2023-06-04 09:49:05.363453', 'Pm system head rate despite thus. Participant behavior morning step.', '90a76966-ecb9-4114-af3b-f23471ba5616', 27128);
INSERT INTO messages (id, inserted_at, message, user_id, channel_id) VALUES (13831, '2019-08-25 11:54:42.843190', 'Country see quality bad. Car home level it foreign. Paper move we join investment.', '50e2395d-31c4-4b13-ac82-1963b7ec3e8a', 36219);
INSERT INTO messages (id, inserted_at, message, user_id, channel_id) VALUES (95177, '2020-01-24 07:11:37.463701', 'Behavior building rate own once. Language spring fine town every prevent name unit.', '222dc7aa-7f87-408c-b8e4-9c237d44fb5b', 86781);
INSERT INTO messages (id, inserted_at, message, user_id, channel_id) VALUES (83295, '2022-03-17 02:30:12.620964', 'Often thing doctor state bar employee amount.', '30d3098d-a436-443b-a4fc-2529e74a0fa9', 36861);
INSERT INTO messages (id, inserted_at, message, user_id, channel_id) VALUES (15873, '2023-10-27 00:45:44.025040', 'West ball local hope who up successful cell. Sometimes resource piece born.', '28959251-33ed-4bb4-8da7-6903704348f3', 71838);
INSERT INTO messages (id, inserted_at, message, user_id, channel_id) VALUES (81716, '2022-08-08 00:33:36.679287', 'Rise century seven. Energy cold character process employee quality. Every long figure we.', 'ef61ef82-53f4-41ea-94e7-ad67f6379b91', 17512);
INSERT INTO messages (id, inserted_at, message, user_id, channel_id) VALUES (49017, '2024-04-07 18:21:02.268999', 'Hotel fish reveal out thing know senior. Training rich contain senior.', '28959251-33ed-4bb4-8da7-6903704348f3', 47791);
INSERT INTO messages (id, inserted_at, message, user_id, channel_id) VALUES (47786, '2023-08-30 20:33:23.228606', 'Head through five partner two old. Data level include return turn.', 'ec1c09f2-9b79-48f9-b838-df6db4ec88f0', 51366);
INSERT INTO messages (id, inserted_at, message, user_id, channel_id) VALUES (68759, '2022-04-16 02:00:48.278659', 'Parent concern hand require lawyer moment. West right pull seven street.', '291ecf4e-53e6-4227-80e3-7904e0f23368', 53550);
INSERT INTO messages (id, inserted_at, message, user_id, channel_id) VALUES (79768, '2022-09-09 11:33:12.720931', 'Will rule during force national green. Rather amount treat tax argue east. Car program simply.', 'deeae4e6-1fc3-40ed-9966-30bebaddeb5a', 12409);
INSERT INTO messages (id, inserted_at, message, user_id, channel_id) VALUES (61389, '2023-06-06 20:39:48.632478', 'Agent bit live nation reveal.', 'b9d94cba-bde5-41bc-a634-720d65c23cfb', 92250);
INSERT INTO messages (id, inserted_at, message, user_id, channel_id) VALUES (21994, '2021-08-30 06:54:20.623673', 'Of else plant collection reduce author.
Rule assume call under. Long design contain face.', 'b9d94cba-bde5-41bc-a634-720d65c23cfb', 87023);
INSERT INTO messages (id, inserted_at, message, user_id, channel_id) VALUES (13869, '2021-05-05 15:00:10.359249', 'Research charge network near amount apply yourself. Reflect itself society quite some turn.', '30d3098d-a436-443b-a4fc-2529e74a0fa9', 23239);
INSERT INTO messages (id, inserted_at, message, user_id, channel_id) VALUES (8967, '2021-07-22 05:33:42.737113', 'Night name skill Mr east. Song hope past successful rule claim of. Real experience should network.', 'a2fbe746-3bce-4e28-bce6-305775398857', 71838);
INSERT INTO messages (id, inserted_at, message, user_id, channel_id) VALUES (23113, '2022-06-05 14:34:46.890886', 'Car dream indicate actually at line.', '7836b471-3efd-4ccd-a61d-9de717a0051f', 35432);
INSERT INTO messages (id, inserted_at, message, user_id, channel_id) VALUES (92209, '2023-04-17 14:05:25.187421', 'Talk evening performance. Relationship star air teacher require decision.', 'b9d94cba-bde5-41bc-a634-720d65c23cfb', 86781);
INSERT INTO messages (id, inserted_at, message, user_id, channel_id) VALUES (75522, '2021-03-07 18:21:26.112487', 'Fly challenge camera sell physical analysis time. Business house exist control.', 'deeae4e6-1fc3-40ed-9966-30bebaddeb5a', 189);
INSERT INTO messages (id, inserted_at, message, user_id, channel_id) VALUES (87427, '2024-02-24 00:23:44.322691', 'Hard shoulder challenge. Town put nation four middle my authority.', '1471c3bc-dc10-4d91-9918-271e6ffcf32a', 44763);
INSERT INTO messages (id, inserted_at, message, user_id, channel_id) VALUES (57630, '2023-12-05 12:13:43.520500', 'Upon get three relate interview. Guy system picture onto or.', '6d074ed9-cfa9-4bbc-9be8-14ad71bb1330', 71298);
INSERT INTO messages (id, inserted_at, message, user_id, channel_id) VALUES (17791, '2023-01-30 20:16:39.331593', 'Buy south this central hear. Bring especially play skin far role pattern.', '22b3bfaf-f35c-4e40-90cf-87805c4a3c2d', 93875);
INSERT INTO messages (id, inserted_at, message, user_id, channel_id) VALUES (92282, '2023-08-16 17:29:36.931592', 'Cause middle sense million outside all after. South order believe available.', 'bfde79a0-19e4-42a6-93f0-aa33b5d0b16f', 22166);
```

## Future Improvements

- Add support for more SQL databases.
- Add support for more complex date setting (e.g., created_date vs last_updated).
- ~~Add support for more complex datatypes, for instance recognizing and mimicking emails or usernames.~~

## Conclusion

You have successfully generated seed data for your SQL database using the `--seed` option with `supabase-pydantic`. This feature is very useful when you need to populate your database with test data or test your application with a large dataset & Pydantic models.

<br><br><br>
