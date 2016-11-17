# Copyright (c) 2016 Nokia, Inc.
# All Rights Reserved
#
#    Licensed under the Apache License, Version 2.0 (the "License"); you may
#    not use this file except in compliance with the License. You may obtain
#    a copy of the License at
#
#         http://www.apache.org/licenses/LICENSE-2.0
#
#    Unless required by applicable law or agreed to in writing, software
#    distributed under the License is distributed on an "AS IS" BASIS, WITHOUT
#    WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the
#    License for the specific language governing permissions and limitations
#    under the License.

from gluon.sync_etcd.thread import SyncData


def logupdate(f):
    def decorate(self, *args):
        record = {"table": self.__tname__,
                  "service": self._service_name,
                  "key": self.__getattribute__(self._primary_key),
                  "operation": "update"}
        f(self, *args)
        if SyncData.sync_thread_running:
            SyncData.sync_queue.put(record)
    return decorate


def logdelete(f):
    def decorate(self, *args):
        record = {"table": self.__tname__,
                  "service": self._service_name,
                  "key": self.__getattribute__(self._primary_key),
                  "operation": "delete"}
        f(self, *args)
        if SyncData.sync_thread_running:
            SyncData.sync_queue.put(record)
    return decorate
