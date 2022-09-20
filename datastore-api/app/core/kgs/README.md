# SQuARE Knowledge Graphs API


## Development setup
For setting up the datastore-api, which also includes the KG-api, we refer to the Datastore setup. 


## Getting started
A deailed documentation on available API-Requests regarding the KG-API is listed [here](https://square.ukp-lab.de/docs/api/datastores/#tag/Knowledge-Graphs).


## Authentification
1. Get the bearer token via the following request. The token is valid for 5 minutes.
```python
curl --location --request POST 'https://square.ukp-lab.de/auth/realms/square/protocol/openid-connect/token' \
--header 'Content-Type: application/x-www-form-urlencoded' \
--data-urlencode 'grant_type=password' \
--data-urlencode 'client_id=web-app' \
--data-urlencode 'username=<SQUARE_USERNAME>' \
--data-urlencode 'password=<SQUARE_PASSWORD>'
```


2. Pass the received access token to the request. An example to check the available KGs 
can be seen below:

```python
curl --location --request GET 'https://square.ukp-lab.de/api/datastores/kg' \
--header 'Authorization: Bearer <access_Token>'
```

```response
Response: []
```


## Uploading new KGs

1. Create the Knowledge graph:
   
```python
curl --location --request PUT 'http://localhost:7000/datastores/kg/conceptnet' \
--header 'Authorization: Bearer <access_Token>' \
--header 'Content-Type: application/json' \
--data-raw '[
      {
        "name": "name",
        "type": "keyword"
      },
      {
        "name": "type",  
        "type": "keyword"
      },
      {
        "name": "description",
        "type": "text"
      },
      {
        "name": "weight",
        "type": "double"
      },

      {
        "name": "in_id",
        "type": "keyword"
      },
      {
        "name": "out_id",
        "type": "keyword"
      },
      {
        "name": "in_out_id",
        "type": "keyword"
      }
    ]'
```

2. Download KG and unzip data (In this case Conceptnet)

   The bash script [download_conceptnet.sh](download_conceptnet.sh) will create the directory [data/cpnet/](data/cpnet/) and download the KG.
   ```bash
   bash download_conceptnet.sh
   ```


3. Exchange <USER_NAME> and <USER_PASSWORD> with your User-Creds inside of [easy_connect.py](easy_connect.py)
4. Upload data:
  
   ```python
   python upload_conceptnet.py   
   ```

 