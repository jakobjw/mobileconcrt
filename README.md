# mobileconcrt
Taking certificate (.crt) files as input, creates Apple .mobileconfig profile files for installation on Apple Mac systems

### Usage
- Call the script with the usage as indicated in the help message (call it without args or with --help)
- The resulting .mobileconfig file is created in the current working directory or at the specified path

### Limitations
- Scope for the profile installation currently limited to "User" (other option would be "System")
- Device type currently limited to "Mac" (other options would be other Apple device types)

### About
- Author: jakobjw
- License: MIT
