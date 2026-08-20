# MiniCommerce V2 Architecture — 5-Tier Data Layer Specification

## Overview

MiniCommerce V2 expands the 4-tier V1 backend into a **5-Tier Data Layer Architecture** by introducing an explicit **Repository Layer**. This decouples SQL/SQLAlchemy query logic from business services and HTTP routers.

```text
                           HTTP REQUEST
                                |
                                v
                       MIDDLEWARE PIPELINE
                    /           |          \
            Request ID     Rate Limit     Logging
                    \           |          /
                                v
                           ROUTER LAYER
                          (app/api/v1/)
                                |
                                v
                          SERVICE LAYER
                         (app/services/)
                                |
                                v
                        REPOSITORY LAYER
                       (app/repositories/)
                                |
                                v
                        SQLALCHEMY 2.x ORM
                                |
                                v
                        PGBOUNCER / POOL
                                |
                                v
                       POSTGRESQL DATABASE
```

## Layer Definitions & Rules

1. **Router Layer (`app/api/v1/`)**:
   - Thin HTTP endpoints validating incoming Pydantic schemas, extracting request headers (e.g. `Idempotency-Key`), delegating to services, and returning serialized response schemas.
   - Routers perform zero SQL execution or domain validation.

2. **Service Layer (`app/services/`)**:
   - Domain business logic, stock validation, transaction boundaries, idempotency checks, and order processing.
   - Services delegate all database persistence operations to the Repository Layer.

3. **Repository Layer (`app/repositories/`)**:
   - Encapsulated data access components (`UserRepository`, `ProductRepository`, `CartRepository`, `OrderRepository`).
   - Handles pagination (`OFFSET`), sorting, price filtering, and row-level locking (`SELECT ... FOR UPDATE`).
   - Repositories do not inspect HTTP requests or raise HTTP exceptions.

4. **SQLAlchemy 2.x ORM (`app/models/`)**:
   - Declarative mapped models representing PostgreSQL tables, check constraints, and relationships with eager loading (`selectinload`).

5. **PostgreSQL Database**:
   - Persistent store enforcing check constraints (`stock >= 0`, `price >= 0`, `quantity > 0`), primary keys (UUID), foreign keys, and unique indexes (`(user_id, idempotency_key)`).
