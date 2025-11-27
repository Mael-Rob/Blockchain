"""
This module define a transaction class. A transaction is a message signed by a private key.
The signature can be verified with the public key.

A transaction is a dictionary with the following keys:
    - message: the message to sign
    - date: the date of the transaction
    - author: the hash of the public key
    - vk: the public key
    - signature: the signature of the message

The signature and the public key are binary strings. Both are converted to hexadecimal (base64) string to be
stored in the transaction.

The hash of the transaction is the hash of the dictionary (keys are sorted).
"""
import json
import hashlib
from ecdsa import VerifyingKey, BadSignatureError
from rich.console import Console
from rich.table import Table
from datetime import datetime


def get_time():
    """
    Return a string representing the current time in format "%Y-%m-%d %H:%M:%S.%f"
    :return: str
    """
    return str(datetime.now())


def str_to_time(s):
    """
    Convert a string into a datetime object.
    :param s: str
    :return:
    """
    return datetime.strptime(s, "%Y-%m-%d %H:%M:%S.%f")




class IncompleteTransaction(Exception):
    pass


class Transaction(object):
    def __init__(self, message, date=None, signature=None, vk=None, author=None):
        """
        Initialize a transaction. If date is None, the current time is used.
        Signature and verifying key may be None.

        Author is the hash of the verifying key (or None if vk is not specified).

        :param message: str
        :param date: str in format "%Y-%m-%d %H:%M:%S.%f" see (module "utils")
        :param signature: str
        :param vk: str
        """
        
        self.message = message
        if date is None:
            self.date = get_time()
        else:
            self.date = date

    
        self.vk = vk
        self.author = author
        self.signature = signature

        if vk is not None:
            vk_bytes = vk if isinstance(vk, (bytes, bytearray)) else str(vk).encode()
            self.author = hashlib.sha256(vk_bytes).hexdigest()
        else:
            self.author = None
        
        pass

    def json_dumps(self):
        """
        Return a json representation of the transaction. The keys are sorted.
        :return:
        """
        return json.dumps(self.data, sort_keys=True)

    @property
    def data(self):
        d = {
            "message": self.message,
            "date": self.date,
            "author": self.author,
            "vk": self.vk
        }
        return d

    def sign(self, sk):
        """
        Sign a transaction with a signing key. Set both attributes "signature" and "vk"
        :param sk: A signing key (private)
        """
        vk_bytes = sk.verifying_key.to_pem()
        self.vk = vk_bytes.hex()
        self.author = hashlib.sha256(vk_bytes).hexdigest()

        d = {
            "message": self.message,
            "date": self.date,
            "author": self.author,
            "vk": self.vk
        }


        self.signature = sk.sign(json.dumps(d, sort_keys=True).encode()).hex()

    def verify(self):
        """
        Verify the signature of the transaction and the author.
        :return: True or False
        """
        try :
            str_vk = self.vk
            vk = VerifyingKey.from_pem(bytes.fromhex(str_vk))
            binary_signature = bytes.fromhex(self.signature)
        
            d = {
                "message": self.message,
                "date": self.date,
                "author": self.author,
                "vk": self.vk
            }
        
            data = json.dumps(d, sort_keys=True).encode()

            vk.verify(binary_signature, data)
            return True 
        
        except BadSignatureError:
            return False
        

    def __str__(self):
        """
        :return: A string representation of the transaction
        """
        return (
            f"Transaction(\n"
            f"  message={self.message},\n"
            f"  date={self.date},\n"
            f"  author={self.author},\n"
            f"  vk={self.vk},\n"
            f"  signature={self.signature}\n"
            f")"
                )
        
        
    def __lt__(self, other):
        """
        Compare two transactions. The comparison is based on the hash of the transaction if it is defined else, the date.
        :param other: a transaction
        :return: True or False
        """
        
        if self.author is None and other.author is None:
            return False  # elles sont égales dans ce sens
        if self.author is None:
            return True
        if other.author is None:
            return False

        return self.author < other.author


    def hash(self):
        """
        Compute the hash of the transaction.
        :raise IncompleteTransaction: if signature or vk is None
        """
        if self.signature is None or self.vk is None:
            raise IncompleteTransaction("Transaction must be signed before hashing.")

        # Construire un dictionnaire avec les 5 attributs
        d = {
            "message": self.message,
            "date": self.date,
            "author": self.author,
            "vk": self.vk,
            "signature": self.signature
        }

        # Convertir en chaîne JSON
        s = json.dumps(d, sort_keys=True)

        # Hash SHA256 de la chaîne encodée
        return hashlib.sha256(s.encode()).hexdigest()


    @staticmethod
    def log(transactions):
        """
        Print a nice log of set of the transactions
        :param transactions:
        :return:
        """
        table = Table(title=f"List of transactions")
        table.add_column("Hash", justify="left", style="cyan")
        table.add_column("Message", justify="left", style="cyan")
        table.add_column("Date", justify="left", style="cyan")
        table.add_column("Signature", justify="left", style="cyan")
        table.add_column("Author", justify="left", style="cyan")

        for t in sorted(transactions):
            table.add_row(
                None if t.vk is None else t.hash()[:14] + "...",
                t.message,
                t.date[:-7],
                None if t.signature is None else t.signature[:7] + "...",
                None if t.author is None else t.author[:7] + "..."
            )

        console = Console()
        console.print(table)


def test0():
    from ecdsa import SigningKey, NIST384p
    sk = SigningKey.generate(curve=NIST384p)
    t1 = Transaction("One")
    t2 = Transaction("Two")
    t3 = Transaction("Three")
    t4 = Transaction("Four")
    t3.sign(sk)
    t4.sign(sk)
    Transaction.log([t1, t2, t3, t4])


def test1():
    from ecdsa import SigningKey, NIST384p
    sk = SigningKey.generate(curve=NIST384p)
    t = Transaction("Message de test")
    print(t)
    t.sign(sk)
    print(t)
    print(t.hash())
    print(t.vk)
    print(t.verify())
    t.message += "2"
    print(t.verify())


def test2():
    """
    Warning: sk.verifying_key.to_pem().hex() produce a long string starting and ending with common information.
    It is easy to manually check that the two strings are different, but it is not easy to see the difference.
    This is the reason why the hash of the public key is used for author instead of the public key itself.
    """
    from ecdsa import SigningKey
    sk = SigningKey.generate()
    sk2 = SigningKey.generate()
    print(sk.verifying_key.to_pem().hex())
    print(sk2.verifying_key.to_pem().hex())
    print(sk.verifying_key.to_pem().hex() == sk2.verifying_key.to_pem().hex())


if __name__ == "__main__":
    print("Test Transaction")
    #test0()
    #test1()
    #test2()

