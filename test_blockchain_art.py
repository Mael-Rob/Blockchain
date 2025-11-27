import hashlib
from ecdsa import SigningKey, NIST384p

from bc_art import (
    Blockchain,
    create_work_transaction,
    transfer_work_transaction,
    rent_work_transaction,
)

# petite classe "Block" minimale pour ton add_block()
class DummyBlock:
    def __init__(self, transactions):
        self.transactions = transactions


def addr_from_sk(sk):
    """Même logique que tx.author : hash de la clé publique."""
    vk_bytes = sk.verifying_key.to_pem()
    return hashlib.sha256(vk_bytes).hexdigest()


def test_blockchain_art():
    print("=== Test blockchain d’œuvres numériques ===")

    # --- Clés des acteurs ---
    sk_artist = SigningKey.generate(curve=NIST384p)
    sk_buyer = SigningKey.generate(curve=NIST384p)
    sk_renter1 = SigningKey.generate(curve=NIST384p)
    sk_renter2 = SigningKey.generate(curve=NIST384p)

    addr_artist = addr_from_sk(sk_artist)
    addr_buyer = addr_from_sk(sk_buyer)
    addr_renter1 = addr_from_sk(sk_renter1)
    addr_renter2 = addr_from_sk(sk_renter2)

    # --- Initialisation blockchain ---
    bc = Blockchain()

    # inscrire l'artiste comme "reconnu"
    bc.add_recognized_artist(addr_artist)


    # ========== 1. CRÉATION D’UNE ŒUVRE ==========
    tx_create = create_work_transaction(
        sk=sk_artist,
        work_id="work-1",
        file_hash="hash_du_fichier_1",
        title="Œuvre 1"
    )
    block1 = DummyBlock([tx_create])
    bc.add_block(block1)

    assert "work-1" in bc.works_state
    assert bc.works_state["work-1"]["owner"] == addr_artist
    assert bc.works_state["work-1"]["renters"] == set()
    print("[OK] Création d’œuvre : propriétaire = artiste")

    # ========== 2. LOCATION À PLUSIEURS ACTEURS ==========
    tx_rent1 = rent_work_transaction(sk_artist, "work-1", addr_renter1)
    tx_rent2 = rent_work_transaction(sk_artist, "work-1", addr_renter2)
    block2 = DummyBlock([tx_rent1, tx_rent2])
    bc.add_block(block2)

    renters = bc.works_state["work-1"]["renters"]
    assert addr_renter1 in renters
    assert addr_renter2 in renters
    print("[OK] Location à plusieurs acteurs autorisée")

    # ========== 3. VENTE INTERDITE SI L’ŒUVRE EST LOUÉE ==========
    tx_bad_transfer = transfer_work_transaction(sk_artist, "work-1", addr_buyer)
    block3 = DummyBlock([tx_bad_transfer])

    try:
        bc.add_block(block3)
        raise AssertionError("La vente aurait dû être refusée car l’œuvre est louée")
    except Exception as e:
        print("[OK] Vente refusée car l’œuvre est louée :", e)

    # ========== 4. ŒUVRE NON LOUÉE PEUT ÊTRE VENDUE ==========
    tx_create2 = create_work_transaction(
        sk=sk_artist,
        work_id="work-2",
        file_hash="hash_du_fichier_2",
        title="Œuvre 2"
    )
    block4 = DummyBlock([tx_create2])
    bc.add_block(block4)

    tx_good_transfer = transfer_work_transaction(sk_artist, "work-2", addr_buyer)
    block5 = DummyBlock([tx_good_transfer])
    bc.add_block(block5)

    assert bc.works_state["work-2"]["owner"] == addr_buyer
    print("[OK] Vente d’une œuvre non louée acceptée (nouveau propriétaire = acheteur)")
    
    addr_artist = addr_from_sk(sk_artist)
    bc = Blockchain()
    bc.add_recognized_artist(addr_artist)

    print("=== Tous les tests sont passés ✅ ===")


if __name__ == "__main__":
    test_blockchain_art()
