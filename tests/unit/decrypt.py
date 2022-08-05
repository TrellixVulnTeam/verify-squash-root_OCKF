import unittest
from pathlib import Path
from unittest import mock
from unittest.mock import call
from verify_squash_root.decrypt import format_cmd, TAR_FILE, KEY_DIR, \
    decrypt_secure_boot_keys, DecryptKeys
from .test_helper import wrap_tempdir, get_test_files_path

MOCK_BASE = "verify_squash_root.decrypt"


class DecryptTest(unittest.TestCase):

    def test__format_cmd(self):
        self.assertEqual(format_cmd("\nage -d -o {}\n/etc/keys.tar.age",
                                    "/tmp/keys.tar"),
                         ["age", "-d", "-o", "/tmp/keys.tar",
                          "/etc/keys.tar.age"])

    @wrap_tempdir
    def test__decrypt_secure_boot_keys__mock(self, tempdir):
        key_dir = tempdir / "keys"
        all_mocks = mock.MagicMock()
        with (mock.patch("{}.exec_binary".format(MOCK_BASE),
                         new=all_mocks.exec_binary),
              mock.patch("{}.KEY_DIR".format(MOCK_BASE),
                         new=key_dir),
              mock.patch("{}.tarfile".format(MOCK_BASE),
                         new=all_mocks.tarfile)):
            config = {
                "DEFAULT": {
                    "DECRYPT_SECURE_BOOT_KEYS_CMD": "cp /root/keys.tar {}",
                }
            }
            self.assertEqual(key_dir.is_dir(), False)
            decrypt_secure_boot_keys(config)
            self.assertEqual(
                all_mocks.mock_calls,
                [call.exec_binary(["cp", "/root/keys.tar", str(TAR_FILE)]),
                 call.tarfile.open(TAR_FILE),
                 call.tarfile.open().__enter__(),
                 call.tarfile.open().__enter__().extractall(key_dir),
                 call.tarfile.open().__exit__(None, None, None)])
            self.assertEqual(key_dir.is_dir(), True)

    @wrap_tempdir
    def test__decrypt_secure_boot_keys__filesystem(self, tempdir):
        key_dir = tempdir / "keys"
        tarpath = get_test_files_path("decrypt") / "keys.tar"
        config = {
            "DEFAULT": {
                "DECRYPT_SECURE_BOOT_KEYS_CMD": "cp {} {{}}".format(tarpath),
            }
        }
        self.assertEqual(TAR_FILE,
                         Path("/tmp/verify_squash_root/keys/keys.tar"))
        self.assertEqual(key_dir.is_dir(), False)
        with (mock.patch("{}.TAR_FILE".format(MOCK_BASE),
                         new=key_dir / "keys.tar"),
              mock.patch("{}.KEY_DIR".format(MOCK_BASE),
                         new=key_dir)):
            decrypt_secure_boot_keys(config)
        self.assertEqual(key_dir.is_dir(), True)
        key = (b"Secret DB Key\ntest file\n"
               b"From tar file\nIn Love\n - Maintainer\n")
        self.assertEqual(
            (key_dir / "db.key").read_bytes(), key)
        self.assertEqual(
            (key_dir / "db.crt").read_bytes(),
            b"The DB cert file\nextracted\n")

    def test__decrypt_keys(self):
        all_mocks = mock.Mock()
        config = mock.Mock()
        with (mock.patch("{}.decrypt_secure_boot_keys".format(MOCK_BASE),
                         new=all_mocks.decrypt_secure_boot_keys),
              mock.patch("{}.shutil".format(MOCK_BASE),
                         new=all_mocks.shutil)):
            with DecryptKeys(config):
                all_mocks.inner_func()
            self.assertEqual(
                all_mocks.mock_calls,
                [call.decrypt_secure_boot_keys(config),
                 call.inner_func(),
                 call.shutil.rmtree(KEY_DIR)])
