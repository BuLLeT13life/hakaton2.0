
import os
from cryptography.hazmat.primitives import hashes, hmac, serialization
from cryptography.hazmat.primitives.serialization import load_pem_public_key
from cryptography.hazmat.primitives.asymmetric import rsa, padding
from cryptography.hazmat.backends import default_backend
import binascii
import sqlite3
import base64
import hashlib



def assign_digital_signature(img):
    # Чтение данных из изображения
    with open(img, "rb") as f:
        data = f.read()

    # Генерация ключа RSA
    private_key = rsa.generate_private_key(
        public_exponent=65537,
        key_size=2048,
        backend=default_backend()
    )
    public_key = private_key.public_key()

    # Создаем хеш фотографии
    hasher = hashes.Hash(hashes.SHA256(), default_backend())
    hasher.update(data)
    photo_hash = hasher.finalize()

    # Создание подписи
    signature = private_key.sign(
        photo_hash,
        padding.PSS(
            mgf=padding.MGF1(hashes.SHA256()),
            salt_length=padding.PSS.MAX_LENGTH
        ),
        hashes.SHA256()
    )



    # сохранение приватного ключа в файл
    with open("static/keys/private_key.pem", "wb") as private_key_file:
        private_key_file.write(
            private_key.private_bytes(
                encoding=serialization.Encoding.PEM,
                format=serialization.PrivateFormat.TraditionalOpenSSL,
                encryption_algorithm=serialization.NoEncryption()
            )
        )

    # Спрячем подпись и открытый ключ в фото

    pem = public_key.public_bytes(
        encoding=serialization.Encoding.PEM,
        format=serialization.PublicFormat.SubjectPublicKeyInfo
    )

    with open(img, "ab") as f:
        f.write(pem)
        f.write(signature)

    return signature, pem

def connect_to_database():
    pass


def check_signature(signature, pem, img):

    # Проверим подпись
    with open(img, "rb") as f:
        data = f.read()

    image_signature = data[-len(signature):]
    image_public_key = data[(-len(pem) - len(signature)):-len(signature)]

    image_hash = hashlib.sha256()
    image_hash.update(data[:-len(signature) - len(image_public_key)])
    hash_digest = image_hash.digest()

    public_key = serialization.load_pem_public_key(
        image_public_key,
        backend=default_backend()
    )

    try:
        public_key.verify(
            image_signature,
            hash_digest,
            padding.PSS(mgf=padding.MGF1(hashes.SHA256()), salt_length=padding.PSS.MAX_LENGTH),
            hashes.SHA256()
        )
        print("Подпись верна!")
    except:
        print("Подпись неверна!")


def update_database():
    pass

def main():
    signature, pem = assign_digital_signature("x.jpg")
    check_signature(signature, pem, "x.jpg")


if __name__ == '__main__':
    main()
