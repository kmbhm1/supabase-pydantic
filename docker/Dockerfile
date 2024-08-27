# Use the official PostgreSQL image
FROM postgres:14

# Set environment variables
ENV POSTGRES_USER=supabase_user
ENV POSTGRES_PASSWORD=supabase_pass
ENV POSTGRES_DB=supabase_db

# Expose the default PostgreSQL port
EXPOSE 5432

# Use a volume to persist data
VOLUME ["/var/lib/postgresql/data"]
