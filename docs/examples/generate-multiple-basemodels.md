# Generate Multiple BaseModels for Multiple Schemas

This example demonstrates how to generate multiple BaseModel files corresponding to multiple database schemas. The `--all-schemas` option with `supabase-pydantic` allows the generation of BaseModel files for all schemas that are not empty. Additionally, the `--schema` option can be used to specify a specific schema to generate a BaseModel file for. The default behavior is to generate a BaseModel file for the `public` schema if neither of these option is provided. This feature is useful when you want to create Pydantic models for schemas other than `public` in your database.

!!! info "Please note ..."

    This is a developing feature :hatching_chick:. It is imperfect, so please report any issues you encounter.

## Prerequisites

Ensure that you have followed the setup & prerequisites guide in the [Slack Clone example](setup-slack-simple-fastapi.md#setup) to initialize your local Supabase instance.

## Generating BaseModels for a Specific Schema

To generate a BaseModel file for a specific schema, use one or more `--schema` options with the `generate` command. For example, run the following command:

```bash title="Generate BaseModel for a Specific Schema"
$ sb-pydantic gen --type pydantic --framework fastapi --local --schema public --schema auth --schema extensions

PostGres connection is open.
Processing schema: public
Processing schema: auth
Processing schema: extensions
PostGres connection is closed.
Generating Pydantic models...
Pydantic models generated successfully for schema 'auth': /path/to/your/project/entities/fastapi/schema_auth_latest.py
Generating Pydantic models...
Pydantic models generated successfully for schema 'extensions': /path/to/your/project/entities/fastapi/schema_extensions_latest.py
Generating Pydantic models...
Pydantic models generated successfully for schema 'public': /path/to/your/project/entities/fastapi/schema_public_latest.py
File formatted successfully: /path/to/your/project/entities/fastapi/schema_auth_latest.py
File formatted successfully: /path/to/your/project/entities/fastapi/schema_extensions_latest.py
File formatted successfully: /path/to/your/project/entities/fastapi/schema_public_latest.py
```

An example of the generated BaseModel file for the `auth` schema can be found here: 

??? example "schema_auth_latest.py"
    ```python
    from __future__ import annotations

    import datetime
    from ipaddress import IPv4Address, IPv6Address

    from pydantic import UUID4, BaseModel, Field, Json

    # CUSTOM CLASSES
    # Note: This is a custom model class for defining common features among
    # Pydantic Base Schema.


    class CustomModel(BaseModel):
        pass


    # BASE CLASSES


    class AuditLogEntriesBaseSchema(CustomModel):
        """AuditLogEntries Base Schema."""

        # Primary Keys
        id: UUID4

        # Columns
        created_at: datetime.datetime | None = Field(default=None)
        instance_id: UUID4 | None = Field(default=None)
        ip_address: str
        payload: dict | Json | None = Field(default=None)


    class FlowStateBaseSchema(CustomModel):
        """FlowState Base Schema."""

        # Primary Keys
        id: UUID4

        # Columns
        auth_code: str
        auth_code_issued_at: datetime.datetime | None = Field(default=None)
        authentication_method: str
        code_challenge: str
        code_challenge_method: str
        created_at: datetime.datetime | None = Field(default=None)
        provider_access_token: str | None = Field(default=None)
        provider_refresh_token: str | None = Field(default=None)
        provider_type: str
        updated_at: datetime.datetime | None = Field(default=None)
        user_id: UUID4 | None = Field(default=None)


    class IdentitiesBaseSchema(CustomModel):
        """Identities Base Schema."""

        # Primary Keys
        id: UUID4

        # Columns
        created_at: datetime.datetime | None = Field(default=None)
        email: str | None = Field(default=None)
        identity_data: dict | Json
        last_sign_in_at: datetime.datetime | None = Field(default=None)
        provider: str
        provider_id: str
        updated_at: datetime.datetime | None = Field(default=None)
        user_id: UUID4


    class InstancesBaseSchema(CustomModel):
        """Instances Base Schema."""

        # Primary Keys
        id: UUID4

        # Columns
        created_at: datetime.datetime | None = Field(default=None)
        raw_base_config: str | None = Field(default=None)
        updated_at: datetime.datetime | None = Field(default=None)
        uuid: UUID4 | None = Field(default=None)


    class MfaAmrClaimsBaseSchema(CustomModel):
        """MfaAmrClaims Base Schema."""

        # Primary Keys
        id: UUID4

        # Columns
        authentication_method: str
        created_at: datetime.datetime
        session_id: UUID4
        updated_at: datetime.datetime


    class MfaChallengesBaseSchema(CustomModel):
        """MfaChallenges Base Schema."""

        # Primary Keys
        id: UUID4

        # Columns
        created_at: datetime.datetime
        factor_id: UUID4
        ip_address: IPv4Address | IPv6Address
        otp_code: str | None = Field(default=None)
        verified_at: datetime.datetime | None = Field(default=None)


    class MfaFactorsBaseSchema(CustomModel):
        """MfaFactors Base Schema."""

        # Primary Keys
        id: UUID4

        # Columns
        created_at: datetime.datetime
        factor_type: str
        friendly_name: str | None = Field(default=None)
        last_challenged_at: datetime.datetime | None = Field(default=None)
        phone: str | None = Field(default=None)
        secret: str | None = Field(default=None)
        status: str
        updated_at: datetime.datetime
        user_id: UUID4


    class OneTimeTokensBaseSchema(CustomModel):
        """OneTimeTokens Base Schema."""

        # Primary Keys
        id: UUID4

        # Columns
        created_at: datetime.datetime
        relates_to: str
        token_hash: str
        token_type: str
        updated_at: datetime.datetime
        user_id: UUID4


    class RefreshTokensBaseSchema(CustomModel):
        """RefreshTokens Base Schema."""

        # Primary Keys
        id: int

        # Columns
        created_at: datetime.datetime | None = Field(default=None)
        instance_id: UUID4 | None = Field(default=None)
        parent: str | None = Field(default=None)
        revoked: bool | None = Field(default=None)
        session_id: UUID4 | None = Field(default=None)
        token: str | None = Field(default=None)
        updated_at: datetime.datetime | None = Field(default=None)
        user_id: str | None = Field(default=None)


    class SamlProvidersBaseSchema(CustomModel):
        """SamlProviders Base Schema."""

        # Primary Keys
        id: UUID4

        # Columns
        attribute_mapping: dict | Json | None = Field(default=None)
        created_at: datetime.datetime | None = Field(default=None)
        entity_id: str
        metadata_url: str | None = Field(default=None)
        metadata_xml: str
        name_id_format: str | None = Field(default=None)
        sso_provider_id: UUID4
        updated_at: datetime.datetime | None = Field(default=None)


    class SamlRelayStatesBaseSchema(CustomModel):
        """SamlRelayStates Base Schema."""

        # Primary Keys
        id: UUID4

        # Columns
        created_at: datetime.datetime | None = Field(default=None)
        flow_state_id: UUID4 | None = Field(default=None)
        for_email: str | None = Field(default=None)
        redirect_to: str | None = Field(default=None)
        request_id: str
        sso_provider_id: UUID4
        updated_at: datetime.datetime | None = Field(default=None)


    class SchemaMigrationsBaseSchema(CustomModel):
        """SchemaMigrations Base Schema."""

        # Primary Keys
        version: str


    class SessionsBaseSchema(CustomModel):
        """Sessions Base Schema."""

        # Primary Keys
        id: UUID4

        # Columns
        aal: str | None = Field(default=None)
        created_at: datetime.datetime | None = Field(default=None)
        factor_id: UUID4 | None = Field(default=None)
        ip: IPv4Address | IPv6Address | None = Field(default=None)
        not_after: datetime.datetime | None = Field(default=None)
        refreshed_at: datetime.datetime | None = Field(default=None)
        tag: str | None = Field(default=None)
        updated_at: datetime.datetime | None = Field(default=None)
        user_agent: str | None = Field(default=None)
        user_id: UUID4


    class SsoDomainsBaseSchema(CustomModel):
        """SsoDomains Base Schema."""

        # Primary Keys
        id: UUID4

        # Columns
        created_at: datetime.datetime | None = Field(default=None)
        domain: str
        sso_provider_id: UUID4
        updated_at: datetime.datetime | None = Field(default=None)


    class SsoProvidersBaseSchema(CustomModel):
        """SsoProviders Base Schema."""

        # Primary Keys
        id: UUID4

        # Columns
        created_at: datetime.datetime | None = Field(default=None)
        resource_id: str | None = Field(default=None)
        updated_at: datetime.datetime | None = Field(default=None)


    class UsersBaseSchema(CustomModel):
        """Users Base Schema."""

        # Primary Keys
        id: UUID4

        # Columns
        aud: str | None = Field(default=None)
        banned_until: datetime.datetime | None = Field(default=None)
        confirmation_sent_at: datetime.datetime | None = Field(default=None)
        confirmation_token: str | None = Field(default=None)
        confirmed_at: datetime.datetime | None = Field(default=None)
        created_at: datetime.datetime | None = Field(default=None)
        deleted_at: datetime.datetime | None = Field(default=None)
        email: str | None = Field(default=None)
        email_change: str | None = Field(default=None)
        email_change_confirm_status: int | None = Field(default=None)
        email_change_sent_at: datetime.datetime | None = Field(default=None)
        email_change_token_current: str | None = Field(default=None)
        email_change_token_new: str | None = Field(default=None)
        email_confirmed_at: datetime.datetime | None = Field(default=None)
        encrypted_password: str | None = Field(default=None)
        instance_id: UUID4 | None = Field(default=None)
        invited_at: datetime.datetime | None = Field(default=None)
        is_anonymous: bool
        is_sso_user: bool
        is_super_admin: bool | None = Field(default=None)
        last_sign_in_at: datetime.datetime | None = Field(default=None)
        phone: str | None = Field(default=None)
        phone_change: str | None = Field(default=None)
        phone_change_sent_at: datetime.datetime | None = Field(default=None)
        phone_change_token: str | None = Field(default=None)
        phone_confirmed_at: datetime.datetime | None = Field(default=None)
        raw_app_meta_data: dict | Json | None = Field(default=None)
        raw_user_meta_data: dict | Json | None = Field(default=None)
        reauthentication_sent_at: datetime.datetime | None = Field(default=None)
        reauthentication_token: str | None = Field(default=None)
        recovery_sent_at: datetime.datetime | None = Field(default=None)
        recovery_token: str | None = Field(default=None)
        role: str | None = Field(default=None)
        updated_at: datetime.datetime | None = Field(default=None)


    # OPERATIONAL CLASSES


    class AuditLogEntries(AuditLogEntriesBaseSchema):
        """AuditLogEntries Schema for Pydantic.

        Inherits from AuditLogEntriesBaseSchema. Add any customization here.
        """

        pass


    class FlowState(FlowStateBaseSchema):
        """FlowState Schema for Pydantic.

        Inherits from FlowStateBaseSchema. Add any customization here.
        """

        # Foreign Keys
        saml_relay_states: list[SamlRelayStates] | None = Field(default=None)


    class Identities(IdentitiesBaseSchema):
        """Identities Schema for Pydantic.

        Inherits from IdentitiesBaseSchema. Add any customization here.
        """

        # Foreign Keys
        users: list[Users] | None = Field(default=None)


    class Instances(InstancesBaseSchema):
        """Instances Schema for Pydantic.

        Inherits from InstancesBaseSchema. Add any customization here.
        """

        pass


    class MfaAmrClaims(MfaAmrClaimsBaseSchema):
        """MfaAmrClaims Schema for Pydantic.

        Inherits from MfaAmrClaimsBaseSchema. Add any customization here.
        """

        # Foreign Keys
        sessions: list[Sessions] | None = Field(default=None)


    class MfaChallenges(MfaChallengesBaseSchema):
        """MfaChallenges Schema for Pydantic.

        Inherits from MfaChallengesBaseSchema. Add any customization here.
        """

        # Foreign Keys
        mfa_factors: list[MfaFactors] | None = Field(default=None)


    class MfaFactors(MfaFactorsBaseSchema):
        """MfaFactors Schema for Pydantic.

        Inherits from MfaFactorsBaseSchema. Add any customization here.
        """

        # Foreign Keys
        users: list[Users] | None = Field(default=None)
        mfa_challenges: list[MfaChallenges] | None = Field(default=None)


    class OneTimeTokens(OneTimeTokensBaseSchema):
        """OneTimeTokens Schema for Pydantic.

        Inherits from OneTimeTokensBaseSchema. Add any customization here.
        """

        # Foreign Keys
        users: list[Users] | None = Field(default=None)


    class RefreshTokens(RefreshTokensBaseSchema):
        """RefreshTokens Schema for Pydantic.

        Inherits from RefreshTokensBaseSchema. Add any customization here.
        """

        # Foreign Keys
        sessions: list[Sessions] | None = Field(default=None)


    class SamlProviders(SamlProvidersBaseSchema):
        """SamlProviders Schema for Pydantic.

        Inherits from SamlProvidersBaseSchema. Add any customization here.
        """

        # Foreign Keys
        sso_providers: list[SsoProviders] | None = Field(default=None)


    class SamlRelayStates(SamlRelayStatesBaseSchema):
        """SamlRelayStates Schema for Pydantic.

        Inherits from SamlRelayStatesBaseSchema. Add any customization here.
        """

        # Foreign Keys
        flow_state: list[FlowState] | None = Field(default=None)
        sso_providers: list[SsoProviders] | None = Field(default=None)


    class SchemaMigrations(SchemaMigrationsBaseSchema):
        """SchemaMigrations Schema for Pydantic.

        Inherits from SchemaMigrationsBaseSchema. Add any customization here.
        """

        pass


    class Sessions(SessionsBaseSchema):
        """Sessions Schema for Pydantic.

        Inherits from SessionsBaseSchema. Add any customization here.
        """

        # Foreign Keys
        users: list[Users] | None = Field(default=None)
        mfa_amr_claims: list[MfaAmrClaims] | None = Field(default=None)
        refresh_tokens: list[RefreshTokens] | None = Field(default=None)


    class SsoDomains(SsoDomainsBaseSchema):
        """SsoDomains Schema for Pydantic.

        Inherits from SsoDomainsBaseSchema. Add any customization here.
        """

        # Foreign Keys
        sso_providers: list[SsoProviders] | None = Field(default=None)


    class SsoProviders(SsoProvidersBaseSchema):
        """SsoProviders Schema for Pydantic.

        Inherits from SsoProvidersBaseSchema. Add any customization here.
        """

        # Foreign Keys
        saml_providers: list[SamlProviders] | None = Field(default=None)
        saml_relay_states: list[SamlRelayStates] | None = Field(default=None)
        sso_domains: list[SsoDomains] | None = Field(default=None)


    class Users(UsersBaseSchema):
        """Users Schema for Pydantic.

        Inherits from UsersBaseSchema. Add any customization here.
        """

        # Foreign Keys
        identities: list[Identities] | None = Field(default=None)
        mfa_factors: list[MfaFactors] | None = Field(default=None)
        one_time_tokens: list[OneTimeTokens] | None = Field(default=None)
        sessions: list[Sessions] | None = Field(default=None)
    ```

## Generating BaseModels for All Schemas

To generate BaseModel files for all schemas, use the `--all-schemas` option with the `generate` command. Note, this will take precedence over any `--schema` options provided. For example, run the following command:

```bash title="Generate BaseModels for All Schemas"
$ sb-pydantic gen --type pydantic --framework fastapi --local --all-schemas

PostGres connection is open.
Processing schema: public
Processing schema: graphql
Processing schema: graphql_public
Processing schema: vault
Processing schema: pgsodium_masks
Processing schema: pgsodium
Processing schema: auth
Processing schema: storage
Processing schema: realtime
Processing schema: net
Processing schema: supabase_functions
Processing schema: pg_toast_temp_20
Processing schema: pg_temp_20
Processing schema: pg_toast_temp_27
Processing schema: pg_temp_27
Processing schema: pg_toast_temp_19
Processing schema: pg_temp_19
Processing schema: _supavisor
Processing schema: _analytics
Processing schema: _realtime
Processing schema: pg_toast_temp_31
Processing schema: pg_temp_31
Processing schema: pg_toast_temp_30
Processing schema: pg_temp_30
Processing schema: pg_toast_temp_32
Processing schema: pg_temp_32
Processing schema: pg_toast_temp_28
Processing schema: extensions
Processing schema: pg_temp_28
Processing schema: pg_toast_temp_29
Processing schema: pg_temp_29
Processing schema: pg_toast
PostGres connection is closed.
The following schemas have no tables and will be skipped: graphql, graphql_public, pgsodium_masks, pg_toast_temp_20, pg_temp_20, pg_toast_temp_27, pg_temp_27, pg_toast_temp_19, pg_temp_19, _supavisor, _realtime, pg_toast_temp_31, pg_temp_31, pg_toast_temp_30, pg_temp_30, pg_toast_temp_32, pg_temp_32, pg_toast_temp_28, pg_temp_28, pg_toast_temp_29, pg_temp_29, pg_toast
Generating Pydantic models...
Pydantic models generated successfully for schema 'public': /path/to/your/project/entities/fastapi/schema_public_latest.py
Generating Pydantic models...
Pydantic models generated successfully for schema 'vault': /path/to/your/project/entities/fastapi/schema_vault_latest.py
Generating Pydantic models...
Pydantic models generated successfully for schema 'pgsodium': /path/to/your/project/entities/fastapi/schema_pgsodium_latest.py
Generating Pydantic models...
Pydantic models generated successfully for schema 'auth': /path/to/your/project/entities/fastapi/schema_auth_latest.py
Generating Pydantic models...
Pydantic models generated successfully for schema 'storage': /path/to/your/project/entities/fastapi/schema_storage_latest.py
Generating Pydantic models...
Pydantic models generated successfully for schema 'realtime': /path/to/your/project/entities/fastapi/schema_realtime_latest.py
Generating Pydantic models...
Pydantic models generated successfully for schema 'net': /path/to/your/project/entities/fastapi/schema_net_latest.py
Generating Pydantic models...
Pydantic models generated successfully for schema 'supabase_functions': /path/to/your/project/entities/fastapi/schema_supabase_functions_latest.py
Generating Pydantic models...
Pydantic models generated successfully for schema '_analytics': /path/to/your/project/entities/fastapi/schema__analytics_latest.py
Generating Pydantic models...
Pydantic models generated successfully for schema 'extensions': /path/to/your/project/entities/fastapi/schema_extensions_latest.py
File formatted successfully: /path/to/your/project/entities/fastapi/schema_public_latest.py
File formatted successfully: /path/to/your/project/entities/fastapi/schema_vault_latest.py
File formatted successfully: /path/to/your/project/entities/fastapi/schema_pgsodium_latest.py
File formatted successfully: /path/to/your/project/entities/fastapi/schema_auth_latest.py
File formatted successfully: /path/to/your/project/entities/fastapi/schema_storage_latest.py
File formatted successfully: /path/to/your/project/entities/fastapi/schema_realtime_latest.py
File formatted successfully: /path/to/your/project/entities/fastapi/schema_net_latest.py
File formatted successfully: /path/to/your/project/entities/fastapi/schema_supabase_functions_latest.py
File formatted successfully: /path/to/your/project/entities/fastapi/schema__analytics_latest.py
File formatted successfully: /path/to/your/project/entities/fastapi/schema_extensions_latest.py
```

Note that each schema will have its own BaseModel file generated in the `entities` directory of your project. As a result, each will have a prepended `schema_` prefix and a `_latest` suffix, with the name of the corresponding schema.

## Conclusion

Using the `--schema` option with the `generate` command makes it easy to generate Pydantic models for select database schemas. The `--all-schemas` option is particularly useful if you want to create models for every schema without specifying each one individually.

Please note that some of the following features which will be created in future releases:

- Enable better foreign table key linking for relationships with foreign schemas.

<br><br><br>


