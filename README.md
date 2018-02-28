# dos-indexd-lambda

This presents an [Amazon Lambda](https://aws.amazon.com/lambda/) microservice
following the [Data Object Service](https://github.com/ga4gh/data-object-service-schemas)([view the OpenAPI description](https://ga4gh.github.io/data-object-service-schemas/)!).
It allows data in [indexd](https://github.com/uc-cdis/indexd) to be accessed using Data
Object Service APIs.

## Using the service

A development version of this service is available at https://mkc9oddwq0.execute-api.us-west-2.amazonaws.com/api/ .
To make proper use of the service, one can either use cURL or an HTTP client to write API requests
following the [OpenAPI description](https://mkc9oddwq0.execute-api.us-west-2.amazonaws.com/api/swagger.json).

```
# Will request the first page of Data Objects from the service.
curl -X POST --header 'Content-Type: application/json' --header 'Accept: application/json' -d '{}' 'https://mkc9oddwq0.execute-api.us-west-2.amazonaws.com/api/ga4gh/dos/v1/dataobjects/list'
```

There is also a Python client available, that makes it easier to use the service from code.

```
from ga4gh.dos.client import Client
client = Client("https://mkc9oddwq0.execute-api.us-west-2.amazonaws.com/api/")
local_client = client.client
models = client.models
local_client.ListDataObjects(body={}).result()
```

For more information refer to the [Data Object Service](https://github.com/ga4gh/data-object-service-schemas).

## Development

### Status

This software is being actively developed to provide the greatest level of feature parity
between DOS and indexd. It also presents an area to explore features that might extend the DOS
API. Current development items can be seen in [the Issues](https://github.com/DataBiosphere/dos-indexd-lambda/issues).

### Feature development

The Data Object Service can present many of the features of indexd naturally. This
lambda should present a useful client for the latest releases of the indexd API.

In addition, the DOS schemas may be extended to present features available in indexd,
but not yet in DOS.

#### indexd/fence Features

* Authentication/Authorization
* Aliases
* Index management
* Storage management

#### DOS Features

* Bundle listing
  *  Associate arbitrary data objects with each other.

### Installing and Deploying

The gateway portion of the AWS Lambda microservice is provided by chalice. So to manage
deployment and to develop you'll need to install chalice.

Once you have installed chalice, you can download and deploy your own version of the
service.

```
pip install chalice
git clone https://github.com/DataBiosphere/dos-indexd-lambda.git
cd dos-indexd-lambda
chalice deploy
```

Chalice will return a HTTP location that you can issue DOS requests to. You can then use
HTTP requests in the style of the [Data Object Service](https://ga4gh.github.io/data-object-service-schemas).

### Accessing data using DOS client

A Python client for the Data Object Service is made available [here](https://github.com/ga4gh/data-object-service-schemas/blob/master/python/ga4gh/dos/client.py).
Install this client and then view the example in [Example Usage](https://github.com/DataBiosphere/dos-indexd-lambda/dos_indexd_signed_url.ipynb).
This notebook will guide you through basic read access to data in indexd via DOS.

### Issues

If you have a problem accessing the service or deploying it for yourself, please head
over to [the Issues](https://github.com/DataBiosphere/dos-indexd-lambda/issues) to let us know!


## TODO

* Validation
* Error handling
* Aliases
* Filter by URL

