# IdentificationCardFraudDetection

Introduction
Medium article link : https://saineshnakra.medium.com/fake-id-card-detection-system-using-computer-vision-af3feea226fe

This can be used by organizations to check the veracity of the Identification-Card. Currently companies manually check online but with this project we can automate the process and do it instantly.

Steps to perform:

1. Get images from User

2. Check for size and format of the image

3. Change the shape and size of image according to the original image

4. Convert the image to grayscale

5. Find the similarity index of the images

6. Finding the threshold of the image

7. Finding contour and grab those contours using imutils.

8. Draw a bounding rectangle using these contours.

9. Plot difference, threshold, original and tampered image.

10. Compare all the images and check the similarity score to decide

tampering

Platform used:

Google Colab -> we will not require a GPU or TPU for this project.
Link :
https://colab.research.google.com/drive/1ulefSYeT6pChfEagXoN5CNJaSiyyw3FC?usp=sharing

Libraries used:

1. from skimage.metrics we will import structural_similarity -> this will help us in finding the structural similarity score between two images.

2. from imutils -> helps in grabbing the contours of the image

3. cv2 -> for all computer vision requirements

4. from PIL import Image -> downloading and visualizing the image

5. requests -> fetch data from urls
Summary

Finding out structural similarity of the images helped us in finding the difference or similarity in the shape of the images. Similarly, finding out the threshold and contours based on those threshold for the images converted into grayscale binary also helped us in shape analysis and recognition.

As, our SSIM is ~31.2% we can say that the image user provided is fake or tampered.

Finally we visualized the differences and similarities between the images using by displaying the images with contours, difference and threshold.

Computer Vision Concepts Used and F.A.Qs

1. Why are we converting the images to a grayscale format?
Ans. This is because in image processing it is better to understand a grayscale image which only has one channel as compared to an rgb image(colored image) as it has three channels and therefore it is a bit tough to identify the important edges in a colored image

2, We are using Structural similarity index. What is structural similarity index?
Ans. Here, we are trying to find the similarity between the original and tampered image. The lower the SSIM score lower is the similarity. SSIM is a fantastic tool that allows us to evaluate the structural similarity between two images by considering various components.

When it comes to comparing images using SSIM, we take into account three key factors: luminance, contrast, and structure.

Firstly, we consider luminance. SSIM evaluates the overall brightness or luminance of the images. It looks at the mean luminance and ensures that both images have similar intensity levels.

Next up is contrast. SSIM measures the similarity of contrast between corresponding local regions of the images. It compares the local variations in intensity or color are preserved in the compared images basically comparing how the contrasts match up.

Lastly, we have the structural comparison. SSIM evaluates the similarity of structural patterns or textures in the images. This helps us analyze the preservation of structure within the images.

The SSIM metric combines these components to provide an overall assessment of the structural similarity between the two images. The SSIM index ranges from -1 to 1, with values closer to 1 informing us about a higher structural similarity. So, the closer the SSIM value is to 1, the higher the similarity in the structures of the images provided.

3.We are using the threshold function. What does it do?
Ans. The threshold function is a basic and commonly used image processing technique that converts a grayscale or color image into a binary image. It is used to segment the image, separating regions of interest from the background based on pixel intensity values.

The threshold function takes an input image and a threshold value as parameters and produces an output binary image. The process involves comparing the intensity values of pixels in the input image with the threshold value and assigning a binary value (usually 0 or 255) to each pixel in the output image based on the result of the comparison.

There are different types of thresholding methods commonly used in computer vision:

    Global Thresholding
    Adaptive Thresholding
    Otsu’s Thresholding

Quick tip on when to use which type of thresholding :

Global Thresholding: When the lighting is even and difference is clear.

Adaptive Thresholding: When the lighting is uneven.

Otsu’s Thresholding: When in doubt.

4. We are using the contours and grab contours functions. Why?

Ans. Find contours works on binary images and retrieves the contours of the images. This contours are a useful tool to analyze tool when the purpose is shape analysis and recognition. Grab contours will grab the appropriate value of the contours

Contours is one of the most important tools to use in OpenCV. You can use contours to detect shapes and also analyze it without using ML or deep learning.

Uses of contours in computer vision:

    Edge Detection
    Shape Analysis
    Object Detection
    Image Segmentation
    Visualizing and Rendering

Note: Preprocessing is very important when using contours.

5. What is a bounding rectangle and how is it used?

Ans. Bounding rectangle(bounding box) tightly encloses an object or region of interest in an image or video frame. It is a common technique used for object detection, tracking, and various other computer vision tasks.

The bounding rectangle is defined by four parameters: the coordinates of the top-left corner (x, y) and the width and height (w, h) of the rectangle. These parameters describe the position and size of the rectangle relative to the image or frame coordinate system.

Uses of bounding rectangles:

    Object Localization
    Object Detection
    Object Tracking
    Region of Interest (ROI) Extraction
    Data Augmentation
    Evaluation Metrics

We compute the bounding box of the contour and then draw the bounding box on both input images to represent and highlight where the two images are different .
