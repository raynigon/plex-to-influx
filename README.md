**plex-to-influx**
------------------------------
![Linting](https://github.com/raynigon/plex-to-influx/workflows/Python%20application/badge.svg)
[
![Docker Build Status](https://img.shields.io/docker/cloud/build/raynigon/plex-to-influx)
![Docker Pulls](https://img.shields.io/docker/pulls/raynigon/plex-to-influx)
![Docker Stars](https://img.shields.io/docker/stars/raynigon/plex-to-influx)
](https://hub.docker.com/r/raynigon/plex-to-influx)

## Configuration
#### GENERAL
|Ini File       |Environment Variable       |Description                                                                                |
|:--------------|:--------------------------|:------------------------------------------------------------------------------------------|
|Delay          |PDC_GENERAL_DELAY          |Delay between updating metrics                                                             |
|ReportCombined |PDC_GENERAL_REPORTCOMBINED |When using multiple servers report total streams over all servers                          |
#### INFLUXDB
|Ini File       |Environment Variable       |Description                                                                                |
|:--------------|:--------------------------|:------------------------------------------------------------------------------------------|
|Address        |PDC_INFLUXDB_ADDRESS       |Delay between updating metrics                                                             |
|Port           |PDC_INFLUXDB_PORT          |InfluxDB port to connect to.  8086 in most cases                                           |
|Database       |PDC_INFLUXDB_DATABASE      |Database to write collected stats to                                                       |
|Username       |PDC_INFLUXDB_USERNAME      |User that has access to the database                                                       |
|Password       |PDC_INFLUXDB_PASSWORD      |Password for above user                                                                    |
|Verify_SSL     |PDC_INFLUXDB_VERIFYSSL     |Disable SSL verification for InfluxDB Connection                                           |
#### PLEX
|Ini File       |Environment Variable       |Description                                                                                |
|:--------------|:--------------------------|:------------------------------------------------------------------------------------------|
|Username       |PDC_PLEX_USERNAME          |Plex username                                                                              |
|Password       |PDC_PLEX_PASSWORD          |Plex Password                                                                              |
|Servers        |PDC_PLEX_SERVERS           |A comma separated list of servers you wish to pull data from.                              |
|HTTPS          |PDC_PLEX_HTTPS             |Connect to server using HTTPS                                                              |
|Verify_SSL     |PDC_PLEX_VERIFYSSL         |Disable SSL verification (Use this if you have a self sign SSL)                            |
#### LOGGING
|Ini File       |Environment Variable       |Description                                                                                |
|:--------------|:--------------------------|:------------------------------------------------------------------------------------------|
|Level          |PDC_LOGGING_LEVEL          |Minimum type of message to log.  Valid options are: critical, error, warning, info, debug  |
