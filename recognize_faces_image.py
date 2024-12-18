# import the necessary packages
import face_recognition
import pickle
import argparse
from google.colab.patches import cv2_imshow
import cv2

# construct the argument parser and parse the arguments
ap = argparse.ArgumentParser()
ap.add_argument("-i", "--image", required=True,
                help="path to input image")
ap.add_argument("-e", "--encodings-file", required=True,
                help="path to serialized db of facial encodings")
ap.add_argument("-m", "--detection-method", type=str, default='cnn',
                help="face detection model to use: either 'hog' or 'cnn' ")

def get_command_line_args():
    args = vars(ap.parse_args())

    return args['image'], args['encodings_file'], args['detection_method']

input_image, encodings_file, detection_method = get_command_line_args()

# load the known faces and embeddings
print("[INFO] loading encodings...")
data = pickle.loads(open(encodings_file, "rb").read())

# load the input image and convert it from BGR to RGB
image = cv2.imread(input_image)
rgb_image = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)

# detect the (x,y)-coordinates of the bounding boxes cooresponding to each
# face in the input image, then compute the facial embeddings for each face
print("[INFO] recognize faces...")
boxes = face_recognition.face_locations(rgb_image, model=detection_method)
encodings = face_recognition.face_encodings(rgb_image, boxes)

# initialize the list of names for each face detected
names = []

# loop over the facial embeddings
for encoding in encodings:
    # attempt to match each face in the input to our known encodings
    # This function returns a list of True / False  values, one for each image in our dataset.
    # since the dataset has 218 Jurassic Park images, len(matches)=218
    matches = face_recognition.compare_faces(data["encodings"], encoding)
    name = "Desconocido"

    # check to see if we have found any matches
    if True in matches:
        # find the indexes of all matched faces then initialize a dictionary to count
        # the total number of times each face was matched
        matchedIdxs = [i for (i, b) in enumerate(matches) if b]
        counts = {}

        # loop over the matched indexes and maintain a count for each recognized face face
        for i in matchedIdxs:
            name = data['names'][i]
            counts[name] = counts.get(name, 0) + 1

        # determine the recognized face with the largest number of votes: (notes: in the event of an unlikely
        # tie, Python will select first entry in the dictionary)
        name = max(counts, key=counts.get)
    names.append(name)

# loop over the recognized faces
for ((top, right, bottom, left), name) in zip(boxes, names):
    # draw the predicted face name on the image
    cv2.rectangle(image, (left, top), (right, bottom), (0, 255, 0), 2)
    y = top - 15 if top - 15 > 15 else top + 15
    cv2.putText(image, name, (left, y), cv2.FONT_HERSHEY_SIMPLEX,
                0.75, (0, 255, 0), 2)

# show the output image
#cv2.imshow("Image", image)
cv2_imshow(image)
cv2.waitKey(0)
