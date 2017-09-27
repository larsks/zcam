DEFAULTS = {
    'proxy_bind_addr': '*',
    'proxy_pub_port': '7700',
    'proxy_sub_port': '7701',
    'proxy_connect_addr': '127.0.0.1',

    # used by the proxy
    'pub_bind_uri': 'tcp://%(proxy_bind_addr)s:%(proxy_pub_port)s',
    'sub_bind_uri': 'tcp://%(proxy_bind_addr)s:%(proxy_sub_port)s',

    # used by clients to connect to the proxy
    'pub_connect_uri': 'tcp://%(proxy_connect_addr)s:%(proxy_pub_port)s',
    'sub_connect_uri': 'tcp://%(proxy_connect_addr)s:%(proxy_sub_port)s',
}
