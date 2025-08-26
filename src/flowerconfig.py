from dotenv import dotenv_values
config = dotenv_values(".env")


port = 5555
max_tasks = 10000
auto_refresh = True

basic_auth = [f'admin:{config.get("CELERY_FLOWER_PASSWORD")}']