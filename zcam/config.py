DEFAULTS = {
    'proxy_bind_addr': '*',
    'proxy_pub_port': '7700',
    'proxy_sub_port': '7701',
    'proxy_connect_addr': '127.0.0.1',
    'puburi': 'tcp://%(proxy_bind_addr)s:%(proxy_pub_port)s',
    'suburi': 'tcp://%(proxy_bind_addr)s:%(proxy_sub_port)s',
}
