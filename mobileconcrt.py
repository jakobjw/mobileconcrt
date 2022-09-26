# mobileconcrt
#
# Version: 0.2
# Description: Taking certificate (.crt) files as input, creates Apple .mobileconfig profile files for installation on Apple Mac systems
#
# Usage:
# - Call this script with the usage as indicated in the help message (call it without args or with --help)
# - The resulting .mobileconfig file is created in the current working directory or at the specified path
#
# Limitations:
# - Scope for the profile installation currently limited to "User" (other option would be "System")
# - Device type currently limited to "Mac" (other options would be other Apple device types)
#
# Author: jakobjw
# License: MIT
# URL: https://github.com/jakobjw/mobileconcrt


import os, plistlib, uuid, time, argparse


ALLOWED_EXTENSION_CRT_FILES = ".crt"
OUTPUT_FILENAME_PREFIX = "mobileconcrt"
OUTPUT_FILENAME_EXTENSION = ".mobileconfig"


argument_parser = argparse.ArgumentParser()
argument_parser.add_argument("-in", "--inputdir", dest="input_directory", help="[REQUIRED] input directory with the .crt files, e.g. \"../my-crt-files\"", required=True)
argument_parser.add_argument("-pn", "--profilename", dest="profile_name", help="[REQUIRED] profile display name, e.g. \"Profile 1\"", required=True)
argument_parser.add_argument("-pd", "--profiledescription", dest="profile_description", help="optional profile description, e.g. \"This profile is for that\"", required=False)
argument_parser.add_argument("-id", "--identifier", dest="identifier", help="[REQUIRED] reverse-DNS style identifier, e.g. \"com.example.profile1\"", required=True)
argument_parser.add_argument("-org", "--organization", dest="organization", help="optional organization name, e.g. \"Contoso\"", required=False)
argument_parser.add_argument("-out", "--outpath", dest="outpath", help="optional output mobileconfig path for the .mobileconfig file (including filename), e.g. \"../out/my-profile.mobileconfig\"", required=False)
try:
 args = argument_parser.parse_args()
except:
 argument_parser.print_help()
 exit()


def log(text):
 print("[mobileconcrt] " + text)


certs = []
# entries shall be dicts with the following items:
# - cert_filename: the filename of the .crt file, without the .crt extension
# - cert_content: bytes object with the .crt file content (plistlib handles the base64 encoding)
# - cert_uuid: a unique UUID string (uppercase, including the dashes)


def generate_uuid_random_uppercase():
 # generates an uppercase UUID string (as used in plist files)
 return str(uuid.uuid4()).upper()  # https://stackoverflow.com/a/534847


def add_certificate(crt_files_path, filename, filename_without_extension):
 log("Adding certificate: " + filename)
 with open(os.path.realpath(os.path.join(crt_files_path, filename)), "rb") as crt_file:
  crt_content = crt_file.read()
  certs.append(dict(
   cert_filename = filename_without_extension,
   cert_content = crt_content,
   cert_uuid = generate_uuid_random_uppercase()
  ))


crt_files_path = os.path.realpath(os.path.join(os.getcwd(), args.input_directory))
input_path_dir = os.fsencode(crt_files_path)
for file in os.listdir(input_path_dir):
 filename = os.fsdecode(file)
 if filename.endswith(ALLOWED_EXTENSION_CRT_FILES):
  filename_without_extension = os.path.splitext(filename)[0]
  add_certificate(crt_files_path, filename, filename_without_extension)
 else:
  continue


if len(certs) < 1:
 log("Error: no valid certificate ("+ALLOWED_EXTENSION_CRT_FILES+") files found in: " + crt_files_path)
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


output_path_relative = args.outpath  or  OUTPUT_FILENAME_PREFIX + " " + time.strftime("%Y-%m-%d %H.%M.%S") + " (" + str(len(certs)) + " certificates)" + OUTPUT_FILENAME_EXTENSION
if not output_path_relative.endswith(OUTPUT_FILENAME_EXTENSION):
 output_path_relative += OUTPUT_FILENAME_EXTENSION

output_path = os.path.realpath(os.path.join(os.getcwd(), output_path_relative))
os.makedirs(os.path.dirname(output_path), exist_ok=True)
log("Writing mobileconfig file to: " + output_path)

with open(output_path, "wb") as mobileconfig_file:
 plistlib.dump(plist_dict, mobileconfig_file)
 log("Wrote mobileconfig file to: " + output_path)
