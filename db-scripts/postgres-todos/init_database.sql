--
-- For use with:
-- https://github.com/supabase/supabase/tree/master/examples/todo-list/sveltejs-todo-list or
-- https://github.com/supabase/examples-archive/tree/main/supabase-js-v1/todo-list
--

create table users (
  id uuid primary key default gen_random_uuid(),
  email text unique not null,
  password text not null,
  inserted_at timestamp with time zone default timezone('utc'::text, now()) not null
);

create table todos (
  id bigint generated by default as identity primary key,
  user_id uuid references public.users not null,
  task text check (char_length(task) > 3),
  is_complete boolean default false,
  inserted_at timestamp with time zone default timezone('utc'::text, now()) not null
);
alter table todos enable row level security;
create policy "Individuals can create todos." on todos for
    insert with check (user_id = (select users.id from users));
create policy "Individuals can view their own todos. " on todos for
    select using ((select users.id from users) = user_id);
create policy "Individuals can update their own todos." on todos for
    update using ((select users.id from users) = user_id);
create policy "Individuals can delete their own todos." on todos for
    delete using ((select users.id from users) = user_id);
