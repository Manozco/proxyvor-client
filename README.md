# Proxyvor
## Client

### Informations
Proxyvor is a solution for testing proxys.

It works with a client and a server(target). You launch the target in a remote place
and the client will try to reach it using a proxy and then reach it directly.
The target will record the headers (plus some additional ip informations) and will return them to the client when requested.
The client will then compare the results and give you some informations about the quality and the anonymity of the proxy

For the moment, the criterias for anonymity are:
*   If your ip address appears on the server ==> Bad anonymity
*   If your ip address doesn't appear, but the server knows there is a proxy ==> Neutral Anonymity
*   Else ==> Good anonymity

The criterias for the quality are:
*   If the User-Agent is changed ==> Bad quality
*   If the proxy ip doesn't appear on the server ==> Warning!

The client works with plugins, for the moment the only plugin provided is the plugin for analyze of the quality/anonymity of the proxy

### Dependencies
You will need to have pycurl installed
```bash
sudo apt-get install python-pycurl
```

### Usage
The client is launched using `python main.py`.

Various arguments can be specified:
*   `-i, --ip`: Ip of the proxy to test (*default 127.0.0.1*)
*   `-p, --port`: Port of the proxy to test (*default 80*)
*   `-t, --type`: Type of the proxy to test(**http**, **socks4**, **socks5**) (*default http*)
*   `-c, --config`: Config file to use (*default config.json*)

### Plugins
If you want to develop your own plugin, you have to create directory containing 2 files:
*   `main.py`: The file which will be imported, must contains a class `Plugin` which will be instantiated.
*   `plugin_config.json`: The plugin configuration, must be of this form:
```json
{
    "author": "diateam <contact@diateam.net>",
    "name": "ProxyAnalyzer",
    "description": "Analyze the anonymity and the quality of the proxy tested",
    "version": "1",
    "extra":{}
}
```
The `extra` part will be stored in `self._plugin_config`.
Your module `main.py` must import `plugin.py` and your class must inherit `plugin.ProxyvorClientBasePlugin` and you have to call the `ProxyvorClientBasePlugin` constructor in your constructor.


We will instantiate all the `Plugin` classes in all the different modules with two arguments:
*   `plugin_config_path`: The file path corresponding to your config file path. It is automatically opened and parsed by the `ProxyvorClientBasePlugin` constructor
*   `data`: A dict containing 2 subobjects (for **proxyvor**):
    -   'config': The configuration of the main program.
    -   'proxy': Informations about the proxy we are currently testing

After the connections have been done with the target, we will get the result back (in the form of a `ProxyResult` object) and we will pass it to the `run` method of each `Plugin`

The `ProxyResult` is a dict mapping the results obtained:
*   It can be printed in Json format (`print proxy_result_obj`)
*   There is also these methods:
    -   `real`: returns the 'real' part of the result
    -   `proxy`: returns the 'proxy' part of the result

You can have a look on the plugins we provide in the folder `plugins/`

### Config file
#### target
**(mandatory)**
```json
"target": {
        "base_url": "http://192.168.10.93",
        "base_port": 8080,
        "token_create_url": "proxy_checks/create",
        "token_key_in_result": "token",
        "result_base_url": "proxy_checks"
    }
```
This represents the configuration of the server you want to reach (it is the server on which you are running proxyvor-target)
If you changed the routes on the server, or the keys in the json you can specify this here. Otherwise, leave the default ones and focus on the ip address and the port.

#### plugins_path
**(mandatory)**
```json
"plugin_path": "plugins/"
```
This represents the folder where the program will look for plugins


### Example of use
If you have the server running, you can use the client like this:
```bash
$ python client.py -i 192.168.10.232 -p 3128
Content-Length: 638
Content-Type: application/json
Connection: close
Date: Fri, 18 Apr 2014 08:37:09 GMT
Server: arathorn

{
    "proxy": {
        "client_ip": "192.168.10.93",
        "client_remote_route": [
            "192.168.10.93"
        ],
        "http_headers": {
            "Accept-Encoding": "identity",
            "Cache-Control": "max-age=259200",
            "Connection": "keep-alive",
            "Host": "192.168.10.93:8080",
            "User-Agent": "Python-urllib/2.7",
            "Via": "1.1 debian.hynesim.lab:3128 (squid/2.7.STABLE9)",
            "X-Forwarded-For": "192.168.10.93"
        },
        "remote_addr": "192.168.10.232"
    },
    "real": {
        "client_ip": "192.168.10.93",
        "client_remote_route": [
            "192.168.10.93"
        ],
        "http_headers": {
            "Accept-Encoding": "identity",
            "Connection": "close",
            "Host": "192.168.10.93:8080",
            "User-Agent": "Python-urllib/2.7"
        },
        "remote_addr": "192.168.10.93"
    }
}
Bad anonymity (your ip address is visible)
Good quality, nothing bad detected
```
