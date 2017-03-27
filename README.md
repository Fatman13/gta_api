# Introdution

Flask API adapter for ctrip.

# Invocation

To get a list of destination services...

`GET` `/destinationServices`

Following request params are accepted...

1. `?cityCode`
2. `?itemCode`
3. `?fromDate=2017-02-23&toDate=2017-04-16`

Example...

`http://X.X.X.X/destinationServices?cityCode=CAL5&itemCode=TURA01-GTA09&fromDate=2017-02-23&toDate=2017-04-16`

# Authentication

For authentication, send request with `Api-Token: [Your secret token]` header.

# Question?

Please send an email to <mailto:yu.leng@gta-travel.com>.