..
      Copyright 2016 and 2017, Nokia

      Licensed under the Apache License, Version 2.0 (the "License"); you may
      not use this file except in compliance with the License. You may obtain
      a copy of the License at

          http://www.apache.org/licenses/LICENSE-2.0

      Unless required by applicable law or agreed to in writing, software
      distributed under the License is distributed on an "AS IS" BASIS, WITHOUT
      WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the
      License for the specific language governing permissions and limitations
      under the License.

      Convention for heading levels in Gluon documentation:
      =======  Heading 0 (reserved for the title in a document)
      -------  Heading 1
      ~~~~~~~  Heading 2
      +++++++  Heading 3
      '''''''  Heading 4
      (Avoid deeper levels because they do not render well.)

==========================
Install ``etcd`` for Gluon
==========================

The following instructions are from reference [1]_.

You need at least three nodes for the ``etcd`` cluster to work, e.g. one
controller and two computes.

On Each Node
------------

**STEP-1**: Download ``etcd`` Package

.. code-block:: bash

    curl -L  https://github.com/coreos/etcd/releases/download/v2.3.6/etcd-v2.3.6-linux-amd64.tar.gz -o etcd-v2.3.6-linux-amd64.tar.gz
    Unzip/Untar the downloaded file

**STEP-2**: Copy executables to ``/usr/local/bin``

.. code-block:: bash

    cd etcd-v2.3.6-linux-amd64
    sudo cp etcd /usr/local/bin
    sudo cp etcdctl /usr/local/bin

**STEP-3**: Create a directory for ``etcd`` data

.. code-block:: bash

    sudo mkdir /var/etcd

**STEP-4**: Create upstart ``init`` file:

In ``/etc/init`` directory, create a file called ``etcd.conf``, and paste the
following into it:

.. code-block:: bash

    description "etcd 2.0 distributed key-value store"
    author "Scott Lowe <scott.lowe@scottlowe.org>"
    start on (net-device-up
              and local-filesystems
              and runlevel [2345])
    stop on runlevel [016]
    respawn
    respawn limit 10 5
    script
      if [ -f "/etc/default/etcd" ]; then
        . /etc/default/etcd
      fi
    chdir /var/etcd
    exec /usr/local/bin/etcd >>/var/log/etcd.log 2>&1
    end script

**STEP-5**: Create an override file for ``etcd`` parameters:

In ``/etc/init`` directory, create a file called ``etcd.override`` and paste
the following into it:

.. code-block:: bash

    # Override file for etcd Upstart script providing some environment variables
    env ETCD_INITIAL_CLUSTER="etcd-01=http://10.2.0.32:2380,etcd-02=http://10.2.0.102:2380,etcd-03=http://10.2.0.101:2380"
    env ETCD_INITIAL_CLUSTER_STATE="new"
    env ETCD_INITIAL_CLUSTER_TOKEN="etcd-cluster-1"
    env ETCD_INITIAL_ADVERTISE_PEER_URLS="http://10.2.0.32:2380"
    env ETCD_DATA_DIR="/var/etcd"
    env ETCD_LISTEN_PEER_URLS="http://10.2.0.32:2380"
    env ETCD_LISTEN_CLIENT_URLS="http://10.2.0.32:2379,http://127.0.0.1:2379"
    env ETCD_ADVERTISE_CLIENT_URLS="http://10.2.0.32:2379"
    env ETCD_NAME="etcd-01"


**NOTE**:

* The IP Addresses will need to be changed for your own machines!
* For each node in the cluster, the file will be slightly different, i.e. the
  IP address of "advertise" and "listen" URLs, and ``etcd`` names will be for
  each specific node.

For instance, the files on the other two nodes would look like:

.. code-block:: bash
    
    # Override file for etcd Upstart script providing some environment variables
    env ETCD_INITIAL_CLUSTER="etcd-01=http://10.2.0.32:2380,etcd-02=http://10.2.0.102:2380,etcd-03=http://10.2.0.101:2380"
    env ETCD_INITIAL_CLUSTER_STATE="new"
    env ETCD_INITIAL_CLUSTER_TOKEN="etcd-cluster-1"
    env ETCD_INITIAL_ADVERTISE_PEER_URLS="http://10.2.0.102:2380"
    env ETCD_DATA_DIR="/var/etcd"
    env ETCD_LISTEN_PEER_URLS="http://10.2.0.102:2380"
    env ETCD_LISTEN_CLIENT_URLS="http://10.2.0.102:2379,http://127.0.0.1:2379"
    env ETCD_ADVERTISE_CLIENT_URLS="http://10.2.0.102:2379"
    env ETCD_NAME="etcd-02"

.. code-block:: bash

    # Override file for etcd Upstart script providing some environment variables
    env ETCD_INITIAL_CLUSTER="etcd-01=http://10.2.0.32:2380,etcd-02=http://10.2.0.102:2380,etcd-03=http://10.2.0.101:2380"
    env ETCD_INITIAL_CLUSTER_STATE="new"
    env ETCD_INITIAL_CLUSTER_TOKEN="etcd-cluster-1"
    env ETCD_INITIAL_ADVERTISE_PEER_URLS="http://10.2.0.101:2380"
    env ETCD_DATA_DIR="/var/etcd"
    env ETCD_LISTEN_PEER_URLS="http://10.2.0.101:2380"
    env ETCD_LISTEN_CLIENT_URLS="http://10.2.0.101:2379,http://127.0.0.1:2379"
    env ETCD_ADVERTISE_CLIENT_URLS="http://10.2.0.101:2379"
    env ETCD_NAME="etcd-03"

**STEP-6**: Adjust ``iptables``:

.. code-block:: bash

    sudo iptables -A INPUT -p tcp -m multiport --ports 2380,2379 -m comment --comment "etcd" -j ACCEPT
    sudo invoke-rc.d iptables-persistent save

**STEP-7**: Start the ``etcd`` server:

As root:

.. code-block:: bash

    initctl start etcd

Or on ``ubuntu 14.04``, run:

.. code-block:: bash

    sudo start etcd

**STEP-8**: Verify the cluster is healty:

.. code-block:: bash

    $ etcdctl cluster-health
    member 5cd8baf7fb9d49b7 is healthy: got healthy result from http://10.2.0.102:2379
    member 9e95400273fd2acb is healthy: got healthy result from http://10.2.0.101:2379
    member ce8a4cd91a34b3f2 is healthy: got healthy result from http://10.2.0.32:2379
    cluster is healthy

References

.. [1] http://blog.scottlowe.org/2015/04/15/running-etcd-20-cluster/
