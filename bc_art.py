import json
from transaction import Transaction

def make_create_message(work_id, file_hash, title):
    return json.dumps({
        "type": "CREATE",
        "work_id": work_id,
        "file_hash": file_hash,
        "title": title,
    }, sort_keys=True)

def make_transfer_message(work_id, new_owner):
    return json.dumps({
        "type": "TRANSFER",
        "work_id": work_id,
        "new_owner": new_owner,   # adresse (hash de clé publique)
    }, sort_keys=True)

def make_rent_message(work_id, renter):
    return json.dumps({
        "type": "RENT",
        "work_id": work_id,
        "renter": renter,         # adresse du locataire
    }, sort_keys=True)




def create_work_transaction(sk, work_id, file_hash, title):
    msg = make_create_message(work_id, file_hash, title)
    t = Transaction(message=msg)
    t.sign(sk)
    return t

def transfer_work_transaction(sk, work_id, new_owner_addr):
    msg = make_transfer_message(work_id, new_owner_addr)
    t = Transaction(message=msg)
    t.sign(sk)
    return t

def rent_work_transaction(sk, work_id, renter_addr):
    msg = make_rent_message(work_id, renter_addr)
    t = Transaction(message=msg)
    t.sign(sk)
    return t



class Blockchain:
    def __init__(self):
        self.chain = []
        # ...
        self.works_state = {}  
        # work_id -> {
        #   "owner": <adresse propriétaire>,
        #   "renters": set([...])
        # }
        self.works_state = {}
        self.chain = []         # liste des blocs
        self.pending = []       # transactions en attente
        self.difficulty = 2
        # Liste des artistes "reconnus" (adresses)
        self.recognized_artists = set()

    def apply_transaction(self, tx: Transaction):
        # On parse le message JSON
        payload = json.loads(tx.message)
        ttype = payload["type"]

        if ttype == "CREATE":
            self._apply_create(tx, payload)
        elif ttype == "TRANSFER":
            self._apply_transfer(tx, payload)
        elif ttype == "RENT":
            self._apply_rent(tx, payload)



    def _apply_create(self, tx: Transaction, payload: dict):
        work_id = payload["work_id"]
        file_hash = payload["file_hash"]
        author = tx.author  # créateur = propriétaire initial

        if work_id in self.works_state:
            raise Exception("Work already exists")

        self.works_state[work_id] = {
            "owner": author,
            "renters": set(),
            "file_hash": file_hash,
        }


    def _apply_transfer(self, tx: Transaction, payload: dict):
        work_id = payload["work_id"]
        new_owner = payload["new_owner"]
        author = tx.author  # celui qui signe = celui qui vend

        if work_id not in self.works_state:
            raise Exception("Unknown work")

        state = self.works_state[work_id]

        # 1) Seul le propriétaire peut vendre
        if state["owner"] != author:
            raise Exception("Only the owner can transfer this work")

        # 2) L’œuvre ne doit pas être louée pour être vendue
        if len(state["renters"]) > 0:
            raise Exception("Work is currently rented, cannot be sold")

        # Si tout est OK → on change de propriétaire
        state["owner"] = new_owner

    def _apply_rent(self, tx: Transaction, payload: dict):
        work_id = payload["work_id"]
        renter = payload["renter"]
        author = tx.author  # celui qui signe = propriétaire qui loue

        if work_id not in self.works_state:
            raise Exception("Unknown work")

        state = self.works_state[work_id]

        # Seul le propriétaire peut louer
        if state["owner"] != author:
            raise Exception("Only the owner can rent this work")

        # On ajoute le locataire (plusieurs possibles)
        state["renters"].add(renter)


    def add_block(self, block):
        # vérifier le hash, previous_hash, etc.
        # vérifier toutes les transactions du bloc
        for tx in block.transactions:
            # vérifier la signature :
            if not tx.verify():
                raise Exception("Invalid signature")
            # appliquer à l’état métier :
            self.apply_transaction(tx)
        self.chain.append(block)
        
    def add_recognized_artist(self, artist_addr: str):
        """
        Ajoute un artiste "reconnu" dans la whitelist.
        artist_addr = hash de la clé publique (même format que tx.author)
        """
        self.recognized_artists.add(artist_addr)
    
    
    def _apply_create(self, tx: Transaction, payload: dict):
        work_id = payload["work_id"]
        file_hash = payload["file_hash"]
        author = tx.author  # créateur = propriétaire initial

        # Vérifier que l'artiste est "reconnu"
        if author not in self.recognized_artists:
            raise Exception("Artist is not recognized, cannot mint this work")

        if work_id in self.works_state:
            raise Exception("Work already exists")

        self.works_state[work_id] = {
            "owner": author,
            "renters": set(),
            "file_hash": file_hash,
        }

