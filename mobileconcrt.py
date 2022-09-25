# mobileconcrt
#
# Version: 0.1
# Description: Taking certificate (.crt) files as input, creates Apple .mobileconfig profile files for installation on Apple Mac systems
#
# Usage:
# - Place .crt files in a directory "input-crt-files" next to this script
# - Call this script with the usage as indicated in the help message (call without args or with --help)
# - The resulting .mobileconfig file is created in a directory "output" next to this script
#
# Limitations:
# - Scope for the profile installation currently limited to "User" (other option would be "System")
# - Device type currently limited to "Mac" (other options would be other Apple device types)
#
# Author: jakobjw
# License: MIT


import os, plistlib, uuid, time, argparse


DIR_NAME_INPUT_CRT_FILES = "input-crt-files"
ALLOWED_EXTENSION_CRT_FILES = ".crt"
DIR_NAME_OUTPUT = "output"
OUTPUT_FILENAME_PREFIX = "mobileconcrt"
OUTPUT_FILENAME_EXTENSION = ".mobileconfig"


argument_parser = argparse.ArgumentParser()
argument_parser.add_argument("-pn", "--profilename", dest="profile_name", help="profile display name, e.g. \"Profile 1\"", required=True)
argument_parser.add_argument("-pd", "--profiledescription", dest="profile_description", help="profile description, e.g. \"This profile is for that\"", required=False)
argument_parser.add_argument("-id", "--identifier", dest="identifier", help="reverse-DNS style identifier, e.g. \"com.example.profile1\"", required=True)
argument_parser.add_argument("-org", "--organization", dest="organization", help="organization name, e.g. \"Contoso\"", required=False)
argument_parser.add_argument("-out", "--outfile", dest="outfile", help="output mobileconfig filename, e.g. \"my-profile.mobileconfig\"", required=False)
try:
 args = argument_parser.parse_args()
except:
 argument_parser.print_help()
 exit()


certs = []
# entries shall be dicts with the following items:
# - cert_filename: the filename of the .crt file, without the .crt extension
# - cert_content: bytes object with the .crt file content (plistlib does the base64-encoding)
# - cert_uuid: a unique UUID string (uppercase, including the dashes)


def generate_uuid_random_uppercase():
 # generates an uppercase UUID string (as used in plist files)
 return str(uuid.uuid4()).upper()  # https://stackoverflow.com/a/534847


def add_certificate(crt_files_path, filename, filename_without_extension):
 print("Adding certificate:", filename)
 with open(os.path.realpath(os.path.join(crt_files_path, filename)), "rb") as crt_file:
  crt_content = crt_file.read()
  certs.append(dict(
   cert_filename = filename_without_extension,
   cert_content = crt_content,
   cert_uuid = generate_uuid_random_uppercase()
  ))


crt_files_path = os.path.realpath(os.path.join(os.getcwd(), os.path.dirname(__file__), DIR_NAME_INPUT_CRT_FILES))
input_path_dir = os.fsencode(crt_files_path)
for file in os.listdir(input_path_dir):
 filename = os.fsdecode(file)
 if filename.endswith(ALLOWED_EXTENSION_CRT_FILES):
  filename_without_extension = os.path.splitext(filename)[0]
  add_certificate(crt_files_path, filename, filename_without_extension)
 else:
  continue


if len(certs) < 1:
 print("Error: no valid certificate ("+ALLOWED_EXTENSION_CRT_FILES+") files found in:", crt_files_path)
 exit()


plist_dict = dict(
 PayloadDisplayName = args.profile_name,
 PayloadDescription = args.profile_description or "",
 PayloadIdentifier = args.identifier,
 PayloadOrganization = args.organization or "",
 PayloadScope = "User",  # NOTE: hard-coded to "User", also possible: "System" (see https://developer.apple.com/documentation/devicemanagement/toplevel)
 PayloadType = "Configuration",
 PayloadUUID = generate_uuid_random_uppercase(),
 PayloadVersion = 1,
 TargetDeviceType = 5,  # NOTE: hard-coded to 5 (=Mac), other Apple device types are possible (see https://developer.apple.com/documentation/devicemanagement/toplevel)
 PayloadContent = []  # populated below
)

for cert in certs:
 plist_dict["PayloadContent"].append(
  dict(
   PayloadType = "com.apple.security.pem",
   PayloadDisplayName = "Certificate",
   PayloadCertificateFileName = cert["cert_filename"],
   PayloadIdentifier = "com.apple.security.pem." + cert["cert_uuid"],
   PayloadUUID = cert["cert_uuid"],
   PayloadVersion = 1,
   PayloadContent = cert["cert_content"]  # plistlib handles the base64 encoding
  )
 )


output_filename = args.outfile  or  OUTPUT_FILENAME_PREFIX + " " + time.strftime("%Y-%m-%d %H.%M.%S") + " (" + str(len(certs)) + " certs)" + OUTPUT_FILENAME_EXTENSION
if not output_filename.endswith(OUTPUT_FILENAME_EXTENSION):
 output_filename += OUTPUT_FILENAME_EXTENSION

output_path = os.path.realpath(os.path.join(os.getcwd(), os.path.dirname(__file__), DIR_NAME_OUTPUT, output_filename))
os.makedirs(os.path.dirname(output_path), exist_ok=True)
print("Writing mobileconfig file to:", output_path)

with open(output_path, "wb") as mobileconfig_file:
 plistlib.dump(plist_dict, mobileconfig_file)
 print("Wrote mobileconfig file:", output_filename)
