## Run Alembic Migrations
### Confguration 

- Update the `alembic.ini` with your database credentials (`sqlalchemy.url`)

### create new Migration

```bash
alembic revision --autogenerate -m "ex. Add...."
```

### upgrade the database 

```bash
alembic upgrade head
```
