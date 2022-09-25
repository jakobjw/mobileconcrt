# mobileconcrt
Taking certificate (.crt) files as input, creates Apple .mobileconfig profile files for installation on Apple Mac systems

### Usage
- Place .crt files in a directory "input-crt-files" next to the script
- Call the script with the usage as indicated in the help message (call without args or with --help)
- The resulting .mobileconfig file is created in a directory "output" next to the script

### Limitations
- Scope for the profile installation currently limited to "User" (other option would be "System")
- Device type currently limited to "Mac" (other options would be other Apple device types)

### About
- Author: jakobjw
- License: MIT
