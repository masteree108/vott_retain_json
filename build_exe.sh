# only for ubutu
# note 1: this buiild_exe.sh that needs to setup module please as follows
# pip install pyinstaller
# note 2: chmod +x build_exe.sh
# ubuntu
pyinstaller -F ./main.py
cp ./dist/main ./
mv main vott_retain_json.exe
rm -rf dist
rm -rf __pycache__
rm -rf build
rm *.spec

