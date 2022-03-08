# This Source Code Form is subject to the terms of the Mozilla Public License, v. 2.0.
# If a copy of the MPL was not distributed with this file,
# You can obtain one at http://mozilla.org/MPL/2.0/.
import glob
import os
import subprocess
import sys
from subprocess import PIPE, Popen

import sublime
import sublime_plugin

PROJECT_NAME = "phpcsfixer-Formatter"
SETTINGS_FILE = PROJECT_NAME + ".sublime-settings"
PLATFORM = sublime.platform()
ARCHITECTURE = sublime.arch()
KEYMAP_FILE = "Default (" + PLATFORM + ").sublime-keymap"
IS_WINDOWS = PLATFORM == "windows"


class FormatPhpcsfixerCommand(sublime_plugin.TextCommand):
	def run(self, edit):
		# Save the current viewport position to scroll to it after formatting.
		previous_selection = list(self.view.sel())  # Copy.
		previous_position = self.view.viewport_position()

		# Save the already folded code to refold it after formatting.
		# Backup of folded code is taken instead of regions because the start and end pos
		# of folded regions will change once formatted.
		folded_regions_content = [self.view.substr(region) for region in self.view.folded_regions()]

		# Get the current text in the buffer and save it in a temporary file.
		# This allows for scratch buffers and dirty files to be linted as well.
		# entire_buffer_region = sublime.Region(0, self.view.size()) # NOT USED

		[stdout, stderr] = self.run_script_on_file(filename=self.view.file_name())

		# log output in debug mode
		if PluginUtils.get_pref(["debug"], self.view):
			print(f">>> stderr:\n{stderr}>>> stdout:\n{stdout}")

		self.refold_folded_regions(folded_regions_content, stdout)
		self.view.set_viewport_position((0, 0), False)
		self.view.set_viewport_position(previous_position, False)
		self.view.sel().clear()

		# Restore the previous selection if formatting wasn't performed only for it.
		# if not is_formatting_selection_only:
		for region in previous_selection:
			self.view.sel().add(region)

	def get_lint_directory(self, filename):
		project_path = PluginUtils.project_path(None)

		if project_path is not None:
			return PluginUtils.normalize_path(project_path)

		if filename is not None:
			cdir = os.path.dirname(filename)

			if os.path.exists(cdir):
				return cdir

		return os.getcwd()

	def run_script_on_file(self, filename=None):
		try:
			dirname = filename and os.path.dirname(filename)
			php_path = PluginUtils.get_php_path(self.view)
			phpcsfixer_path = PluginUtils.get_phpcsfixer_path(dirname, self.view)

			if phpcsfixer_path is False:
				sublime.error_message("phpcsfixer could not be found on your path")
				return

			if filename is None:
				sublime.error_message("Cannot lint unsaved file")

			# Better support globally-available phpcsfixer binaries that don't need to be invoked with php.
			php_cmd = [php_path] if php_path else []
			cmd = php_cmd + [phpcsfixer_path, "fix", filename]

			project_path = PluginUtils.project_path()
			config_path = PluginUtils.get_pref(["config_path"], self.view)
			config_path = sublime.expand_variables(config_path, sublime.active_window().extract_variables())
			extra_args = PluginUtils.get_pref(["extra_args"], self.view)

			if os.path.isfile(config_path):
				# If config file path exists, use as is
				full_config_path = config_path
			else:
				# Find config file relative to project path
				full_config_path = os.path.join(project_path, ".php-cs-fixer.dist.php")

			if os.path.isfile(full_config_path):
				cmd.extend([f"--config={full_config_path}"])
				print(f">>> Using configuration from {full_config_path}")

			if extra_args:
				cmd += [arg.replace("$project_path", project_path) for arg in extra_args]

			if PluginUtils.get_pref(["debug"], self.view):
				cmd = [arg for arg in cmd if arg not in ["-q", "--quiet"]]
				cmd += ["-vvv"]
				print(">>> phpcsfixer command line", cmd)
			else:
				cmd = [arg for arg in cmd if arg not in ["-v", "-vv", "-vvv", "--verbose"]]
				cmd += ["-q"]

			cdir = self.get_lint_directory(filename)

			[stdout, stderr] = PluginUtils.get_output(cmd, cdir)

			return [stdout, stderr]

		except:
			# Something bad happened.
			msg = str(sys.exc_info()[1])
			print(f"Unexpected error({sys.exc_info()[0]}): {msg}")
			sublime.error_message(msg)

	def refold_folded_regions(self, folded_regions_content, entire_file_contents):
		self.view.unfold(sublime.Region(0, len(entire_file_contents)))
		region_end = 0

		for content in folded_regions_content:
			region_start = entire_file_contents.index(content, region_end)
			if region_start > -1:
				region_end = region_start + len(content)
				self.view.fold(sublime.Region(region_start, region_end))


class PhpcsfixerFormatterEventListeners(sublime_plugin.EventListener):
	@staticmethod
	def should_run_command(view):
		if not PluginUtils.get_pref(["format_on_save"], view):
			return False

		extensions = PluginUtils.get_pref(["format_on_save_extensions"], view)
		extension = os.path.splitext(view.file_name())[1][1:]

		# Default to using filename if no extension
		if not extension:
			extension = os.path.basename(view.file_name())

		# Skip if extension is not listed
		return not extensions or extension in extensions

	@staticmethod
	def on_post_save(view):
		if PhpcsfixerFormatterEventListeners.should_run_command(view):
			view.run_command("format_phpcsfixer")


class PluginUtils:
	@staticmethod
	# Fetches root path of open project
	def project_path(fallback=os.getcwd()):
		project_data = sublime.active_window().project_data()

		# if cannot find project data, use cwd
		if project_data is None:
			return fallback

		folders = project_data["folders"]
		folder_path = folders[0]["path"]

		if folder_path == ".":
			folder_path = sublime.active_window().folders()[0]

		return folder_path

	@staticmethod
	def get_pref(key_list, view=None):
		if view is not None:
			settings = view.settings()

			# Flat settings in .sublime-project
			flat_keys = ".".join(key_list)
			if settings.has(f"{PROJECT_NAME}.{flat_keys}"):
				value = settings.get(f"{PROJECT_NAME}.{flat_keys}")
				return value

			# Nested settings in .sublime-project
			if settings.has(PROJECT_NAME):
				value = settings.get(PROJECT_NAME)

				for key in key_list:
					try:
						value = value[key]
					except:
						value = None
						break

				if value is not None:
					return value

		global_settings = sublime.load_settings(SETTINGS_FILE)
		value = global_settings.get(key_list[0])

		# Load active project settings
		project_settings = sublime.active_window().active_view().settings()

		# Overwrite global config value if it's defined
		if project_settings.has(PROJECT_NAME):
			value = project_settings.get(PROJECT_NAME).get(key_list[0], value)

		return value

	@staticmethod
	def get_php_path(view=None):
		platform = sublime.platform()

		# .sublime-project
		php = PluginUtils.get_pref(["php_path", platform], view)

		# .sublime-settings
		php = php.get(platform) if isinstance(php, dict) else php

		if isinstance(php, str):
			print(f">>> Using php path on '{platform}': {php}")
		else:
			print("Not using explicit php path")

		return php

	# Convert path that possibly contains a user tilde and/or is a relative path into an absolute path.
	@staticmethod
	def normalize_path(path, realpath=False):
		if realpath:
			return os.path.realpath(os.path.expanduser(path))
		else:
			project_dir = sublime.active_window().project_file_name()
			cwd = os.path.dirname(project_dir) if project_dir else os.getcwd()
			return os.path.normpath(os.path.join(cwd, os.path.expanduser(path)))

	# Yield path and every directory above path.
	@staticmethod
	def walk_up(path):
		curr_path = path
		while 1:
			yield curr_path
			curr_path, tail = os.path.split(curr_path)
			if not tail:
				break

	# Find the first path matching a given pattern within dirname or the nearest ancestor of dirname.
	@staticmethod
	def findup(pattern, dirname=None):
		if dirname is None:
			project_path = PluginUtils.project_path()
			normalized_directory = PluginUtils.normalize_path(project_path)
		else:
			normalized_directory = PluginUtils.normalize_path(dirname)

		for directory in PluginUtils.walk_up(normalized_directory):
			matches = glob.glob(os.path.join(directory, pattern))
			if matches:
				return matches[0]

		return None

	@staticmethod
	def get_local_phpcsfixer(dirname, view=None):
		pkg = PluginUtils.findup("vendor/php-cs-fixer", dirname)
		if pkg is None:
			return None
		else:
			platform = sublime.platform()

			# .sublime-project
			path = PluginUtils.get_pref(["local_phpcsfixer_path", platform], view)

			# .sublime-settings
			path = path.get(platform) if isinstance(path, dict) else path

			if not path:
				return None

			directory = os.path.dirname(os.path.dirname(pkg))
			local_phpcsfixer_path = os.path.join(directory, path)

			if os.path.isfile(local_phpcsfixer_path):
				return local_phpcsfixer_path
			else:
				return None

	@staticmethod
	def get_phpcsfixer_path(dirname, view=None):
		platform = sublime.platform()
		phpcsfixer = dirname and PluginUtils.get_local_phpcsfixer(dirname, view)

		# if local phpcsfixer not available, then using the settings config
		if phpcsfixer is None:
			# .sublime-project
			phpcsfixer = PluginUtils.get_pref(["phpcsfixer_path", platform], view)

			# .sublime-settings
			phpcsfixer = phpcsfixer.get(platform) if isinstance(phpcsfixer, dict) else phpcsfixer

		print(f">>> Using phpcsfixer path on '{platform}': {phpcsfixer}")
		return phpcsfixer

	@staticmethod
	def get_output(cmd, cdir):
		try:
			info = None
			if os.name == "nt":
				info = subprocess.STARTUPINFO()
				info.dwFlags |= subprocess.STARTF_USESHOWWINDOW
				info.wShowWindow = subprocess.SW_HIDE

			process = Popen(cmd, stdout=PIPE, stdin=PIPE, stderr=PIPE, startupinfo=info, cwd=cdir, shell=IS_WINDOWS)
		except OSError:
			raise Exception("Couldn't find php. Make sure it's in your $PATH by running `php -v` in your command-line.")

		stdout, stderr = process.communicate()
		stdout = stdout.decode("utf-8")
		stderr = stderr.decode("utf-8")

		if process.returncode == 127:
			raise Exception(f">>> stderr:\n{stderr}>>> stdout:\n{stdout}")
		else:
			return [stdout, stderr]
