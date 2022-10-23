from typing import TypeVar
from google.cloud import firestore
PathOrRef = TypeVar('PathOrRef', bound = str | tuple[str, ...] | firestore.DocumentReference)
class BaseService:
    _client: firestore.Client
    _aclient: firestore.AsyncClient

    def __init__(self, client, async_client):
        self._client = client
        self._aclient = async_client

    def doc(self, path_or_ref: PathOrRef) -> firestore.DocumentReference:
        if type(path_or_ref) == str:
            return self._client.document(*path_or_ref.split('/'))
        elif type(path_or_ref) == firestore.DocumentReference:
            return self._client.document(path_or_ref.path)
        elif type(path_or_ref) == tuple:
            return self._client.document(*path_or_ref)