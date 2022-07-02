# ETL-Project Porfolio

## Architecture
![Architecture](images/architecture.png)


## Visualisation
![Visualisation](images/grafana.png)


## Prerequisites:
- Create .env file in parent folder with following content
```
AIRFLOW_UID=50000
SLACK_TOKEN="<Your Slack Token>"
```


## Start Stack
```
docker-compose up -d
```

## Destroy Stack
```
docker-compose down --remove-orphans --volumes
```