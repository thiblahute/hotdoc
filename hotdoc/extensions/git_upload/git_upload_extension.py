# -*- coding: utf-8 -*-
#
# Copyright © 2017 Thibault Saunier <tsaunier@gnome.org>
#
# This library is free software; you can redistribute it and/or modify it under
# the terms of the GNU Lesser General Public License as published by the Free
# Software Foundation; either version 2.1 of the License, or (at your option)
# any later version.
#
# This library is distributed in the hope that it will be useful, but WITHOUT
# ANY WARRANTY; without even the implied warranty of MERCHANTABILITY or FITNESS
# FOR A PARTICULAR PURPOSE.  See the GNU Lesser General Public License for more
# details.
#
# You should have received a copy of the GNU Lesser General Public License
# along with this library.  If not, see <http://www.gnu.org/licenses/>.

"""GitUploadExtension"""

import os
import shutil
import subprocess
from subprocess import check_output as call

from hotdoc.utils.utils import recursive_overwrite
from hotdoc.core.extension import Extension
from hotdoc.core.exceptions import HotdocException
from hotdoc.utils.loggable import Logger, warn

Logger.register_warning_code('no-local-repository', HotdocException,
                             domain='git-uploader')
Logger.register_warning_code('dirty-local-repository', HotdocException,
                             domain='git-uploader')

DESCRIPTION =\
    """
An extension to upload the result of a hotdoc build
to git a repository.

It can be used to upload to github pages for example.
"""


class GitUploadExtension(Extension):
    """Extension to upload generated doc to a git repository"""
    extension_name = 'git-upload'
    argument_prefix = 'git-upload'

    activated = False

    def __init__(self, app, project):
        self.__local_repo = None
        self.__remote_branch = None
        self.__commit_message = None
        self.__copy_only = False
        self.__repository = None
        self.__activate = False
        Extension.__init__(self, app, project)

    def setup(self):
        super(GitUploadExtension, self).setup()
        self.app.formatted_signal.connect_after(self.__formatted_cb)

    def __formatted_cb(self, app):
        repo = self.__local_repo
        if not repo:
            if not self.__repository or not self.__activate:
                return

            repo = os.path.join(self.app.private_folder, 'git-upload-repo')
            try:
                call(['git', 'rev-parse', '--show-toplevel'], cwd=repo,
                     stderr=subprocess.STDOUT)
            except (subprocess.CalledProcessError, FileNotFoundError):
                print("Cloning %s" % self.__repository)
                subprocess.check_call(['git', 'clone', self.__repository,
                                       repo])

        try:
            call(['git', 'rev-parse', '--show-toplevel'], cwd=repo,
                 stderr=subprocess.STDOUT)
        except subprocess.CalledProcessError as exception:
            warn('no-local-repository',
                 "Specified local repository %s does not exist, "
                 "not uploading. (%s)" % (repo, str(exception)))

        if subprocess.call(['git', 'diff-index', '--quiet', 'HEAD'],
                           cwd=repo) != 0:
            warn('dirty-local-repository',
                 "Specified local repository %s is dirty, not uploading."
                 % (repo))
            return

        html_path = os.path.join(app.output, "html/")
        print("Uploading %s to %s!" % (html_path, repo))
        print("Removing previous assets %s" % os.path.join(repo, "assets/"))
        shutil.rmtree(os.path.join(repo, "assets/"), ignore_errors=True)

        print("Removing previous html files")
        # pylint: disable=unused-variable
        for root, subdirs, files in os.walk(repo):
            for filename in files:
                if filename.endswith('.html'):
                    os.remove(os.path.join(root, filename))

        print("Copying newly built files")
        for filename in os.listdir(html_path):
            built_f = os.path.join(html_path, filename)
            copy_dest = os.path.join(repo, filename)

            recursive_overwrite(built_f, copy_dest)

            call(['git', 'add', copy_dest], cwd=repo)

        if self.__copy_only:
            return

        if subprocess.call(['git', 'diff-index', '--quiet', 'HEAD'],
                           cwd=repo) == 0:
            print("No changes to push")
            return

        print("Committing %s" % self.__commit_message)
        subprocess.check_call(['git', 'commit', '-a', '-m',
                               self.__commit_message], cwd=repo)

        print("Pushing to %s" % '/'.join(self.__remote_branch))
        subprocess.check_call(['git', 'push'] + self.__remote_branch, cwd=repo)

    @staticmethod
    def add_arguments(parser):
        group = parser.add_argument_group('Git upload extension',
                                          DESCRIPTION)
        group.add_argument(
            '--git-upload-local-repo',
            help="Local repository to use to upload.\n"
                 "It can contain the path in which the html files reside.\n"
                 "Specifying it activates the upload.\n"
                 "NOTE: It should most probably never be in the config file."
                 " - html files from that directory will be deleted and only.",
            default=None)
        group.add_argument(
            '--git-upload-repository',
            help="Git repository to upload to.\n Will be used only if "
            "--git-upload-local-repo is not available.\n", default=None)
        group.add_argument('--git-upload-remote-branch',
                           help="Remove/branch to push the update to",
                           default="origin/master")
        group.add_argument('--git-upload-commit-message',
                           help="Commit message to use for the update.",
                           default="Update")
        group.add_argument('--git-upload-copy-only',
                           action='store_true',
                           help="Only copy files, without committing or "
                           "uploading.")
        group.add_argument(
            '--git-upload',
            action='store_true',
            help="Make the upload happen. \n"
            "NOTE: It should most probably never be in the config file.")

    def parse_toplevel_config(self, config):
        super().parse_toplevel_config(config)
        self.__local_repo = config.get('git_upload_local_repo')
        self.__remote_branch = config.get(
            'git_upload_remote_branch', '').split('/', 1)
        self.__commit_message = config.get('git_upload_commit_message')
        self.__copy_only = config.get('git_upload_copy_only')
        self.__repository = config.get('git_upload_repository')
        self.__activate = config.get('git_upload')


def get_extension_classes():
    """Nothing important, really"""
    return [GitUploadExtension]
