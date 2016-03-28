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
    assert get_package_cls(
        "foo_https_git",
        "https://github.com/mesos-magellan/traveling-sailor.git"
    ) == GitRepo


def test__mkdir_p():
    mkdir_p(ENRIQUE_DIR)
    assert os.path.exists(ENRIQUE_DIR)
    mkdir_p(ENRIQUE_DIR)


def test__GitRepo():
    package_name = "__ENRIQUE_TEST_TS_.GIT"
    package = GitRepo(package_name,
                      "https://github.com/mesos-magellan/traveling-sailor.git")
    assert package.get_https_dl_url() == \
           "https://github.com/mesos-magellan/traveling-sailor.git"
    assert package.package_path == os.path.join(PACKAGES_DIR, package_name)
    assert os.path.exists(package.package_path)
    package.remove()
    assert not os.path.exists(package.package_path)

    package = GitRepo(package_name,
                      "git://github.com/mesos-magellan/traveling-sailor")
    assert package.get_https_dl_url() == \
           "https://github.com/mesos-magellan/traveling-sailor"
    package.fetch()  # clone
    assert os.path.exists(os.path.join(package.problem_path, ".git"))
    package.fetch()  # pull
    assert os.path.exists(os.path.join(package.problem_path, ".git"))
    package.remove()
