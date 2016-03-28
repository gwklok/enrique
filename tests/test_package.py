import os

from enrique.package import get_package_cls
from enrique.package import GitRepo
from enrique.package import GzipArchive
from enrique.package import mkdir_p
from enrique.package import ENRIQUE_DIR, PACKAGES_DIR


def test__get_package_cls():
    assert get_package_cls(
        "foo_tar",
        "https://foo.bar/baz.tar.gz"
    ) == GzipArchive
    assert get_package_cls(
        "foo_git",
        "git://github.com/mesos-magellan/traveling-sailor"
    ) == GitRepo


def test__mkdir_p():
    mkdir_p(ENRIQUE_DIR)
    assert os.path.exists(ENRIQUE_DIR)
    mkdir_p(ENRIQUE_DIR)
