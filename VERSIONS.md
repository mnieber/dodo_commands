# Version history

## 0.1.0

- BREAKING: Renamed option projects_folder to projects_dir in dodo_commands.config.
- BREAKING: Added option python_interpreter (default=python) to dodo_commands.config. This option sets the python interpreter that is used in the project's virtualenv.
- FIX: Changed version back from 1.0.0 to 0.1.0 to indicate beta status
- FIX: Several other fixes
- NEW: Commands new-command, git-gui, gitk, gitsplit, git, config-get, bootstrap

## 0.1.1

- FIX: Added documentation and fixed broken references to defaults/commands
- NEW: Argument --create-from to dodo_activate

## 0.1.2

- BREAKING: Store env inside dodo_commands, and config.yaml in dodo_commands/res
- FIX: Fix layer and print-config, update README.md to explain configuration layers