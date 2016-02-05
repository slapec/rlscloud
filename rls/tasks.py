# coding: utf-8

import os
from datetime import timedelta
from io import BytesIO
from subprocess import check_output

from django.conf import settings
from PIL import Image

from rlscloud import app


class CreateThumbnailTask(app.Task):
    def get_duration(self, path):
        return float(check_output(['ffprobe', '-i', path, '-show_entries', 'format=duration', '-v', 'quiet', '-of', 'csv=p=0']))

    def get_filter(self):
        width, height = settings.THUMBNAIL_SIZE
        return "scale='if(gt(a,4/3),{width},-1)':'if(gt(a,4/3),-1,{height})'".format(width=width, height=height)

    def create_strip(self, release, count: int) -> Image:
        # Setting up the canvas ------------------------------------------------
        width, height = settings.THUMBNAIL_SIZE
        strip_width = width * settings.THUMBNAIL_COUNT
        strip = Image.new('RGB', (strip_width, height))

        # Creating thumbnails --------------------------------------------------
        release_path = release.file.path
        duration = self.get_duration(release_path)

        sampling = duration / (count + 1)
        for i in range(count):
            time_code = str(timedelta(seconds=i*sampling))
            thumbnail_bytes = check_output(['ffmpeg',
                                            '-ss', time_code,
                                            '-i', release_path,
                                            '-vframes', '1',
                                            '-vf', self.get_filter(),
                                            '-v', 'quiet',
                                            '-f', 'mjpeg',
                                            '-'])

            thumbnail = Image.open(BytesIO(thumbnail_bytes))
            thumb_width, thumb_height = thumbnail.size

            strip.paste(thumbnail, (int(thumb_width*i), int((height-thumb_height) / 2)))

        return strip

    def run(self, release_id: int, count=settings.THUMBNAIL_COUNT):
        from rls.models import Release

        release = Release.objects.get(pk=release_id)
        strip = self.create_strip(release, count)

        media_destination = os.path.join(settings.THUMBNAILS_DIR, '{0}.jpg'.format(release.file_hash))
        absolute_destination = os.path.join(settings.MEDIA_ROOT, media_destination)
        strip.save(absolute_destination)

        release.thumbnail = media_destination
        release.save()


create_thumbnails = CreateThumbnailTask()
