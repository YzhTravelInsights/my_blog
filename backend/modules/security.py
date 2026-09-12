"""
API 密钥安全模块（Windows DPAPI）

把敏感密钥（如 DEEPSEEK_API_KEY）以加密形式存进 .env：
    - 明文 key 只在本模块加密/解密时短暂存在于内存，从不落盘明文
    - 运行期 get_deepseek_api_key() 解密一次并缓存（进程内），之后直接用缓存
    - 避免明文 key 出现在 .env / git / 日志 / 错误回显中

加密方式：Windows DPAPI（CryptProtectData / CryptUnprotectData）
    - 零第三方依赖（仅用 ctypes，stdlib）
    - 密钥绑定「当前 Windows 用户 + 当前机器」，无需额外的密钥文件
    - 换用户 / 换机器后密文无法解密（这是特性，不是 bug）

向后兼容：若 .env 里仍是旧版明文 DEEPSEEK_API_KEY（如测试环境），
仍会原样读取，保证测试与未加密部署可用。

Linux / 跨平台说明：
    - DPAPI 仅存在于 Windows；本模块在非 Windows 上可正常 import，
      但 encrypt_secret / decrypt_secret 会抛 RuntimeError。
    - 因此 get_api_key() 在 Linux 上会自动回退读取明文 DEEPSEEK_API_KEY
      （部署到 Linux 服务器时用这种方式配置，见 README 部署章节）。
    - 注意 ctypes.wintypes 在 Linux 上 import 即报错（"_type_ 'v' not supported"），
      故此处只用 ctypes.c_uint32 表达 DWORD，不 import ctypes.wintypes。
"""

import base64
import ctypes
import logging
import os

logger = logging.getLogger("security")

# 进程内解密缓存：name -> 明文。只解密一次，之后直接命中。
_DECRYPT_CACHE: dict[str, str] = {}


class _DATA_BLOB(ctypes.Structure):
    # DWORD：用 c_uint32 而非 ctypes.wintypes.DWORD，避免在 Linux 上必须 import wintypes
    _fields_ = [
        ("cbData", ctypes.c_uint32),
        ("pbData", ctypes.POINTER(ctypes.c_char)),
    ]


def _protect(data: bytes) -> bytes:
    blob_in = _DATA_BLOB(
        len(data),
        ctypes.cast(
            ctypes.create_string_buffer(data, len(data)),
            ctypes.POINTER(ctypes.c_char),
        ),
    )
    blob_out = _DATA_BLOB()
    ok = ctypes.windll.crypt32.CryptProtectData(
        ctypes.byref(blob_in), None, None, None, None, 0, ctypes.byref(blob_out)
    )
    if not ok:
        raise ctypes.WinError()
    try:
        return ctypes.string_at(blob_out.pbData, blob_out.cbData)
    finally:
        ctypes.windll.kernel32.LocalFree(blob_out.pbData)


def _unprotect(data: bytes) -> bytes:
    blob_in = _DATA_BLOB(
        len(data),
        ctypes.cast(
            ctypes.create_string_buffer(data, len(data)),
            ctypes.POINTER(ctypes.c_char),
        ),
    )
    blob_out = _DATA_BLOB()
    ok = ctypes.windll.crypt32.CryptUnprotectData(
        ctypes.byref(blob_in), None, None, None, None, 0, ctypes.byref(blob_out)
    )
    if not ok:
        raise ctypes.WinError()
    try:
        return ctypes.string_at(blob_out.pbData, blob_out.cbData)
    finally:
        ctypes.windll.kernel32.LocalFree(blob_out.pbData)


def encrypt_secret(plaintext: str) -> str:
    """将明文加密为 base64 密文（用于写回 .env 的 *_ENC 变量）。"""
    if os.name != "nt":
        raise RuntimeError("DPAPI 加密仅支持 Windows 平台")
    return base64.b64encode(_protect(plaintext.encode("utf-8"))).decode("ascii")


def decrypt_secret(ciphertext_b64: str) -> str:
    """将 base64 密文解密回明文（仅当前 Windows 用户可解）。"""
    if os.name != "nt":
        raise RuntimeError("DPAPI 解密仅支持 Windows 平台")
    data = base64.b64decode(ciphertext_b64.encode("ascii"))
    return _unprotect(data).decode("utf-8")


def get_api_key(
    enc_var: str = "DEEPSEEK_API_KEY_ENC",
    plain_var: str = "DEEPSEEK_API_KEY",
) -> str | None:
    """
    安全读取 API key：
      1. 优先解密 *_ENC 密文变量（进程内只解密一次，缓存后续直接命中）
      2. 解密失败 / 无密文时，回退读旧版明文变量（测试、未加密环境）
    均不存在返回 None。
    """
    cached = _DECRYPT_CACHE.get(enc_var)
    if cached is not None:
        return cached

    enc = os.getenv(enc_var)
    if enc:
        try:
            key = decrypt_secret(enc)
            _DECRYPT_CACHE[enc_var] = key
            return key
        except Exception as e:  # noqa: BLE001 —— 解密失败不应中断服务
            logger.warning("API key 解密失败（%s），回退明文变量", e)
            # 继续走明文回退

    return os.getenv(plain_var)


def get_deepseek_api_key() -> str | None:
    """读取 DeepSeek API key：优先解密一次缓存，兼容明文。"""
    return get_api_key()
