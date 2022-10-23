from google.cloud.firestore import \
    Client, \
    AsyncClient, \
    DocumentReference, \
    DocumentSnapshot, \
    Transaction
    
from typing import TypeVar

PathOrRef = TypeVar('PathOrRef', bound = str | tuple[str, ...] | DocumentReference)

client: Client = Client()
aclient: AsyncClient = AsyncClient()
clients = {
    'client': client,
    'aclient': aclient
}

from google.cloud.firestore import DocumentSnapshot, DocumentReference

def doc(path_or_ref: PathOrRef) -> DocumentReference:
    if type(path_or_ref) == str:
        return client.document(*path_or_ref.split('/'))
    elif type(path_or_ref) == DocumentReference:
        return client.document(path_or_ref.path)
    elif type(path_or_ref) == tuple:
        return client.document(*path_or_ref)