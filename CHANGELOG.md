# Changelog

## 2020-04-23

### Added

- Monitor mode. When displaying a job with 'show job id 123' one can now add '| monitor' to refresh the job status until the job finishes or Ctrl+C is invoked.

- Auto-expansion of parameters. It is now possible to define parameters as default in the YAML specification. For example, the 'sync' command can have 'dry_run' set to True by default. This will let the user type in 'sync device hostname test' and it will expand to 'sync device hostname test dry_run true' if the dry_run parameter is not added.

- More detailed device output. If a single device is listed with 'show device id 123' all details about the device will now be displayed.

- More detailed job output. Just like devices, if a single job is displayed with 'show job id 123' all job details including exceptions etc will be shown.

- Better tab completion. Command and attribute descriptions will be dispöayed in a better way when tab completion is used.

- 'exit' to leave the CLI. Now possible to use both 'quit' and 'exit' to leave the CLI.

- A new command, 'update', is introduced. This can be used to update values of already existing devices. For example, to change state of a device, 'update device id 123 state MANAGED' can be used.

- Handle the rare case where a command should send a PUT towards the API instead of a POST.
