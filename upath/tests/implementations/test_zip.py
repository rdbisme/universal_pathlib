from zipfile import ZipFile

import pytest  # noqa: F401

from upath import UPath

from ..cases import BaseTests


class TestUPathZip(BaseTests):
    @pytest.fixture(autouse=True, scope="function")
    def path(self, zip_fixture):
        self.path = UPath(f"zip://{zip_fixture}")

    def test_stat(self):
        # self.path.stat() doesn't make sense?
        assert (self.path / "file1.txt").stat()

    def test_is_dir(self):
        # self.path.is_dir() doesn't make sense?
        assert (self.path / "folder1").is_dir()

    def test_is_file(self):
        path = self.path / "file1.txt"
        assert path.is_file()
        # assert not self.path.is_file()

        assert not (self.path / "not-existing-file.txt").is_file()

    def test_zip_in_zip(self, tmp_path):
        filename = tmp_path / "test.zip"
        with ZipFile(filename, "w") as zip_file:
            zip_file.writestr("A.zip", "Content")

        new_path = UPath(f"zip://{filename}")

        nested_zip = new_path / "A.zip"

        assert nested_zip.read_text() == "Content"

    def test_double_extension(self, tmp_path):
        filename = tmp_path / "test.zip.zip"
        with ZipFile(filename, "w") as zip_file:
            zip_file.writestr("A.zip", "Content")

        new_path = UPath(f"zip://{filename}")

        nested_zip = new_path / "A.zip"

        assert nested_zip.read_text() == "Content"

    @pytest.mark.xfail(
        reason="Current fsspec ZipFileSystem implementation is read only"
    )
    def test_mkdir(self):
        super().test_mkdir()

    @pytest.mark.xfail(
        reason="Current fsspec ZipFileSystem implementation is read only"
    )
    def test_mkdir_exists_ok_true(self):
        super().test_mkdir_exists_ok_true()

    @pytest.mark.xfail(
        reason="Current fsspec ZipFileSystem implementation is read only"
    )
    def test_mkdir_exists_ok_false(self):
        super().test_mkdir_exists_ok_false()

    @pytest.mark.xfail(
        reason="Current fsspec ZipFileSystem implementation is read only"
    )
    def test_touch_unlink(self):
        super().test_touch_unlink()

    @pytest.mark.xfail(
        reason="Current fsspec ZipFileSystem implementation is read only"
    )
    def test_write_bytes(self, pathlib_base):
        return super().test_write_bytes(pathlib_base)

    @pytest.mark.xfail(
        reason="Current fsspec ZipFileSystem implementation is read only"
    )
    def test_write_text(self, pathlib_base):
        return super().test_write_text(pathlib_base)

    @pytest.mark.xfail(
        reason="Current fsspec ZipFileSystem implementation is read only"
    )
    def test_fsspec_compat(self):
        return super().test_fsspec_compat()
