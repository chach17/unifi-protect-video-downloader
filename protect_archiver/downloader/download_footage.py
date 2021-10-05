import logging
import os
import time
from datetime import datetime
from os import path

from protect_archiver.dataclasses import Camera
from protect_archiver.downloader import download_file
from protect_archiver.utils import calculate_intervals, make_camera_name_fs_safe


def download_footage(client, start: datetime, end: datetime, camera: Camera):
	# make camera name safe for use in file name
	camera_name_fs_safe = make_camera_name_fs_safe(camera)

	logging.info(f"Downloading footage for camera '{camera.name}' ({camera.id})")

	# start and end time of the video segment to be downloaded
	js_timestamp_range_start = int(start.timestamp()) * 1000
	js_timestamp_range_end = int(end.timestamp()) * 1000

	# file path for download
	if bool(client.use_subfolders):
		folder_year = start.strftime("%Y")
		folder_month = start.strftime("%m")
		folder_day = start.strftime("%d")

		dir_by_date_and_name = (
			f"{folder_year}/{folder_month}/{folder_day}/{camera_name_fs_safe}"
		)
		target_with_date_and_name = (
			f"{client.destination_path}/{dir_by_date_and_name}"
		)

		download_dir = target_with_date_and_name
		if not os.path.isdir(target_with_date_and_name):
			os.makedirs(target_with_date_and_name, exist_ok=True)
			logging.info(f"Created path {target_with_date_and_name}")
			download_dir = target_with_date_and_name
	else:
		download_dir = client.destination_path

	# file name for download
	filename_timestamp = start.strftime("%Y-%m-%d_%H.%M.%S%z")
	filename = f"{download_dir}/{camera_name_fs_safe}_{filename_timestamp}.mp4"

	logging.info(
		f"Downloading video for time range {start} - {end} to {filename}"
	)

	# create file without content if argument --touch-files is present
	# XXX(dcramer): would be nice to document why you'd ever want this
	if bool(client.touch_files) and not path.exists(filename):
		logging.debug(
			f"Argument '--touch-files' is present. Creating file at {filename}"
		)
		open(filename, "a").close()

	# build video export query
	video_export_query = f"/video/export?camera={camera.id}&start={js_timestamp_range_start}&end={js_timestamp_range_end}"

	# download the file
	download_file(client, video_export_query, filename)
