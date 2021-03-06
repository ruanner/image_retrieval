#!flask/bin/python
################################################################################################################################
# ------------------------------------------------------------------------------------------------------------------------------
# This file implements the REST layer. It uses flask micro framework for server implementation. Calls from front end reaches 
# here as json and being branched out to each projects. Basic level of validation is also being done in this file. #                                                                                                                                  	       
# -------------------------------------------------------------------------------------------------------------------------------
################################################################################################################################
from flask import Flask, jsonify, abort, request, make_response, url_for, redirect, render_template
from flask_httpauth import HTTPBasicAuth
from werkzeug.utils import secure_filename
import os
import star
import shutil
import numpy as np
from search import recommend
from getTypes import get_types


UPLOAD_FOLDER = 'uploads'
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg'}
from tensorflow.python.platform import gfile

app = Flask(__name__, static_url_path="")
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
app.jinja_env.variable_start_string = '{['
app.jinja_env.variable_end_string = ']}'
auth = HTTPBasicAuth()

# ==============================================================================================================================
#                                                                                                                              
#    Loading the extracted feature vectors for image retrieval                                                                 
#                                                                          						        
#                                                                                                                              
# ==============================================================================================================================
extracted_features = np.zeros((10000, 2048), dtype=np.float32)
with open('saved_features_recom.txt') as f:
    for i, line in enumerate(f):
        extracted_features[i, :] = line.split()
print("loaded extracted_features")


# ==============================================================================================================================
#                                                                                                                              
#  This function is used to do the image search/image retrieval
#                                                                                                                              
# ==============================================================================================================================
@app.route('/imgUpload', methods=['GET', 'POST'])
# def allowed_file(filename):
#    return '.' in filename and \
#           filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

def upload_img():
    print("image upload")
    result = 'static/result'
    if not gfile.Exists(result):
        os.mkdir(result)
    shutil.rmtree(result)

    if request.method == 'POST' or request.method == 'GET':
        print(request.method)
        # check if the post request has the file part
        if 'file' not in request.files:
            print('No file part')
            return redirect(request.url)

        file = request.files['file']
        print(file.filename)
        # if user does not select file, browser also
        # submit a empty part without filename
        if file.filename == '':
            print('No selected file')
            return redirect(request.url)
        if file:  # and allowed_file(file.filename):
            filename = secure_filename(file.filename)
            file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
            inputloc = os.path.join(app.config['UPLOAD_FOLDER'], filename)
            print(inputloc)
            recommend(inputloc, extracted_features)
            os.remove(inputloc)
            image_path = "/result"
            image_list = [os.path.join(image_path, file) for file in os.listdir(result)
                          if not file.startswith('.')]
            images = {
                'image0': image_list[0],
                'image1': image_list[1],
                'image2': image_list[2],
                'image3': image_list[3],
                'image4': image_list[4],
                'image5': image_list[5],
                'image6': image_list[6],
                'image7': image_list[7],
                'image8': image_list[8]
            }
            print(images)
            return jsonify(images)


@app.route('/getTypes', methods=['GET', 'POST'])
def get_type():
    print("get type")
    imageList = request.values.get('imageList')
    print(imageList)

    if request.method == 'POST' or request.method == 'GET':
        print(request.method)
        typeList = get_types(imageList)
        return jsonify({'typeList': typeList})


@app.route('/getStar', methods=['GET', 'POST'])
def get_star():
    print("get star")
    imageList = star.get_star_list()
    return jsonify({'imageList': imageList})


@app.route('/delStar', methods=['GET', 'POST'])
def del_star():
    print("del star")
    imageDel = request.values.get('imageDel')
    print(imageDel)
    star.del_star(imageDel)
    imageList = star.get_star_list()
    return jsonify({'imageList': imageList})


@app.route('/addStar', methods=['GET', 'POST'])
def add_star():
    print("add star")
    imageStar = request.values.get('imageStar')
    star.add_star(imageStar)
    imageList = star.get_star_list()
    return jsonify({'imageList': imageList})
# ==============================================================================================================================
#                                                                                                                              
#                                           Main function                                                        	            #
#  				                                                                                                
# ==============================================================================================================================
@app.route("/")
def main():
    return render_template("main.html")


@app.route("/collect")
def collect():
    return render_template("collection.html")


if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0')
