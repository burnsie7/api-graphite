# Running asynchronous workers to process graphite metrics
### This is meant as a proof of concept only. Not to be used in production.

### Step 1 - Graphite sink(s)

```
git clone https://github.com/burnsie7/api-graphite.git
cd api-grapite
sudo apt-get update
sudo apt-get install supervisor
sudo apt-get install python-pip
sudo pip install datadog
sudo pip install tornado
```

Edit /etc/supervisor/conf.d/supervisor.conf.  Add the following, updating 'numprocs'.
```
[program:graphite-sink]
command=python /exact/path/to/api-grapite/graphite.py 1731%(process_num)01d
process_name=%(program_name)s_%(process_num)01d
redirect_stdout=true
user=ubuntu
stdout_logfile=/var/log/gsink-%(process_num)01d.log
numprocs=<NUMBER OF PROCS ALLOCATED>
```

Update supervisor and restart all services.

```
sudo supervisorctl
update
restart all
```

### Step 2 - Your carbon-relay

Point your carbon relay at the graphite sinks specified in step 2.  Note that the number of sinks on an individual host is configured by 'numprocs' in /etc/supervisor/conf.d/supervisor.conf.  The port of the first sink will be 17310 and the port will increment for additional procs.  For example, if numprocs were set to 4:

sink-hostname:17310
sink-hostname:17311
sink-hostname:17312
sink-hostname:17313

There are different options for distributing carbon relay, whether set with destinations directly in the carbon config or using haproxy.  Distribute the requests across the different sinks you have configured.

If using relay rules it is advantageous to send only the metrics you wish to see in datadog to the sinks.  For example:

[datadog]
pattern = ^zxyzxy\.webapp.+
destinations = haproxy:port

[default]
default = true
destinations = 127.0.0.1:2004
