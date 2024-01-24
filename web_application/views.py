from django.shortcuts import render
from django.shortcuts import render,redirect
from django.contrib.auth import authenticate,login,logout
from django.contrib import messages
from django.contrib.auth.models import User
from django.contrib.auth.forms import UserCreationForm
from django import forms
from .forms import SignUpForm
from django.core.files.storage import FileSystemStorage
from django.http import HttpResponse
from .forms import UploadFileForm
from .models import UploadedFile
from django.http import JsonResponse
from PIL import Image, ImageOps
import tensorflow as tf
import os
import numpy as np
from web_application.utils.list_of_fields_question import fields_questions_list_for_invoice,fields_questions_list_for_bills
from web_application.utils.text_getter import generate_result
from django.views.decorators.csrf import csrf_exempt
from django.http import JsonResponse
import json

#logger = logging.getLogger(__name__)

# this view is for home page
def home(request):
    #logger.info("Inside 'home' function in views.py")
    return render(request, 'home.html')

def about(request):
    #logger.info("Inside 'about' function in views.py")
    return render(request, 'about.html')

def contact(request):
    #logger.info("Inside 'contact' function in views.py")
    return render(request, 'contact.html')

@csrf_exempt
def login_user(request):
    #logger.info("Inside 'login_user' function in views.py")
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')
        user = authenticate(request,username=username,password=password)
        if user is not None:
            #logger.info(f"Successfully login for user: {username}")            
            login(request,user)
            messages.success(request,(f"Welcome {username}. You have been Logged in Successfully.!"))
            return redirect('home')
        else:
            #logger.error(f"Failed login attempt for user: {username}")
            messages.error(request,("There was an error logining in. Please try again.!"))
            return redirect('login')  
    else:
        return render(request, 'login.html',{})

@csrf_exempt
def register_user(request):
    #logger.info("Inside 'register_user' function in views.py")
    form = SignUpForm()
    if request.method == 'POST':
        form = SignUpForm(request.POST)
        if form.is_valid():
            form.save()
            username = form.cleaned_data['username']
            password = form.cleaned_data['password1']

            # log in user
            user = authenticate(username=username,password=password)
            login(request,user)
            messages.success(request,("You have been Registered Successfully.! Login to your account..."))
            return redirect('login')
        else:
            #logger.error("Error in user registration.")
            messages.success(request,("There was an error in registering. Please try again.!"))
            return redirect('register')
    else:
        return render(request, 'register.html',{'form':form})

def logout_user(request):
    #logger.info("Inside 'logout_user' function in views.py")
    logout(request)
    #logger.info("{User logged out.}")
    messages.success(request,("You have been logged out."))
    return redirect('home')
 
@csrf_exempt
def upload_invoice(request):
    #logger.info("Inside 'upload_invoice' function in views.py")
    if request.method == 'POST':
        form = UploadFileForm(request.POST, request.FILES)
        if form.is_valid():
            form.save()
            messages.success(request,("Image uploaded successfully."))
            return redirect('show_files')
        else:
            messages.error(request,("Error uploading image."))
    else:
            form = UploadFileForm()
    return render(request,'upload_invoice.html', {'form': form})      

def show_files(request):
    files = UploadedFile.objects.order_by('-file_id')
    return render(request, 'show_files.html', {'files': files})

@csrf_exempt
def classification_prediction(request):
    if request.method=='POST':
        # img_file contains path to the image file in media which is in string
        img_file = request.POST['imgFile']
        file_id = request.POST['file_id']
        print('Image File: ',img_file)
        print('File Id: ',file_id)
  
        # loading the model from model directory
        model = tf.keras.models.load_model("models/keras_model.h5", compile=False)
        
        # Load the image classification labels
        with open("models/labels.txt", "r") as labels_file:
            class_names = [line.strip() for line in labels_file.readlines()]
        
        # openin the image from the img_file path with pillow Image
        image_classify = Image.open('.'+ img_file).convert("RGB")
        
        # setting the size of the image as desired for the model
        img_size = (224, 224)
        # resize and crop an image to fit within a specified bounding box while maintaining its aspect ratio. 
        # It takes three arguments: 
        # the image to be resized (image_classify), 
        # #the target size (img_size),
        # and the resampling filter to be used.
        image_classify = ImageOps.fit(image_classify, img_size, Image.Resampling.LANCZOS)
        # convert image to array
        image_array_classify = np.asarray(image_classify)
        # normalize the image array
        normalized_image_array_classify = (image_array_classify.astype(np.float32) / 127.5) - 1
        '''
        So, the code below is creating a four-dimensional NumPy array to hold image data for classification, 
        where each image has dimensions of 224x224 pixels with three color channels (RGB). 
        The normalized pixel values of the image are then assigned to the first element of this array. 
        This array is  used as input data for machine learning models.
        '''
        data_classify = np.ndarray(shape=(1, 224, 224, 3), dtype=np.float32)
        data_classify[0] = normalized_image_array_classify
        # Make a prediction for image classification
        prediction_classify = model.predict(data_classify)
        index_classify = np.argmax(prediction_classify)
        class_name_classify = class_names[index_classify]
        confidence_score_classify = prediction_classify[0][index_classify]
        confidence_score_classify = confidence_score_classify*100
        # Display the classification prediction and confidence score
        value = f"{class_name_classify[2:]}"
        #global class_name
        class_name = f"{class_name_classify[2:]}"
        confidence_score =f"{confidence_score_classify:.2f} %"
        #logger.info("Image classification Completed Successfully.")
        messages.success(request,("Image Classification Completed Successfully."))
    return render(request, 'classification_prediction.html',{'img_file':img_file,'file_id':file_id,'class_name':class_name,'confidence_score':confidence_score})

@csrf_exempt
def invoice_classification(request):
    if request.method == 'POST':

        # receive image as post request
        img_file = request.FILES['image']

        # openin the image from the img_file path with pillow Image
        image_to_classify = Image.open(img_file)
  
        # loading the model from model directory
        model = tf.keras.models.load_model("models/keras_model.h5", compile=False)
        
        # Load the image classification labels
        with open("models/labels.txt", "r") as labels_file:
            class_names = [line.strip() for line in labels_file.readlines()]
        
        # setting the size of the image as desired for the model
        img_size = (224, 224)
        # resize and crop an image to fit within a specified bounding box while maintaining its aspect ratio. 
        # It takes three arguments: 
        # the image to be resized (image_classify), 
        # #the target size (img_size),
        # and the resampling filter to be used.
        image_classify = ImageOps.fit(image_to_classify, img_size, Image.Resampling.LANCZOS)
        # convert image to array
        image_array_classify = np.asarray(image_classify)
        # normalize the image array
        normalized_image_array_classify = (image_array_classify.astype(np.float32) / 127.5) - 1
        '''
        So, the code below is creating a four-dimensional NumPy array to hold image data for classification, 
        where each image has dimensions of 224x224 pixels with three color channels (RGB). 
        The normalized pixel values of the image are then assigned to the first element of this array. 
        This array is  used as input data for machine learning models.
        '''
        data_classify = np.ndarray(shape=(1, 224, 224, 3), dtype=np.float32)
        data_classify[0] = normalized_image_array_classify
        # Make a prediction for image classification
        prediction_classify = model.predict(data_classify)
        index_classify = np.argmax(prediction_classify)
        class_name_classify = class_names[index_classify]
        confidence_score_classify = prediction_classify[0][index_classify]
        confidence_score_classify = confidence_score_classify*100
        # Display the classification prediction and confidence score
        value = f"{class_name_classify[2:]}"
        #global class_name
        class_name = f"{class_name_classify[2:]}"
        confidence_score =f"{confidence_score_classify:.2f} %"
        #logger.info("Image classification Completed Successfully.")
        messages.success(request,("Image Classification Completed Successfully."))
        result = {'class_name':class_name,'confidence_score':confidence_score}
        return JsonResponse(result)
    else:
        return JsonResponse({'error': 'Invalid request method. Use POST.'})

@csrf_exempt
def text_extraction_page(request):
    #logger.info("Inside 'text_extraction_page' function in views.py")  
    if request.method=='POST':
        # class_name is the invoice classfied type
        class_name = request.POST['class_name']
        #print("Class Name : ",class_name)
        # img_file contains path to the image file in media which is in string
        img_file = request.POST['img_file']
        #print("Image Path: ",img_file)
        #image = Image.open('.'+ img_file).convert("RGB")
    return render(request,'text_extraction_page.html',{'class_name':class_name,
        'img_file':img_file,
        'fields_questions_list_for_invoice':fields_questions_list_for_invoice,
        'fields_questions_list_for_bills':fields_questions_list_for_bills})

def text_show_files(request):
    #logger.info("Inside 'text_show_files' view.")
    if request.method =="POST":
        img_file = request.POST['img_file']
        class_name = request.POST['class_name']
        image = Image.open('.'+ img_file).convert("RGB")   
            
        # getting the selected fields from checkbox.
        selected_fields = request.POST.getlist('selected_fields')
        print("Selected Fields:", selected_fields)
        
        selected_questions = []
        if class_name == "Invoice":
            # getting the selected questions for the respective fields
            for field in selected_fields:
                #print(fields_questions_list_for_invoice[field])
                selected_question = fields_questions_list_for_invoice[field]
                selected_questions.append(selected_question)
            print("Selected Questions:",selected_questions)
        elif class_name == "Restaurant_Bill":
            for field in selected_fields:
                #print(fields_questions_list_for_invoice[field])
                selected_question = fields_questions_list_for_bills[field]
                selected_questions.append(selected_question)
            print("Selected Questions:",selected_questions)
        else:
            return HttpResponse("Under Process")
        selected_dict = dict(zip(selected_fields, selected_questions))
        print('Selected Dictionary: ',selected_dict)
        extracted_data = {}
        if class_name == "Invoice":
            for field,question in selected_dict.items():
                user_question = question
                answer = str.upper(generate_result(user_question,image))
                extracted_data[field]=answer
            print("Extracted Data: ",extracted_data)
        elif class_name == 'Restaurant_Bill':
            for field,question in selected_dict.items():
                user_question = question
                answer = str.upper(generate_result(user_question,image))
                extracted_data[field]=answer
            print("Extracted Data: ",extracted_data)
        else:
            pass           
        messages.success(request,("Data Extraction Successfull...!"))
        #logger.info("Data Extraction Successfull.")
    return render(request, 'text_show_files.html',{'img_file':img_file,'extracted_data':extracted_data}) 

@csrf_exempt
def invoice_text_extraction(request):
    if request.method == 'POST':
        # receive image as post request
        img_file = request.FILES['image']

        # openin the image from the img_file path with pillow Image
        image_to_extract_text = Image.open(img_file)
        
        class_name = request.POST['class_name']
            
        # getting the selected fields from checkbox as a comma-separated string
        selected_fields = request.POST.get('selected_fields', '').split(',')
        
        selected_questions = []
        if class_name == "Invoice":
            # getting the selected questions for the respective fields
            for field in selected_fields:
                #print(fields_questions_list_for_invoice[field])
                selected_question = fields_questions_list_for_invoice[field]
                selected_questions.append(selected_question)
            print("Selected Questions:",selected_questions)
        elif class_name == "Restaurant_Bill":
            for field in selected_fields:
                #print(fields_questions_list_for_invoice[field])
                selected_question = fields_questions_list_for_bills[field]
                selected_questions.append(selected_question)
            print("Selected Questions:",selected_questions)
        else:
            return HttpResponse("Under Process")
        
        selected_dict = dict(zip(selected_fields, selected_questions))
        print('Selected Dictionary: ',selected_dict)
        
        extracted_data = {}
        if class_name == "Invoice":
            for field,question in selected_dict.items():
                user_question = question
                answer = str.upper(generate_result(user_question,image_to_extract_text))
                extracted_data[field]=answer
            print("Extracted Data: ",extracted_data)
        elif class_name == 'Restaurant_Bill':
            for field,question in selected_dict.items():
                user_question = question
                answer = str.upper(generate_result(user_question,image_to_extract_text))
                extracted_data[field]=answer
            print("Extracted Data: ",extracted_data)
        else:
            pass
        result = {'Extracted_data':extracted_data}
        messages.success(request,("Data Extraction Successfull...!"))
        #logger.info("Data Extraction Successfull.")
    return JsonResponse(result) 

@csrf_exempt
def classification_text_extraction(request):
    if request.method == 'POST':

        # receive image as post request
        img_file = request.FILES['image']

        # openin the image from the img_file path with pillow Image
        image = Image.open(img_file)
  
        # loading the model from model directory
        model = tf.keras.models.load_model("models/keras_model.h5", compile=False)
        
        # Load the image classification labels
        with open("models/labels.txt", "r") as labels_file:
            class_names = [line.strip() for line in labels_file.readlines()]
        
        # setting the size of the image as desired for the model
        img_size = (224, 224)
        # resize and crop an image to fit within a specified bounding box while maintaining its aspect ratio. 
        # It takes three arguments: 
        # the image to be resized (image_classify), 
        # #the target size (img_size),
        # and the resampling filter to be used.
        image_classify = ImageOps.fit(image, img_size, Image.Resampling.LANCZOS)
        # convert image to array
        image_array_classify = np.asarray(image_classify)
        # normalize the image array
        normalized_image_array_classify = (image_array_classify.astype(np.float32) / 127.5) - 1
        '''
        So, the code below is creating a four-dimensional NumPy array to hold image data for classification, 
        where each image has dimensions of 224x224 pixels with three color channels (RGB). 
        The normalized pixel values of the image are then assigned to the first element of this array. 
        This array is  used as input data for machine learning models.
        '''
        data_classify = np.ndarray(shape=(1, 224, 224, 3), dtype=np.float32)
        data_classify[0] = normalized_image_array_classify
        # Make a prediction for image classification
        prediction_classify = model.predict(data_classify)
        index_classify = np.argmax(prediction_classify)
        class_name_classify = class_names[index_classify]
        confidence_score_classify = prediction_classify[0][index_classify]
        confidence_score_classify = confidence_score_classify*100
        # Display the classification prediction and confidence score
        value = f"{class_name_classify[2:]}"
        #global class_name
        class_name = f"{class_name_classify[2:]}"
        confidence_score =f"{confidence_score_classify:.2f} %"
        #logger.info("Image classification Completed Successfully.")
        messages.success(request,("Image Classification Completed Successfully."))
        
        
        # getting the selected fields from checkbox as a comma-separated string
        selected_fields = request.POST.get('selected_fields', '').split(',')
        #selected_fields = request.POST.getlist('selected_fields')
        
        selected_questions = []
        if class_name == "Invoice":
            # getting the selected questions for the respective fields
            for field in selected_fields:
                #print(fields_questions_list_for_invoice[field])
                selected_question = fields_questions_list_for_invoice[field]
                selected_questions.append(selected_question)
            print("Selected Questions:",selected_questions)
        elif class_name == "Restaurant_Bill":
            for field in selected_fields:
                #print(fields_questions_list_for_invoice[field])
                selected_question = fields_questions_list_for_bills[field]
                selected_questions.append(selected_question)
            print("Selected Questions:",selected_questions)
        else:
            return HttpResponse("Under Process")
        
        selected_dict = dict(zip(selected_fields, selected_questions))
        print('Selected Dictionary: ',selected_dict)
        
        extracted_data = {}
        if class_name == "Invoice":
            for field,question in selected_dict.items():
                user_question = question
                answer = str.upper(generate_result(user_question,image))
                extracted_data[field]=answer
            print("Extracted Data: ",extracted_data)
        elif class_name == 'Restaurant_Bill':
            for field,question in selected_dict.items():
                user_question = question
                answer = str.upper(generate_result(user_question,image))
                extracted_data[field]=answer
            print("Extracted Data: ",extracted_data)
        else:
            pass
        result = {'class_name':class_name,'confidence_score':confidence_score,'Extracted_data':extracted_data}
        messages.success(request,("Data Extraction Successfull...!"))
        return JsonResponse(result)

    
def verify_predictions(request):
    #logger.info("Inside 'verify_prediction' view.")
    if request.method == 'POST':
        file_id = request.POST.get('file_id')
        class_name = request.POST.get('class_name')
        confidence_score = request.POST.get('confidence_score')
        img_file = request.POST.get('img_file')
        file = UploadedFile.objects.get(pk=file_id)
        print("Class Name: ",class_name)
        #logger.info(f"Class Name Predicted from Model: {class_name}")
        print("Confidence Score: ",confidence_score)
        #logger.info(f"Confidence Score Generated from Model: {confidence_score}")
    return render(request,'verify_predictions.html', {'file': file,'class_name': class_name,'confidence_score': confidence_score,'img_file':img_file})




