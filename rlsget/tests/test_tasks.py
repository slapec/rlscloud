# coding: utf-8

from unittest.mock import patch

from django.conf import settings
from django.contrib.auth.models import User
from django.core.exceptions import ObjectDoesNotExist
from django.test import TestCase

from rlsget.models import DownloadTask
from rlsget.tasks import youtube_dl


class TestYoutubeDLTask(TestCase):
    def setUp(self):
        settings.CELERY_ALWAYS_EAGER = True
        settings.CELERY_EAGER_PROPAGATES_EXCEPTIONS = True
        self.user = User.objects.create(username='test_user')
        self.download_task = DownloadTask.objects.create(url='some_url', created_by=self.user)

    @patch('rlsget.tasks.log')
    def test_database_exception(self, mock_log):
        self.assertRaises(ObjectDoesNotExist, lambda: youtube_dl.apply_async([0]))
        mock_log.exception.assert_called_with('Exception while updating DownloadTask. id=0')

    @patch('os.remove')
    @patch('copy.deepcopy')  # It doesn't matter which object is mocked in the try ... block
    def test_task_cancellation_attr_error(self, mock_deepcopy, mock_remove):
        mock_deepcopy.side_effect = SystemExit()
        youtube_dl.apply_async([self.download_task.id])
        mock_remove.assert_not_called()

    @patch('os.remove')
    @patch('copy.deepcopy')  # It doesn't matter which object is mocked in the try ... block
    def test_task_cancellation_success(self, mock_deepcopy, mock_remove):
        mock_deepcopy.side_effect = SystemExit()
        youtube_dl._last_status = {
            'tmpfilename': 'some_tmpfilename'
        }
        youtube_dl(self.download_task.id)
        del youtube_dl._last_status
        mock_remove.assert_called_with('some_tmpfilename')

    @patch('rlsget.tasks.log')
    @patch('os.remove')
    @patch('copy.deepcopy')  # It doesn't matter which object is mocked in the try ... block
    def test_task_cancellation_other_exception(self, mock_deepcopy, mock_remove, mock_log):
        mock_deepcopy.side_effect = SystemExit()
        mock_remove.side_effect = ValueError()
        youtube_dl._last_status = {
            'tmpfilename': 'some_tmpfilename'
        }

        self.assertRaises(ValueError, lambda: youtube_dl(self.download_task.id))
        del youtube_dl._last_status

        mock_log.exception.assert_called_with('Exception while removing temporary file.'
                                              ' id=1, tempfilename=some_tmpfilename')

    @patch('rlsget.tasks.log')
    @patch('rlsget.tasks.YoutubeDL.download')
    def test_task_other_exception(self, mock_download, mock_log):
        mock_download.side_effect = ValueError()

        self.assertRaises(ValueError, lambda: youtube_dl.apply_async([self.download_task.id]))
        self.assertEqual(self.download_task.tracebacks.count(), 1)
