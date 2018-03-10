protonclient --api net-l3vpn port-create --id 153f734e-396a-4201-b3ab-f16d08140545 --mac_address fa:16:3e:b7:38:45 --vlan_transparency true --mtu 2 --vnic_type normal --tenant_id dfb96f8694274eca9b1502bb867f9342 --admin_state_up true --name test_port --status ACTIVE

protonclient --api net-l3vpn vpn-create --name testing --route_distinguishers 2200:1 --tenant_id dfb96f8694274eca9b1502bb867f9342 --id 58e361a8-d2a6-410d-92a1-35bbb2b2b1e6

protonclient --api net-l3vpn vpnbinding-create --interface_id 153f734e-396a-4201-b3ab-f16d08140545 --gateway 172.18.0.1 --ipaddress 172.18.0.12 --subnet_prefix 24 --service_id 58e361a8-d2a6-410d-92a1-35bbb2b2b1e6 --tenant_id dfb96f8694274eca9b1502bb867f9342
