from threading import RLock
from uuid import UUID
from .models import ChangeRequest

class ChangeNotFound(LookupError): pass
class InMemoryChangeRepository:
    def __init__(self): self._lock=RLock(); self._items:dict[tuple[UUID,UUID],tuple[ChangeRequest,...]]={}
    def append(self,item:ChangeRequest)->ChangeRequest:
        key=(item.tenant_id,item.change_request_id)
        with self._lock:
            history=self._items.get(key,())
            if history and item.version!=history[-1].version+1: raise ValueError("version must be monotonic")
            if not history and item.version!=1: raise ValueError("first version must be one")
            self._items[key]=(*history,item)
        return item
    def history(self,tenant_id:UUID,change_id:UUID)->tuple[ChangeRequest,...]:
        history=self._items.get((tenant_id,change_id),())
        if not history: raise ChangeNotFound("change request not found")
        return history
    def latest(self,tenant_id:UUID,change_id:UUID)->ChangeRequest:return self.history(tenant_id,change_id)[-1]
