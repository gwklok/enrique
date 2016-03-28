import os
import shutil
from urlparse import urlparse
from hashlib import sha1

from plumbum.cmd import git, tar, wget, pip


def mkdir_p(path):
    path = os.path.abspath(os.path.expanduser(path))
    if not os.path.exists(path):
        os.makedirs(path)
    return path

ENRIQUE_DIR = mkdir_p("~/.mesos-magellan/enrique")
PACKAGES_DIR = mkdir_p(os.path.join(ENRIQUE_DIR, "packages"))


def get_package_cls(url):
    package_cls = None
    url_parsed = urlparse(url)
    if url_parsed.scheme == "git":
        package_cls = GitRepo
    elif url_parsed.scheme in ["http", "https"]:
        if url.endswith("tar.gz"):
            package_cls = GzipArchive
        if url.endswith(".git"):
            package_cls = GitRepo

    if package_cls is None:
        raise ValueError

    return package_cls


def get_name_from_url(url):
    return sha1(url).hexdigest()


def get_package(url):
    package_cls = get_package_cls(url)
    name = get_name_from_url(url)
    package = package_cls(name, url)
    package.fetch()
    package.setup()
    return package


class Package(object):
    def __init__(self, name, url):
        self.name = name
        self.url = url
        self._problem_path = None
        mkdir_p(self.package_path)

    def fetch(self):
        raise NotImplementedError

    def remove(self):
        shutil.rmtree(self.package_path)

    def setup(self):
        reqs_txt_path = os.path.join(self.problem_path, "requirements.txt")
        if os.path.exists(reqs_txt_path):
            install_reqs = pip['install', '--user', '-r', reqs_txt_path]
            install_reqs()

    @property
    def problem_path(self):
        return self._problem_path

    @property
    def package_path(self):
        package_home = os.path.join(PACKAGES_DIR, self.name)
        return package_home

    def download_http(self):
        localfile_path = self._download_file(self.url, self.package_path)
        return localfile_path

    @staticmethod
    def _download_file(url, download_path):
        """Download file from url"""
        local_filename = os.path.join(download_path, url.split('/')[-1])
        if os.path.exists(local_filename):
            os.remove(local_filename)
        wget_dl = wget['-P', download_path, url]
        wget_dl()
        assert os.path.exists(local_filename)
        return local_filename


class Archive(Package):
    def _extract_package(self, localfile_path):
        raise NotImplementedError

    def fetch(self):
        localfile_path = self.download_http()
        problem_path = self._extract_package(localfile_path)
        self._problem_path = problem_path


class GzipArchive(Archive):
    def _extract_package(self, localfile_path):
        archive_path = localfile_path
        dirname = os.path.split(localfile_path)[-1].split(".tar.gz")[0]
        target_dir = os.path.join(self.package_path, dirname)
        if os.path.exists(target_dir):
            shutil.rmtree(target_dir)
        os.makedirs(target_dir)
        untar = tar['-xzf', archive_path, '-C', target_dir]
        untar()

        extracted_list = os.listdir(target_dir)
        if len(extracted_list) == 1:
            item = os.path.join(target_dir, extracted_list[0])
            if os.path.isdir(item):
                # This is a single extracted directory so we help the
                #  user out and go inside it and return that for the
                #  problem_path
                return item

        return target_dir


class GitRepo(Package):
    def fetch(self):
        url = self.get_https_dl_url()
        local_dirname = os.path.join(self.package_path,
                                     url.split('/')[-1].split('.git')[0])
        if not os.path.exists(local_dirname):
            clone = git['clone', url, local_dirname]
            clone()
        else:
            # If repo exists, pull instead of cloning
            pull = git['-C', local_dirname, 'pull']
            pull()
        self._problem_path = local_dirname

    def get_https_dl_url(self):
        url_parsed = urlparse(self.url)
        if url_parsed.scheme == "git":
            url = self.url.replace('git', 'https', 1)
        elif url_parsed.scheme == "https" and self.url.endswith(".git"):
            url = self.url
        else:
            raise ValueError
        return url
