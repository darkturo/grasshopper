# tracker
This is a coding exercise in Python3 featuring a simple service to track cpu usage 
and execution times of an application using a script called grasshopper. 
The grasshopper is a simple python script that wraps any command and reports on a
given (default to 0.5 seconds) interval the cpu usage of the system it is running 
on to a grasshoper-tracker service. 

The grasshopper.tracker service offers a simple UI to register as a user and obtain 
a TOKEN (JWT) which will be used by the grasshopper script to authenticate with the
service and log any runs with the grasshopper script.

The API for the grasshopper.tracker service is: 

```
POST /api/v1/auth
Request:
{
    "username": "admin",
    "password": "admin"
}
Response:
{
    "token": "... jwt token ..."
}

POST /api/v1/test
Request:
{
    "name": "my test run ",
    "description": "running on a sunny day",
    "threshold": 0.5,
}
Response:
{
    "id": 1,
    "start_time": "2021-01-01T00:00:00"
}

POST /api/v1/test/:id/usage
Request:
{
    "cpu_usage": 0.5,
    "timestamp": "2021-01-01T00:00:00",
}
Response:
{
    "id": 1,
    "above_threshold": false,
}

POST /api/v1/test/:id/stop
Request:
{
    "end_time": "2021-01-01T00:00:00",
}

GET /api/v1/test/:id
Response:
{
    "id": 1,
    "time_above_threshold": 0,"
    "active": false,
    "start_time": "2021-01-01T00:00:00",
    "end_time": "2021-01-01T00:00:00",
    "duration": 0, // seconds
}
```

## Running the service
To start the project, you will need to create a database first.

You can do this by running the following command:

```bash
flask --app grasshopper.tracker init-db
```

To run the service you can use flask as follows:
```bash
flask --app grasshopper.tracker run
```

or the following you want to enable debug mode:

```bash
flask --app grasshopper.tracker run --debug
```


### Docker
These are the steps if you plan to execute the service with docker instead.
Download the image from the github repo (or build it yourself with the
Dockerfile) and then run the following command to create the DB:

```bash
docker run -w /PATH_TO_SQLITE/:/app/instance --rm grasshopper flask --app grasshopper.tracker init-db
```

Then to run the service you just need to:

```bash
docker run -p 5000:5000 -w /PATH_TO_SQLITE/:/app/instance --rm grasshopper.tracker 
```

Observe that `PATH_TO_SQLITE` is the path to the sqlite file that will be created
by the service to store the data.


## Running the grasshopper script
The script can be run from any machine or host that has access to the service.

If you're runnning the service localhost you can just run the following 
command if you have build and install the grasshopper pacakge:

```bash
grasshopper --jwt <JWT_TOKEN> <command>
```

or the following if you're running it directly from the source:

```bash
poetry run grasshopper --jwt <JWT_TOKEN> <command>
```

With <command> being any command you want to wrap with the grasshopper script, and
the <JWT_TOKEN> a token you obtained from the web service or via the api.

If the server is elsewhere, you can also specify the host and port with the
`server` option:

```bash
grasshopper --jwt $TOKEN --server http://myserver.somewhere.in.theinternet:5000 <command>
```

### Running grasshopper script to monitor cpu usage
You can also run the grasshopper script without a command to just monitor the cpu 
usage of the system. To do that you, use this:

```bash
grasshopper --jwt $TOKEN --no-command
```
 
### Report intervals
You can adjust the interval of the reports by using the `--interval` option. Controlling
this will give you the chance to adjust the granularity of the observations, getting a more 
precise reports. 


### Running the grasshopper script with docker
The script is also part of the docker image and can be run as a docker 
container as well. To do so just type:

```bash
docker run -rm grasshopper grasshopper.py --jwt $TOKEN ...
```
