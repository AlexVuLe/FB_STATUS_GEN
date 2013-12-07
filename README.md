FB_STATUS_GEN
=============
Instruction:

A. Obtaining own Facebook statuses:

1. Install modules facebook-sdk and PyYAML

2. Visit https://developers.facebook.com/tools/explorer/ to create user access token. You need to permit 'user_status' in 'user data permission' and 'update_status' in 'extended permission'

3. Create a .yaml file named user_access_token.yaml with format token:user_access_token in the same working directory. Do not commit the .yaml file. It is your personal access token. I have edited .gitignore to ignore any .yaml file. Add a space after token:

4. Run get_user_data.py to get your past statuses and associated numbers of likes in a list of tuples (likes, message).

B. Text Processing:

1. If you are using MacOSX, unzip the pyenchant egg in required_pkgs folder and copy folder enchant to your Python site-packages folder.

2. First time using nltk, import nltk and run nltk.download() in python console to download all the required packages.
