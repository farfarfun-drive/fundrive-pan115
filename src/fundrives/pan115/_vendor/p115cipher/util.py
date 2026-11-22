#!/usr/bin/env python3
# encoding: utf-8

from collections.abc import Callable, Iterator

from fundrives.pan115._vendor.filewrap import to_bytes_view
from collections.abc import Buffer
from typing import Final, Literal


G_kts: Final = bytes(
    (
        0xF0,
        0xE5,
        0x69,
        0xAE,
        0xBF,
        0xDC,
        0xBF,
        0x8A,
        0x1A,
        0x45,
        0xE8,
        0xBE,
        0x7D,
        0xA6,
        0x73,
        0xB8,
        0xDE,
        0x8F,
        0xE7,
        0xC4,
        0x45,
        0xDA,
        0x86,
        0xC4,
        0x9B,
        0x64,
        0x8B,
        0x14,
        0x6A,
        0xB4,
        0xF1,
        0xAA,
        0x38,
        0x01,
        0x35,
        0x9E,
        0x26,
        0x69,
        0x2C,
        0x86,
        0x00,
        0x6B,
        0x4F,
        0xA5,
        0x36,
        0x34,
        0x62,
        0xA6,
        0x2A,
        0x96,
        0x68,
        0x18,
        0xF2,
        0x4A,
        0xFD,
        0xBD,
        0x6B,
        0x97,
        0x8F,
        0x4D,
        0x8F,
        0x89,
        0x13,
        0xB7,
        0x6C,
        0x8E,
        0x93,
        0xED,
        0x0E,
        0x0D,
        0x48,
        0x3E,
        0xD7,
        0x2F,
        0x88,
        0xD8,
        0xFE,
        0xFE,
        0x7E,
        0x86,
        0x50,
        0x95,
        0x4F,
        0xD1,
        0xEB,
        0x83,
        0x26,
        0x34,
        0xDB,
        0x66,
        0x7B,
        0x9C,
        0x7E,
        0x9D,
        0x7A,
        0x81,
        0x32,
        0xEA,
        0xB6,
        0x33,
        0xDE,
        0x3A,
        0xA9,
        0x59,
        0x34,
        0x66,
        0x3B,
        0xAA,
        0xBA,
        0x81,
        0x60,
        0x48,
        0xB9,
        0xD5,
        0x81,
        0x9C,
        0xF8,
        0x6C,
        0x84,
        0x77,
        0xFF,
        0x54,
        0x78,
        0x26,
        0x5F,
        0xBE,
        0xE8,
        0x1E,
        0x36,
        0x9F,
        0x34,
        0x80,
        0x5C,
        0x45,
        0x2C,
        0x9B,
        0x76,
        0xD5,
        0x1B,
        0x8F,
        0xCC,
        0xC3,
        0xB8,
        0xF5,
    )
)
ECDH_REMOTE_PUBKEY: Final = bytes(
    (
        0x57,
        0xA2,
        0x92,
        0x57,
        0xCD,
        0x23,
        0x20,
        0xE5,
        0xD6,
        0xD1,
        0x43,
        0x32,
        0x2F,
        0xA4,
        0xBB,
        0x8A,
        0x3C,
        0xF9,
        0xD3,
        0xCC,
        0x62,
        0x3E,
        0xF5,
        0xED,
        0xAC,
        0x62,
        0xB7,
        0x67,
        0x8A,
        0x89,
        0xC9,
        0x1A,
        0x83,
        0xBA,
        0x80,
        0x0D,
        0x61,
        0x29,
        0xF5,
        0x22,
        0xD0,
        0x34,
        0xC8,
        0x95,
        0xDD,
        0x24,
        0x65,
        0x24,
        0x3A,
        0xDD,
        0xC2,
        0x50,
        0x95,
        0x3B,
        0xEE,
        0xBA,
    )
)
RSA_PUBKEY_PAIR: Final = (
    0x8686980C0F5A24C4B9D43020CD2C22703FF3F450756529058B1CF88F09B8602136477198A6E2683149659BD122C33592FDB5AD47944AD1EA4D36C6B172AAD6338C3BB6AC6227502D010993AC967D1AEF00F0C8E038DE2E4D3BC2EC368AF2E9F10A6F1EDA4F7262F136420C07C331B871BF139F74F3010E3C4FE57DF3AFB71683,
    0x10001,
)


from_bytes = int.from_bytes
to_bytes = int.to_bytes


def _pad(data, /):
    if not isinstance(data, (bytes, bytearray)):
        data = bytes(data)
    if pad_size := -len(data) & 15:
        return data + bytes((pad_size,) * pad_size)
    return data


def _unpad(data, /):
    view = to_bytes_view(data)
    if 0 < (pad_size := view[-1]) < 16 and all(c == pad_size for c in view[-pad_size:]):
        return view[:-pad_size].tobytes()
    return data


aes_cbc_encrypt: Callable[[Buffer, bytes, bytes], bytes]
aes_cbc_decrypt: Callable[[Buffer, bytes, bytes], bytes]
try:
    from Crypto.Cipher import AES

    def aes_cbc_encrypt(data, aes_key, aes_iv):
        return AES.new(aes_key, AES.MODE_CBC, aes_iv).encrypt(_pad(data))

    def aes_cbc_decrypt(cipher_data, aes_key, aes_iv):
        view = to_bytes_view(cipher_data)
        return _unpad(
            AES.new(aes_key, AES.MODE_CBC, aes_iv).decrypt(view[: len(view) & -16])
        )
except ImportError:
    try:
        from cryptography.hazmat.primitives.ciphers import Cipher, algorithms, modes

        def aes_cbc_encrypt(data, aes_key, aes_iv):
            cipher = Cipher(algorithms.AES(aes_key), modes.CBC(aes_iv))
            encryptor = cipher.encryptor()
            return encryptor.update(_pad(data)) + encryptor.finalize()

        def aes_cbc_decrypt(cipher_data, aes_key, aes_iv):
            cipher = Cipher(algorithms.AES(aes_key), modes.CBC(aes_iv))
            decryptor = cipher.decryptor()
            return _unpad(decryptor.update(cipher_data) + decryptor.finalize())
    except ImportError:
        from shutil import which

        if which("openssl"):
            from subprocess import check_output

            def aes_cbc_encrypt(data, aes_key, aes_iv):
                return check_output(
                    [
                        "openssl",
                        "enc",
                        "-aes-128-cbc",
                        "-e",
                        "-K",
                        aes_key.hex(),
                        "-iv",
                        aes_iv.hex(),
                        "-nosalt",
                    ],
                    input=data,
                )

            def aes_cbc_decrypt(cipher_data, aes_key, aes_iv):
                return check_output(
                    [
                        "openssl",
                        "enc",
                        "-aes-128-cbc",
                        "-d",
                        "-K",
                        aes_key.hex(),
                        "-iv",
                        aes_iv.hex(),
                        "-nosalt",
                    ],
                    input=cipher_data,
                )
        else:
            from .aes import AES as AES_

            def aes_cbc_encrypt(data, aes_key, aes_iv):
                encrypt = AES_(aes_key).encrypt
                view = to_bytes_view(_pad(data))
                b = bytearray()
                puts = b.extend
                last_cipher = aes_iv
                for i in range(0, len(view), 16):
                    last_cipher = encrypt(
                        [(p ^ l) for (p, l) in zip(view[i : i + 16], last_cipher)]
                    )
                    puts(last_cipher)
                return b

            def aes_cbc_decrypt(cipher_data, aes_key, aes_iv):
                decrypt = AES_(aes_key).decrypt
                view = to_bytes_view(cipher_data)
                b = bytearray()
                puts = b.extend
                last_cipher = aes_iv
                for i in range(0, len(view), 16):
                    puts(
                        p ^ l for (p, l) in zip(decrypt(view[i : i + 16]), last_cipher)
                    )
                    last_cipher = view[i : i + 16]
                return _unpad(b)


lz4_block_decompress: Callable[[Buffer, int], bytes]
try:
    from lz4.block import decompress as lz4_block_decompress  # type: ignore
except ImportError:
    from ctypes.util import find_library

    if lz4_path := find_library("lz4"):
        import ctypes
        from ctypes import create_string_buffer

        _lz4 = ctypes.CDLL(lz4_path)
        LZ4_decompress_safe = _lz4.LZ4_decompress_safe
        LZ4_decompress_safe.argtypes = [
            ctypes.c_char_p,
            ctypes.c_char_p,
            ctypes.c_int,
            ctypes.c_int,
        ]
        LZ4_decompress_safe.restype = ctypes.c_int

        def lz4_block_decompress(source, uncompressed_size):
            dst_buf = create_string_buffer(uncompressed_size)
            result = LZ4_decompress_safe(
                bytes(source),
                dst_buf,
                len(source),
                uncompressed_size,
            )
            if result < 0:
                raise ValueError("LZ4 decompression failed")
            return dst_buf.raw[:result]
    else:

        def lz4_block_decompress(source, uncompressed_size=-1):
            src = to_bytes_view(source)
            src_len = len(source)
            src_ptr = 0
            dest = bytearray()
            dest_extend = dest.extend
            while src_ptr < src_len:
                token = src[src_ptr]
                src_ptr += 1
                lit_len = token >> 4
                if lit_len == 15:
                    start_ptr = src_ptr
                    try:
                        while src[src_ptr] == 255:
                            src_ptr += 1
                        lit_len += (src_ptr - start_ptr) * 255 + src[src_ptr]
                        src_ptr += 1
                    except IndexError:
                        pass
                if lit_len:
                    dest_extend(src[src_ptr : src_ptr + lit_len])
                    src_ptr += lit_len
                if src_ptr >= src_len:
                    break
                offset = src[src_ptr] | (src[src_ptr + 1] << 8)
                src_ptr += 2
                match_len = token & 0x0F
                if match_len == 15:
                    start_ptr = src_ptr
                    try:
                        while src[src_ptr] == 255:
                            src_ptr += 1
                        match_len += (src_ptr - start_ptr) * 255 + src[src_ptr]
                        src_ptr += 1
                    except IndexError:
                        pass
                match_len += 4
                dest_ptr = len(dest)
                match_pos = dest_ptr - offset
                if offset >= match_len:
                    dest_extend(dest[match_pos : match_pos + match_len])
                else:
                    if offset == 1:
                        dest_extend((dest[match_pos],) * match_len)
                    else:
                        end_ptr = dest_ptr + match_len
                        while dest_ptr < end_ptr:
                            copy_size = (
                                offset
                                if offset < (end_ptr - dest_ptr)
                                else (end_ptr - dest_ptr)
                            )
                            dest_extend(dest[match_pos : match_pos + copy_size])
                            dest_ptr += copy_size
                            offset += offset
            return dest


def acc_step(
    start: int,
    stop: None | int = None,
    step: int = 1,
) -> Iterator[tuple[int, int, int]]:
    if stop is None:
        start, stop = 0, start
    for i in range(start + step, stop, step):
        yield start, (start := i), step
    if start != stop:
        yield start, stop, stop - start


def bytes_xor(
    v1: Buffer,
    v2: Buffer,
    /,
    size: int = 0,
    byteorder: Literal["little", "big"] = "big",
) -> bytes:
    if size:
        v1 = to_bytes_view(v1)[:size]
        v2 = to_bytes_view(v2)[:size]
    else:
        size = memoryview(v1).nbytes
    return to_bytes(from_bytes(v1) ^ from_bytes(v2), size, byteorder=byteorder)


def xor(
    src: Buffer,
    key: Buffer,
    /,
    byteorder: Literal["little", "big"] = "big",
) -> bytearray:
    src = to_bytes_view(src)
    key = to_bytes_view(key)
    secret = bytearray()
    if i := len(src) & 0b11:
        secret += bytes_xor(src, key, i, byteorder=byteorder)
    for i, j, s in acc_step(i, len(src), len(key)):
        secret += bytes_xor(src[i:j], key[:s], byteorder=byteorder)
    return secret


def generate_ecdh_pair() -> tuple[bytes, bytes]:
    """获取 AES 密钥对（基于 ECC-DH 协议）

    :return: (公钥, 私钥) 的 2 元组

    .. code::

        aes_pubkey, aes_secret = generate_ecdh_pair()
        aes_key = secret[:16]
        aes_iv  = secret[-16:]
    """
    from ecdsa import ECDH, NIST224p, SigningKey  # type: ignore

    secret_key = SigningKey.generate(NIST224p)
    public_key = secret_key.verifying_key
    ecdh = ECDH(NIST224p)
    ecdh.load_private_key(secret_key)
    ecdh.load_received_public_key_bytes(ECDH_REMOTE_PUBKEY)
    public = public_key.pubkey.point.to_bytes()
    x, y = public[:28], public[28:]
    pubkey = bytes((28 + 1, 0x02 + (from_bytes(y) & 1))) + x
    # NOTE: Roughly equivalent to
    # n = int((ecdh.public_key.pubkey.point * from_bytes(secret_key.to_string())).x())
    # secret = to_bytes(n, (n.bit_length() + 0b111) >> 3)
    secret = ecdh.generate_sharedsecret_bytes()
    return pubkey, secret


def rsa_gen_key(
    rand_key: Buffer,
    sk_len: int = 4,
    /,
) -> bytearray:
    rand_key = to_bytes_view(rand_key)
    xor_key = bytearray(sk_len)
    length = sk_len * (sk_len - 1)
    index = 0
    for i in range(sk_len):
        x = (rand_key[i] + G_kts[index]) & 0xFF
        xor_key[i] = G_kts[length] ^ x
        length -= sk_len
        index += sk_len
    return xor_key


def pad_pkcs1_v1_5(message: Buffer, /) -> int:
    data = bytearray(b"\x00")
    data += b"\x02" * (126 - memoryview(message).nbytes)
    data += b"\x00"
    data += message
    return from_bytes(data)


def rsa_encrypt_with_pubkey(data: Buffer, /) -> bytearray:
    "把数据用 RSA 公钥加密"
    cipher_data = bytearray()
    view = to_bytes_view(data)
    for l, r, _ in acc_step(0, len(view), 117):
        cipher_data += to_bytes(
            pow(pad_pkcs1_v1_5(view[l:r]), RSA_PUBKEY_PAIR[1], RSA_PUBKEY_PAIR[0]), 128
        )
    return cipher_data


def rsa_decrypt_with_pubkey(cipher_data: Buffer, /) -> bytearray:
    "把数据用 RSA 公钥解密"
    data = bytearray()
    view = to_bytes_view(cipher_data)
    for l, r, _ in acc_step(0, len(view), 128):
        p = pow(from_bytes(view[l:r]), RSA_PUBKEY_PAIR[1], RSA_PUBKEY_PAIR[0])
        b = to_bytes(p, (p.bit_length() + 0b111) >> 3)
        data += memoryview(b)[b.index(0) + 1 :]
    return data


def lz4_decompress(source: Buffer, /) -> bytes:
    src = to_bytes_view(source)
    data = b""
    while src and src.nbytes > 2 and (src_len := (src[0] + (src[1] << 8))):
        data += lz4_block_decompress(src[2 : src_len + 2], 0x2000)
        src = src[src_len + 2 :]
    return data
