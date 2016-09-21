from gluon.sync_etcd.thread import SyncData

def logupdate(f):
    def decorate(self, *args):
        record = {"table": self.__name__, "key": self.__getattribute__(self._primary_key), "operation": "update"}
        f(self, *args)
        if SyncData.sync_thread_running:
            SyncData.sync_queue.put(record)
    return decorate


def logdelete(f):
    def decorate(self, *args):
        record = {"table": self.__name__, "key": self.__getattribute__(self._primary_key), "operation": "delete"}
        f(self, *args)
        if SyncData.sync_thread_running:
            SyncData.sync_queue.put(record)
    return decorate
