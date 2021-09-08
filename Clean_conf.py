from ciscoconfparse import CiscoConfParse
from flask import Flask, flash , render_template, request, redirect,abort,send_file, send_from_directory
from werkzeug.utils import secure_filename
from os import listdir, path, remove,mkdir, rmdir
from datetime import datetime
import cleaning

app = Flask(__name__)

cleanConfig = cleaning.cleaning()


# main page
@app.route('/')
def index():
    ## list the 'input' directory
    files_input = listdir('input')

    ## will list in the wepage all the file to be cleaned
    return render_template('index.html', files_input = files_input)
###


# clean process step 1
@app.route('/clean', methods = ['GET', 'POST'])
def clean():
    ## list the vrf of all the devices configuration within the 'input' directory
    ## and fill the dictionnary 'cleaning.vrf' with all the vrfs
    if len(request.form.getlist('files'))==0 :
        return redirect('/')

    cleanConfig.cleaning['files'] = request.form.getlist('files')
    
    vrfFileList = cleanConfig.vrfList(cleanConfig.cleaning['files'])
    ## the webpage is rendered with all the options to be cleaned and the vrfs
    return render_template('clean.html', cleaning = cleanConfig.cleaning, vrf = vrfFileList)
###

# add a function that will clean the selected options and give the output files in 
# 'output' directory
@app.route('/clean_process', methods = ['GET', 'POST'])
def clean_process():
    if request.method == 'POST':
        directory = path.join('output',datetime.now().strftime("%Y_%m_%d_%H%M%S"))
        mkdir(directory)
        
        cleanConfig.cleaning['basic'] = checkbox(request.form.get('basic'))
        cleanConfig.cleaning['username'] = checkbox(request.form.get('username'))
        cleanConfig.cleaning['access-list'] = checkbox(request.form.get('access-list'))
        cleanConfig.cleaning['management'] = checkbox(request.form.get('management'))
        cleanConfig.cleaning['shutdown-interfaces'] = checkbox(request.form.get('shutdown-interfaces'))
        cleanConfig.vrfToClean(request.form.getlist('vrf'))
        cleanConfig.confclean()
        

        return redirect('/output')


##################################################################################
@app.route('/output', defaults={'zePath': ''})
@app.route('/output/<path:zePath>')
def list_output(zePath):
    baseDir = 'output'
    newPath = path.join(baseDir,zePath)
    if not path.exists(newPath):
        return abort(404)
    
    if path.isfile(newPath):
        return send_from_directory(baseDir,zePath)

    files = list(dict.fromkeys(listdirNh(newPath)))
    fileList = []
    
    for f in files:
        if path.isdir(path.join(newPath,f)):
            fileList.append([f, '(Dir) '+str(len(list(listdirNh(path.join(newPath,f)))))+' files'])
        else:
            fileList.append([f, '(File)'])
    return render_template('output.html', files=fileList)
    
            
# manage files
@app.route('/upload')
def upload_file():
    ## list all the file to be deleted or not
    files_input = list(dict.fromkeys(listdirNh('input')))

    ## the webpage will list the file already upladed and give the possibility
    ## to delete one or many files at once or upload one or more files
    ## 
    return render_template('upload.html', files_input = files_input)

@app.route('/uploader', methods = ['GET', 'POST'])
def uploader_file():
   if request.method == 'POST':
      files_up = request.files.getlist('file[]')
      for f in files_up:
        f.save(path.join('input',secure_filename(f.filename)))
      return redirect('/upload')

@app.route('/delete_input_files', methods = ['GET', 'POST'])
def delete_input_files():
    if request.method == 'POST':
        delete_files = request.form.getlist('files')
        for file in delete_files:
            remove(path.join('input',file))
        return redirect('/upload')

@app.route('/delete_output_files', methods = ['GET', 'POST'])
def delete_output_files():
    if request.method == 'POST':
        delete_files = request.form.getlist('files')
        for file in delete_files:
            removeRec(path.join('output',file))
        return redirect('/output')


def checkbox(value):
    if value is None:
        return False
    else:
        return True

def listdirNh(p):
    for f in listdir(p):
        if not f.startswith('.'):
            yield f

def removeRec(f):
    if path.isfile(f):
        remove(f)
    elif path.isdir(f):
        listD = listdir(f)
        for r in listD:
            removeRec(path.join(f,r))
        rmdir(f)
        

        


if __name__ == '__main__':
    app.run(debug=True)