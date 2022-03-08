# phpcsfixer Formatter for Sublime Text

*Please note the plugin hasn't been submitted to [packagecontrol.io](https://packagecontrol.io/). Thus has to be installed manually.*

<br>

### Installation

#### Installing plugin

- `Package Control: Add Repository` Method (Recommended)
	1. Open `Command Palette` (Default: `Primary + Shift + p`)
	2. `Package Control: Add Repository`
	3. `https://raw.githubusercontent.com/LetsZiggy/phpcsfixer-Formatter/main/repository-package.json`
	4. Open `Command Palette`
	5. `Package Control: Install Package`
	6. `phpcsfixer-Formatter`
- "Manual" Method (Requires manual update)
	1. Download this repository through `Download ZIP`
	2. Rename folder to `phpcsfixer-Formatter`
	3. Move folder to `[SublimeText]/Packages` folder
		- To access `[SublimeText]/Packages` folder:
			1. Open/Restart `Sublime Text`
			2. Open the `Command Palette` (Default: `Primary + Shift + p`)
			3. `Preferences: Browse Packages`
	4. Restart `Sublime Text`

---

### Usage

Save file to run PHP-CS-Fixer.

phpcsfixer Formatter can only format on saved files as PHP-CS-Fixer do not output its result to stdout. phpcsfixer Formatter is disabled by default. Set `format_on_save: true` to enable phpcsfixer Formatter (see [Settings > format_on_save](#user-content-default-settings)).

---

### Configuring Settings

#### To access and modify settings file

Go to `Preferences -> Package Settings -> phpcsfixer-Formatter -> Settings`

#### To override settings per project basis

To override global plugin configuration for a specific project, add a settings object with a `phpcsfixer-Formatter` key in your `.sublime-project`. This file is accessible via `Project -> Edit Project`.

```javascript
/* EXAMPLE */
{
  "folders": [
    {
      "path": ".",
    },
  ],
  "settings": {
    "phpcsfixer-Formatter": {
      "format_on_save": true,
    },
  },
}
```

#### Default settings

```javascript
{
  // Simply using `php` without specifying a path sometimes doesn't work :(
  // https://www.php.net/manual/en/install.php
  // If these are false, we'll invoke the phpcsfixer binary directly.
  "php_path": {
    "windows": "php.exe",
    "linux": "/usr/bin/php",
    "osx": "/usr/local/bin/php",
  },

  // The location to search for a locally installed phpcsfixer package
  // These are all relative paths to a project's directory
  // If this is not found or are false, it will try to fallback to a global package
  // (see "phpcsfixer_path" below)
  "local_phpcsfixer_path": {
    "windows": "vendor/bin/php-cs-fixer",
    "linux": "vendor/bin/php-cs-fixer",
    "osx": "vendor/bin/php-cs-fixer",
  },

  // The location of the globally installed phpcsfixer package to use as a fallback
  "phpcsfixer_path": {
    "windows": "%APPDATA%/Roaming/Composer/vendor/bin/php-cs-fixer",
    "linux": "~/.composer/vendor/bin/php-cs-fixer",
    "osx": "~/.composer/vendor/bin/php-cs-fixer",
  },

  // Specify this path to an phpcsfixer config file to override the default behavior
  // Passed to phpcsfixer as --config. Read more here:
  // https://cs.symfony.com/doc/config.html
  // If an absolute path is provided, it will use as is.
  // Else, it will look for ".php-cs-fixer.dist.php" in the root of the project directory.
  // Failing either, it will skip the config file
  "config_path": "",

  // Pass additional arguments to phpcsfixer.
  // Read more here: https://cs.symfony.com/doc/usage.html
  // Please note that "-v | -vv | -vvv | --verbose | -q | --quiet" args will be edited (see `debug` below)
  "extra_args": [
    "--path-mode=override",
    "--no-interaction",
  ],

  // Automatically format when a file is saved
  "format_on_save": false,

  // Only attempt to format files with whitelisted extensions on save.
  // Leave empty to disable the check
  "format_on_save_extensions": [ "php" ],

  // Logs phpcsfixer output messages to console when set to true
  // `extra_args` will be edited as below if `debug` set to:
  //   - `false`:
  //     - "-v | -vv | -vvv | --verbose" will be removed
  //     - "-q" will be added
  //   - `true`:
  //     - "-q | --quiet" will be removed
  //     - "-vvv" will be added
  "debug": false,
}
```
